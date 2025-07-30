import mimetypes
import os
from pathlib import Path
from urllib.parse import unquote, urlparse
import subprocess
import json
from typing import Dict, Any

import opendal
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse, JSONResponse

# Create a router
router = APIRouter(prefix="/api/proxy", tags=["proxy"])

# Cache for operator instances
operators: dict[str, opendal.Operator] = {}

# Get workspace root directory (assuming we're running from the project root)
WORKSPACE_ROOT = Path(os.getcwd()).absolute()

def get_operator(scheme: str, host: str | None = None) -> opendal.Operator:
    """Get or create an opendal Operator for the given scheme."""
    key = f"{scheme}://{host}" if host else scheme

    if key in operators:
        return operators[key]

    if scheme in {"fs", "file"}:
        # For filesystem storage - using default settings without root
        # This will use the OS filesystem directly, and we'll handle paths explicitly
        op = opendal.Operator("fs")
        operators[key] = op
        return op
    if scheme == "s3":
        # For S3 storage (requires credentials)
        if not host:
            host = os.environ.get("S3_ENDPOINT", "s3.amazonaws.com")

        op = opendal.Operator("s3", {
            "root": "/",
            "bucket": host,
            "endpoint": os.environ.get("S3_ENDPOINT", "https://s3.amazonaws.com"),
            "access_key_id": os.environ.get("AWS_ACCESS_KEY_ID", ""),
            "secret_access_key": os.environ.get("AWS_SECRET_ACCESS_KEY", ""),
            "region": os.environ.get("AWS_REGION", "us-east-1"),
        })
        operators[key] = op
        return op
    # Add more storage backends as needed
    msg = f"Unsupported storage scheme: {scheme}"
    raise ValueError(msg)

def get_mime_type(path: str) -> str:
    """Get the MIME type for a file based on its extension."""
    mime_type, _ = mimetypes.guess_type(path)
    return mime_type or "application/octet-stream"

def get_path_from_url(url: str, data_directory: str | None = None) -> tuple[str, str, str]:
    """Parse a URL and extract the scheme, host (if applicable), and path."""
    parsed = urlparse(url)
    scheme = parsed.scheme or "fs"
    path = parsed.path
    host = parsed.netloc

    # Handle special cases for fs:// protocol
    if scheme == "fs":
        # Special handling for fs://./... URLs (packed evaluation paths)
        if host == "." and path.startswith("/"):
            # This is a packed evaluation path like fs://./resources/...
            # Reconstruct the original relative path
            path = "." + path  # becomes "./resources/..."
            host = None
            
            # Now resolve the relative path
            if data_directory:
                # Resolve relative to the data directory's parent (the packed eval root)
                data_dir_path = Path(data_directory)
                if data_dir_path.name == "data":
                    # This is a packed evaluation structure
                    eval_root = data_dir_path.parent
                    path = str(eval_root / path[2:])
                else:
                    # Not a standard packed structure, resolve relative to data directory
                    path = str(Path(data_directory) / path[2:])
            else:
                # Fallback to workspace root
                path = os.path.join(WORKSPACE_ROOT, path[2:])
        # For fs:// URLs, we want absolute paths for security
        elif host:
            if host.startswith("/"):
                # Absolute path from root - use as is
                path = f"{host}{path}"
            else:
                # Relative path - resolve against workspace
                path = os.path.join(WORKSPACE_ROOT, host, path.lstrip("/"))
            host = None
        else:
            # No host provided, handle both absolute and relative paths
            if not path.startswith("/"):
                # Relative path - resolve against appropriate base directory
                if path.startswith("./"):
                    # Handle packed evaluation paths that start with "./"
                    if data_directory:
                        # Resolve relative to the data directory's parent (the packed eval root)
                        data_dir_path = Path(data_directory)
                        if data_dir_path.name == "data":
                            # This is a packed evaluation structure
                            eval_root = data_dir_path.parent
                            path = str(eval_root / path[2:])
                        else:
                            # Not a standard packed structure, resolve relative to data directory
                            path = str(Path(data_directory) / path[2:])
                    else:
                        # Fallback to workspace root
                        path = os.path.join(WORKSPACE_ROOT, path[2:])
                else:
                    # Other relative paths - resolve against workspace or data directory
                    base_dir = data_directory if data_directory else WORKSPACE_ROOT
                    path = os.path.join(base_dir, path)
            # For absolute paths, use as-is

    # Decode URL encoding
    path = unquote(path)

    return scheme, host, path

def get_file_size_str(size_in_bytes: int) -> str:
    """Convert file size in bytes to human-readable string."""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size_in_bytes < 1024.0:
            return f"{size_in_bytes:.1f} {unit}"
        size_in_bytes /= 1024.0
    return f"{size_in_bytes:.1f} PB"

def get_image_metadata(file_path: str) -> Dict[str, Any]:
    """Extract metadata from an image file using PIL."""
    try:
        from PIL import Image
        with Image.open(file_path) as img:
            size_bytes = os.path.getsize(file_path)
            return {
                "format": img.format,
                "width": img.width,
                "height": img.height,
                "size": get_file_size_str(size_bytes),
            }
    except Exception as e:
        import traceback
        print(f"Error extracting image metadata: {e}\n{traceback.format_exc()}")
        return {
            "format": os.path.splitext(file_path)[1][1:].upper(),
            "size": get_file_size_str(os.path.getsize(file_path)),
        }

def get_video_metadata(file_path: str) -> Dict[str, Any]:
    """Extract metadata from a video file using ffprobe."""
    try:
        # Try using ffprobe if installed
        cmd = [
            "ffprobe",
            "-v", "error",
            "-select_streams", "v:0",
            "-show_entries", "stream=width,height,codec_name,avg_frame_rate,duration",
            "-show_entries", "format=size,format_name",
            "-of", "json",
            file_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        
        # Extract relevant information
        stream_info = data.get("streams", [{}])[0]
        format_info = data.get("format", {})
        
        # Calculate FPS
        fps_str = stream_info.get("avg_frame_rate", "")
        fps = None
        if fps_str and fps_str != "0/0":
            try:
                num, den = map(int, fps_str.split("/"))
                if den != 0:
                    fps = round(num / den, 1)
            except (ValueError, ZeroDivisionError):
                pass
                
        # Format metadata
        size_bytes = int(format_info.get("size", 0))
        return {
            "format": format_info.get("format_name", "").split(",")[0].upper(),
            "width": stream_info.get("width"),
            "height": stream_info.get("height"),
            "fps": fps,
            "duration": float(stream_info.get("duration", 0)),
            "codec": stream_info.get("codec_name", "").upper(),
            "size": get_file_size_str(size_bytes),
        }
    except (subprocess.SubprocessError, json.JSONDecodeError) as e:
        # If ffprobe fails, return basic info
        import traceback
        print(f"Error with ffprobe: {e}\n{traceback.format_exc()}")
        
        # Fallback to basic file information
        try:
            size_bytes = os.path.getsize(file_path)
            return {
                "format": os.path.splitext(file_path)[1][1:].upper(),
                "size": get_file_size_str(size_bytes),
            }
        except Exception as fallback_error:
            print(f"Fallback error: {fallback_error}")
            return {"format": "Unknown"}

@router.get("/metadata")
async def get_media_metadata(url: str, request: Request):
    """Get metadata for a media file (image or video).
    
    Args:
        url: The URL to the resource, e.g., fs://path/to/file, s3://bucket/path/to/file
    
    Returns:
        A JSON object with metadata about the media file.
    """
    try:
        # Get data directory context from app state
        data_directory = getattr(request.app.state, 'data_directory', None)
        data_directory_str = str(data_directory) if data_directory else None
        scheme, host, path = get_path_from_url(url, data_directory_str)
        
        # Currently only support local filesystem metadata extraction
        if scheme not in {"fs", "file"}:
            raise HTTPException(
                status_code=400, 
                detail="Metadata extraction is only supported for local files"
            )
            
        # Path is already absolute by this point
        abs_path = path
        
        # Check if file exists
        if not os.path.exists(abs_path):
            raise HTTPException(
                status_code=404, 
                detail=f"Resource not found: {url}, resolved path: {abs_path}"
            )
            
        # Determine file type by mime type
        mime_type = get_mime_type(abs_path)
        
        if mime_type.startswith("image/"):
            metadata = get_image_metadata(abs_path)
        elif mime_type.startswith("video/"):
            metadata = get_video_metadata(abs_path)
        else:
            # For other files, return basic info
            size_bytes = os.path.getsize(abs_path)
            metadata = {
                "format": os.path.splitext(abs_path)[1][1:].upper() or "UNKNOWN",
                "size": get_file_size_str(size_bytes),
            }
            
        return JSONResponse(content=metadata)
        
    except Exception as e:
        # Detailed error for debugging
        import traceback
        error_detail = f"Error: {e!s}\nURL: {url}\n{traceback.format_exc()}"
        raise HTTPException(status_code=500, detail=error_detail)

@router.get("/resource")
async def proxy_resource(url: str, request: Request):
    """Proxy a resource from any supported storage backend.

    Args:
        url: The URL to the resource, e.g., fs://path/to/file, s3://bucket/path/to/file

    """
    try:
        # Get data directory context from app state
        data_directory = getattr(request.app.state, 'data_directory', None)
        data_directory_str = str(data_directory) if data_directory else None
        scheme, host, path = get_path_from_url(url, data_directory_str)

        # For filesystem scheme, resolve to absolute path
        if scheme in {"fs", "file"}:
            # Path is already absolute by this point
            abs_path = path

            # Check if file exists directly using os.path
            if not os.path.exists(abs_path):
                raise HTTPException(status_code=404, detail=f"Resource not found: {url}, resolved path: {abs_path}")

            # Use FileResponse directly for filesystem files instead of OpenDAL
            # This is more direct and likely to work better with the local filesystem
            from fastapi.responses import FileResponse
            return FileResponse(
                abs_path,
                media_type=get_mime_type(abs_path),
                headers={
                    "Cache-Control": "public, max-age=86400, immutable",  # Cache for 24 hours with immutable hint
                    "Access-Control-Allow-Origin": "*",
                    "Accept-Ranges": "bytes",  # Enable range requests for better video streaming
                },
            )

        # For other schemes like S3, use OpenDAL
        op = get_operator(scheme, host)

        # Check if file exists
        if not await op.is_exist(path):
            raise HTTPException(status_code=404, detail=f"Resource not found: {url}, resolved path: {path}")

        # Get file stats for content type and size
        stat = await op.stat(path)
        size = stat.content_length()
        mime_type = get_mime_type(path)

        # Stream the file content
        async def content_iterator():
            # Read the file in chunks to avoid loading large files into memory
            with await op.reader(path) as reader:
                while chunk := await reader.read(8192):  # 8KB chunks
                    yield chunk

        return StreamingResponse(
            content_iterator(),
            media_type=mime_type,
            headers={
                "Content-Length": str(size),
                "Cache-Control": "public, max-age=86400, immutable",  # Cache for 24 hours
                "Access-Control-Allow-Origin": "*",
                "Accept-Ranges": "bytes",
            },
        )

    except Exception as e:
        # More detailed error for debugging
        import traceback
        error_detail = f"Error: {e!s}\nURL: {url}\n{traceback.format_exc()}"
        raise HTTPException(status_code=500, detail=error_detail)

def rewrite_resource_url(url: str | None, request: Request) -> str | None:
    """Rewrite resource URLs to go through the proxy.

    Args:
        url: The original URL (fs://, s3://, etc.)
        request: The current request for building the proxy URL

    Returns:
        The rewritten URL pointing to the proxy endpoint

    """
    if not url:
        return None

    # If already a HTTP URL, return as is
    if url.startswith(("http://", "https://")):
        return url

    # Build the proxy URL
    base_url = str(request.base_url).rstrip("/")
    return f"{base_url}/api/proxy/resource?url={url}"

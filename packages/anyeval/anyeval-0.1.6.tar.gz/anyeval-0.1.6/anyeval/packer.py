"""
Resource packing functionality for AnyEval.
Packs evaluation parquet files and their referenced resources into a portable folder structure.
"""

import json
import logging
import os
import shutil
from pathlib import Path
from typing import Dict, List, Set, Any
from urllib.parse import urlparse
import pandas as pd
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)


class EvalPacker:
    """Pack evaluation data and resources into a portable structure."""
    
    def __init__(self, source_path: Path, output_path: Path):
        """
        Initialize the packer.
        
        Args:
            source_path: Path to parquet file or directory containing parquet files
            output_path: Path where the packed evaluation will be created
        """
        self.source_path = Path(source_path)
        self.output_path = Path(output_path)
        self.resource_map: Dict[str, str] = {}  # original_path -> relative_path
        self.packed_resources: Set[str] = set()
        
    def pack(self) -> Dict[str, Any]:
        """
        Pack the evaluation data and resources.
        
        Returns:
            Metadata about the packed evaluation
        """
        logger.info(f"Starting to pack evaluation from {self.source_path} to {self.output_path}")
        
        # Create output directory structure
        self._create_directory_structure()
        
        # Find all parquet files
        parquet_files = self._find_parquet_files()
        if not parquet_files:
            raise ValueError(f"No parquet files found in {self.source_path}")
        
        logger.info(f"Found {len(parquet_files)} parquet files to process")
        
        # Collect all resource paths from parquet files
        all_resources = self._collect_resource_paths(parquet_files)
        logger.info(f"Found {len(all_resources)} unique resources to pack")
        
        # Copy resources and build mapping
        self._copy_resources(all_resources)
        
        # Process and copy parquet files with updated paths
        copied_files = self._process_parquet_files(parquet_files)
        
        # Create metadata
        metadata = self._create_metadata(copied_files, len(all_resources))
        
        # Write metadata
        metadata_path = self.output_path / "metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2, default=str)
        
        logger.info(f"Successfully packed evaluation to {self.output_path}")
        return metadata
    
    def _create_directory_structure(self):
        """Create the packed evaluation directory structure."""
        self.output_path.mkdir(parents=True, exist_ok=True)
        (self.output_path / "data").mkdir(exist_ok=True)
        (self.output_path / "resources").mkdir(exist_ok=True)
        (self.output_path / "resources" / "images").mkdir(exist_ok=True)
        (self.output_path / "resources" / "videos").mkdir(exist_ok=True)
        (self.output_path / "resources" / "audio").mkdir(exist_ok=True)
    
    def _find_parquet_files(self) -> List[Path]:
        """Find all parquet files in the source path."""
        if self.source_path.is_file() and self.source_path.suffix == ".parquet":
            return [self.source_path]
        elif self.source_path.is_dir():
            return list(self.source_path.glob("*.parquet"))
        else:
            return []
    
    def _collect_resource_paths(self, parquet_files: List[Path]) -> Set[str]:
        """Collect all resource paths from parquet files."""
        all_resources = set()
        
        for parquet_file in parquet_files:
            logger.info(f"Scanning resources in {parquet_file.name}")
            df = pd.read_parquet(parquet_file)
            
            for _, row in df.iterrows():
                # Check input fields for media resources
                if isinstance(row.get('input'), dict):
                    for key, value in row['input'].items():
                        if isinstance(key, str) and key.startswith('@') and '->' in key:
                            if isinstance(value, str) and value.startswith('fs://'):
                                all_resources.add(value)
                
                # Check output fields for media resources
                if isinstance(row.get('output'), dict):
                    for key, value in row['output'].items():
                        if isinstance(key, str) and key.startswith('@') and '->' in key:
                            if isinstance(value, str) and value.startswith('fs://'):
                                all_resources.add(value)
        
        return all_resources
    
    def _copy_resources(self, resources: Set[str]):
        """Copy resources to the packed structure and build path mapping."""
        logger.info("Copying resources...")
        
        for resource_url in resources:
            try:
                # Parse the fs:// URL to get the actual file path
                parsed = urlparse(resource_url)
                if parsed.scheme != 'fs':
                    logger.warning(f"Skipping non-fs resource: {resource_url}")
                    continue
                
                source_file = Path(parsed.path)
                if not source_file.exists():
                    logger.warning(f"Resource not found: {source_file}")
                    continue
                
                # Determine target subdirectory based on file type
                file_ext = source_file.suffix.lower()
                if file_ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']:
                    subdir = "images"
                elif file_ext in ['.mp4', '.avi', '.mov', '.webm', '.mkv']:
                    subdir = "videos"
                elif file_ext in ['.mp3', '.wav', '.ogg', '.m4a', '.flac']:
                    subdir = "audio"
                else:
                    # Default to images directory for unknown types
                    subdir = "images"
                    logger.warning(f"Unknown file type {file_ext}, placing in images directory")
                
                # Create target path with same filename
                target_file = self.output_path / "resources" / subdir / source_file.name
                
                # Handle filename conflicts by adding a counter
                counter = 1
                original_target = target_file
                while target_file.exists():
                    stem = original_target.stem
                    suffix = original_target.suffix
                    target_file = original_target.parent / f"{stem}_{counter}{suffix}"
                    counter += 1
                
                # Copy the file
                shutil.copy2(source_file, target_file)
                
                # Create relative path for the packed structure
                relative_path = f"resources/{subdir}/{target_file.name}"
                self.resource_map[resource_url] = relative_path
                self.packed_resources.add(str(target_file))
                
                logger.debug(f"Copied {source_file} -> {target_file}")
                
            except Exception as e:
                logger.error(f"Failed to copy resource {resource_url}: {e}")
    
    def _process_parquet_files(self, parquet_files: List[Path]) -> List[str]:
        """Process parquet files and update resource paths."""
        logger.info("Processing parquet files...")
        
        copied_files = []
        
        for parquet_file in parquet_files:
            logger.info(f"Processing {parquet_file.name}")
            df = pd.read_parquet(parquet_file)
            
            # Update resource paths in the dataframe
            for idx, row in df.iterrows():
                # Update input fields
                if isinstance(row.get('input'), dict):
                    updated_input = row['input'].copy()
                    for key, value in updated_input.items():
                        if isinstance(key, str) and key.startswith('@') and '->' in key:
                            if isinstance(value, str) and value in self.resource_map:
                                updated_input[key] = f"fs://./{self.resource_map[value]}"
                    df.at[idx, 'input'] = updated_input
                
                # Update output fields
                if isinstance(row.get('output'), dict):
                    updated_output = row['output'].copy()
                    for key, value in updated_output.items():
                        if isinstance(key, str) and key.startswith('@') and '->' in key:
                            if isinstance(value, str) and value in self.resource_map:
                                updated_output[key] = f"fs://./{self.resource_map[value]}"
                    df.at[idx, 'output'] = updated_output
            
            # Save the updated parquet file
            target_file = self.output_path / "data" / parquet_file.name
            df.to_parquet(target_file, index=False)
            copied_files.append(parquet_file.name)
            
            logger.info(f"Saved updated parquet file: {target_file}")
        
        return copied_files
    
    def _create_metadata(self, parquet_files: List[str], resource_count: int) -> Dict[str, Any]:
        """Create metadata for the packed evaluation."""
        # Create file list for all packed files
        file_list = []
        
        # Add parquet files
        for parquet_file in parquet_files:
            file_path = self.output_path / "data" / parquet_file
            if file_path.exists():
                file_list.append({
                    "path": f"data/{parquet_file}",
                    "type": "parquet",
                    "size": file_path.stat().st_size
                })
        
        # Add resource files
        for resource_path in self.packed_resources:
            resource_file = Path(resource_path)
            if resource_file.exists():
                relative_path = resource_file.relative_to(self.output_path)
                file_list.append({
                    "path": str(relative_path),
                    "type": "resource",
                    "size": resource_file.stat().st_size
                })
        
        # Add metadata file itself
        file_list.append({
            "path": "metadata.json",
            "type": "metadata",
            "size": 0  # Will be updated after file is written
        })
        
        return {
            "pack_id": str(uuid.uuid4()),
            "created_at": datetime.now().isoformat(),
            "anyeval_version": "0.1.6",  # Could be read from __about__.py
            "source_path": str(self.source_path),
            "parquet_files": parquet_files,
            "resource_count": resource_count,
            "packed_resources": len(self.packed_resources),
            "file_list": file_list,
            "structure": {
                "data/": "Parquet files with updated resource paths",
                "resources/images/": "Image files referenced in the evaluation",
                "resources/videos/": "Video files referenced in the evaluation", 
                "resources/audio/": "Audio files referenced in the evaluation",
                "metadata.json": "This metadata file"
            },
            "usage": {
                "command": f"anyeval run {self.output_path / 'data'}",
                "description": "Run anyeval on the data/ directory to view this packed evaluation"
            }
        }


class EvalMerger:
    """Merge two packed evaluation folders."""
    
    def __init__(self, source1_path: Path, source2_path: Path, output_path: Path):
        """
        Initialize the merger.
        
        Args:
            source1_path: Path to first packed evaluation folder
            source2_path: Path to second packed evaluation folder
            output_path: Path where the merged evaluation will be created
        """
        self.source1_path = Path(source1_path)
        self.source2_path = Path(source2_path)
        self.output_path = Path(output_path)
        self.file_conflicts: Dict[str, List[str]] = {}
        
    def merge(self) -> Dict[str, Any]:
        """
        Merge two packed evaluations.
        
        Returns:
            Metadata about the merged evaluation
        """
        logger.info(f"Starting to merge {self.source1_path} and {self.source2_path} to {self.output_path}")
        
        # Validate source paths
        self._validate_sources()
        
        # Create output directory structure
        self._create_directory_structure()
        
        # Load metadata from both sources
        metadata1 = self._load_metadata(self.source1_path)
        metadata2 = self._load_metadata(self.source2_path)
        
        # Merge data files (parquet files)
        merged_parquet_files = self._merge_data_files()
        
        # Merge resource files
        merged_resources = self._merge_resources()
        
        # Create merged metadata
        merged_metadata = self._create_merged_metadata(metadata1, metadata2, merged_parquet_files, merged_resources)
        
        # Write merged metadata
        metadata_path = self.output_path / "metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(merged_metadata, f, indent=2, default=str)
        
        logger.info(f"Successfully merged evaluations to {self.output_path}")
        return merged_metadata
    
    def _validate_sources(self):
        """Validate that source paths are valid packed evaluations."""
        for source_path in [self.source1_path, self.source2_path]:
            if not source_path.exists():
                raise ValueError(f"Source path does not exist: {source_path}")
            
            metadata_path = source_path / "metadata.json"
            if not metadata_path.exists():
                raise ValueError(f"Not a valid packed evaluation (missing metadata.json): {source_path}")
            
            data_path = source_path / "data"
            if not data_path.exists():
                raise ValueError(f"Not a valid packed evaluation (missing data directory): {source_path}")
    
    def _create_directory_structure(self):
        """Create the merged evaluation directory structure."""
        self.output_path.mkdir(parents=True, exist_ok=True)
        (self.output_path / "data").mkdir(exist_ok=True)
        (self.output_path / "resources").mkdir(exist_ok=True)
        (self.output_path / "resources" / "images").mkdir(exist_ok=True)
        (self.output_path / "resources" / "videos").mkdir(exist_ok=True)
        (self.output_path / "resources" / "audio").mkdir(exist_ok=True)
    
    def _load_metadata(self, source_path: Path) -> Dict[str, Any]:
        """Load metadata from a packed evaluation."""
        metadata_path = source_path / "metadata.json"
        with open(metadata_path, 'r') as f:
            return json.load(f)
    
    def _merge_data_files(self) -> List[str]:
        """Merge parquet files from both sources, handling name conflicts."""
        merged_files = []
        
        # Copy files from source1
        source1_data = self.source1_path / "data"
        if source1_data.exists():
            for parquet_file in source1_data.glob("*.parquet"):
                target_file = self.output_path / "data" / parquet_file.name
                shutil.copy2(parquet_file, target_file)
                merged_files.append(parquet_file.name)
                logger.debug(f"Copied data file: {parquet_file.name}")
        
        # Copy files from source2, handling conflicts
        source2_data = self.source2_path / "data"
        if source2_data.exists():
            for parquet_file in source2_data.glob("*.parquet"):
                target_file = self.output_path / "data" / parquet_file.name
                
                # Handle filename conflicts
                if target_file.exists():
                    original_name = parquet_file.name
                    counter = 1
                    stem = parquet_file.stem
                    suffix = parquet_file.suffix
                    
                    while target_file.exists():
                        new_name = f"{stem}_merged_{counter}{suffix}"
                        target_file = self.output_path / "data" / new_name
                        counter += 1
                    
                    self.file_conflicts.setdefault("data", []).append(f"{original_name} -> {target_file.name}")
                    logger.info(f"Data file conflict resolved: {original_name} -> {target_file.name}")
                
                shutil.copy2(parquet_file, target_file)
                merged_files.append(target_file.name)
                logger.debug(f"Copied data file: {target_file.name}")
        
        return merged_files
    
    def _merge_resources(self) -> int:
        """Merge resource files from both sources, handling name conflicts."""
        merged_count = 0
        
        # Copy resources from both sources
        for source_path in [self.source1_path, self.source2_path]:
            source_resources = source_path / "resources"
            if not source_resources.exists():
                continue
            
            for subdir in ["images", "videos", "audio"]:
                source_subdir = source_resources / subdir
                if not source_subdir.exists():
                    continue
                
                target_subdir = self.output_path / "resources" / subdir
                
                for resource_file in source_subdir.iterdir():
                    if resource_file.is_file():
                        target_file = target_subdir / resource_file.name
                        
                        # Handle filename conflicts
                        if target_file.exists():
                            original_name = resource_file.name
                            counter = 1
                            stem = resource_file.stem
                            suffix = resource_file.suffix
                            
                            while target_file.exists():
                                new_name = f"{stem}_merged_{counter}{suffix}"
                                target_file = target_subdir / new_name
                                counter += 1
                            
                            self.file_conflicts.setdefault(f"resources/{subdir}", []).append(f"{original_name} -> {target_file.name}")
                            logger.info(f"Resource conflict resolved: {subdir}/{original_name} -> {target_file.name}")
                        
                        shutil.copy2(resource_file, target_file)
                        merged_count += 1
                        logger.debug(f"Copied resource: {subdir}/{target_file.name}")
        
        return merged_count
    
    def _create_merged_metadata(self, metadata1: Dict[str, Any], metadata2: Dict[str, Any], 
                               parquet_files: List[str], resource_count: int) -> Dict[str, Any]:
        """Create metadata for the merged evaluation."""
        # Create file list for merged files
        file_list = []
        
        # Add parquet files
        for parquet_file in parquet_files:
            file_path = self.output_path / "data" / parquet_file
            if file_path.exists():
                file_list.append({
                    "path": f"data/{parquet_file}",
                    "type": "parquet",
                    "size": file_path.stat().st_size
                })
        
        # Add resource files
        for subdir in ["images", "videos", "audio"]:
            resource_dir = self.output_path / "resources" / subdir
            if resource_dir.exists():
                for resource_file in resource_dir.iterdir():
                    if resource_file.is_file():
                        file_list.append({
                            "path": f"resources/{subdir}/{resource_file.name}",
                            "type": "resource",
                            "size": resource_file.stat().st_size
                        })
        
        # Add metadata file itself
        file_list.append({
            "path": "metadata.json",
            "type": "metadata",
            "size": 0  # Will be updated after file is written
        })
        
        return {
            "pack_id": str(uuid.uuid4()),
            "created_at": datetime.now().isoformat(),
            "anyeval_version": "0.1.6",
            "merge_info": {
                "source1_path": str(self.source1_path),
                "source2_path": str(self.source2_path),
                "source1_pack_id": metadata1.get("pack_id"),
                "source2_pack_id": metadata2.get("pack_id"),
                "file_conflicts": self.file_conflicts
            },
            "parquet_files": parquet_files,
            "resource_count": resource_count,
            "file_list": file_list,
            "structure": {
                "data/": "Merged parquet files with updated resource paths",
                "resources/images/": "Merged image files from both evaluations",
                "resources/videos/": "Merged video files from both evaluations", 
                "resources/audio/": "Merged audio files from both evaluations",
                "metadata.json": "This metadata file"
            },
            "usage": {
                "command": f"anyeval run {self.output_path / 'data'}",
                "description": "Run anyeval on the data/ directory to view this merged evaluation"
            }
        }


def pack_evaluation(source_path: str | Path, output_path: str | Path, overwrite: bool = False) -> Dict[str, Any]:
    """
    Pack an evaluation dataset and its resources into a portable structure.
    
    Args:
        source_path: Path to parquet file or directory containing parquet files
        output_path: Path where the packed evaluation will be created
        overwrite: Whether to overwrite existing output directory
    
    Returns:
        Metadata about the packed evaluation
    
    Raises:
        ValueError: If source path doesn't exist or no parquet files found
        FileExistsError: If output path exists and overwrite is False
    """
    source_path = Path(source_path)
    output_path = Path(output_path)
    
    if not source_path.exists():
        raise ValueError(f"Source path does not exist: {source_path}")
    
    if output_path.exists() and not overwrite:
        raise FileExistsError(f"Output path already exists: {output_path}. Use overwrite=True to replace it.")
    
    if output_path.exists() and overwrite:
        shutil.rmtree(output_path)
    
    packer = EvalPacker(source_path, output_path)
    return packer.pack()


def merge_evaluations(source1_path: str | Path, source2_path: str | Path, output_path: str | Path, overwrite: bool = False) -> Dict[str, Any]:
    """
    Merge two packed evaluation folders into a single evaluation.
    
    Args:
        source1_path: Path to first packed evaluation folder
        source2_path: Path to second packed evaluation folder
        output_path: Path where the merged evaluation will be created
        overwrite: Whether to overwrite existing output directory
    
    Returns:
        Metadata about the merged evaluation
    
    Raises:
        ValueError: If source paths don't exist or are not valid packed evaluations
        FileExistsError: If output path exists and overwrite is False
    """
    source1_path = Path(source1_path)
    source2_path = Path(source2_path)
    output_path = Path(output_path)
    
    if output_path.exists() and not overwrite:
        raise FileExistsError(f"Output path already exists: {output_path}. Use overwrite=True to replace it.")
    
    if output_path.exists() and overwrite:
        shutil.rmtree(output_path)
    
    merger = EvalMerger(source1_path, source2_path, output_path)
    return merger.merge()
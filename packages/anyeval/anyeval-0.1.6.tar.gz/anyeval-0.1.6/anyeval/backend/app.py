import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any, List, Optional, Union

import pandas as pd
import duckdb
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pandas import DataFrame
from pydantic import BaseModel, Field

from anyeval.backend.proxy import rewrite_resource_url
from anyeval.backend.proxy import router as proxy_router

logger = logging.getLogger("anyeval.backend.app")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter("[%(asctime)s] %(levelname)s in %(name)s: %(message)s")
handler.setFormatter(formatter)
if not logger.hasHandlers():
    logger.addHandler(handler)


class DataItem(BaseModel):
    id: str
    dataset: str
    input: dict[str, Any] = {}
    output: dict[str, Any] = {}
    label: dict[str, Any] | None = None
    created_at: str | None = None
    updated_at: str | None = None


class StarRating(BaseModel):
    item_id: str
    rating: int = Field(ge=1, le=5)
    comment: str | None = None
    created_at: str | None = None


class DataResponse(BaseModel):
    items: list[DataItem]
    total: int


class FileInfo(BaseModel):
    name: str
    path: str


# New models for advanced filtering
class FilterCondition(BaseModel):
    key: str
    op: str  # '=', '>', '<', '>=', '<=', '!=', 'IN', 'LIKE'
    val: Optional[Union[str, int, float]] = None
    vals: Optional[List[Union[str, int, float]]] = None


class LogicOperator(BaseModel):
    logic: str  # 'AND', 'OR'


class FilterRequest(BaseModel):
    filters: List[Union[FilterCondition, LogicOperator]] = []
    dataset: Optional[str] = None
    file: Optional[str] = None
    offset: int = 0
    limit: int = 100
    input_fields: List[str] = Field(default_factory=list)
    output_fields: List[str] = Field(default_factory=list)
    include_all_fields: bool = False


def create_app(df: DataFrame, files_list: list[FileInfo] | None = None, data_directory: Path | None = None) -> FastAPI:
    """Create a FastAPI app with the loaded dataframe and files info."""
    app = FastAPI(title="AnyEval API")
    
    # Store data directory context for relative path resolution
    app.state.data_directory = data_directory

    # Set up CORS to allow the frontend to access the API
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include the proxy router
    app.include_router(proxy_router)

    # Get the directory of the static files
    static_dir = Path(__file__).parent / "static"

    # Create a mapping of file names to DataFrames and file paths
    file_dataframes = {}
    file_paths = {}

    # Build dataset label indices for faster filtering
    dataset_label_indices = {}

    # NEW: Add a global label index that works across all datasets
    global_label_index = {"keys": set(), "key_values_map": {}}

    if files_list and len(files_list) > 1:
        # For multiple files, create a mapping of file names to their respective data
        for file_info in files_list:
            file_name = file_info["name"]
            file_path = file_info["path"]
            try:
                # Load data directly from file
                file_df = pd.read_parquet(file_path)
                file_dataframes[file_name] = file_df
                file_paths[file_name] = file_path

                # Build label indices for each dataset in this file
                build_dataset_label_indices(
                    file_df, dataset_label_indices, global_label_index
                )

            except Exception:
                pass
    # For single file case, just use the main dataframe
    elif files_list and len(files_list) == 1:
        file_name = files_list[0]["name"]
        file_path = files_list[0]["path"]
        file_dataframes[file_name] = df
        file_paths[file_name] = file_path

    # Build label indices for the main dataframe
    build_dataset_label_indices(df, dataset_label_indices, global_label_index)

    # Helper function to process resource URLs in data items
    def process_resource_urls(
        data_item: dict[str, Any], request: Request
    ) -> dict[str, Any]:
        """Process all resource URLs in a data item and convert them to proxied URLs."""
        processed_item = data_item.copy()

        # Process input dictionary
        if "input" in processed_item and isinstance(processed_item["input"], dict):
            for key, value in processed_item["input"].items():
                if isinstance(key, str) and key.startswith("@") and "->" in key:
                    # This is a resource field (e.g., @image->input_image)
                    if isinstance(value, str):
                        processed_item["input"][key] = rewrite_resource_url(
                            value, request
                        )

        # Process output dictionary
        if "output" in processed_item and isinstance(processed_item["output"], dict):
            for key, value in processed_item["output"].items():
                if isinstance(key, str) and key.startswith("@") and "->" in key:
                    # This is a resource field (e.g., @video->output_video)
                    if isinstance(value, str):
                        processed_item["output"][key] = rewrite_resource_url(
                            value, request
                        )

        return processed_item

    # Helper function to build SQL from filter conditions
    def build_sql_from_filters(
        filters: List[Union[FilterCondition, LogicOperator]], parquet_path: str
    ) -> tuple[str, list]:
        """Build a SQL query from filter conditions."""
        if not filters:
            return f"SELECT * FROM '{parquet_path}'", []

        sql_parts = [f"SELECT * FROM '{parquet_path}' WHERE "]
        params = []

        for i, condition in enumerate(filters):
            if hasattr(condition, "logic"):
                # This is a logic operator
                sql_parts.append(f" {condition.logic} ")
            else:
                # This is a filter condition
                key = condition.key
                op = condition.op.upper()

                # Handle different field types
                # List of standard top-level columns that are not in the label JSON
                top_level_columns = ["id", "dataset", "created_at", "updated_at"]

                if key in top_level_columns:
                    # This is a top-level column, reference it directly
                    json_path = key
                elif "." not in key:
                    # Assume it's a label field if it doesn't have a dot
                    json_path = f"label['{key}']"
                else:
                    # For other fields with dots, use as is (could be nested JSON)
                    json_path = key

                if op == "IN" and condition.vals:
                    placeholders = []
                    for val in condition.vals:
                        placeholders.append("?")
                        params.append(val)

                    sql_parts.append(f"{json_path} IN ({', '.join(placeholders)})")
                elif op == "LIKE" and condition.val is not None:
                    sql_parts.append(f"{json_path} LIKE ?")
                    params.append(f"%{condition.val}%")
                elif condition.val is not None:
                    sql_parts.append(f"{json_path} {op} ?")
                    params.append(condition.val)

        return "".join(sql_parts), params

    # Keep existing GET endpoint for backward compatibility
    @app.get("/api/data", response_model=DataResponse)
    async def get_data(
        request: Request,
        offset: int = 0,
        limit: int = 100,
        dataset: str | None = None,
        search: str | None = None,
        label: str | None = None,
        file: str | None = None,
    ):
        # Initialize empty lists
        label_keys = []
        label_values = []
        input_fields = []
        output_fields = []

        # Get all values with the same key name, including duplicates
        for key, value in request.query_params._list:
            if key == "label_keys":
                label_keys.append(value)
            elif key == "label_values":
                label_values.append(value)
            elif key == "input_fields":
                input_fields.append(value)
            elif key == "output_fields":
                output_fields.append(value)

        # Use the existing implementation for backward compatibility
        # ... existing get_data implementation ...
        # Determine which DataFrame to use based on file parameter
        filtered_df = df.copy()

        # If file parameter is provided and we have multiple files
        if file and files_list and len(files_list) > 1 and file in file_dataframes:
            filtered_df = file_dataframes[file].copy()

        # Apply dataset filter if provided
        if dataset:
            filtered_df = filtered_df[filtered_df["dataset"] == dataset]

        # Apply search filter if provided
        if search and not search.isspace() and len(search) > 0:
            filtered_df = filtered_df[
                filtered_df.astype(str).apply(
                    lambda row: row.str.contains(search, case=False).any(), axis=1
                )
            ]

        # Apply legacy label filter if provided
        if label and not label.isspace() and len(label) > 0:
            # Convert label column to string for comparison
            filtered_df = filtered_df[
                filtered_df["label"].astype(str).str.contains(label, case=False)
            ]

        # Apply new label key-value filtering if provided
        if (len(label_keys) > 0 or len(label_values) > 0) and len(filtered_df) > 0:

            def label_filter(row):
                # If label is missing or not a dictionary, skip this row
                if row["label"] is None or not isinstance(row["label"], dict):
                    return False

                label_dict = row["label"]

                # If both keys and values are provided, perform a cross search
                # This will match ANY key with ANY value (so it works as multiple OR conditions)
                if len(label_keys) > 0 and len(label_values) > 0:
                    # For each key and each value, check if any combination matches
                    for key in label_keys:
                        # Skip if key doesn't exist in this label
                        if key not in label_dict:
                            continue

                        label_value = label_dict[key]
                        # Check if this label value matches any of the requested values
                        for value in label_values:
                            if str(label_value).lower() == str(value).lower():
                                return True

                    # If we got here, no matches were found
                    return False

                # If only keys are provided (no values)
                if len(label_keys) > 0 and len(label_values) == 0:
                    # Check if ANY of the requested keys exist in the label
                    return any(key in label_dict for key in label_keys)

                # If only values are provided (no keys)
                if len(label_values) > 0 and len(label_keys) == 0:
                    # Check if ANY label value matches ANY of the requested values
                    return any(
                        str(label_value).lower() == str(filter_value).lower()
                        for label_value in label_dict.values()
                        for filter_value in label_values
                    )

                # Fallback - should never reach here if either label_keys or label_values is provided
                return True

            # Apply the filter function to each row
            filtered_df = filtered_df[filtered_df.apply(label_filter, axis=1)]

        total = len(filtered_df)

        # Apply pagination
        if offset >= total:
            return {"items": [], "total": total}

        end_idx = min(offset + limit, total)
        page_df = filtered_df.iloc[offset:end_idx]

        # Convert to list of dictionaries
        items = page_df.to_dict(orient="records")

        # Process resource URLs in all items
        processed_items = [process_resource_urls(item, request) for item in items]

        # Filter input and output fields if specified
        if input_fields or output_fields:
            for item in processed_items:
                # Filter input fields
                if input_fields and "input" in item and isinstance(item["input"], dict):
                    filtered_input = {}
                    for field in input_fields:
                        if field in item["input"]:
                            filtered_input[field] = item["input"][field]
                    item["input"] = filtered_input

                # Filter output fields
                if (
                    output_fields
                    and "output" in item
                    and isinstance(item["output"], dict)
                ):
                    filtered_output = {}
                    for field in output_fields:
                        if field in item["output"]:
                            filtered_output[field] = item["output"][field]
                    item["output"] = filtered_output

        return {
            "items": processed_items,
            "total": total,
        }

    # Add new POST endpoint for advanced filtering with DuckDB
    @app.post("/api/data", response_model=DataResponse)
    async def post_data(request: Request, filter_request: FilterRequest):
        """Filter data using DuckDB with advanced filtering capabilities."""
        try:
            # Determine which file to use
            parquet_path = None
            if filter_request.file and filter_request.file in file_paths:
                # User selected a specific file
                parquet_path = file_paths[filter_request.file]
                logger.info(f"Using specific file: {parquet_path}")
            elif not filter_request.file and files_list and len(files_list) > 1:
                # No file selected and multiple files available - use all files
                # Create a union query across all parquet files
                logger.info("No specific file selected, will query all files")
                all_parquet_paths = [file_info["path"] for file_info in files_list]
                return await process_multiple_files(
                    request, filter_request, all_parquet_paths
                )
            elif files_list and len(files_list) == 1:
                # If only one file, use that
                parquet_path = file_paths[files_list[0]["name"]]
                logger.info(f"Only one file available, using: {parquet_path}")
            else:
                # No valid file specified or no files available
                raise HTTPException(
                    status_code=400,
                    detail="No valid file specified or no files available",
                )

            # Log the request for debugging
            logger.info(f"Processing filter request: {filter_request.dict()}")

            # Build SQL from filters
            filters = filter_request.filters

            # Add dataset filter if provided
            if filter_request.dataset:
                # Insert at the beginning if filters already exist
                if filters:
                    # Add AND operator after this condition if there are other filters
                    filters = [
                        FilterCondition(
                            key="dataset", op="=", val=filter_request.dataset
                        ),
                        LogicOperator(logic="AND"),
                    ] + filters
                else:
                    filters = [
                        FilterCondition(
                            key="dataset", op="=", val=filter_request.dataset
                        )
                    ]
            else:
                logger.info("No dataset filter specified, querying all datasets")

            # Build SQL query
            sql, params = build_sql_from_filters(filters, parquet_path)
            logger.info(f"Generated SQL: {sql}")
            logger.info(f"SQL Parameters: {params}")

            # Connect to DuckDB
            conn = duckdb.connect(database=":memory:")

            try:
                # Apply limit and offset for pagination
                paging_sql = (
                    f"{sql} LIMIT {filter_request.limit} OFFSET {filter_request.offset}"
                )

                # Execute count query for total
                count_sql = f"SELECT COUNT(*) as total FROM ({sql}) as filtered_data"
                logger.info(f"Count SQL: {count_sql}")

                total_result = conn.execute(count_sql, params).fetchone()
                total = total_result[0] if total_result else 0
                logger.info(f"Total matching records: {total}")

                # Execute main query
                result = conn.execute(paging_sql, params).fetch_df()
                logger.info(f"Fetched {len(result)} records")

                # Convert to list of dictionaries
                items = result.to_dict(orient="records")

                # Process resource URLs in all items
                processed_items = [
                    process_resource_urls(item, request) for item in items
                ]

                # Filter input and output fields if specified and include_all_fields is not True
                if (filter_request.input_fields or filter_request.output_fields) and not filter_request.include_all_fields:
                    for item in processed_items:
                        # Filter input fields
                        if (
                            filter_request.input_fields
                            and "input" in item
                            and isinstance(item["input"], dict)
                        ):
                            filtered_input = {}
                            for field in filter_request.input_fields:
                                if field in item["input"]:
                                    filtered_input[field] = item["input"][field]
                            item["input"] = filtered_input

                        # Filter output fields
                        if (
                            filter_request.output_fields
                            and "output" in item
                            and isinstance(item["output"], dict)
                        ):
                            filtered_output = {}
                            for field in filter_request.output_fields:
                                if field in item["output"]:
                                    filtered_output[field] = item["output"][field]
                            item["output"] = filtered_output

                return {
                    "items": processed_items,
                    "total": total,
                }
            except duckdb.duckdb.Error as db_error:
                # Specific handling for DuckDB errors
                error_msg = str(db_error)
                logger.error(f"DuckDB error: {error_msg}")

                # Add additional diagnostics
                try:
                    # Check if file exists and is readable
                    if not os.path.exists(parquet_path):
                        raise HTTPException(
                            status_code=400,
                            detail=f"Parquet file not found: {parquet_path}",
                        )

                    # Try to read file schema
                    schema_sql = f"DESCRIBE SELECT * FROM '{parquet_path}' LIMIT 0"
                    schema = conn.execute(schema_sql).fetchall()
                    schema_info = "\n".join([f"{col[0]}: {col[1]}" for col in schema])
                    logger.info(f"Parquet schema:\n{schema_info}")

                    # Try a simple query
                    simple_sql = f"SELECT * FROM '{parquet_path}' LIMIT 1"
                    simple_result = conn.execute(simple_sql).fetch_df()
                    logger.info(
                        f"Simple query succeeded with {len(simple_result)} rows"
                    )

                    # If we get here, the file is readable but there's an issue with the query
                    raise HTTPException(
                        status_code=400,
                        detail=f"Error executing DuckDB query: {error_msg}. SQL was: {sql}",
                    )
                except duckdb.duckdb.Error as schema_error:
                    # If we can't even read the schema, there's a problem with the file
                    raise HTTPException(
                        status_code=500,
                        detail=f"Error reading Parquet file: {schema_error}. Original error: {error_msg}",
                    )
        except HTTPException:
            # Re-raise HTTP exceptions directly
            raise
        except Exception as e:
            # Generic error handler
            import traceback

            error_detail = f"Error: {str(e)}\n{traceback.format_exc()}"
            logger.error(error_detail)
            raise HTTPException(status_code=500, detail=error_detail)

    # New helper function to process multiple files
    async def process_multiple_files(
        request: Request, filter_request: FilterRequest, parquet_paths: List[str]
    ):
        """Process a filter request across multiple parquet files."""
        try:
            # Create DuckDB connection
            conn = duckdb.connect(database=":memory:")

            # Build filters (excluding dataset filter which will be applied after union)
            filters = filter_request.filters
            dataset_filter = None

            # Extract dataset filter if present
            if filter_request.dataset and filter_request.dataset.strip():
                dataset_filter = FilterCondition(
                    key="dataset", op="=", val=filter_request.dataset
                )
                # Remove dataset from filters if present
                filters = [
                    f
                    for f in filters
                    if not (hasattr(f, "key") and getattr(f, "key") == "dataset")
                ]
            else:
                dataset_filter = None
                logger.info(
                    "No dataset filter specified, querying all datasets across files"
                )

            # Build a UNION ALL query across all files
            union_parts = []
            for path in parquet_paths:
                # Build base SQL for this file (without dataset filter)
                file_sql, file_params = build_sql_from_filters([], path)
                union_parts.append((file_sql, file_params))

            # Combine the SQL for all files with UNION ALL
            if len(union_parts) == 1:
                # Just one file
                base_sql, base_params = union_parts[0]
            else:
                # Multiple files - create UNION ALL
                base_sql = " UNION ALL ".join([sql for sql, _ in union_parts])
                base_params = []
                for _, params in union_parts:
                    base_params.extend(params)

            # Wrap the union in a subquery
            if dataset_filter or filters:
                sql = f"SELECT * FROM ({base_sql}) AS all_data WHERE "
                params = base_params.copy()

                # Apply dataset filter first if exists
                if dataset_filter:
                    sql += "dataset = ?"
                    params.append(dataset_filter.val)

                    # Add AND for additional filters
                    if filters:
                        sql += " AND "

                # Apply remaining filters
                if filters:
                    filter_sql, filter_params = build_sql_from_filters(filters, "")
                    # Remove the initial "SELECT * FROM '' WHERE " part
                    filter_sql = filter_sql.replace("SELECT * FROM '' WHERE ", "")
                    sql += filter_sql
                    params.extend(filter_params)
            else:
                # No filters, use the base union
                sql = base_sql
                params = base_params

            # Apply pagination
            paging_sql = (
                f"{sql} LIMIT {filter_request.limit} OFFSET {filter_request.offset}"
            )

            # Log the query
            logger.info(f"Multi-file SQL: {paging_sql}")
            logger.info(f"Parameters: {params}")

            # Execute count first to get total results
            count_sql = f"SELECT COUNT(*) as total FROM ({sql}) as filtered_data"
            total_result = conn.execute(count_sql, params).fetchone()
            total = total_result[0] if total_result else 0

            # Execute the main query
            result = conn.execute(paging_sql, params).fetch_df()

            # Convert to list of dictionaries
            items = result.to_dict(orient="records")

            # Process resource URLs in all items
            processed_items = [process_resource_urls(item, request) for item in items]

            # Apply input/output field filtering if include_all_fields is not True
            if (filter_request.input_fields or filter_request.output_fields) and not filter_request.include_all_fields:
                for item in processed_items:
                    # Filter input fields
                    if (
                        filter_request.input_fields
                        and "input" in item
                        and isinstance(item["input"], dict)
                    ):
                        filtered_input = {}
                        for field in filter_request.input_fields:
                            if field in item["input"]:
                                filtered_input[field] = item["input"][field]
                        item["input"] = filtered_input

                    # Filter output fields
                    if (
                        filter_request.output_fields
                        and "output" in item
                        and isinstance(item["output"], dict)
                    ):
                        filtered_output = {}
                        for field in filter_request.output_fields:
                            if field in item["output"]:
                                filtered_output[field] = item["output"][field]
                        item["output"] = filtered_output

            return {
                "items": processed_items,
                "total": total,
            }

        except Exception as e:
            logger.error(f"Error in process_multiple_files: {str(e)}")
            import traceback

            logger.error(traceback.format_exc())
            raise HTTPException(
                status_code=500, detail=f"Error processing multiple files: {str(e)}"
            )

    @app.get("/api/datasets")
    async def get_datasets(file: str | None = None):
        """Get list of unique datasets with their corresponding file information."""
        datasets_info = []

        if file and files_list and len(files_list) > 1 and file in file_dataframes:
            # If file parameter is provided and valid, get datasets from that file
            filtered_df = file_dataframes[file]
            datasets = filtered_df["dataset"].unique().tolist()
            for dataset in datasets:
                datasets_info.append({"name": dataset, "file": file})
        else:
            # Get datasets from all files with file information
            for file_info in files_list:
                file_name = file_info["name"]
                if file_name in file_dataframes:
                    file_df = file_dataframes[file_name]
                    file_datasets = file_df["dataset"].unique().tolist()
                    for dataset in file_datasets:
                        datasets_info.append({"name": dataset, "file": file_name})

        return {"datasets": datasets_info}

    @app.get("/api/labels")
    async def get_labels(
        dataset: str | None = None, key: str | None = None, file: str | None = None
    ):
        """Get all unique label keys and values in a dataset."""
        # If no dataset is provided, use the global index
        if not dataset:
            # For file-specific global filtering
            if file and files_list and len(files_list) > 1 and file in file_dataframes:
                # If file specified, build a file-specific global index on the fly
                file_global_index = {"keys": set(), "key_values_map": {}}
                file_df = file_dataframes[file]

                # Extract datasets in this file
                file_datasets = file_df["dataset"].unique()

                # Combine indices for datasets in this file
                for ds in file_datasets:
                    if ds in dataset_label_indices:
                        # Add keys
                        file_global_index["keys"].update(
                            dataset_label_indices[ds]["keys"]
                        )

                        # Add values for each key
                        for k, values in dataset_label_indices[ds][
                            "key_values_map"
                        ].items():
                            if k not in file_global_index["key_values_map"]:
                                file_global_index["key_values_map"][k] = set()
                            file_global_index["key_values_map"][k].update(values)

                # Use the file-specific global index
                active_index = file_global_index
            else:
                # Use the full global index
                active_index = global_label_index

            # If a specific key is requested from the active index
            if key and key in active_index["key_values_map"]:
                return {
                    "keys": [key],
                    "values": sorted(list(active_index["key_values_map"][key])),
                }

            # Return all keys and values from the active index
            all_values = set()
            for values in active_index["key_values_map"].values():
                all_values.update(values)

            return {
                "keys": sorted(list(active_index["keys"])),
                "values": sorted(list(all_values)),
            }

        # If dataset doesn't exist in indices, return empty result
        if dataset not in dataset_label_indices:
            return {"keys": [], "values": []}

        # If a specific key is provided, return just values for that key
        if key and key in dataset_label_indices[dataset]["key_values_map"]:
            return {
                "keys": [key],
                "values": sorted(
                    list(dataset_label_indices[dataset]["key_values_map"][key])
                ),
            }

        # Otherwise return all keys for the dataset and all values combined
        all_values = set()
        for values_set in dataset_label_indices[dataset]["key_values_map"].values():
            all_values.update(values_set)

        return {
            "keys": sorted(list(dataset_label_indices[dataset]["keys"])),
            "values": sorted(list(all_values)),
        }

    @app.get("/api/fields")
    async def get_fields(dataset: str | None = None, file: str | None = None):
        """Get all available input and output fields in a dataset."""
        # Determine which DataFrames to use based on file parameter
        dataframes_to_check = []

        if file and files_list and len(files_list) > 1 and file in file_dataframes:
            # If specific file is selected, use that file's dataframe
            dataframes_to_check.append(file_dataframes[file].copy())
        elif files_list and len(files_list) == 1:
            # If only one file exists, use that
            file_name = files_list[0]["name"]
            dataframes_to_check.append(file_dataframes[file_name].copy())
        else:
            # Otherwise use all dataframes
            for file_info in files_list:
                if file_info["name"] in file_dataframes:
                    dataframes_to_check.append(
                        file_dataframes[file_info["name"]].copy()
                    )

        # Extract all unique input and output fields
        input_fields = set()
        output_fields = set()

        for dataframe in dataframes_to_check:
            # Filter by dataset if provided
            if dataset:
                filtered_df = dataframe[dataframe["dataset"] == dataset]
            else:
                filtered_df = dataframe

            # Skip if filtered dataframe is empty
            if len(filtered_df) == 0:
                continue

            # Extract fields from each row
            for _, row in filtered_df.iterrows():
                if isinstance(row.get("input"), dict):
                    for field in row["input"].keys():
                        input_fields.add(field)

                if isinstance(row.get("output"), dict):
                    for field in row["output"].keys():
                        output_fields.add(field)

        return {
            "input_fields": sorted(list(input_fields)),
            "output_fields": sorted(list(output_fields)),
        }

    @app.get("/api/files")
    async def get_files():
        """Get list of files being analyzed."""
        if files_list is None or len(files_list) == 0:
            return {"is_single_file": True, "files": [], "current_file": ""}
        if len(files_list) == 1:
            return {
                "is_single_file": True,
                "files": files_list,
                "current_file": files_list[0]["name"],
            }
        return {"is_single_file": False, "files": files_list, "current_file": ""}

    @app.get("/api/data/{item_id}", response_model=DataItem)
    async def get_item(item_id: str, request: Request):
        """Get a specific data item by ID."""
        item = df[df["id"] == item_id]
        if len(item) == 0:
            raise HTTPException(status_code=404, detail="Item not found")

        # Process resource URLs in the item
        item_dict = item.iloc[0].to_dict()
        return process_resource_urls(item_dict, request)

    @app.put("/api/data/{item_id}")
    async def update_item(item_id: str, item: DataItem):
        """Update a data item (e.g. for evaluation)."""
        # Find the index of the item
        idx = df.index[df["id"] == item_id].tolist()
        if not idx:
            raise HTTPException(status_code=404, detail="Item not found")

        # Update the item in the dataframe
        df.loc[idx[0]] = item.dict()

        return {"message": "Item updated successfully"}

    # Star rating endpoints
    @app.post("/api/ratings")
    async def add_star_rating(rating: StarRating):
        """Add a star rating for an evaluation record."""
        # Verify the item exists
        item_exists = df[df["id"] == rating.item_id]
        if len(item_exists) == 0:
            raise HTTPException(status_code=404, detail="Item not found")

        # Set created_at if not provided
        if not rating.created_at:
            rating.created_at = datetime.now().isoformat()

        # Create ratings directory if it doesn't exist
        ratings_dir = Path("ratings")
        ratings_dir.mkdir(exist_ok=True)
        
        ratings_file = ratings_dir / "star_ratings.parquet"
        
        # Create new rating record
        rating_record = {
            "item_id": rating.item_id,
            "rating": rating.rating,
            "comment": rating.comment,
            "created_at": rating.created_at
        }
        
        # Load existing ratings or create new DataFrame
        if ratings_file.exists():
            ratings_df = pd.read_parquet(ratings_file)
            # Check if rating already exists for this item
            existing_rating = ratings_df[ratings_df["item_id"] == rating.item_id]
            if len(existing_rating) > 0:
                # Update existing rating
                ratings_df.loc[ratings_df["item_id"] == rating.item_id, "rating"] = rating.rating
                ratings_df.loc[ratings_df["item_id"] == rating.item_id, "comment"] = rating.comment
                ratings_df.loc[ratings_df["item_id"] == rating.item_id, "created_at"] = rating.created_at
            else:
                # Add new rating
                new_rating_df = pd.DataFrame([rating_record])
                ratings_df = pd.concat([ratings_df, new_rating_df], ignore_index=True)
        else:
            # Create new ratings file
            ratings_df = pd.DataFrame([rating_record])
        
        # Save to parquet
        ratings_df.to_parquet(ratings_file, index=False)
        
        return {"message": "Star rating added successfully", "rating": rating_record}

    @app.get("/api/ratings")
    async def get_star_ratings(item_id: str | None = None):
        """Get star ratings, optionally filtered by item_id."""
        ratings_file = Path("ratings") / "star_ratings.parquet"
        
        if not ratings_file.exists():
            return {"ratings": []}
        
        ratings_df = pd.read_parquet(ratings_file)
        
        if item_id:
            ratings_df = ratings_df[ratings_df["item_id"] == item_id]
        
        ratings = ratings_df.to_dict(orient="records")
        return {"ratings": ratings}

    @app.get("/api/ratings/all")
    async def get_all_star_ratings(request: Request, file: str | None = None):
        """Get all star ratings with associated evaluation data."""
        ratings_file = Path("ratings") / "star_ratings.parquet"
        
        if not ratings_file.exists():
            return {"items": []}
        
        ratings_df = pd.read_parquet(ratings_file)
        
        # Determine which DataFrame to use based on file parameter
        source_df = df.copy()
        if file and files_list and len(files_list) > 1 and file in file_dataframes:
            # Use specific file's data
            source_df = file_dataframes[file].copy()
        
        # Join with evaluation data
        result_items = []
        for _, rating_row in ratings_df.iterrows():
            item_id = rating_row["item_id"]
            item_data = source_df[source_df["id"] == item_id]
            
            if len(item_data) > 0:
                item_dict = item_data.iloc[0].to_dict()
                item_dict["star_rating"] = rating_row["rating"]
                item_dict["star_comment"] = rating_row["comment"]
                item_dict["rating_created_at"] = rating_row["created_at"]
                
                # Process resource URLs like in other endpoints
                processed_item = process_resource_urls(item_dict, request)
                result_items.append(processed_item)
        
        return {"items": result_items}

    @app.delete("/api/ratings/{item_id}")
    async def delete_star_rating(item_id: str):
        """Delete a star rating for an item."""
        ratings_file = Path("ratings") / "star_ratings.parquet"
        
        if not ratings_file.exists():
            raise HTTPException(status_code=404, detail="Rating not found")
        
        ratings_df = pd.read_parquet(ratings_file)
        
        # Check if rating exists
        if len(ratings_df[ratings_df["item_id"] == item_id]) == 0:
            raise HTTPException(status_code=404, detail="Rating not found")
        
        # Remove the rating
        ratings_df = ratings_df[ratings_df["item_id"] != item_id]
        
        # Save updated ratings
        if len(ratings_df) > 0:
            ratings_df.to_parquet(ratings_file, index=False)
        else:
            # If no ratings left, remove the file
            ratings_file.unlink()
        
        return {"message": "Star rating deleted successfully"}

    # Add specific route for manifest.json
    @app.get("/manifest.json", response_class=FileResponse)
    async def get_manifest():
        """Serve the manifest.json file."""
        manifest_path = static_dir / "manifest.json"
        if os.path.exists(manifest_path):
            return FileResponse(manifest_path, media_type="application/json")
        raise HTTPException(status_code=404, detail="Manifest not found")

    # Add specific route for favicon.ico
    @app.get("/favicon.ico", response_class=FileResponse)
    async def get_favicon():
        """Serve the favicon.ico file."""
        favicon_path = static_dir / "favicon.ico"
        if os.path.exists(favicon_path):
            return FileResponse(favicon_path, media_type="image/x-icon")
        raise HTTPException(status_code=404, detail="Favicon not found")

    # Mount static files for specific paths
    # Create additional mount for the nested static directory
    app.mount(
        "/static/js", StaticFiles(directory=static_dir / "static" / "js"), name="js"
    )
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

    # Serve index.html for the root path
    @app.get("/", response_class=FileResponse)
    async def get_index():
        """Serve the index.html file."""
        index_path = static_dir / "index.html"
        if os.path.exists(index_path):
            return FileResponse(index_path)
        return {"message": "Frontend not installed"}

    # Serve index.html for any other unmatched path (SPA routing)
    @app.get("/{path:path}")
    async def serve_spa(path: str):
        # Exclude API paths
        if path.startswith("api/"):
            raise HTTPException(status_code=404, detail="Not Found")

        # Serve index.html for all other paths for SPA routing
        index_path = static_dir / "index.html"
        if os.path.exists(index_path):
            return FileResponse(index_path)

        raise HTTPException(status_code=404, detail="Not Found")

    return app


# Helper function to build dataset label indices
def build_dataset_label_indices(
    df: DataFrame, dataset_label_indices: dict, global_label_index: dict = None
):
    """Build label indices for each dataset in the dataframe and update the global index."""
    # Get unique datasets
    datasets = df["dataset"].unique()

    for dataset in datasets:
        dataset_df = df[df["dataset"] == dataset]

        # Initialize index for this dataset if not exists
        if dataset not in dataset_label_indices:
            dataset_label_indices[dataset] = {"keys": set(), "key_values_map": {}}

        # Extract all label keys and values
        for label in dataset_df["label"].dropna():
            if isinstance(label, dict):
                for k, v in label.items():
                    # Add to dataset-specific index
                    dataset_label_indices[dataset]["keys"].add(k)

                    # Initialize key entry in key_values_map if not exists
                    if k not in dataset_label_indices[dataset]["key_values_map"]:
                        dataset_label_indices[dataset]["key_values_map"][k] = set()

                    # Add value to the key's values set
                    if v is not None:
                        dataset_label_indices[dataset]["key_values_map"][k].add(str(v))

                    # Add to global index if provided
                    if global_label_index is not None:
                        # Add to keys set
                        global_label_index["keys"].add(k)

                        # Initialize key in global key_values_map if needed
                        if k not in global_label_index["key_values_map"]:
                            global_label_index["key_values_map"][k] = set()

                        # Add value to global set
                        if v is not None:
                            global_label_index["key_values_map"][k].add(str(v))

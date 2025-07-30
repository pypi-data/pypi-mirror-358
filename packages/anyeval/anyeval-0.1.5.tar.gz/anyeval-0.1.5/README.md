# anyeval

Universal Evaluation for Gen AI

## Usage

```bash
pip install anyeval
```

```bash
# run evaluation for a parquet file or directory.
anyeval run [parquet_file|dir]
```

## Design

##### Data Schema (Parquet)

| id  | dataset | label | input | output | created_at | updated_at |
| --- | ------- | ----- | ----- | ------ | ---------- | ---------- |

##### Columns

**id**: is a UUID column.
**dataset**: is a String column.
**label**: is a JSON column. key value must be String.  
**input**: is a JSON column. key must be String. can include _media data_.  
**output**: is a JSON column. key must be String. can include _media data_.

> media data key must start by '@[file_type]->key'  
> only `@image->`, `@video->`, `@audio->` file types are supported.

Example:

```json
{
  "prompt": "make the image to video",
  "@image->input_image": "fs://path/to/image.jpg"
}
```

```json
{
  "inference_time": "1.234",
  "inference_device": "NVIDIA GeForce RTX 4090",
  "@video->output_video": "fs://path/to/output.mp4",
  "@video->output_video_thumbnail": "s3://path/to/output.jpg"
}
```

**created_at**: is a timestamp column.  
**updated_at**: is a timestamp column.

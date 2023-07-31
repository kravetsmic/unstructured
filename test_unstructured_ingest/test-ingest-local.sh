#!/usr/bin/env bash

set -e

SCRIPT_DIR=$(dirname "$(realpath "$0")")
cd "$SCRIPT_DIR"/.. || exit 1
OUTPUT_FOLDER_NAME=local
OUTPUT_DIR=$SCRIPT_DIR/structured-output/$OUTPUT_FOLDER_NAME

PYTHONPATH=. ./unstructured/ingest/main.py \
    local \
    --metadata-exclude coordinates,filename,file_directory,metadata.data_source.date_processed,metadata.date \
    --partition-strategy hi_res \
    --reprocess \
    --structured-output-dir "$OUTPUT_DIR" \
    --verbose \
    --file-glob "*.html" \
    --input-path example-docs

sh "$SCRIPT_DIR"/check-num-files-output.sh 9 $OUTPUT_FOLDER_NAME

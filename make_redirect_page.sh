#!/bin/bash
REDIRECT_LINK="$1"
OUTPUT_PATH="$2"
FILE_NAME="$3"

python $CIS_TOOLS/make_redirect_page.py --redirect_link "$REDIRECT_LINK" --output_path "$OUTPUT_PATH" --file_name "$FILE_NAME"
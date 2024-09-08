#!/bin/bash

PYTHON_SCRIPT="generate-compose.py"

SERVICE_COUNT=2
SERVICE_TYPE=freeze
START_FROM=27984
TEMPLATE_FILE="template/${SERVICE_TYPE}-template.yml"
OUTPUT_FILE="../../_bootstrap/compose/${SERVICE_TYPE}-compose.yml"

python3 "$PYTHON_SCRIPT" "$SERVICE_COUNT" "$SERVICE_TYPE" "$START_FROM" "$TEMPLATE_FILE" "$OUTPUT_FILE"
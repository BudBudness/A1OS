#!/bin/bash
CATEGORY=$1
if [[ -z "$CATEGORY" || "$CATEGORY" == "cache" || "$CATEGORY" == "data" ]]; then echo "$(date): ERROR: Invalid category" && exit 1; fi
SOURCE_DIR="$HOME/A1OS/data/$CATEGORY"
CACHE_DIR="$HOME/A1OS/data/cache/$CATEGORY"
if [ -d "$SOURCE_DIR" ]; then mkdir -p "$CACHE_DIR" && find "$SOURCE_DIR" -mindepth 1 -maxdepth 1 -exec cp -r {} "$CACHE_DIR/" \; && echo "$(date): REFRESHED $CACHE_DIR"; else echo "$(date): ERROR: Source $SOURCE_DIR not found" && exit 1; fi

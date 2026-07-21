#!/bin/bash
find "$HOME/A1OS/logs/" -name "*.log" -size +10M -exec truncate -s 0 {} \;

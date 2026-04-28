#!/usr/bin/env bash
# Log to ./logs/ relative to this script's parent (the plugin root).
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PLUGIN_ROOT="$(dirname "$SCRIPT_DIR")"
LOG="$PLUGIN_ROOT/logs/debug-env.log"
mkdir -p "$(dirname "$LOG")"
echo "--- $(date) ---" >> "$LOG"
echo "CWD=$(pwd)" >> "$LOG"
echo "SCRIPT_DIR=$SCRIPT_DIR" >> "$LOG"
echo "PLUGIN_ROOT=$PLUGIN_ROOT" >> "$LOG"
env | sort >> "$LOG"
echo "--- END ---" >> "$LOG"

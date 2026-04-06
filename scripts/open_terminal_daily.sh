#!/bin/bash
# =============================================================================
# INDAVILLAS DAILY BLOG CRON TRIGGER
# =============================================================================
# Called by crontab once a day.

PROJECT_ROOT="/Users/kristapsjansons/Documents_Local/Clone - Antigravity/IndaVillas"

echo "🚀 Starting daily IndaVillas pipeline..."

# Open a new Terminal window and run the pipeline
osascript -e "tell application \"Terminal\" to do script \"bash \\\"$PROJECT_ROOT/scripts/run_gemini_blog_task.sh\\\"\""

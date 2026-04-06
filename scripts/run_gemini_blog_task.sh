#!/bin/bash
# =============================================================================
# INDAVILLAS BLOG AUTOMATION PIPELINE (1 ARTICLE)
# =============================================================================
set -e

PROJECT_ROOT="/Users/kristapsjansons/Documents_Local/Clone - Antigravity/IndaVillas"
cd "$PROJECT_ROOT" || exit 1

echo "🚀 Starting Daily IndaVillas Blog Pipeline..."
echo "📅 Date: $(date +'%Y-%m-%d %H:%M:%S')"
echo "=================================================="

# Eval the python script output to set variables
eval "$(/usr/bin/python3 scripts/get_next_article.py)"

if [ "$EXHAUSTED" = "true" ]; then
    echo "⚠️ All articles in queue.json have been written. Exiting."
    exit 0
fi

if [ -z "$MASTER_KEYWORD" ]; then
    echo "❌ Failed to read next article from queue."
    exit 1
fi

TODAY=$(date +'%Y-%m-%d')
POST_PATH="posts/${SLUG}.md"

echo "🎯 Topic: $ARTICLE_TOPIC"
echo "🔑 Master Keyword: $MASTER_KEYWORD"
echo "📎 Secondary Keywords: $SECONDARY_KEYWORDS"
echo "📄 Target File: $POST_PATH"
echo "=================================================="

# ── Job: Write Full Draft ──
echo "📝 Writing full draft with Gemini CLI..."

/usr/local/bin/gemini --yolo --prompt "
Write a 1500-2500 word SEO blog article for IndaVillas.

Business: IndaVillas — luxury villa marketing & digital growth services (SEO, listing optimization, revenue strategy, content marketing).
Note: We are NOT a property management company. We do not do cleaning, operations, or check-ins.

Article Topic: '$ARTICLE_TOPIC'
Master Keyword: '$MASTER_KEYWORD'
Secondary Keywords to naturally include: '$SECONDARY_KEYWORDS'

Follow these rules:
1. Write like an expert consulting a peer — technical precision, zero fluff, conversational and human tone.
2. The article must be highly optimized for the Master Keyword and include the Secondary Keywords naturally.
3. Write standard Markdown (.md) file using EXACTLY this YAML frontmatter at the top:
---
title: \"(Write a catchy click-worthy title here, up to 60 characters)\"
slug: \"$SLUG\"
excerpt: \"(Short 2-3 sentence overview)\"
meta_description: \"(SEO description containing the master keyword, under 160 characters)\"
status: publish
author: \"IndaVillas Team\"
author_role: \"Lead Property Manager\"
date: \"$TODAY\"
last_updated: \"$TODAY\"
tags: [\"Luxury Hospitality\", \"Property Management\"]
reading_time: \"10 min read\"
canonical_url: \"https://indavillas.com/blog/$SLUG\"
---
4. Include an impressive header image if possible or leave a placeholder. Ensure the content addresses luxury property owners and marketing strategies for 5+ bedroom villas where applicable.
5. Save the final markdown content directly via the write_to_file tool to '$POST_PATH'. Do NOT wrap in markdown block quotes, the tool should directly write the final file.
6. Make sure to generate the file. Do not just print it.
7. End with a clear CTA for IndaVillas services.
"

# Verify word count
if [ -f "$POST_PATH" ]; then
    WC=$(wc -w < "$POST_PATH" | tr -d ' ')
    echo "📊 Word count: $WC"
    if [ "$WC" -lt 1000 ]; then
        echo "❌ Job FAILED: Draft is only $WC words. Something went wrong."
        exit 1
    fi
else
    echo "❌ Job FAILED: Draft file not found at $POST_PATH"
    exit 1
fi

echo "✅ Article successfully written to $POST_PATH"

echo "📤 Committing and pushing to GitHub..."
git pull --rebase origin main || true
git add "$POST_PATH"
git add "keyword_strategy/queue.json"
git commit -m "feat(blog): automated publish of '$ARTICLE_TOPIC'"
git push origin main

echo "✅ Pipeline successfully completed!"

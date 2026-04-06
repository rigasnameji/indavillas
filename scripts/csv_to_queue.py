import csv
import json
import os
import re

base_dir = '/Users/kristapsjansons/Documents_Local/Clone - Antigravity/IndaVillas/keyword_strategy'
priority_csv = os.path.join(base_dir, '03_priority_opportunities.csv')
clusters_csv = os.path.join(base_dir, '02_article_clusters.csv')
output_json = os.path.join(base_dir, 'queue.json')

# Read clusters for secondary keywords
clusters = {}
with open(clusters_csv, mode='r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        clusters[row['Article Topic']] = row['Secondary Keywords']

queue = []
with open(priority_csv, mode='r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        topic = row['Article Topic']
        slug = re.sub(r'[^a-z0-9]+', '-', row['Master Keyword'].lower()).strip('-')
        
        queue.append({
            "id": int(row['Priority Rank']),
            "status": "pending",
            "article_topic": topic,
            "master_keyword": row['Master Keyword'],
            "secondary_keywords": clusters.get(topic, ""),
            "volume": int(row['Master Volume']),
            "seo_difficulty": int(row['SEO Difficulty']),
            "slug": slug,
            "post_file": f"posts/{slug}.md"
        })

with open(output_json, mode='w', encoding='utf-8') as f:
    json.dump(queue, f, indent=2)

print(f"Generated queue.json with {len(queue)} articles.")

import json
import os
import sys

base_dir = '/Users/kristapsjansons/Documents_Local/Clone - Antigravity/IndaVillas'
queue_path = os.path.join(base_dir, 'keyword_strategy/queue.json')

if not os.path.exists(queue_path):
    print("echo 'Queue not found'")
    sys.exit(1)

with open(queue_path, 'r', encoding='utf-8') as f:
    queue = json.load(f)

found = False
for item in queue:
    if item['status'] == 'pending':
        item['status'] = 'done' # mark as done immediately since we're writing
        
        # print environment variables for bash to eval
        print(f"export ARTICLE_TOPIC=\"{item['article_topic']}\"")
        print(f"export MASTER_KEYWORD=\"{item['master_keyword']}\"")
        print(f"export SECONDARY_KEYWORDS=\"{item['secondary_keywords']}\"")
        print(f"export SLUG=\"{item['slug']}\"")
        
        found = True
        break

if found:
    with open(queue_path, 'w', encoding='utf-8') as f:
        json.dump(queue, f, indent=2)
else:
    print("export EXHAUSTED=true")

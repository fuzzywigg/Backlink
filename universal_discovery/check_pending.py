import json

try:
    with open('review_system/reviews.json') as f:
        data = json.load(f)
        pending = [i for i in data if i.get('recommendation') == 'PENDING']
        print(f"Pending items: {len(pending)}")
        for i in pending:
            print(f"- {i.get('url')}")
except Exception as e:
    print(f"Error: {e}")

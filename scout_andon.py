
import requests
import re
import json

def scout_page():
    url = "https://andonlabs.com/evals/radio"
    print(f"Fetching raw source from: {url}")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        html = response.text
        
        print(f"Status: {response.status_code}")
        print(f"Content Length: {len(html)} bytes")
        
        # 1. Look for Next.js Data (Common in modern React sites)
        next_data = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html)
        if next_data:
            print("\n[FOUND] Next.js Data Blob!")
            try:
                data = json.loads(next_data.group(1))
                # Dump structure to see where the radio stats are
                print("Keys:", data.keys())
                if 'props' in data:
                    print("Props Keys:", data['props'].keys())
                    if 'pageProps' in data['props']:
                         print("PageProps Keys:", data['props']['pageProps'].keys())
                         # Save this specific useful blob
                         with open("andon_data.json", "w") as f:
                             json.dump(data['props']['pageProps'], f, indent=2)
                         print("Saved pageProps to andon_data.json")
            except Exception as e:
                print(f"Error parsing JSON: {e}")
                
        # 2. Look for other JSON blobs
        other_json = re.findall(r'<script type="application/json">(.*?)</script>', html)
        for i, blob in enumerate(other_json):
            print(f"\n[FOUND] Other JSON Blob #{i}")
            print(blob[:100] + "...")

    except Exception as e:
        print(f"Scout Failed: {e}")

if __name__ == "__main__":
    scout_page()

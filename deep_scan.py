
import requests
import re

def deep_scan():
    url = "https://andonlabs.com/evals/radio"
    print(f"Deep Scanning: {url}")
    
    html = requests.get(url).text
    
    # 1. Hidden Comments
    print("\n--- HIDDEN COMMENTS ---")
    comments = re.findall(r'<!--(.*?)-->', html, re.DOTALL)
    for c in comments:
        c_clean = c.strip()
        if "svelte" not in c_clean and "Plausible" not in c_clean: # Filter common noise
            print(f"[*] {c_clean}")

    # 2. Variable Hunt
    print("\n--- INTERESTING VARIABLES ---")
    # Patterns for JSON-like objects or strict variables
    patterns = [
        r'const \w+\s*=\s*{.*?}', 
        r'let \w+\s*=\s*{.*?}',
        r'window\.\w+\s*='
    ]
    # This is a naive regex, actual parsing is hard, but we look for keywords
    keywords = ["debug", "flag", "admin", "test", "secret", "api_key", "dev"]
    
    lines = html.split('\n')
    for i, line in enumerate(lines):
        line_lower = line.lower()
        for k in keywords:
            if k in line_lower:
                # Print context
                print(f"[Line {i}] Match '{k}': {line.strip()[:100]}...")

    # 3. Svelte Hydration Payload
    print("\n--- DATA PAYLOADS ---")
    # Svelte often puts data in slightly different places depending on adapter
    # Searching for large JSON structures
    json_blobs = re.findall(r'\{"\w+":.*?\}(?=</script>)', html) 
    if len(json_blobs) > 0:
        print(f"Found {len(json_blobs)} potential data blobs.")
        # Print keys of the first one to verify
        print("Blob 1 Sample:", json_blobs[0][:200])

if __name__ == "__main__":
    deep_scan()

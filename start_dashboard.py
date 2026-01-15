import http.server
import socketserver
import webbrowser
import os
import json
import urllib.request
import urllib.parse
from datetime import datetime

# Configuration
PORT = 8000
DIRECTORY = "review_system"
REVIEWS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "review_system", "reviews.json")

# Simple AI Integration (Placeholder for the "free LLM API link" the user mentioned)
# In a real scenario, this would call OpenAI/Gemini/Anthropic/Models.dev
def mock_ai_review(url):
    """
    This is where the 'Free LLM API' would go. 
    For now, we simulate a 'Pending Analysis' state so the User (HITL) 
    or the Agent (Antigravity) can finalize it.
    """
    domain = urllib.parse.urlparse(url).netloc
    return {
        "timestamp": datetime.now().isoformat(),
        "url": url,
        "name": f"Pending Review: {domain}",
        "summary": "Submitted via Dashboard. Waiting for AI/Human analysis.",
        "scores": {
            "strategic": 0,
            "sovereign": 0,
            "agentic": 0,
            "technical": 0
        },
        "weighted_score": 0.0,
        "analysis": "Content has been queued. Please ask Antigravity to 'Process Pending Reviews' or configure the API key in start_dashboard.py.",
        "recommendation": "PENDING"
    }

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=os.path.abspath(DIRECTORY), **kwargs)

    def do_POST(self):
        if self.path == '/api/submit':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data)
                url = data.get('url')
                
                if not url:
                    self.send_error(400, "Missing URL")
                    return

                print(f"Received submission for: {url}")
                
                # 1. Generate the Review (Mock or Call API)
                review_entry = mock_ai_review(url)
                
                # 2. Save to JSON
                reviews_data = []
                if os.path.exists(REVIEWS_FILE):
                    try:
                        with open(REVIEWS_FILE, 'r') as f:
                            reviews_data = json.load(f)
                    except:
                        pass
                
                # Prepend to top
                reviews_data.insert(0, review_entry)
                
                with open(REVIEWS_FILE, 'w') as f:
                    json.dump(reviews_data, f, indent=2)

                # 3. Respond
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "success", "entry": review_entry}).encode())

            except Exception as e:
                print(f"Error: {e}")
                self.send_error(500, str(e))
        else:
            self.send_error(404)

def run():
    print(f"Starting Hive Scout Dashboard on http://localhost:{PORT}")
    print(f"Serving directory: {os.path.abspath(DIRECTORY)}")
    print(f"Database: {REVIEWS_FILE}")
    
    # Try to find a free port
    port = PORT
    httpd = None
    while port < PORT + 10:
        try:
            httpd = socketserver.TCPServer(("", port), Handler)
            break
        except OSError:
            print(f"Port {port} in use, trying {port+1}...")
            port += 1
    
    if httpd is None:
        print("Could not find a free port.")
        return

    print(f"Scout Dashboard running on http://localhost:{port}/dashboard.html")
    webbrowser.open(f"http://localhost:{port}/dashboard.html")

    with httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server.")
            httpd.shutdown()

if __name__ == "__main__":
    run()

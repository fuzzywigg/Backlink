import requests

# Configuration for Local Sovereign Intelligence
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.2:3b"  # Fast, efficient, runs comfortably on your RTX 5070


def generate_dj_script(track_metadata, station_status="Online"):
    """
    Sends track metadata to the local Llama 3.2 model to generate
    a 'Curator' persona script.
    """

    prompt = f"""
    You are 'The Curator' of FuzzRadio, a sovereign underground radio station.
    Your voice is: Omniscient, Cool, Precise, Cyberpunk.
    STATUS: {station_status}

    CURRENT TRACK:
    Title: {track_metadata.get("title")}
    Artist: {track_metadata.get("artist")}
    Era: {track_metadata.get("era", "Unknown")}
    Mood: {track_metadata.get("mood", "Analyzing...")}

    TASK:
    Write a 1-sentence intro for this track.
    DO NOT say "Hey guys".
    DO NOT be cheerful.
    Be informative and slightly mysterious.
    """

    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.7, "num_predict": 100},
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload)
        response.raise_for_status()
        result = response.json()
        return result.get("response", "").strip()
    except Exception as e:
        return f"[SYSTEM ERROR: Local Neural Link Unstable - {str(e)}]"


if __name__ == "__main__":
    # Test the Brain
    test_track = {"title": "Midnight City", "artist": "M83", "era": "2010s", "mood": "Energetic"}
    print("Testing Local Intelligence...")
    print(generate_dj_script(test_track))

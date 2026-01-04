import os
import time
import requests
import logging
from datetime import datetime
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("StreamMonitor")

STREAM_URL = "https://das-edge12-live365-dal02.cdnstream.com/a13541"
CHUNK_DURATION_SECONDS = 30
OUTPUT_DIR = "data/stream_capture"
API_KEY = os.environ.get("GEMINI_API_KEY")

if not API_KEY:
    logger.error("GEMINI_API_KEY not found. Please create a .env file with GEMINI_API_KEY=...")
    # Attempt to load from hive/keys.json as fallback (simulating KeyManager logic)
    try:
        import json
        keys_path = os.path.join("hive", "keys.json")
        if os.path.exists(keys_path):
            with open(keys_path) as f:
                data = json.load(f)
                API_KEY = data.get("GEMINI_API_KEY")
                if API_KEY:
                    logger.info("Loaded API Key from hive/keys.json")
    except Exception as e:
        logger.warning(f"Failed to check keys.json: {e}")

if not API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment or keys.json.")


client = genai.Client(api_key=API_KEY)

def monitor_stream():
    """
    Connects to the audio stream, captures chunks, and sends them to Gemini for analysis.
    """
    logger.info(f"Connecting to stream: {STREAM_URL}")
    
    try:
        # Open the stream
        with requests.get(STREAM_URL, stream=True) as response:
            if response.status_code != 200:
                logger.error(f"Failed to connect to stream. Status: {response.status_code}")
                return

            logger.info("Stream connected. Starting capture...")
            
            # Approximate bitrate calculation (128kbps is standard for streams)
            # 128 kbps = 16 KB/s
            # 30 seconds = 480 KB (approx)
            # safer to just measure time, but for blocking read we need a byte size.
            # Let's assume 128kbps for chunk sizing to get roughly 30s.
            # 128 * 1024 / 8 * 30 = 491520 bytes.
            chunk_size = 512 * 1024 # 512KB chunks, roughly 30s
            
            buffer = bytearray()
            
            # Streaming loop
            for block in response.iter_content(1024):
                buffer.extend(block)
                
                if len(buffer) >= chunk_size:
                    process_chunk(buffer)
                    buffer = bytearray() # Reset buffer
                    
    except KeyboardInterrupt:
        logger.info("Stopping stream monitor...")
    except Exception as e:
        logger.error(f"Stream error: {e}")

def process_chunk(audio_data):
    """
    Saves the audio chunk and sends it to Gemini for transcription.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(OUTPUT_DIR, f"capture_{timestamp}.mp3")
    
    # 1. Save Audio File
    try:
        with open(filename, "wb") as f:
            f.write(audio_data)
        logger.info(f"Captured: {filename}")
    except Exception as e:
        logger.error(f"Failed to write file: {e}")
        return

    # 2. Analyze with Gemini
    try:
        analyze_audio(filename)
    except Exception as e:
        logger.error(f"Analysis failed: {e}")

def analyze_audio(file_path):
    """
    Uploads file to Gemini and requests transcription.
    """
    logger.info(f"Analyzing {file_path}...")
    
    # Upload the file
    # Note: genai.Client has different upload semantics than the old SDK.
    # We use the files.upload method if available or pass bytes if supported.
    # The V2/new SDK often uses client.files.upload
    
    try:
        # Check if we can use the file API
        uploaded_file = client.files.upload(path=file_path)
        
        # Wait for processing if strictly needed, but usually small audio is fast.
        # For 'active' state check:
        while uploaded_file.state == "PROCESSING":
            time.sleep(1)
            uploaded_file = client.files.get(name=uploaded_file.name)
            
        if uploaded_file.state == "FAILED":
             logger.error("Audio processing failed.")
             return

        prompt = """
        Listen to this audio segment.
        1. Is this primarily Speech, Music, or Silence?
        2. If Speech: Transcribe the spoken words verbatim.
        3. If Music: Identify the song and artist if possible.
        4. If it's a mix (DJ talking over music), transcribe the speech and mention the background track.
        
        Output strictly in JSON format:
        {
            "segment_type": "speech" | "music" | "mixed" | "silence",
            "transcript": "The transcribed text...",
            "song_info": "Artist - Title (if identified)",
            "notes": "Any additional context"
        }
        """
        
        response = client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=[uploaded_file, prompt],
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )
        
        result = response.text
        print(f"\n--- STREAM LOG [{datetime.now().strftime('%H:%M:%S')}] ---\n{result}\n--------------------------------------------\n")
        
        # Append to transcript log
        log_file = os.path.join(OUTPUT_DIR, "transcript_log.txt")
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now().strftime('%H:%M:%S')}] {result}\n")
        
        # Cleanup remote file
        # client.files.delete(name=uploaded_file.name) 
        # (Optional: keep strictly within quota limits)

    except Exception as e:
        logger.error(f"Gemini API Error: {e}")

if __name__ == "__main__":
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    
    # Disable requests logging noise
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    
    print("----------------------------------------------------------------")
    print("   AUDIO SCOUT ACTIVE - LISTENING TO STREAM   ")
    print("   Target: " + STREAM_URL)
    print("   Output: " + OUTPUT_DIR)
    print("   Press Ctrl+C to Stop")
    print("----------------------------------------------------------------")
    
    monitor_stream()

import json
import urllib.parse
import urllib.request


class MetadataEnricher:
    """
    Sovereign Metadata Enrichment using iTunes Public API.
    No API Keys Required. Anonymous. Rate Limit ~20/min.
    """

    def __init__(self):
        self.enabled = True
        self.base_url = "https://itunes.apple.com/search"

    def search_track(self, query):
        """
        Search iTunes for a track and return best match.
        """
        try:
            # 1. Clean Query
            clean_query = query.replace("Unknown", "").strip()
            if not clean_query:
                return None

            # 2. Encode
            params = {"term": clean_query, "media": "music", "entity": "song", "limit": 1}
            url = f"{self.base_url}?{urllib.parse.urlencode(params)}"

            # 3. Request (Standard Library to keep it lightweight)
            with urllib.request.urlopen(url) as response:
                if response.status != 200:
                    print(f"⚠️ [ENRICHER] iTunes Error: {response.status}")
                    return None

                data = json.loads(response.read().decode())

                if data["resultCount"] == 0:
                    return None

                track = data["results"][0]

                return {
                    "title": track.get("trackName"),
                    "artist": track.get("artistName"),
                    "album": track.get("collectionName"),
                    "genre": track.get("primaryGenreName", "Verified"),
                    "preview_url": track.get("previewUrl"),
                    "cover_art": track.get("artworkUrl100"),
                    "itunes_id": track.get("trackId"),
                }

        except Exception as e:
            print(f"⚠️ [ENRICHER] Search Exception: {e}")
            return None


if __name__ == "__main__":
    # Test
    e = MetadataEnricher()
    print("Testing 'Not Like Us'...")
    from pprint import pprint

    pprint(e.search_track("Not Like Us Kendrick"))

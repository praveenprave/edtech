import os
import requests
from typing import Optional, Dict, Any

class HeyGenClient:
    """
    Client for interacting with the HeyGen API to generate avatar videos.
    """
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("HEYGEN_API_KEY")
        self.base_url = "https://api.heygen.com/v2"
        
        if not self.api_key:
            print("⚠️ WARNING: HEYGEN_API_KEY is not set. Video generation will fail.")

    def _get_headers(self) -> Dict[str, str]:
        return {
            "X-Api-Key": self.api_key,
            "Content-Type": "application/json"
        }

    def check_health(self) -> bool:
        """Simple check to verify API connectivity."""
        if not self.api_key:
            return False
        # There isn't a standard 'health' endpoint, but we can try listing avatars
        try:
            response = requests.get(f"{self.base_url}/avatars", headers=self._get_headers())
            return response.status_code == 200
        except Exception as e:
            print(f"HeyGen Health Check Failed: {e}")
            return False

    def generate_video(self, script_text: str, avatar_id: str = "default_avatar_id", voice_id: str = "default_voice_id") -> Dict[str, Any]:
        """
        Submits a video generation task to HeyGen.
        """
        url = f"{self.base_url}/video/generate"
        payload = {
            "video_inputs": [
                {
                    "character": {
                        "type": "avatar",
                        "avatar_id": avatar_id,
                        "scale": 1.0,
                        "avatar_style": "normal"
                    },
                    "voice": {
                        "type": "text",
                        "voice_id": voice_id,
                        "input_text": script_text
                    }
                }
            ],
            "dimension": {
                "width": 1920,
                "height": 1080
            }
        }
        
        try:
            response = requests.post(url, json=payload, headers=self._get_headers())
            response.raise_for_status()
            return response.json() # Returns job_id
        except Exception as e:
            print(f"❌ HeyGen Generation Failed: {e}")
            raise

    def get_status(self, video_id: str) -> str:
        """
        Checks status of a video generation job.
        """
        url = f"{self.base_url}/video_status.get?video_id={video_id}"
        try:
            response = requests.get(url, headers=self._get_headers())
            response.raise_for_status()
            data = response.json()
            return data.get("data", {}).get("status", "unknown")
        except Exception as e:
            print(f"❌ Error checking status: {e}")
            return "error"

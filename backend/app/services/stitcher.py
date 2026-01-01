import os
import subprocess
import uuid
from google.cloud import storage

class StitcherService:
    def __init__(self):
        self.project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
        # Bucket for final assets. Ensure this matches infra setup.
        self.bucket_name = f"{self.project_id}-assets" if self.project_id else "demo-bucket"
        try:
            self.storage_client = storage.Client()
        except:
            print("⚠️ Warning: GCS Client failed to init. Local mode only.")
            self.storage_client = None

    def stitch(self, intro_url: str, core_url: str) -> str:
        """
        Downloads two videos, stitches them with FFmpeg, uploads result to GCS.
        Returns the public URL of the final video.
        """
        job_id = str(uuid.uuid4())
        work_dir = f"/tmp/{job_id}"
        os.makedirs(work_dir, exist_ok=True)
        
        intro_path = f"{work_dir}/intro.mp4"
        core_path = f"{work_dir}/core.mp4"
        output_path = f"{work_dir}/final.mp4"
        
        print(f"[{job_id}] 🧵 Starting Stitching Process...")

        # 1. Download Files (Mocking download if URLs are fake mock.com)
        self._download_or_mock(intro_url, intro_path)
        self._download_or_mock(core_url, core_path)

        # 2. Create FFmpeg List File
        list_file = f"{work_dir}/input.txt"
        with open(list_file, "w") as f:
            f.write(f"file '{intro_path}'\n")
            f.write(f"file '{core_path}'\n")

        # 3. Run FFmpeg Concat
        # -y: overwrite
        # -f concat: use concat demuxer
        # -safe 0: allow unsafe paths
        # -c copy: stream copy (fastest, no re-encoding) - assume same codec
        # If codecs differ, we'd need re-encoding: -c:v libx264 -c:a aac
        cmd = [
            "ffmpeg", "-y", 
            "-f", "concat",
            "-safe", "0", 
            "-i", list_file,
            "-c", "copy",
            output_path
        ]
        
        try:
            subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print(f"[{job_id}] ✅ FFmpeg Stitching Complete.")
        except subprocess.CalledProcessError as e:
            print(f"[{job_id}] ❌ FFmpeg Failed: {e.stderr.decode()}")
            raise Exception("Video stitching failed during processing.")

        # 4. Upload to GCS
        final_url = self._upload_to_gcs(output_path, f"output/{job_id}_lesson.mp4")
        
        # Cleanup
        # shutil.rmtree(work_dir) # Optional: keep for debugging in this mock env
        
        return final_url

    def _download_or_mock(self, url: str, path: str):
        """
        Real impl would use requests.get(url).
        For this demo, since HeyGen mock URLs are fake, we create dummy mp4 files.
        """
        if "mock.com" in url:
            # Create a dummy MP4 file (1 sec black screen)
            # using ffmpeg to generate it so stitching actually has valid input
            cmd = [
                "ffmpeg", "-y",
                "-f", "lavfi", "-i", "color=c=black:s=1280x720:d=1",
                "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
                "-c:v", "libx264", "-t", "1",
                "-c:a", "aac", 
                path
            ]
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            # Real Download Logic
            import requests
            with requests.get(url, stream=True) as r:
                r.raise_for_status()
                with open(path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)

    def _upload_to_gcs(self, local_path: str, destination_blob_name: str) -> str:
        if not self.storage_client:
            return f"file://{local_path}"
            
        bucket = self.storage_client.bucket(self.bucket_name)
        blob = bucket.blob(destination_blob_name)
        blob.upload_from_filename(local_path)
        
        # Make public (optional, or use signed URL)
        # blob.make_public()
        # return blob.public_url
        return f"https://storage.googleapis.com/{self.bucket_name}/{destination_blob_name}"

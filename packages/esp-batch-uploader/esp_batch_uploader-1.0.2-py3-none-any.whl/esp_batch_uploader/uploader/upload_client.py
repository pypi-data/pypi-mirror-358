import os
import time
import aiohttp
import asyncio
from aiohttp import ClientTimeout

class UploadClient:
    def __init__(self, ip, logger, status_logger):
        self.ip = ip
        self.logger = logger
        self.status_logger = status_logger

    async def upload_file(self, session, file_path, remote_name):
        if not os.path.exists(file_path):
            self.logger.error(f"[ERROR] File does not exist: {file_path}")
            return False

        url = f"http://{self.ip}/upload/{remote_name}"
        file_size = os.path.getsize(file_path)
        self.logger.info(f"Uploading to: {url} ({file_size / 1024:.2f} KB)")
        self.status_logger.info(f"Start upload {remote_name} to {self.ip}")

        try:
            start_time = time.time()
            with open(file_path, 'rb') as f:
                async with session.post(url, data=f) as resp:
                    duration = time.time() - start_time
                    if resp.status == 200:
                        speed = file_size / duration if duration > 0 else 0
                        self.logger.info(f"[SUCCESS] Uploaded {remote_name} to {self.ip} in {duration:.2f}s ({speed/1024/1024:.2f} MB/s)")
                        self.status_logger.info(f"[SUCCESS] {self.ip} <- {remote_name} OK")
                        return True
                    else:
                        text = await resp.text()
                        self.logger.error(f"[ERROR] Upload failed: {resp.status} - {text}")
                        self.status_logger.info(f"[ERROR] {self.ip} <- {remote_name} FAILED")
                        return False
        except Exception as e:
            self.logger.error(f"[ERROR] Upload error to {self.ip}: {str(e)}")
            self.status_logger.info(f"[ERROR] Upload error to {self.ip}: {str(e)}")
            return False

    async def upload_files(self, file_paths):
        timeout = ClientTimeout(total=1800, sock_connect=10, sock_read=30)

        async with aiohttp.ClientSession(timeout=timeout) as session:
            for path in file_paths:
                remote_name = os.path.basename(path)
                success = await self.upload_file(session, path, remote_name)
                if not success:
                    self.logger.warning(f"[RETRY] Retrying {remote_name} to {self.ip}")
                    await asyncio.sleep(2)
                    success = await self.upload_file(session, path, remote_name)

                    if not success:
                        self.logger.error(f"[ERROR] Retry failed for {remote_name} to {self.ip}")
                        self.status_logger.info(f"[ERROR] {self.ip} <- {remote_name} RETRY FAILED")
                        await asyncio.sleep(2)  # Wait before next file

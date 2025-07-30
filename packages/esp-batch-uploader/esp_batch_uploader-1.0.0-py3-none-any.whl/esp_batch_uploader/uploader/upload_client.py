import os
import time
import aiohttp
import asyncio

class UploadClient:
    def __init__(self, ip, logger, status_logger):
        self.ip = ip
        self.logger = logger
        self.status_logger = status_logger

    async def upload_file(self, session, file_path, remote_name):
        if not os.path.exists(file_path):
            self.logger.error(f"File does not exist: {file_path}")
            return False

        url = f"http://{self.ip}/upload/{remote_name}"
        file_size = os.path.getsize(file_path)

        self.logger.info(f"Uploading to {url} ({file_size / 1024:.2f} KB)")
        self.status_logger.info(f"Start upload {remote_name} to {self.ip}")

        try:
            start_time = time.time()
            with open(file_path, 'rb') as f:
                async with session.post(url, data=f) as resp:
                    duration = time.time() - start_time
                    if resp.status == 200:
                        speed = file_size / duration if duration > 0 else 0
                        self.logger.info(f"✅ Uploaded {remote_name} to {self.ip} in {duration:.2f}s ({speed/1024/1024:.2f} MB/s)")
                        self.status_logger.info(f"✅ {self.ip} <- {remote_name} OK")
                        return True
                    else:
                        text = await resp.text()
                        self.logger.error(f"❌ Upload failed: {resp.status} - {text}")
                        self.status_logger.info(f"❌ {self.ip} <- {remote_name} FAILED")
                        return False
        except Exception as e:
            self.logger.exception(f"Upload error to {self.ip}: {e}")
            self.status_logger.info(f"❌ {self.ip} <- {remote_name} ERROR")
            return False

    async def upload_files(self, file_paths):
        async with aiohttp.ClientSession() as session:
            for path in file_paths:
                remote_name = os.path.basename(path)
                success = await self.upload_file(session, path, remote_name)
                if not success:
                    self.logger.warning(f"Retrying {remote_name} to {self.ip} after failure")
                    await asyncio.sleep(2)
                    await self.upload_file(session, path, remote_name)

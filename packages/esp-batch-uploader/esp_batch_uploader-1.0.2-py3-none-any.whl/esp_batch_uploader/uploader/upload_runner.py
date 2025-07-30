import asyncio
from esp_batch_uploader.uploader.upload_client import UploadClient

async def upload_to_batch(batch_ips, file_paths, logger, status_logger):
    tasks = []
    for ip in batch_ips:
        client = UploadClient(ip, logger, status_logger)
        task = asyncio.create_task(client.upload_files(file_paths))
        tasks.append(task)
    await asyncio.gather(*tasks)

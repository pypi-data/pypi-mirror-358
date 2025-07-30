# esp_batch_uploader/uploader/batch_manager.py

import os
from esp_batch_uploader.uploader.discovery import discover_esp32_devices
from esp_batch_uploader.uploader.upload_runner import upload_to_batch


def split_batches(devices, batch_size):
    return [devices[i:i + batch_size] for i in range(0, len(devices), batch_size)]


async def run_batches(files_dir, batch_size, udp_port, logger, status_logger):
    logger.info("Discovering ESP32 devices...")
    devices = await discover_esp32_devices(udp_port)
    if not devices:
        logger.error("No devices found.")
        status_logger.info("No devices found during discovery")
        return

    logger.info(f"Discovered {len(devices)} device(s): {devices}")
    status_logger.info(f"Devices discovered: {devices}")

    file_paths = [
        os.path.join(files_dir, f)
        for f in os.listdir(files_dir)
        if os.path.isfile(os.path.join(files_dir, f))
    ]

    if not file_paths:
        logger.error("No files to upload.")
        return

    batches = split_batches(devices, batch_size)
    logger.info(f"Split into {len(batches)} batch(es) of size {batch_size}")

    for i, batch in enumerate(batches, 1):
        logger.info(f"Processing batch {i}/{len(batches)}: {batch}")
        status_logger.info(f"Uploading to batch {i}: {batch}")
        await upload_to_batch(batch, file_paths, logger, status_logger)

    logger.info("All batches processed.")
    status_logger.info("✅ All uploads completed")

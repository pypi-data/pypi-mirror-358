# esp_batch_uploader/__main__.py

import asyncio
from esp_batch_uploader.uploader.batch_manager import run_batches
from esp_batch_uploader.config import parse_args
from esp_batch_uploader.logger import setup_logger

async def main():
    args, files_dir = parse_args()
    logger, status_logger = setup_logger(args.verbose)

    logger.info("Starting ESP32 batch uploader")
    status_logger.info("Starting ESP32 batch uploader")

    try:
        await run_batches(
            files_dir=files_dir,
            batch_size=args.batch_size,
            udp_port=args.udp_port,
            logger=logger,
            status_logger=status_logger
        )
    except Exception as e:
        logger.exception("Unexpected error during batch upload")
        status_logger.error(f"Unexpected error: {e}")

# 👇 This is the entry point for CLI installation
def main_entry():
    asyncio.run(main())

if __name__ == "__main__":
    main_entry()

# ESP32 Batch File Uploader

This tool discovers multiple ESP32 devices on the network via UDP and uploads files to them over HTTP. Each ESP32 acts as a file upload server.

## Features

- Automatically discovers ESP32 devices via UDP broadcast
- Organizes devices into configurable batches
- Uploads files to each device sequentially, but uploads to devices in parallel
- Logs detailed and high-level status to file and console
- Modular and extensible design

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. ESP32 Server

Each ESP32 should expose an HTTP endpoint like:

```
POST /upload/<filename>
Body: Raw binary data
```

Respond with HTTP 200 on success.

### 3. Run the Script

```bash
python -m esp_batch_uploader
```

You'll be prompted to configure:

- Verbose logging
- Batch size
- HTTP and UDP ports

The tool will:

1. Discover ESP32s
2. Split them into batches
3. Upload files from your current working directory

## Logs

Two log files are generated in `./logs/`:
- `traceback-*.txt` – Detailed logs and errors
- `status-*.txt` – High-level status of uploads

## File Structure

```
esp_batch_uploader/
├── __main__.py
├── config.py
├── logger.py
├── uploader/
│   ├── batch_manager.py
│   ├── discovery.py
│   ├── upload_client.py
│   └── upload_runner.py
```

## License

MIT

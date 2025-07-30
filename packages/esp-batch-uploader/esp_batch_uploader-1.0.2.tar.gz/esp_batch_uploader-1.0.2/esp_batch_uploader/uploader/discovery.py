import asyncio
import socket
import logging

logger = logging.getLogger("ESP32BatchServer.Discovery")

class UDPProtocol(asyncio.DatagramProtocol):
    def __init__(self, queue):
        self.queue = queue

    def datagram_received(self, data, addr):
        ip, _ = addr
        msg = data.decode().strip()
        logger.debug(f"Received UDP from {ip}: {msg}")
        self.queue.put_nowait((ip, msg))


async def discover_esp32_devices(udp_port, timeout=5.0, http_port=8000):
    loop = asyncio.get_running_loop()
    queue = asyncio.Queue()

    # Start UDP listener
    transport, _ = await loop.create_datagram_endpoint(
        lambda: UDPProtocol(queue),
        local_addr=("0.0.0.0", udp_port)
    )

    # === Broadcast discovery message ===
    broadcast_msg = f"SERVER:{socket.gethostbyname(socket.gethostname())}:{http_port}"
    logger.info(f"Broadcasting: {broadcast_msg}")

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.sendto(broadcast_msg.encode(), ("<broadcast>", udp_port))

    logger.info(f"Listening for ESP32 responses on UDP port {udp_port} for {timeout}s")

    discovered = set()
    try:
        start = loop.time()
        while loop.time() - start < timeout:
            try:
                ip, msg = await asyncio.wait_for(queue.get(), timeout=timeout - (loop.time() - start))
                if msg.startswith("ESP32_RESPONSE"):
                    discovered.add(ip)
                    logger.info(f"Discovered ESP32 at {ip}")
            except asyncio.TimeoutError:
                break
    finally:
        transport.close()

    return list(discovered)

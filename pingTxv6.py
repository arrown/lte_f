import asyncio
import websockets
import time
import json
import csv
import os
from datetime import datetime

v = "3mps"
h = "50m"
SERVER_URL = "ws://121.140.95.216:5000/ws/device1"

log_dir = "pingponglogs"
os.makedirs(log_dir, exist_ok=True)
LOG_FILE = os.path.join(log_dir, f"rtt_log_{v}_{h}.csv")

# CSV 헤더 작성 (처음 1회만)
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "start_time(ms)",
            "relay_time(ms)",
            "pong_time(ms)",
            "recv_time(ms)",
            "one_way(ms)",
            "rtt_reported(ms)",
            "rtt_measured(ms)"
        ])

async def ping_loop():
    try:
        print(f"🔌 Connecting to {SERVER_URL}...")
        async with websockets.connect(SERVER_URL) as websocket:
            print("✅ Connected to server as device1")

            while True:
                try:
                    start_time = time.time() * 1000  # ms
                    ping_message = {
                        "type": "ping",
                        "start_time": start_time
                    }

                    await websocket.send(json.dumps(ping_message))
                    print(f"\n📤 Sent ping at {start_time:.2f} ms")

                    response = await asyncio.wait_for(websocket.recv(), timeout=5)
                    recv_time = time.time() * 1000
                    msg = json.loads(response)

                    if msg.get("type") == "pong":
                        relay_time = msg.get("relay_time")
                        pong_time = msg.get("pong_time")

                        if relay_time and pong_time:
                            rtt_half = relay_time - start_time
                            rtt_reported = pong_time - start_time
                            rtt_measured = recv_time - start_time

                            print("↩ Pong received!")
                            print(f"   ▶ One-way  (device1 → device2): {rtt_half:.2f} ms")
                            print(f"   ▶ RTT reported by device2     : {rtt_reported:.2f} ms")
                            print(f"   ▶ RTT measured at device1     : {rtt_measured:.2f} ms")

                            with open(LOG_FILE, "a", newline="") as f:
                                writer = csv.writer(f)
                                writer.writerow([
                                    f"{start_time:.2f}",
                                    f"{relay_time:.2f}",
                                    f"{pong_time:.2f}",
                                    f"{recv_time:.2f}",
                                    f"{rtt_half:.2f}",
                                    f"{rtt_reported:.2f}",
                                    f"{rtt_measured:.2f}"
                                ])
                        else:
                            print("⚠️ Incomplete pong received.")
                    else:
                        print(f"⚠️ Unexpected message: {msg}")

                except asyncio.TimeoutError:
                    print("⏰ Timeout: No pong received.")
                except Exception as e:
                    print(f"❌ Error in loop: {e}")

                await asyncio.sleep(1)

    except KeyboardInterrupt:
        print("\n🛑 Stopped by user (KeyboardInterrupt)")
    except Exception as conn_err:
        print(f"❌ Connection error: {conn_err}")
    finally:
        print("📁 WebSocket session closed. Logs are preserved.")

if __name__ == "__main__":
    asyncio.run(ping_loop())


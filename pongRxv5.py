import asyncio
import websockets
import time
import json

SERVER_URL = "ws://121.140.95.216:5000/ws/device2"

async def pong_loop():
    try:
        async with websockets.connect(SERVER_URL) as websocket:
            print("✅ Connected to server as device2")

            while True:
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=10)
                    msg = json.loads(message)

                    if msg.get("type") == "ping":
                        start_time = msg.get("start_time")
                        relay_time = time.time() * 1000

                        # pong 응답 생성
                        pong_message = {
                            "type": "pong",
                            "start_time": start_time,
                            "relay_time": relay_time,
                            "pong_time": time.time() * 1000
                        }

                        await websocket.send(json.dumps(pong_message))
                        print(f"↩ Pong sent at {relay_time:.2f} ms")

                except asyncio.TimeoutError:
                    print("⏳ Waiting for ping...")
                except Exception as e:
                    print(f"❌ Error: {e}")

    except Exception as conn_err:
        print(f"❌ Could not connect to server: {conn_err}")

if __name__ == "__main__":
    asyncio.run(pong_loop())

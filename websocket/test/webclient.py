# client.py
import asyncio
import websockets
import time

async def send_message(websocket):
    while True:
        message = f"Message sent at {time.time()}"
        print(f"Sending: {message}")
        await websocket.send(message)
        await asyncio.sleep(0.1)

async def receive_message(websocket):
    while True:
        try:
            response = await websocket.recv()
            print(f"Received: {response}")
        except websockets.ConnectionClosedOK:
            print("Connection closed by server")
            break
        except websockets.ConnectionClosedError as e:
            print(f"Connection error: {e}")
            break
        await asyncio.sleep(0.1)

async def main():
    uri = "ws://localhost:8765"
    async with websockets.connect(uri) as websocket:
        send_task = asyncio.create_task(send_message(websocket))
        receive_task = asyncio.create_task(receive_message(websocket))

        await asyncio.wait([send_task, receive_task], return_when=asyncio.FIRST_COMPLETED)

if __name__ == "__main__":
    asyncio.run(main())

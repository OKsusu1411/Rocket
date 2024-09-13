from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QVBoxLayout, QWidget
import asyncio
import websockets
from qasync import QEventLoop

class ServerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("WebSocket Server")
        self.setGeometry(100, 100, 600, 400)

        self.text_edit = QTextEdit(self)
        self.text_edit.setReadOnly(True)

        layout = QVBoxLayout()
        layout.addWidget(self.text_edit)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.server = None

    async def start_server(self):
        async with websockets.serve(self.echo, "localhost", 8765):
            self.text_edit.append("Server started...")
            await asyncio.Future()  # Run forever

    async def echo(self,websocket, path):
        receive_task = asyncio.create_task(self.receive_messages(websocket))
        send_task = asyncio.create_task(self.send_messages(websocket))

        await asyncio.wait([receive_task, send_task], return_when=asyncio.ALL_COMPLETED)

    async def send_messages(self, websocket):# Send new interval to client
        while True:
            try:
                # Send new interval to client
                message = f"Server message at {asyncio.get_event_loop().time()}"
                await websocket.send(message)
                self.text_edit.append(f"Sent: {message}")

                await asyncio.sleep(1)  # 1초 대기 후 다음 메시지 전송
                
            except websockets.exceptions.ConnectionClosed:
                print("Connection to server closed.")

            except Exception as e:
                print(f"Error: {e}")
    
    async def receive_messages(self, websocket):
        async for message in websocket:
            print(f"Received: {message}")

def run_server():
    app = QApplication([])
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    window = ServerWindow()
    window.show()

    loop.run_until_complete(window.start_server())
    with loop:
        loop.run_forever()

if __name__ == "__main__":
    run_server()

import websockets
import threading
import json
from qasync import QEventLoop
import queue
from PyQt5.QtCore import *

import time
import math
import asyncio

connected = set()

class CommunicationManager(QThread):

    velocity_data = pyqtSignal(list)
    w_velocity_data = pyqtSignal(list)
    position_data = pyqtSignal(list)
    Is1stServo_data = pyqtSignal(bool)
    Is2stServo_data = pyqtSignal(bool)
    IsIgnition_data = pyqtSignal(bool)
    IsSeperation_data = pyqtSignal(bool)
    Time_data = pyqtSignal(str)

    def __init__(self,parent):
        super().__init__(parent)
        #'단분리 실행','2단 이그나이터 정지','2단 이그나이터 실행', '2단 낙하산 사출'
        #단분리 서보 기본    2단 서보 기본
        self.mSendDataQueue = queue.Queue()
        self.parent=parent
        self.SERVER_IP = '127.0.0.1'  # 서버의 IP 주소를 입력하세요
        self.SERVER_PORT = 8765  # 서버의 포트를 입력하세요
    
    # async def send_messages(self, websocket):# Send new interval to client
    #     while True:
    #         try:
    #             # Send new interval to client
    #             if self.mSendDataQueue.qsize()>=1:
    #                 print("sendwait")
    #                 senddata = self.mSendDataQueue.get_nowait()
    #                 json_senddata = json.dumps(senddata)
    #                 print(json_senddata)
    #                 await websocket.send(json_senddata)
                
    #         except websockets.exceptions.ConnectionClosed:
    #             print("Connection to server closed.")

    #         except json.JSONDecodeError as e:
    #             print(f"JSON decode error: {e}")
            
    #         except Exception as e:
    #             print(f"Error: {e}")
    async def send_messages(self, websocket):# Send new interval to client
        while True:
            try:
                # Send new interval to client
                message = f"Server message at {asyncio.get_event_loop().time()}"
                await websocket.send(message)
                print(f"Sent: {message}")

                await asyncio.sleep(1)  # 1초 대기 후 다음 메시지 전송
                
            except websockets.exceptions.ConnectionClosed:
                print("Connection to server closed.")

            except Exception as e:
                print(f"Error: {e}")
    

    
    async def receive_messages(self, websocket):
        async for message in websocket:
            print(f"Received: {message}")
        # while True:
        #     try:
        #         # 실제 데이터 수신
        #         json_data = await websocket.recv()
        #         if not json_data:
        #             return
                
        #         # 데이터 가공
        #         readData = json.loads(json_data)
        #         print(readData)
        #         self.velocity_data.emit(readData["IMUData"].split(',')[3:6])
        #         self.w_velocity_data.emit(readData["IMUData"].split(',')[0:3])
        #         self.position_data.emit(readData["IMUData"].split(',')[6:8])
        #         self.Is1stServo_data.emit(readData["Is1stServo"])
        #         self.Is2stServo_data.emit(readData["Is2stServo"])
        #         self.IsIgnition_data.emit(readData["IsIgnition"])
        #         self.IsSeperation_data.emit(readData["IsSeperation"])
        #         t =float(readData["Time"])-round(time.time()%60,3)
        #         if(t>5):
        #             self.Time_data.emit("5second overValue")
        #         else: 
        #             self.Time_data.emit(str(t))
                        
        #     except websockets.exceptions.ConnectionClosed:
        #         print("Connection to server closed.")

        #     except json.JSONDecodeError as e:
        #         print(f"JSON decode error: {e}")
            
        #     except Exception as e:
        #         print(f"Error: {e}")
    
    async def start_server(self):
        async with websockets.serve(self.echo, "localhost", 8765):
            print("Server started...")
            await asyncio.Future()  # Run forever

    async def echo(self,websocket, path):
        receive_task = asyncio.create_task(self.receive_messages(websocket))
        send_task = asyncio.create_task(self.send_messages(websocket))

        await asyncio.wait([receive_task, send_task], return_when=asyncio.ALL_COMPLETED)


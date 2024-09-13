import threading
from IMUmanager import IMUmanager
from RocketProtocol import RocketProtocol
import time
import asyncio

import numpy as np

IMU_ON = False
COMMUNICATION_ON = True


if __name__== "__main__":
    start = time.time()

    mRocketProtocol = RocketProtocol()
    #mRocketProtocol.Cleanup()
    mIMUmanager= IMUmanager(mRocketProtocol)

    if(IMU_ON):
        IMUthread= threading.Thread(target=mIMUmanager.getData)

        IMUthread.start()

    if(COMMUNICATION_ON):
        Commuincationthread= threading.Thread(target=mIMUmanager.communicationMain)
        Commuincationthread.start()
        

    item=[0,0,0,0,0,0,0,0,0]
    while True:
        for i in range(0,9):
            item[i] = 0.0
        mIMUmanager.mSensorCommunicationDataQueue.put(item)
        time.sleep(0.1)
    while not mRocketProtocol.AlgorithmProcess(mIMUmanager.mSensorDataQueue):
        continue

    print("end")
    

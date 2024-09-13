RPI=True

import RPi.GPIO as GPIO


from time import sleep
from time import time


class RocketProtocol:
    def __init__(self):
        ##initial
        self.mSeperationServoPin = 33 ##change

        self.m2ndServoPin = 32

        self.mIgnitionRelayPin = 15 ##change

        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.mSeperationServoPin,GPIO.OUT)
        self.mSeperationServo = GPIO.PWM(self.mSeperationServoPin, 50)
        GPIO.setup(self.m2ndServoPin,GPIO.OUT)
        self.m2ndServo = GPIO.PWM(self.m2ndServoPin, 50)
    
        GPIO.setup(self.mIgnitionRelayPin, GPIO.OUT)
        GPIO.output(self.mIgnitionRelayPin,False)
    
        self.mSeperationServo.start(0)
        self.m2ndServo.start(0)

        self.SERVO_MAX_DUTY = 12.5 # servo Max
        self.SERVO_MIN_DUTY = 2.5

        self.RocketStep=0
        self.RocketMaxStep=4

        # 이그나이터 상태, 단분리 상태, 1단 2단 서보 상태
        self.IsIgnition=False
        self.IsSeperation=True
        self.Is1stServo=False
        self.Is2stServo=True

        self.Is1stAccel=False
        self.Is1stAccelThreshold=10 #m/s

        self.Is2stAccel=True
        self.Is2stAccelThreshold=10 #m/s

    def set2ndServoPos(self,degree):
        if degree > 180:
            degree = 180
        GPIO.setup(self.m2ndServoPin,GPIO.OUT)
        duty =self.SERVO_MIN_DUTY+(degree*(self.SERVO_MAX_DUTY-self.SERVO_MIN_DUTY)/180.0)
        self.m2ndServo.ChangeDutyCycle(duty)
        sleep(0.5)
        GPIO.setup(self.m2ndServoPin,GPIO.IN)

    def set2ndServoBoolean(self,booldata):
        self.Is2stServo=booldata
        if self.Is2stServo:
            self.set2ndServoPos(70);
        else:
            self.set2ndServoPos(105);

    def setSeperationServoPos(self,degree):
        if degree > 180:
            degree = 180
        GPIO.setup(self.mSeperationServoPin,GPIO.OUT)
        duty =self.SERVO_MIN_DUTY+(degree*(self.SERVO_MAX_DUTY-self.SERVO_MIN_DUTY)/180.0)
        self.mSeperationServo.ChangeDutyCycle(duty)
        sleep(0.5)
        GPIO.setup(self.mSeperationServoPin,GPIO.IN)

    def setSeperationServoBoolean(self,booldata):
        self.IsSeperation=booldata
        if self.IsSeperation:
            self.setSeperationServoPos(90);
        else:
            self.setSeperationServoPos(65);
    
    def setIgnition(self,booldata):
        self.IsIgnition=booldata
        if booldata:
             GPIO.setup(self.mIgnitionRelayPin, GPIO.OUT)
             GPIO.output(self.mIgnitionRelayPin,self.IsIgnition)
        else:
             GPIO.setup(self.mIgnitionRelayPin, GPIO.OUT)
             GPIO.output(self.mIgnitionRelayPin,self.IsIgnition)
             #GPIO.setup(self.mIgnitionRelayPin, GPIO.IN)

    
    def Cleanup(self):
        if RPI:
            GPIO.cleanup()


    def Algorithm1Check(self,data):
        # 1차 점화 완료 체크
        # 가속도 Global z값 확인
        if self.Is1stAccel:
            self.previous_value = self.current_value
            self.current_value = data[5]
            
            if self.increasing:
                if self.current_value < self.previous_value:
                    self.increasing = False
                return False
            else:
                if self.current_value < self.Is1stAccelThreshold:
                    self.RocketStep+=1
                    if RPI:
                        self.setSeperationServoBoolean(True)
                    print("Rocket1")
                    self.increasing = False
                    self.Rocket1time=time();
                    return True
                else:
                    return False

        if abs(data[5])>=self.Is1stAccelThreshold: # threshold 확인
            self.Is1stAccel=True
            self.increasing=True
        return False    
        
    def Algorithm2Check(self,data):
        # 2차 점화전 시작 체크
        # 속도 Global z값 확인(1m/s 이상 True)
        # 각속도 Global x,y값 확인
        self.Rocket2time=time()-self.Rocket1time
        if self.Rocket2time>=0.5:
            if ((data[1]*data[1])+(data[2]*data[2]))**(1/2)<=20: #각도 체크
                self.RocketStep+=1
                print("Rocket2")
                return 2
            else:
                self.RocketStep=4
                return 1
        else:
            return 0    
      
    def Algorithm3Check(self,data):
        # 2차 점화후 완료 체크
        # 알고리즘2 체크후 2초동안 확인, 2초 지나면 점화 중지
        # 가속도 Global z값 확인(가속도가 높아지지 않으면 점화 안된 것)
        # 속도 Global z값 확인(1m/s 이상 유지해야함)
        # 각속도 Global x,y값 확인( 로켓 자세가 이상하게 떨어지면 점화 중지 )
        
        self.RocketStep+=1
        self.Rocket3time=time();
        print("Rocket3")
        return True   
     
    def Algorithm4Check(self,data):
        # 2차 추력 완료 체크 == 알고리즘 1번과 같음
        self.Rocket4time=time()-self.Rocket3time
        if self.Is2stAccel:
            self.previous_value = self.current_value
            self.current_value = data[5]
            
            if self.increasing:
                if self.current_value < self.previous_value:
                    self.increasing = False
                return False
            else:
                if self.current_value < self.Is1stAccelThreshold:
                    self.RocketStep+=1
                    if RPI:
                        self.set2ndServoBoolean(True)
                    print("Rocket4")
                    return True
                else:
                    return False

        if abs(data[5])>=self.Is1stAccelThreshold: # threshold 확인
            self.Is2stAccel=True
            self.increasing=True
            
        if self.Rocket4time>=1:
            self.RocketStep+=1
            self.set2ndServoBoolean(True)
            return True
            
        return False  
    
    def AlgorithmProcess(self,mSensorqueue):
        # 알고리즘 전체
        data = mSensorqueue.get()
#        print(data)
        if(self.RocketStep==0):
#            print("Rocket step1")
            self.Algorithm1Check(data)

        elif(self.RocketStep==1):
#            print("Rocket step2")
            num=self.Algorithm2Check(data);
            if(num!=0):
                if(num==1):
                    print("End")
                if(num==2):
                    print("Engine")

        elif(self.RocketStep==2):
#            print("Rocket step3")
            self.Algorithm3Check(data)

        elif(self.RocketStep==3):
#            print("Rocket step4")
            self.Algorithm4Check(data)

        elif(self.RocketStep==4):
            self.RocketStep+=1
            print("Rocket finished")

        return self.RocketStep>=self.RocketMaxStep    
    

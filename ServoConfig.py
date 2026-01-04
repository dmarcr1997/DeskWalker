from servo import Servo
from time import sleep

servo1=Servo(pin=2)
servo2=Servo(pin=4)
servo3=Servo(pin=15)
servo4=Servo(pin=16)
zero = True

def moveServo(srv, pin_num, max):
    print(f"Moving PIN: {pin_num}")
    srv.move(max)
    sleep(1)
    srv.stop()
    
try:
    while True :
        if zero:
            #right hip forward then centered
            moveServo(servo1, 2, 180)
            moveServo(servo1, 2, 90)
            moveServo(servo1, 2, 180)
            
            #left hip forward then centered
            moveServo(servo3, 15, 90)
            moveServo(servo3, 15, 180)
            moveServo(servo3, 15, 90)
            
            #heels up r
            moveServo(servo2, 4, 65)
            moveServo(servo2, 4, 30)
            moveServo(servo2, 4, 65)
            
            #heels up l
            moveServo(servo4, 16, 90)
            moveServo(servo4, 16, 135)
            moveServo(servo4, 16, 90)
            
            #feet up r
            moveServo(servo2, 4, 65)
            moveServo(servo2, 4, 100)
            moveServo(servo2, 4, 65)
            
            #feet up l
            moveServo(servo4, 16, 90)
            moveServo(servo4, 16, 45)
            moveServo(servo4, 16, 90)
            
        
        
except KeyboardInterrupt:
    print("Keyboard interrupt")
    # Turn off PWM 
    servo.stop()
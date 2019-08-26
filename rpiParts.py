import time,sys

import RPi.GPIO as GPIO
##import Adafruit_MPR121.MPR121 as MPR121


import board
import busio

# Import MPR121 module.
import adafruit_mpr121

def setupGPIO():
    GPIO.setmode(GPIO.BCM)

def cleanup():
    GPIO.cleanup()

class feeder():
    def __init__(self,gpio_step,gpio_direction,gpio_sleep,gpio_full,gpio_empty,gpio_bowllight,gpio_touchlight):
        print('Initializing feeder.')
        self.gpio_step = gpio_step
        self.gpio_direction = gpio_direction
        self.gpio_sleep = gpio_sleep
        self.gpio_full = gpio_full
        self.gpio_empty = gpio_empty
        self.gpio_touchlight = gpio_touchlight
        self.gpio_bowllight = gpio_bowllight
        self.stepsPerMl = 460 # assumes 1/8 step mode
        micorSecondPause = 4 # minumum pause is 1.9 microsecond
        self.pauseInterval = micorSecondPause/1000000
        for pin in [gpio_step,gpio_direction,gpio_sleep,gpio_touchlight,gpio_bowllight]:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin,False)
        for pin in [gpio_full,gpio_empty]:
            GPIO.setup(pin, GPIO.IN)
    def toggleLight(self,type,on):
        if type == 'bowl':
            GPIO.output(self.gpio_bowllight,on)
        if type == 'touch':
            GPIO.output(self.gpio_touchlight,on)
        

    def dispense(self,milliliters):
        GPIO.output(self.gpio_direction,milliliters>=0)
        GPIO.output(self.gpio_sleep,True)
        if milliliters<0:
            _steps = milliliters*self.stepsPerMl*(-1)
        else:
             _steps = milliliters*self.stepsPerMl
        n = 0
        while n < _steps:
            if n>35000:
                print('pump does not appear to be working properly!')
                break
            if GPIO.input(self.gpio_empty) == 1 and milliliters>=0:
                print('Pump is Empty')
                break
            if GPIO.input(self.gpio_full) == 1 and milliliters <0:
                print('Pump is Full')
                break
            GPIO.output(self.gpio_step,True)
            time.sleep(self.pauseInterval)
            GPIO.output(self.gpio_step,False)
            time.sleep(self.pauseInterval)
            n+=1
        GPIO.output(self.gpio_sleep,False)

    def returnToFull(self):
        GPIO.output(self.gpio_direction,False)
        GPIO.output(self.gpio_sleep,True)
        n=0
        while 1==1:
            if n>35000:
                print('pump does not appear to be working properly!')
                break
            if GPIO.input(self.gpio_full) == 1:
                print('Pump is full')
                break
            GPIO.output(self.gpio_step,True)
            time.sleep(self.pauseInterval)
            GPIO.output(self.gpio_step,False)
            time.sleep(self.pauseInterval)
            n+=1
        print('Pump filled in '+str(n)+' steps')
        GPIO.output(self.gpio_sleep,False)

    def emptyPump(self):
        GPIO.output(self.gpio_direction,True)
        GPIO.output(self.gpio_sleep,True)
        n=0
        while 1==1:
            if n>35000:
                print('pump does not appear to be working properly!')
                break
            if GPIO.input(self.gpio_empty) == 1:
                print('Pump is empty')
                break
            GPIO.output(self.gpio_step,True)
            time.sleep(self.pauseInterval)
            GPIO.output(self.gpio_step,False)
            time.sleep(self.pauseInterval)
            n+=        print('Pump emptied in '+str(n)+' steps')
        GPIO.output(self.gpio_sleep,False)


print('Adafruit MPR121 Capacitive Touch Sensor Test')

class touchSensor():
    def __init__(self):
        
        # Create I2C bus.
        i2c = busio.I2C(board.SCL, board.SDA)
        # Create MPR121 object.
        self.mpr121 = adafruit_mpr121.MPR121(i2c)
        #reset the thresholds
        for i in range(12):
            self.mpr121[i].threshold = 50
        self.touched = {'last':None}
        for i in range(12):
            self.touched[i] = False
    
    def resetTouched(self):
        self.touched['last'] = None
        for i in range(12):
            self.touched[i] = False

    def watch(self):
        self.resetTouched()
        while True:
            for i in range(12):
                if self.mpr121[i].value and self.touched[i] == False:
                    self.touched[i] = True
                    self.touched['last'] = i
                    print('Input {} touched!'.format(i))    
            
    def listenForFirstTouch(self,timeout):
        #self.resetTouched()
        #touched = False
        startTime = time.time()
        while True:
            for i in range(12):
                #if self.mpr121[i].value and self.touched[i] == False:
                if self.mpr121[i].value:
                    #self.touched[i] = True
                    #self.touched['last'] = i
                    #print('Input {} touched after {} seconds!'.format(i,round(time.time() - startTime,2)))
                    #touched = True
                    return {'action':'touch','time':round(time.time() - startTime,2),'sensor':i}
            if (time.time() - startTime) > timeout:
                return {'action':'timeout','time':timeout}
                    




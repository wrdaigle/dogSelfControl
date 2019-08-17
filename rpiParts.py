import time,sys

import RPi.GPIO as GPIO
##import Adafruit_MPR121.MPR121 as MPR121


import board
import busio

# Import MPR121 module.
import adafruit_mpr121



#setup instruction at https://learn.adafruit.com/mpr121-capacitive-touch-sensor-on-raspberry-pi-and-beaglebone-black/software



def setupGPIO():
    GPIO.setmode(GPIO.BCM)

def cleanup():
    GPIO.cleanup()


class feeder():
    def __init__(self,gpio_step,gpio_direction,gpio_sleep,gpio_full,gpio_empty):
        print('Initializing feeder.')
        self.gpio_step = gpio_step
        self.gpio_direction = gpio_direction
        self.gpio_sleep = gpio_sleep
        self.gpio_full = gpio_full
        self.gpio_empty = gpio_empty
        #self.pauseInterval = 0.43/1000
        for pin in [gpio_step,gpio_direction,gpio_sleep]:
            GPIO.setup(pin, GPIO.OUT)
        for pin in [gpio_full,gpio_empty]:
            GPIO.setup(pin, GPIO.IN)

    def dispense(self,steps,pauseInterval):
        GPIO.output(self.gpio_direction,True)
        GPIO.output(self.gpio_sleep,True)
        n = 0
        while n < steps:
            if n>2000:
                print('pump does not appear to be working properly!')
                break
            if GPIO.input(self.gpio_empty) == 1:
                print('Pump is Empty')
                break
            GPIO.output(self.gpio_step,True)
            time.sleep(pauseInterval)
            GPIO.output(self.gpio_step,False)
            time.sleep(pauseInterval)
            n+=1
        GPIO.output(self.gpio_sleep,False)

    def returnToFull(self,pauseInterval):
        GPIO.output(self.gpio_direction,False)
        GPIO.output(self.gpio_sleep,True)
        n=0
        while 1==1:
            if n>2000:
                print('pump does not appear to be working properly!')
                break
            if GPIO.input(self.gpio_full) == 1:
                print('Pump is full')
                break
            GPIO.output(self.gpio_step,True)
            time.sleep(pauseInterval)
            GPIO.output(self.gpio_step,False)
            time.sleep(pauseInterval)
            n+=1
        GPIO.output(self.gpio_sleep,False)

    def emptyPump(self,pauseInterval):
        GPIO.output(self.gpio_direction,True)
        GPIO.output(self.gpio_sleep,True)
        n=0
        while 1==1:
            if n>2000:
                print('pump does not appear to be working properly!')
                break
            if GPIO.input(self.gpio_empty) == 1:
                print('Pump is empty')
                break
            GPIO.output(self.gpio_step,True)
            time.sleep(pauseInterval)
            GPIO.output(self.gpio_step,False)
            time.sleep(pauseInterval)
            n+=1
        print('Pump emptied in '+str(n)+' steps')
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
            self.mpr121[i].threshold = 40
        
##        
##        # Create MPR121 instance.
##        self.cap = MPR121.MPR121()
##
##        # Initialize communication with MPR121 using default I2C bus of device, and
##        # default I2C address (0x5A).  On BeagleBone Black will default to I2C bus 0.
##        if not self.cap.begin():
##            print('Error initializing MPR121.  Check your wiring!')
##            sys.exit(1)

        # Alternatively, specify a custom I2C address such as 0x5B (ADDR tied to 3.3V),
        # 0x5C (ADDR tied to SDA), or 0x5D (ADDR tied to SCL).
        #self.cap.begin(address=0x5B)

        # Also you can specify an optional I2C bus with the bus keyword parameter.
        #self.cap.begin(bus=1)

##    def resetStates(self):
##        self.leftPadTouched = False
##        self.rightPadTouched = False

    def watch(self):
        # Main loop to print a message every time a pin is touched.
        print('Press Ctrl-C to quit.')
##        last_touched = self.cap.touched()
        while True:
            for i in range(12):
                # Call is_touched and pass it then number of the input.  If it's touched
                # it will return True, otherwise it will return False.
                if self.mpr121[i].value:
                    print('Input {} touched!'.format(i))
            time.sleep(0.1)
            
##            current_touched = self.cap.touched()
##            # Check each pin's last and current state to see if it was pressed or released.
##            for i in range(12):
##
##                # Each pin is represented by a bit in the touched value.  A value of 1
##                # means the pin is being touched, and 0 means it is not being touched.
##                pin_bit = 1 << i
##                # First check if transitioned from not touched to touched.
##                if current_touched & pin_bit and not last_touched & pin_bit:
##                    print('{0} touched!'.format(i))
##                # Next check if transitioned from touched to not touched.
##                if not current_touched & pin_bit and last_touched & pin_bit:
##                    print('{0} released!'.format(i))
##            # Update last state and wait a short period before repeating.
##            last_touched = current_touched
##            time.sleep(0.1)

            # Alternatively, if you only care about checking one or a few pins you can
            # call the is_touched method with a pin number to directly check that pin.
            # This will be a little slower than the above code for checking a lot of pins.
            #if self.cap.is_touched(0):
            #    print('Pin 0 is being touched!')

            # If you're curious or want to see debug info for each pin, uncomment the
            # following lines:
            #print('\t\t\t\t\t\t\t\t\t\t\t\t\t 0x{0:0X}'.format(self.cap.touched()))
            #filtered = [self.cap.filtered_data(i) for i in range(12)]
            #print 'Filt:', '\t'.join(map(str, filtered))
            #base = [self.cap.baseline_data(i) for i in range(12)]
            #print('Base:', '\t'.join(map(str, base)))



##import RPi.GPIO as GPIO
##import time
##
#### left pump
###pin_step        = 17
###pin_direction   = 27
###pin_sleep       = 22
##pin_limit_full  = 24
##pin_limit_empty = 25
##
#### right pump
##pin_step        = 19
##pin_direction   = 26
##pin_sleep       = 13
###pin_limit_full  = 24
###pin_limit_empty = 25
##
##GPIO.setmode(GPIO.BCM)
##
##print(1)
##
##for pin in [pin_step,pin_direction,pin_sleep]:
##    print('pin',pin)
##    GPIO.setup(pin, GPIO.OUT)
##
##for pin in [pin_limit_full,pin_limit_empty]:
##    GPIO.setup(pin, GPIO.IN)
##
##
##
##print(2)
###time.sleep(3)
##print(3)
##
###set the direction
##def setDirection(direction):
##    if direction == 'left':
##        GPIO.output(pin_direction,True)
##    if direction == 'right':
##        GPIO.output(pin_direction,False)
##
##def movePlunger(direction, steps):
##    print(4)
##    setDirection(direction)
##    #time.sleep(3)
##    print(5)
##    GPIO.output(pin_sleep,True)
##    print(6)
##    #time.sleep(3)
##    print(7)
##    n = 0
##    while n < steps:
##
##        if direction == 'left' and GPIO.input(pin_limit_full) == 1:
##            break
##        if direction == 'right' and GPIO.input(pin_limit_empty) == 1:
##            break
##        GPIO.output(pin_step,True)
##        time.sleep(0.43/1000)
##        GPIO.output(pin_step,False)
##        n+=1
##    print(8)
##    #time.sleep(3)
##    GPIO.output(pin_sleep,False)
##    print(9)
##
##def checkLimitSwitchStatus():
##    n=0
##    while n<50:
##        time.sleep(0.5)
##        n+=1
##        print('')
##        print('full',GPIO.input(pin_limit_full))
##        print('empty',GPIO.input(pin_limit_empty))
###checkLimitSwitchStatus()
##
###movePlunger('left',50)
###movePlunger('right',50)
##movePlunger('left',100)
##time.sleep(3)
##movePlunger('right',100)
##
##GPIO.cleanup()



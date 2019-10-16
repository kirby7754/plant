import os #needed to check if file exists
import serial #needed for Arduino 
import time #needed for sleep
import Adafruit_DHT #temp and hum
import gpiozero #CPUtemp
import RPi.GPIO as GPIO 
from subprocess import call # for shutdown
import datetime

#TEST

filename = "plant_data"
too_dry = 35             # set the trigger for watering

#set birthday#######
birth_year = 2019  #
birth_month = 9    #
birth_day = 1      #
####################

birthday = datetime.date(birth_year, birth_month, birth_day)

#importing Adafruit and setting the GPIO for temp and hum sensor
DHT_SENSOR = Adafruit_DHT.DHT22
DHT_PIN = 4
GPIO.setmode(GPIO.BCM)

#setting CPU temp
cpu = gpiozero.CPUTemperature()

f = open('/home/pi/' + filename + '.csv', 'a+')
if os.stat('/home/pi/' + filename + '.csv').st_size == 0:
    f.write('Date,Time,Temperature,Humidity,CoreTemp, Water Sat,water?, Last watered, Days Old\r\n')
else:
    pass


f.write('RESET,RESET,RESET,RESET,RESET, RESET,RESET,RESET\r\n')


                     ### FUNCTIONS ###


#call to water plants
def water(sec):
    GPIO.output(relay, GPIO.LOW)
    time.sleep(sec)
    GPIO.output(relay, GPIO.HIGH)
    test1 = time.strftime('%m/%d/%y')
    return test1    

#test
def test():
    test1 = time.strftime('%m/%d/%y')
    return test1

#start test to water at 0
water_test = 0

####TODO set up to look up last watered in csv              ######
last_watered = 0

                  #### START infinite loop ####
while True:

    
    today = datetime.date.today()
    age = (today - birthday).days

    #setup arduino, needs to go here
    arduino = serial.Serial("/dev/ttyACM0", timeout=1, baudrate=9600)
    
    #shut down if the core temp gets close to 80*C 
    if int(cpu.temperature) >= 77:
        call("sudo shutdown -h now, shell=True")
    else:
        pass

    #check the time (minutes) and see if its the right time 
    #if True: #FOR TESTING
    if int(time.strftime('%M')) == int(30) or int(time.strftime('%M')) == int(59):

        #read hum and temp
        humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)        

        #read the soil moisture
        try:
            v1 = 0

            soil_read = arduino.readline()
            moist_test = -(((float(soil_read.decode('ASCII')) - 325)/3)-100)
            
            # if the moist test runs an error try again until it works, up to 5 times
            while moist_test >= int(100) or moist_test <= int(1):
                soil_read = arduino.readline()
                moist_test = -(((float(soil_read.decode('ASCII')) - 325)/3)-100)
                v1 += 1
                if v1 > 5:
                    break

                
        except:
            moist_test = 0
        
#should I water__________________________________________________________________
        if moist_test <= too_dry and moist_test > 0: #TEST              ####should be 30
            water_test += 1
        else:
            water_test = max(0, water_test - 1)
            
        #set to water
        if water_test > 5:
            water_yes = True
        else:
            water_yes = False
            
        #set up watering for 1130am and reset count
        #if int(time.strftime('%M')) == int(59) and water_yes == True: ####TEST
        if int(time.strftime('%M')) == int(30) and int(time.strftime('%H')) == int(11) and water_yes == True:
            print("watered") # TEST   WILL BE WATER FUNCTION
            last_watered = test()
            water_test = 0
        else:
            pass

#_________________________________________________________________________________


                            ##writes code to CSV## 
        try:
            f = open('/home/pi/' + filename + '.csv', 'a+')
            f.write('{0},{1},{2:0.1f}*f,{3:0.1f}%,{4:0.1f}*C,{5:0.1f}%,{6},{7},{8}\r\n'.format(
                                                              time.strftime('%m/%d/%y'),
                                                              time.strftime('%H:%M'),
                                                              temperature * 1.8 + 32,
                                                              humidity,
                                                              cpu.temperature,
                                                              moist_test,
                                                              water_yes,
                                                              last_watered,
                                                              age))

        except:
            print("Failed to post data")
            pass
        
#data points
        print(time.strftime('%H:%M'))
        print('moist: ' + str('{0:0.1f}'.format(moist_test)))
        #print('last watered: ' + str(last_watered))
        print('water test: ' + str(water_test))
        print("")
        

        
    else:
        pass
    time.sleep(55)
    #time.sleep(5)

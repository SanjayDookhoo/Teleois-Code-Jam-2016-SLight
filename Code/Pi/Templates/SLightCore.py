from firebase import firebase
import datetime
import ast
import os
import pickle
import time
import threading
#insertHere
import datetime
import time
import calendar
# import RPi.GPIO as GPIO
from EmulatorGUI import GPIO

class Sensor:
    def __init__(self,pin):
        self._pin=pin # GPIO pin related to sensor
        self._state=0 # on or off
        self._time=0 # time last passed
        self._expectedSensorPass=-1 # vehicle expected to pass
        self._distance=0 #distance between sensors, distance that cannot be changed
        
    @property
    def pin(self):
        return self._pin

    @pin.setter
    def pin(self, value):
        self._pin = value
        
        
    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        self._state = value


    @property
    def time(self):
        return self._time

    @time.setter
    def time(self, value):
        self._time = value


    @property
    def expectedSensorPass(self):
        return self._expectedSensorPass

    @expectedSensorPass.setter
    def expectedSensorPass(self, value):
        self._expectedSensorPass = value


    @property
    def distance(self):
        return self._distance

    @distance.setter
    def distance(self, value):
        self._distance = value
        
    # Function used to detect if an object has passed the sensor or not
    def scan(self): 
        curr= GPIO.input(self._pin)
        if curr ==0: # For python 2.7
            return self._pin  
        else:     
            return 0

class Sensors:  
    def __init__(self,sensorsToAdd):
        self._sensors=[]
        for i in range(0,len(sensorsToAdd)):
            self.addNewSensor(sensorsToAdd[i])
        
    @property
    def sensor(self):
        return self._sensor

    @sensor.setter
    def sensor(self, value):
        self._sensors = value
        
    def addNewSensor(self, pin):
        self._sensors.append(Sensor(pin))
        
    def getSensor(self,i):
        return self._sensors[i]
        
    def numSensors(self):
        return len(self._sensors)
        
    # Sets the distance between all sensors to be of even distance which is received as an argument
    def setAllsensorsDistance(self,dist):
        for i in range(0,self.numSensors()):
            self._sensors[i].distance=dist
            
    # Sets the GPIO Pins of the PI's sensors to send input to PI 
    def setGPIOIn(self):
        for i in range(0,self.numSensors()):
            GPIO.setup(self._sensors[i].pin,GPIO.IN)

    # Update ExpectedSensorPass at a position to the vehicle index passed
    def updateExpectedSensorPass(self,passToLeadingPi,sensor,vehicle):
        if sensor<self.numSensors():
            self._sensors[sensor].expectedSensorPass=vehicle
        else:
            #passToLeadingPi.expectedSensorUpdate(-2)
            a=1
    
    # Initialized SensorState to all be off
    def initSensorState(self):
        for i in range(0,self.numSensors()):
            self._sensors[i].state=0
            
class Led:
    def __init__(self,pin):
        self._pin=pin # related GPIO pin
        self._state=0 # on or off   
        self._stateNew=0 #used to ensure vehicles on and off triggering of leds does not conflict
        self._distance=0 # distance between leds
        
    @property
    def pin(self):
        return self._pin

    @pin.setter
    def pin(self, value):
        self._pin = value
        
        
    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        self._state = value


    @property
    def stateNew(self):
        return self._stateNew

    @stateNew.setter
    def stateNew(self, value):
        self._stateNew = value


    @property
    def distance(self):
        return self._distance

    @distance.setter
    def distance(self, value):
        self._distance = value
        
        
class Leds:
    def __init__(self,ledsToAdd):
        self._leds=[]
        for i in range(0,len(ledsToAdd)):
            self.addNewLeds(ledsToAdd[i])
        
    @property
    def led(self):
        return self._led

    @led.setter
    def led(self, value):
        self._led = value
        
    def numLeds(self):
        return len(self._leds)
        
    def addNewLeds(self,pin):
        self._leds.append(Led(pin))
        
    def getLed(self,i):
        return self._leds[i]
        
    def turnOnLeds(self):
        for i in range(0,self.numLeds()):
            if self._leds[i].state:
                GPIO.output(self._leds[i].pin,GPIO.HIGH)
            else:
                GPIO.output(self._leds[i].pin,GPIO.LOW)
        
    # Based on the amount of LEDs that are controlled by the PI, the LEDs distance is calculated evenly based on the sensors distance(most likely set by the function above)
    def setAllLEDsDistance(self,sensors,LEDsMult):
        for i in range(0,sensors.numSensors()):
            if i==0:
                dist=sensors.getSensor(i).distance
                avg=dist/LEDsMult
            else:
                dist=sensors.getSensor(i).distance
                avg=dist/LEDsMult
            
            for j in range(i*LEDsMult,((i+1)*LEDsMult)):
                self._leds[j].distance=avg
                
    # Sets the GPIO Pins of the PI's LEDs to receive output from the PI 
    def setGPIOOut(self):
        for i in range(0,self.numLeds()):
            GPIO.setup(self._leds[i].pin,GPIO.OUT)
    
    def initLEDsStateNew(self):
        for i in range(0,self.numLeds()):
            self._leds[i].stateNew="-"
            
    def initLEDsState(self):
        for i in range(0,self.numLeds()):
            self._leds[i].state=0
            
    #*(vision range should also be accounted for in the range) If the vehicle has now entered the track then the speed cannot be calculated unless there are two points, therefore all LEDs between the succeeding sensor and the previous sensor is turned on to give the most vision possible
    def addVehicleStartingLeds(self,LEDsMult):
        tempLeading=[]
        tempTrailing=[]
        for i in range(0,LEDsMult): # All LEDs between the succeeding sensor and the previous sensor is turned on to give the most vision possible
            self._leds[i].state=1
    
    # Vehicle speed can now be calculated therefore the LEDs that was turned on for vision in the previous function is turned off
    def removeVehicleStartingLeds(self,LEDsMult):
        tempLeading=[]
        tempTrailing=[]
        for i in range(0,LEDsMult):
            self._leds[i].stateNew=0
            
    # LEDsState value is correctly assigned from the buffer LEDsStateNew, whose purpose was to ensure different vehicles LEDs light and fade did not clash due to sequence of operations
    def updateStateFromNew(self):
        for i in range(0,self.numLeds()):
            if self._leds[i].stateNew!="-":
                self._leds[i].state=self._leds[i].stateNew
    
class Vehicle:
    def __init__(self,currentPos,timePlaced,speed,visionRange):
        self._currentPos=currentPos #current positon
        self._timePlaced=timePlaced #time placed in that position
        self._speed=speed #speed
        self._visionRange=visionRange #vision ahead, how many leds ahead
        
        #used for calculating cloud database big data
        self._maxSpeed=0
        self._sensorsPassed=0
        self._avgSpeed=0
        
    @property
    def currentPos(self):
        return self._currentPos

    @currentPos.setter
    def currentPos(self, value):
        self._currentPos = value


    @property
    def timePlaced(self):
        return self._timePlaced

    @timePlaced.setter
    def timePlaced(self, value):
        self._timePlaced = value


    @property
    def speed(self):
        return self._speed

    @speed.setter
    def speed(self, value):
        self._speed = value


    @property
    def visionRange(self):
        return self._visionRange

    @visionRange.setter
    def visionRange(self, value):
        self._visionRange = value


    @property
    def maxSpeed(self):
        return self._maxSpeed

    @maxSpeed.setter
    def maxSpeed(self, value):
        self._maxSpeed = value


    @property
    def sensorsPassed(self):
        return self._sensorsPassed

    @sensorsPassed.setter
    def sensorsPassed(self, value):
        self._sensorsPassed = value


    @property
    def avgSpeed(self):
        return self._avgSpeed

    @avgSpeed.setter
    def avgSpeed(self, value):
        self._avgSpeed = value
    
    def getVehicleDict(self):
        return {"currentPos":self._currentPos,"timePlaced":self._timePlaced,"speed":self._speed,"visionRange":self._visionRange,"maxSpeed":self._maxSpeed,"sensorsPassed":self._sensorsPassed,"avgSpeed":self._avgSpeed}
        
    def setVehicleDict(self,veh):
        
        self._currentPos=veh["currentPos"]
        self._timePlaced=veh["timePlaced"]
        self._speed=veh["speed"]
        self._visionRange=veh["visionRange"]
        self._maxSpeed=veh["maxSpeed"]
        self._sensorsPassed=veh["sensorsPassed"]
        self._avgSpeed=veh["avgSpeed"]
    
class Vehicles:
    def __init__(self):
        self._vehicles=[]
        
    @property
    def vehicle(self):
        return self._vehicle

    @vehicle.setter
    def vehicle(self, value):
        self._vehicle = value
        
    def addNewVehicle(self,currentPos,timePlaced,speed,visionRange):
        self._vehicles.append(Vehicle(currentPos,timePlaced,speed,visionRange))
        
    def getVehicle(self,i):
        return self._vehicles[i]
        
    def numVehicles(self):
        return len(self._vehicles)
        
    def pop(self,i):
        return self._vehicles.pop(i)
        
class LeadingData:
    def __init__(self):
        self._light=[]
        self._fade=[]
        self._newVehicle=None
        self._expectedSensorUpdate=None
        self._lastSensorTime=None
        
    @property
    def light(self):
        return self._light

    @light.setter
    def light(self, value):
        self._light = value


    @property
    def fade(self):
        return self._fade

    @fade.setter
    def fade(self, value):
        self._fade = value


    @property
    def newVehicle(self):
        return self._newVehicle

    @newVehicle.setter
    def newVehicle(self, value):
        self._newVehicle = value


    @property
    def expectedSensorUpdate(self):
        return self._expectedSensorUpdate

    @expectedSensorUpdate.setter
    def expectedSensorUpdate(self, value):
        self._expectedSensorUpdate = value


    @property
    def lastSensorTime(self):
        return self._lastSensorTime

    @lastSensorTime.setter
    def lastSensorTime(self, value):
        self._lastSensorTime = value
         
    def setDataDict(self,data):
        self._light=data["light"]
        self._fade=data["fade"]
        self._newVehicle=data["newVehicle"]
        self._expectedSensorUpdate=data["expectedSensorUpdate"]
        self._lastSensorTime=data["lastSensorTime"]
        
    def getDataDict(self):
        return {"light":self._light,"fade":self._fade,"newVehicle":self._newVehicle,"expectedSensorUpdate":self._expectedSensorUpdate,"lastSensorTime":self._lastSensorTime}

class TrailingData:
    def __init__(self):
        self._light=[]
        self._fade=[]
        
    @property
    def light(self):
        return self._light

    @light.setter
    def light(self, value):
        self._light = value


    @property
    def fade(self):
        return self._fade

    @fade.setter
    def fade(self, value):
        self._fade = value
        
    def setData(self,data):
        self.data=data
        self.change=1
        
    def getData(self):
        return self.data
        
    def setDataDict(self,data):
        self._light=data["light"]
        self._fade=data["fade"]
        
    def getDataDict(self):
        return {"light":self._light,"fade":self._fade}

class FirebaseSys:
    def __init__(self,id):
        self._id=id
        self._avgSpeed=0
        self._numOfNewCars=0
        self._LEDsTurnedOn=0
        
        self._timeBeforeLEDUpdate=time.time()
        self._min=0
        self._sec=0
        
        # Firebase =firebase.FirebaseApplication('https://prog-c99a8.firebaseio.com/')
        Firebase =firebase.FirebaseApplication('https://slight-91c01.firebaseio.com/')
    
    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        self._id = value


    @property
    def avgSpeed(self):
        return self._avgSpeed

    @avgSpeed.setter
    def avgSpeed(self, value):
        self._avgSpeed = value


    @property
    def numOfNewCars(self):
        return self._numOfNewCars

    @numOfNewCars.setter
    def numOfNewCars(self, value):
        self._numOfNewCars = value


    @property
    def LEDsTurnedOn(self):
        return self._LEDsTurnedOn

    @LEDsTurnedOn.setter
    def LEDsTurnedOn(self, value):
        self._LEDsTurnedOn = value
        
        
    @property
    def timeBeforeLEDUpdate(self):
        return self._timeBeforeLEDUpdate

    @timeBeforeLEDUpdate.setter
    def timeBeforeLEDUpdate(self, value):
        self._timeBeforeLEDUpdate = value
        
    
    @property
    def min(self):
        return self._min

    @min.setter
    def min(self, value):
        self._min = value


    @property
    def sec(self):
        return self._sec

    @sec.setter
    def sec(self, value):
        self._sec = value

    def pushData(dataModel):
        ts = time.time()
        hour = datetime.datetime.fromtimestamp(ts).strftime("%H")
        minute = datetime.datetime.fromtimestamp(ts).strftime("%M")
        day = datetime.datetime.fromtimestamp(ts).strftime("%d")
        year= datetime.datetime.fromtimestamp(ts).strftime("%Y")
        month= datetime.datetime.fromtimestamp(ts).strftime("%m")
        parent = "Pi_"+str(dataModel["id"])+"/" +year+"/" + calendar.month_name[int(month)] + "/" +day +"/" 
        Firebase.put(parent+"/"+hour +"/"+ str(minute) ,"No Of Cars",dataModel["numOfNewCars"])
        Firebase.put(parent+"/"+hour +"/"+ str(minute),"Speed",dataModel["avgSpeed"]);
        Firebase.put(parent+"/"+hour +"/"+ str(minute),"LEDsTimeOn",dataModel["LEDsTurnedOn"]);

#GENERAL system functions henceforth        

#*(to rename) Calculation of speed, Application of the formula: Speed = Distance/Time
def calcStepThroughTime(distance,speed):
        return distance/speed

#*(to implement calculation) Vision range is calculated based on how fast the vehicle is travelling, this is necessary because a faster vehicle will need to vision ahead and behind his/her vehicle to then react to a situation
def calcVisionRange(timeDifference):
        return 1

# Calcualtes Speed
def calcSpeed(distance, time):
    return distance/time 
    
# Turns on light ahead of vehicles expected positon and turns off lights that are no longer needed since the vehicle has passed
def stepThrough(vehicles,sensors,leds,passToLeadingPi,passToTrailingPi): 
    currentTime=time.time()
    lengthArr = vehicles.numVehicles()
    i=0
    LEDsNum=leds.numLeds()
    while i<lengthArr: # Light and fade LEDs for all vehicles that entered the tract
        if vehicles.getVehicle(i).speed!=-1: # If the vehicle has a speed of 0 then it has not only just entered the track(as well as all linked tracks), therefore a speed cannot be calculated to determine what lights to turn on. (not controlled here but all LEDs between the sensor passed, the next sensor and previous sensor is turned on) 
            if vehicles.getVehicle(i).currentPos<leds.numLeds(): # If vehicle is still being controlled by this PI, if not the vehicles data is passed to the leading PI
                stepThroughTime=calcStepThroughTime(leds.getLed(vehicles.getVehicle(i).currentPos).distance,vehicles.getVehicle(i).speed) # Speed Calcualted
            
                if stepThroughTime+vehicles.getVehicle(i).timePlaced <currentTime: # If the vehicles speed and the time it was placed determines if at the current time the LEDs should right shift 1 place down
                    # Change timeplaced and currentPosition
                    vehicles.getVehicle(i).timePlaced=vehicles.getVehicle(i).timePlaced+stepThroughTime
                    vehicles.getVehicle(i).currentPos+=1

                    # Update LEDsStateNew
                    pos=vehicles.getVehicle(i).currentPos
                    leadingPos=pos+vehicles.getVehicle(i).visionRange
                    trailingPos=pos-vehicles.getVehicle(i).visionRange
                    
                    # Trailing LED to leading LED must be changed to high
                    tempTrailing=[]# init to an array then proceed to append
                    tempLeading=[]# init to an array then proceed to append
                    for i in range(trailingPos,leadingPos+1):
                        if i<0: # passToTrailingPi-light
                            tempTrailing.append(LEDsNum-i)
                        elif i>=LEDsNum:# passToLeadingPi-light
                            tempLeading.append(i-LEDsNum)
                        else:
                            leds.getLed(i).stateNew=1
                            
                    # Pass data of which LEDs to turn on
                    passToTrailingPi.light=tempTrailing
                    passToLeadingPi.light=tempLeading

                    trailingPos=trailingPos-1#* Two less characters
                    
                    # One LED before trailing LED can be changed to low if possible,to simulate the removal of LEDs as the vehicle passes
                    if trailingPos>=0:
                        leds.getLed(trailingPos).stateNew=0
                    else:
                        #P assToTrailingPi-fade
                        tempTrailing=[]
                        tempTrailing.append(LEDsNum-(trailingPos*-1))
                        passToTrailingPi.fade=tempTrailing
                                        
            else:   
                #Pass vehicle to next pi
                temp=vehicles.pop(i) # Remove vehicle from this PIs list
                
                #converting the object returned to a dict expected
                tempVehicle=temp.getVehicleDict()
                
                tempVehicle["currentPos"]=0 # New vehicle entering the beginning of the track will be at currentPos=0
                passToLeadingPi.newVehicle=tempVehicle
                lengthArr = vehicles.numVehicles()
                
                
        i=i+1;
    

def PassToLeadingPiSend(passToLeadingPi,receiveFromTrailingPi):
    receiveFromTrailingPi.setDataDict(passToLeadingPi.getDataDict())
    return LeadingData()
    
def PassToTrailingPiSend(receiveFromLeadingPi,passToTrailingPi):
    receiveFromLeadingPi.setDataDict(passToTrailingPi.getDataDict())
    return TrailingData()
    
# Receive from leading pi
def ReceiveFromLeadingPiStore(receiveFromLeadingPi,leds):
    # Receive light
    lights=receiveFromLeadingPi.light
    if lights!=None:
        for i in range(0,len(lights)):
            leds.getLed(lights[i]).stateNew=1

    # Receive fade
    fades=receiveFromLeadingPi.fade
    if fades!=None:
        for i in range(0,len(fades)):
            leds.getLed(fades[i]).stateNew=0
        
    # After receiving all data reset data contained for next iteration
    return TrailingData() #no need to check if the value is None here since should this data be needed, it will be guaranteed to exist
        
# Receive from trailing pi
def ReceiveFromTrailingPiStore(receiveFromTrailingPi,leds,vehicles,lastPiSensorTime,sensors,passToLeadingPi):
    #updateExpectedSensorFromPi(expectedSensorPass,receiveFromTrailingPi)#receive expectedSensorTime
    if receiveFromTrailingPi.expectedSensorUpdate==-2:
        sensors.updateExpectedSensorPass(passToLeadingPi,0, -2)
    #receive light
    lights=receiveFromTrailingPi.light
    if lights!=None:
        for i in range(0,len(lights)):
            leds.getLed(lights[i]).stateNew=1
    #receive fade
    fades=receiveFromTrailingPi.fade
    if fades!=None:
        for i in range(0,len(fades)):
            leds.getLed(fades[i]).stateNew=0
    #receive newVehicle
    if receiveFromTrailingPi.newVehicle!=None:
        veh=Vehicle(0,0,0,0) #will be set after
        veh.setVehicleDict(receiveFromTrailingPi.newVehicle)
        #veh=receiveFromTrailingPi.newVehicle
        veh.timePlace=time.time()
        vehicles.addNewVehicle(veh.currentPos,veh.timePlaced,veh.speed,veh.visionRange)
        #addVehicleStartingLEDs(0)#will always be pos 0 since it now exited the previous pis track
        sensors.updateExpectedSensorPass(passToLeadingPi,1, vehicles.numVehicles()-1)
    #receive lastSensorTime
    if receiveFromTrailingPi.lastSensorTime!=None:
        lastPiSensorTime=receiveFromTrailingPi.lastSensorTime

    #after receiving all data reset data contained for next iteration
    return LeadingData() #no need to check if the value is None here since should this data be needed, it will be guaranteed to exist

def genLEDsFirebaseModel(leds):
    model= {}
    for i in range(0,leds.numLeds()):
        model[str(i)]=1
    return model
    
def updateLEDsModel(LEDsModel,timeDiff,leds):
    for i in range(0,leds.numLeds()):
        if(leds.getLed(i).state==1):
            LEDsModel[str(i)]=LEDsModel[str(i)]+timeDiff
    return LEDsModel
    
def main():
    try:
        # variables
        #This is where LEDS and SENSORs as it relates to the pi is hardcoded
        leds=Leds([15,18,23,24,8,7,12,16,21,26,19,13,5,11,9,10,27,17,4,3])
        sensors=Sensors([14,25,20,6,22])
        
        firebaseSys=FirebaseSys(1) #firebase id=1, this id is how the data will be identified on firebase
        passToLeadingPi=LeadingData()
        receiveFromTrailingPi=LeadingData()
        passToTrailingPi=TrailingData()
        receiveFromLeadingPi=TrailingData()
        vehicles=Vehicles()
        LEDsMult=int(leds.numLeds()/sensors.numSensors()) # How many LEDs that is between two sensors
        LEDsModel=genLEDsFirebaseModel(leds)
        dataModelInit={'id':id, 'avgSpeed': 0,'numOfNewCars' :0,'LEDsTurnedOn': {} }
        dataModel=dataModelInit
        
        GPIO.setmode(GPIO.BCM)
        
        sensors.setAllsensorsDistance(5) # value used in this demo does not matter since it is constant
        sensors.setGPIOIn()
        sensors.initSensorState()
        leds.setAllLEDsDistance(sensors,LEDsMult)
        leds.setGPIOOut()
        leds.initLEDsState()
        
        lastPiSensorTime=-1
        
        while True:
            leds.initLEDsStateNew()
            
            # Pi to Pi communication
            receiveFromLeadingPi=ReceiveFromLeadingPiStore(receiveFromLeadingPi,leds)
            receiveFromTrailingPi=ReceiveFromTrailingPiStore(receiveFromTrailingPi,leds,vehicles,lastPiSensorTime,sensors,passToLeadingPi)
            
            # Keeps scanning for motion
            for i in range(0,sensors.numSensors()):
                state = sensors.getSensor(i).scan()
                
                if state and sensors.getSensor(i).state==0: # Vehicle has now passed the sensor
                    sensors.getSensor(i).time=time.time()#the time which the sensor was triggered is stored

                    # passToLeadingPi-LastSensorTime
                    #if state==sensorsNum-1:
                    #    passToLeadingPi.lastSensorTime(sensors.getSensor(i).time)

                    sensors.getSensor(i).state=1
                    
                    #*(to delete fnction isNewVehicle) Create new vehicle if 1st sensor is passed
                    if i==0 and sensors.getSensor(0).expectedSensorPass==-1:
                        # AddVehicle
                        vehicles.addNewVehicle(0,sensors.getSensor(i).time,-1,-1)
                        leds.addVehicleStartingLeds(LEDsMult)
                        sensors.updateExpectedSensorPass(passToLeadingPi,i+1, vehicles.numVehicles() - 1) # Update expectedSensorPass of the next index to this vehicle that was just appended. This is to ensure that the correct vehicle speed is updated
                        
                        #increment car counter to pass to firebase
                        dataModel["numOfNewCars"]=dataModel["numOfNewCars"]+1
                    else:
                        if sensors.getSensor(i).expectedSensorPass>=0:
                            if vehicles.getVehicle(sensors.getSensor(i).expectedSensorPass).speed==-1: # If the last vehicle that entered the track speed=-1, then the starting lights must be removed
                                leds.removeVehicleStartingLeds(LEDsMult)
                            
                        #update expectedsensor since vehicle is progressing through the track
                        if sensors.getSensor(i).expectedSensorPass!=-2:
                            #*(for now treat it as though there is no previous pi, this line will be removed)
                            vehicles.getVehicle(sensors.getSensor(i).expectedSensorPass).speed=calcSpeed(sensors.getSensor(i).distance,sensors.getSensor(i).time-sensors.getSensor(i-1).time)

                            veh=sensors.getSensor(i).expectedSensorPass
                            sensors.updateExpectedSensorPass(passToLeadingPi,i+1, veh)
                            sensors.updateExpectedSensorPass(passToLeadingPi,i, -1)
                        else:# if it was -2 then the sensor was passed before the vehicle entered the track therefore a wrong 
                            sensors.updateExpectedSensorPass(passToLeadingPi,i+1, len(vehicles)-1)
                            sensors.updateExpectedSensorPass(sensorsNum,passToLeadingPi,i, -1)
                                
                                
                        #Update vision range because speed changed
                        vehicles.getVehicle(sensors.getSensor(i).expectedSensorPass).visionRange= calcVisionRange(vehicles.getVehicle(sensors.getSensor(i).expectedSensorPass).speed)
                        
                        #add onto maxSpeed with current speed value to calulate avg
                        vehicles.getVehicle(sensors.getSensor(i).expectedSensorPass).maxSpeed=vehicles.getVehicle(sensors.getSensor(i).expectedSensorPass).maxSpeed + vehicles.getVehicle(sensors.getSensor(i).expectedSensorPass).speed
                        vehicles.getVehicle(sensors.getSensor(i).expectedSensorPass).sensorsPassed=vehicles.getVehicle(sensors.getSensor(i).expectedSensorPass).sensorsPassed+1

                elif state and sensors.getSensor(i).state==1: # Vehicle is still passing the sensor
                    sensors.getSensor(i).state=1
                elif state==0 and sensors.getSensor(i).state==1: # Vehicle has finished passing the sensor
                    sensors.getSensor(i).state=0
                    
            #pass and receive data
            
            #creates cycle if multiple PIs does not exist
            #passToLeadingPi=PassToLeadingPiSend(passToLeadingPi,receiveFromTrailingPi)
            #passToTrailingPi=PassToTrailingPiSend(receiveFromLeadingPi,passToTrailingPi)
            
            # PI to PI communication
            #insertHere
            
            #reset pi to transfer data
            passToLeadingPi=LeadingData()
            passToTrailingPi=TrailingData()
                    
            stepThrough(vehicles,sensors,leds,passToLeadingPi,passToTrailingPi)
            leds.updateStateFromNew()
            
            timeAtLEDUpdate=time.time()
            LEDsModel=updateLEDsModel(LEDsModel,timeAtLEDUpdate-firebaseSys.timeBeforeLEDUpdate,leds)
            firebaseSys.timeBeforeLEDUpdate=timeAtLEDUpdate
            
            leds.turnOnLeds()
            
            # Push data to firebase if the minute changes
            now = datetime.datetime.now()
            if firebaseSys.sec==60:
                firebaseSys.sec=59
                
            if now.minute==firebaseSys.min+1 and (now.second==firebaseSys.sec or now.second==firebaseSys.sec+1):
                # resetdata
                firebaseSys.sec=now.second
                firebaseSys.min=now.minute
                
                #calculate avgspeed 
                avgSpeed=0
                maxSpeed=0
                for i in range(0,vehicles.numVehicles()):
                    print(vehicles.getVehicle(i).maxSpeed)
                    print(vehicles.getVehicle(i).sensorsPassed)
                    vehicles.getVehicle(i).avgSpeed=vehicles.getVehicle(i).maxSpeed / vehicles.getVehicle(i).sensorsPassed#* # avg speed of that vehicle
                    maxSpeed=maxSpeed+vehicles.getVehicle(i).avgSpeed #add average speed of all vehicles
                avgSpeed=maxSpeed /dataModel["numOfNewCars"] #calculate avg speed of all new vehicles
                #reset vehicles data for next minute
                for i in range(0,vehicles.numVehicles()):
                    vehicles.getVehicle(i).avgSpeed=0
                    vehicles.getVehicle(i).maxSpeed=0
                    vehicles.getVehicle(i).sensorsPassed=0
                
                #append avgspeed 
                dataModel["avgSpeed"]=avgSpeed
                dataModel["LEDsTurnedOn"]=LEDsModel

                firebase.Sys.pushData(dataModel)

                #reset data
                dataModel=dataModelInit
                LEDsModel=genLEDsFirebaseModel(LEDsNum)
                dataModel["LEDsTurnedOn"]=LEDsModel
        
    except KeyboardInterrupt:
            run = False
    finally:
        GPIO.cleanup();
        
if __name__ == "__main__": 
    main()
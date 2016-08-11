import time
import datetime
import pandas as pd
from urllib2 import Request, urlopen, URLError
import csv
import json
import requests

starttime = datetime.datetime.now().strftime('%m_%d_%Y_%H_%M_%S')
lengthofreadings = 600 #seconds
frequency = 5  #seconds

print "Starting trending at "+str(starttime)+" for "+str(lengthofreadings)+" seconds at "+str(frequency)+" second intervals" #logs to console

filename = starttime+"datalogger_test.csv"

#1st and 5th are at the top
#2nd and 3rd and 4th go down in order
#6th is at the bottom
#deviceID1 = '54ff72066678574948420567' #Device 49
#device name = "Photon3" #device name, human readable`

#etietelbaum@princeton.edu token
access_token = 'd3fac0f7bb2e16d79fb51e94d54d4d25f9bcf69d'

#ene202.s2016@gmail.com token 
#access_token = '4b5667d370656c334b4e2f5754c4ceea61bf70b6' 


#Particle devices url
particle_url = 'https://api.particle.io/v1/devices?access_token=' + access_token

#sends GET request to our particle api 
req = requests.get(particle_url)

#turns url into json
req_json = req.json()

#Array to store the variable names
nameIndex = []

#Array to store the data from the variables
dataIndex = []

#Array to store the data from the variables
onDeviceArray = []

#List to store names of devices are on
deviceName = []

#Checks to see if there are any devices connected
deviceConnected = False

#This stores the devices that are available to read from
sensorArray = []
index = 1       # Index counter for sensor array

print 'Multiple DHT22 Data Read v1\n\n'

print "Would you like to read all devices or just one? ('all'/'one')"
userResponse = raw_input()
print "\n"

if userResponse.lower() == 'one':
    print "These devices are online. Choose one." 
    for i in req_json:
            if i['connected'] == 1: #1 = true; AKA if device is connected...
                deviceConnected = True
                sensorArray.append(i['name'])
                print str(index) + ". " + i['name']
                index += 1

    print "\n"
    print "Enter the NUMBER of the device you wish to get data from on the list."
    deviceID = int(raw_input())
    print "\n"
    if int(deviceID) <= int(index - 1): #Checks to see if number is within range
            newIndex = deviceID - 1
            with open(filename, "a") as file:
                writer = csv.writer(file, delimiter = ",")
                end = time.time() + lengthofreadings
                nameIndex.append('Timestamp')
                #Start of finding the variable names and posting it to a CSV
                for i in req_json:
                    if i['name'] == sensorArray[newIndex] and i['connected'] == 1: # Finds the sensor that was specified and extracts its data
                        deviceConnected = True
                        print "Device " + str(i['name']) + " is online"
                        #Access online devices API
                        onDevice = requests.get('https://api.particle.io/v1/devices/' + i['id'] + '?access_token=' + access_token)
                        onDevice_json = onDevice.json()
                        deviceName.append(str(i['name']))
            
                    #Access the variables (if there are any) that the sensor is reading
                        if 'variables' in onDevice_json:
                            for var in onDevice_json['variables']:
                                data = requests.get('https://api.particle.io/v1/devices/' + i['id'] + '/' + var + '?access_token=' + access_token)
                                onDeviceArray.append(str('https://api.particle.io/v1/devices/' + i['id'] + '/' + var + '?access_token=' + access_token))
                                data_json = data.json()
                                nameIndex.append(var+'_'+i['name']) #add var name to index along with the device name
                                if 'result' in data_json:
                                    print "Variable: " + str(var) + ": " + str(data_json['result'])
                        else:
                            print "There were no variables detected."                
                        print "\n" 
                if deviceConnected == False:
                    print "There are no devices connected. Ending program."
                writer.writerow(nameIndex)


                #This is where the data is extracted and sent to a CSV file
                #The while loop will run until the current time + length of storage
                while True:
                    if time.time() > end: #or deviceConnected == False:
                        break
                    else:
                        for i in req_json:
                            if i['name'] == sensorArray[newIndex] and i['connected'] == 1 and i['name'] not in deviceName: 
                                deviceConnected = True
                                print "Device " + str(i['name']) + " is online"
                                #Access online devices API
                                onDevice = requests.get('https://api.particle.io/v1/devices/' + i['id'] + '?access_token=' + access_token)
                                onDevice_json = onDevice.json()
                                deviceName.append(str(i['name']))
            
                            #Access the variables (if there are any) that the sensor is reading
                                if 'variables' in onDevice_json:
                                    for var in onDevice_json['variables']:
                                        data = requests.get('https://api.particle.io/v1/devices/' + i['id'] + '/' + var + '?access_token=' + access_token)
                                        onDeviceArray.append(str('https://api.particle.io/v1/devices/' + i['id'] + '/' + var + '?access_token=' + access_token))
                                        data_json = data.json()
                                        nameIndex.append(var+'_'+i['name']) #add var name to index along with the device name
                                        if 'result' in data_json:
                                            print "Variable: " + str(var) + ": " + str(data_json['result'])

                        for url in onDeviceArray:
                            data = requests.get(url)
                            data_json = data.json()
                            if 'result' in data_json:
                                print str(data_json['name']) + ": " + str(data_json['result']) 
                                print str(data_json['coreInfo']['last_heard'])
                                dataIndex.append(str(data_json['result']))
                            else:
                                #If there are no variables detected after the request, that means that the device is no longer online
                                print "ERROR: Device " + str(i['name']) + " is offline."
                                dataIndex.append("OFFLINE")

                        #Prints out to CSV
                        timestamp = datetime.datetime.now().strftime('%m/%d/%Y %H:%M:%S')
                        dataIndex = [str(timestamp)] + dataIndex
                        print dataIndex           
                        writer.writerow(dataIndex) #Print all the data
                        dataIndex = []
                        time.sleep(frequency)
              
        
    else:
        print "That number is not associated with a device. Ending program."

else:
    with open(filename, "a") as file:
            writer = csv.writer(file, delimiter = ",")
            end = time.time() + lengthofreadings
            nameIndex.append('Timestamp')
            #Start of finding the variable names and posting it to a CSV
            for i in req_json:
                if i['connected'] == 1: # 1 = true; AKA if device is connected
                    deviceConnected = True
                    print "Device " + str(i['name']) + " is online"
                    #Access online devices API
                    onDevice = requests.get('https://api.particle.io/v1/devices/' + i['id'] + '?access_token=' + access_token)
                    onDevice_json = onDevice.json()
                    deviceName.append(str(i['name']))
            
                #Access the variables (if there are any) that the sensor is reading
                    if 'variables' in onDevice_json:
                        for var in onDevice_json['variables']:
                            data = requests.get('https://api.particle.io/v1/devices/' + i['id'] + '/' + var + '?access_token=' + access_token)
                            onDeviceArray.append(str('https://api.particle.io/v1/devices/' + i['id'] + '/' + var + '?access_token=' + access_token))
                            data_json = data.json()
                            nameIndex.append(var+'_'+i['name']) #add var name to index along with the device name
                            if 'result' in data_json:
                                print "Variable: " + str(var) + ": " + str(data_json['result'])
                    else:
                        print "There were no variables detected."                
                    print "\n" 
            if deviceConnected == False:
                print "There are no devices connected. Ending program."
            writer.writerow(nameIndex)


            #This is where the data is extracted and sent to a CSV file
            #The while loop will run until the current time + length of storage
            while True:
                if time.time() > end: #or deviceConnected == False:
                    break
                else:
                    for i in req_json:
                        if i['connected'] == 1 and i['name'] not in deviceName: 
                            deviceConnected = True
                            print "Device " + str(i['name']) + " is online"
                            #Access online devices API
                            onDevice = requests.get('https://api.particle.io/v1/devices/' + i['id'] + '?access_token=' + access_token)
                            onDevice_json = onDevice.json()
                            deviceName.append(str(i['name']))
            
                        #Access the variables (if there are any) that the sensor is reading
                            if 'variables' in onDevice_json:
                                for var in onDevice_json['variables']:
                                    data = requests.get('https://api.particle.io/v1/devices/' + i['id'] + '/' + var + '?access_token=' + access_token)
                                    onDeviceArray.append(str('https://api.particle.io/v1/devices/' + i['id'] + '/' + var + '?access_token=' + access_token))
                                    data_json = data.json()
                                    nameIndex.append(var+'_'+i['name']) #add var name to index along with the device name
                                    if 'result' in data_json:
                                        print "Variable: " + str(var) + ": " + str(data_json['result'])

                    for url in onDeviceArray:
                        data = requests.get(url)
                        data_json = data.json()
                        if 'result' in data_json:
                            print str(data_json['name']) + ": " + str(data_json['result']) 
                            dataIndex.append(str(data_json['result']))
                        else:
                            #If there are no variables detected after the request, that means that the device is no longer online
                            print "ERROR: Device " + str(i['name']) + " is offline."
                            dataIndex.append("OFFLINE")

                    #Prints out to CSV
                    timestamp = datetime.datetime.now().strftime('%m/%d/%Y %H:%M:%S')
                    dataIndex = [str(timestamp)] + dataIndex
                    print dataIndex           
                    writer.writerow(dataIndex) #Print all the data
                    dataIndex = []
                    time.sleep(frequency)

































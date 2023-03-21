#!/usr/bin/python
import sys

sys.path.insert(1, "/home/pi/Raspi_MotorHAT")

from Raspi_MotorHAT import Raspi_MotorHAT, Raspi_DCMotor, Raspi_StepperMotor
import RPi.GPIO as GPIO
from time import sleep
import cv2
import numpy as np
import time
import atexit

motors = Raspi_MotorHAT(addr = 0x6F)
motor1 = motors.getMotor(1)
motor2 = motors.getMotor(2)
motor3 = motors.getMotor(3)
motor4 = motors.getMotor(4)


def powerOff():
    motors.getMotor(1).run(Raspi_MotorHAT.RELEASE)
    motors.getMotor(2).run(Raspi_MotorHAT.RELEASE)
    motors.getMotor(3).run(Raspi_MotorHAT.RELEASE)
    motors.getMotor(4).run(Raspi_MotorHAT.RELEASE)
    
atexit.register(powerOff)

distance_array = []

cap = cv2.VideoCapture(0)
doorDetected = False

colorval = np.uint8([[[203, 192, 255]]]) #pink color

colorval_HSV = cv2.cvtColor(colorval, cv2.COLOR_BGR2HSV)

lowerBound = colorval_HSV[0][0][0] - 20, 100, 100
upperBound = colorval_HSV[0][0][0] + 20, 255, 255

lowerBound = np.array(lowerBound)
upperBound = np.array(upperBound)

count = 0

while True:
    _, door_finder = cap.read()
    
    door_finder = cv2.flip(door_finder, 0)
    door_finder = cv2.flip(door_finder, 1)
    
    height, width, _ = door_finder.shape
    
    
    motor1.setSpeed(60)
    motor1.run(Raspi_MotorHAT.FORWARD)
    
    motor2.setSpeed(60)
    motor2.run(Raspi_MotorHAT.FORWARD)
    
    motor3.setSpeed(60)
    motor3.run(Raspi_MotorHAT.BACKWARD)
    
    motor4.setSpeed(60)
    motor4.run(Raspi_MotorHAT.BACKWARD)
    
    HSV_value = cv2.cvtColor(door_finder, cv2.COLOR_BGR2HSV)
    
    #separation_vals = cv2.inRange(HSV_value, (0, 50, 50), (10, 255, 255))
    
    separation_vals = cv2.inRange(HSV_value, lowerBound, upperBound)
    
    contours,_ = cv2.findContours(separation_vals, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if (len(contours) >= 1):
        for k in contours:
            area_contour = cv2.contourArea(k)
            cv2.drawContours(door_finder, [k], -1, (0, 255, 0), 3)
            x, y, w, h = cv2.boundingRect(k)
            door_finder = cv2.rectangle(door_finder, (x,y), (x+w, y+h), (0,0,0), 2)
        
            distance = (3.60 * 69.85 * height) / (h * 45.72)
            
            distance_array.append(distance)
    
        final_distance = (sum(distance_array) / len(distance_array))

        print("Door detected, distance (mm): " + str(final_distance))
        doorDetected = True
    else:
        print("No possible door detected.")
        doorDetected = False
        
    if (doorDetected == True) and (final_distance > 1400): 
        powerOff()
        count+=1
        if (count >= 60):
            powerOff()
            break
        
        

    cv2.imshow('shapes', door_finder)
    
    if cv2.waitKey(1) == ord('c'):
            powerOff()
            break

cap.release()
cv2.destroyAllWindows()
sys.exit("Program terminate.")

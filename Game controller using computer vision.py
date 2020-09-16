import cv2
import imutils
import numpy as np
from collections import deque
import time
import pyautogui
from threading import Thread
class WebcamVideoStream:
    def __init__(self):
        self.stream = cv2.VideoCapture(0)
        self.ret, self.frame = self.stream.read()
        self.stopped = False
    def start(self):
        Thread(target = self.update, args=()).start()
        return self
    def update(self):
        while True:
            if self.stopped:
                return
            self.ret, self.frame = self.stream.read()
    def read(self):
        return self.frame
    def stop(self):
        self.stopped = True
#Define HSV colour range for green colour objects
greenLower = (29, 86, 6)
greenUpper = (64, 255, 255)
#greenLower = (230, 230, 230)
#greenUpper = (255, 255, 255)

#Used in deque structure to store no. of given buffer points
buffer = 20
flag = 0

#Points deque structure storing 'buffer' no. of object coordinates
pts = deque(maxlen = buffer)
#Counts the minimum no. of frames to be detected where direction change occurs
counter = 0
(dx, dy) = (0, 0)
#Variable to store direction string
direction = ''
#Last pressed variable to detect which key was pressed by pyautogui
last_pressed = ''

time.sleep(5)
width,height = pyautogui.size()

vs = WebcamVideoStream().start()
pyautogui.click(int(width/2), int(height/2))
while True:
    frame = vs.read()
    frame = cv2.flip(frame,1)
    frame = imutils.resize(frame, width = 800)
    blurred_frame = cv2.GaussianBlur(frame, (5,5), 0)
    hsv_converted_frame = cv2.cvtColor(blurred_frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv_converted_frame, greenLower, greenUpper)
    mask = cv2.erode(mask, None, iterations = 2)
    mask = cv2.dilate(mask, None, iterations = 2)
    contours,_ = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    center = None
    if(len(contours) > 0):
        c = max(contours, key = cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        M = cv2.moments(c)
        center = (int(M['m10'] / M['m00']), int(M['m01'] / M['m00']))
        if radius > 10:
            cv2.circle(frame, (int(x), int(y)), int(radius), (0,255,255), 2)
            cv2.circle(frame, center, 5, (0,255,255), -1)
            pts.appendleft(center)
    for i in np.arange(1, len(pts)):
        if(pts[i-1] == None or pts[i] == None):
            continue
        if counter >= 10 and i == 1 and pts[-10] is not None:
            dx = pts[-10][0] - pts[i][0]
            dy = pts[-10][1] - pts[i][1]
            (dirX, dirY) = ('', '')
            if np.abs(dx) > 70:
                dirX = 'West' if dx>0 else 'East'

            if np.abs(dy) > 70:
                dirY = 'North' if dy>0 else 'South'
            direction = dirX if dirX != '' else dirY
            cv2.putText(frame, direction, (20,40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 3)
    #If deteced direction is East, press right button
    if direction == 'East':
        if last_pressed != 'right':
            pyautogui.press('right')
            last_pressed = 'right'
            print("Right Pressed")
            #pyautogui.PAUSE = 2
    #If deteced direction is West, press Left button
    elif direction == 'West':
        if last_pressed != 'left':
            pyautogui.press('left')
            last_pressed = 'left'
            print("Left Pressed")
            #pyautogui.PAUSE = 2
    #if detected direction is North, press Up key
    elif direction == 'North':
        if last_pressed != 'up':
            last_pressed = 'up'
            pyautogui.press('up')
            print("Up Pressed")
            #pyautogui.PAUSE = 2
    #If detected direction is South, press down key
    elif direction == 'South':
        if last_pressed != 'down':
            pyautogui.press('down')
            last_pressed = 'down'
            print("Down Pressed")
    cv2.imshow('Game Control Window', frame)
    counter += 1
    if (flag == 0):
        pyautogui.click(int(width/2), int(height/2))
        flag = 1

    #If q is pressed, close the window
    if(cv2.waitKey(1) & 0xFF == ord('q')):
        break
vs.stop()
cv2.destroyAllWindows()
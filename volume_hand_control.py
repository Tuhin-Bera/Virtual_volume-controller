import cv2
import mediapipe as mp
import time
import numpy as np
import hand_tracking_module as htm
import math

from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume


###############################
w_cam, h_cam = 640, 480            # Camera resolution width and height
###############################

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open camera.")
    exit()

time.sleep(2)  # Give the camera time to initialize

cap.set(3, w_cam)   ## Set camera width (property 3)
cap.set(4, h_cam)   ## Set camera height (property 4)


p_time = 0
c_time = 0

detector  = htm.hand_detector(detection_con=0.7)


#################### volume controler --> github

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = interface.QueryInterface(IAudioEndpointVolume)
# volume.GetMute()
# volume.GetMasterVolumeLevel()
vol_range = volume.GetVolumeRange()                     ## we can get the range of the volume by printing the variable
# volume.SetMasterVolumeLevel(-20.0, None)

#######################################

min_vol = vol_range[0]
max_vol = vol_range[1]
vol = 0
vol_bar = 400                 ## here "400" means when the volume is "zero"
vol_perc = 0


    
    
while  True:
    success, img = cap.read()
    
    if not success or img is None:
        print("Error: Failed to capture image")  
        break  # Exit if no frame is captured
    
    img = detector.find_hands(img)
    lm_list, b_box = detector.find_position(img, draw = False)
    
    if len(lm_list) != 0:
        # print(lm_list[4], lm_list[8])
        
        x1, y1 = lm_list[4][1], lm_list[4][2]
        x2, y2 = lm_list[8][1], lm_list[8][2]
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
        
        ## draw hand gestures
        cv2.circle(img, (x1, y1), 7, (255, 0, 0), cv2.FILLED)
        cv2.circle(img, (x2, y2), 7, (255, 0, 0), cv2.FILLED)
        cv2.line(img, (x1, y1), (x2, y2), (255, 0, 0), 3)
        cv2.circle(img, (cx, cy), 5, (255, 0, 0), cv2.FILLED)
        
        length = math.hypot(x2 - x1, y2 - y1)
        # print(length)
        
        ## hand range = (50 --> 250)
        ## volume range = (-63.5 --> 0)
        
        vol = np.interp(length, [50, 250], [min_vol, max_vol])     ## converting the hand length into volume length(adjustment)
        vol_bar = np.interp(length, [50, 250], [400, 150])         ## this is for volume bar 
        vol_perc = np.interp(length, [50, 250], [0, 100])          ## this is for volume percentage text
        print(int(length), vol)
        volume.SetMasterVolumeLevel(vol, None)
        
        if length < 50:
            cv2.circle(img, (cx, cy), 5, (0, 255, 0), cv2.FILLED)     ## creating a point for the min volume 
        
    ## creating volume bar in the img
    cv2.rectangle(img, (50, 150), (85, 400), (0, 255, 0), 3)
    cv2.rectangle(img, (50, int(vol_bar)), (85, 400), (0, 255, 0), cv2.FILLED)
    ## putting a percentage text beside the vol_bar
    cv2.putText(img,f'{int(vol_perc)}%', (40, 450), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
    
    
    c_time  = time.time()
    fps = 1/(c_time - p_time)
    p_time = c_time
    
    cv2.putText(img,f'FPS: {str(int(fps))}', (40, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
    
    cv2.imshow("Image", img)   ## display the proccessed fame

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break  # Press 'q' to exit
    
    
    

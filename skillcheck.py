import cv2
import numpy as np
import time
import win32con, win32api, win32gui, win32ui
import simpy
from datetime import datetime, timedelta
from keyboard import is_pressed, press_and_release
from mss import mss
import cmath
import math


red_merda = 0
top_left = (0,0)

def space():
	win32api.keybd_event(0x20, 0, 0, 0)

def screen_better():
	hwin = win32gui.GetDesktopWindow()
	width = 30 #win32api.GetSystemMetrics(win32con.SM_CXVIRTUALSCREEN)
	height = 28 #win32api.GetSystemMetrics(win32con.SM_CYVIRTUALSCREEN)
	left = 804 #win32api.GetSystemMetrics(win32con.SM_XVIRTUALSCREEN)
	top = 394 #win32api.GetSystemMetrics(win32con.SM_YVIRTUALSCREEN)
	hwindc = win32gui.GetWindowDC(hwin)
	srcdc = win32ui.CreateDCFromHandle(hwindc)
	memdc = srcdc.CreateCompatibleDC()
	bmp = win32ui.CreateBitmap()
	bmp.CreateCompatibleBitmap(srcdc, width, height)
	memdc.SelectObject(bmp)
	memdc.BitBlt((0, 0), (width, height), srcdc, (left, top), win32con.SRCCOPY)
	bmp.SaveBitmapFile(memdc, 'screenshot.bmp')
	return cv2.imread("./screenshot.bmp")

def crop(img):
	return img[200: 780, 300: 1620]
	
def getCircleCrop(img, p1, p2):
	crop_img=img[p1[1]-70: p2[1]+70, p1[0]-40:p2[0]+40]
	return crop_img
	
def returnImage(frame_np):	 #funzione che mi ritorna l'immagine filtrata e tagliata
	hsv=cv2.cvtColor(np.array(frame_np),cv2.COLOR_BGR2HSV)	  #converto il frame sotto forma di np.array in HSV
	lower_red=np.array([0,140,180])		 #setto il valore rosso piu' scuro
	upper_red=np.array([10,255,255])		 #setto il valore rosso piu' chiaro
	lower_red2=np.array([175, 140, 180])		 #setto il valore rosso strano piu' scuro
	upper_red2=np.array([179, 255, 255])		 #setto il valore rosso strano piu' chiaro
	lower_white=np.array([0,0,200])		   #setto il valore bianco piu' scuro
	upper_white=np.array([255,30,255])		#setto il valore bianco piu' chiaro
	mask=cv2.inRange(hsv, lower_red, upper_red)	   #creo la maschera rossa dell'immagine hsv
	mask2 =cv2.inRange(hsv, lower_white, upper_white)  #creo la maschera bianca dell'immagine hsv
	mask3=cv2.inRange(hsv, lower_red2, upper_red2)	#creo la maschera rossa strana dell'immagine hsv
	img=cv2.addWeighted(mask, 1.0, mask3, 1.0, 0.0,0) #unisco le due maschere
	img=cv2.addWeighted(img, 1.0, mask2, 1.0, 0.0, 0)
	
	return img				  #ritorno l'immagine (non l'avrei mai detto)

def returnRedImage(frame_np):	 #funzione che mi ritorna l'immagine filtrata e tagliata
	hsv=cv2.cvtColor(np.array(frame_np),cv2.COLOR_BGR2HSV)	  #converto il frame sotto forma di np.array in HSV
	lower_red=np.array([0,140,180])		 #setto il valore rosso piu' scuro
	upper_red=np.array([10,255,255])		 #setto il valore rosso piu' chiaro
	lower_red2=np.array([175, 140, 180])		 #setto il valore rosso strano piu' scuro
	upper_red2=np.array([179, 255, 255])		 #setto il valore rosso strano piu' chiaro
	mask=cv2.inRange(hsv, lower_red, upper_red)	   #creo la maschera rossa dell'immagine hsv
	mask2=cv2.inRange(hsv, lower_red2, upper_red2)	#creo la maschera rossa strana dell'immagine hsv
	img=cv2.addWeighted(mask, 1.0, mask2, 1.0, 0.0,0) #unisco le due maschere
	
	return img	
	
def returnWhiteImage(frame_np):	 #funzione che mi ritorna l'immagine filtrata e tagliata
	hsv=cv2.cvtColor(np.array(frame_np),cv2.COLOR_BGR2HSV)	  #converto il frame sotto forma di np.array in HSV
	lower_white=np.array([0,0,200])		   #setto il valore bianco piu' scuro
	upper_white=np.array([255,30,255])		#setto il valore bianco piu' chiaro
	mask =cv2.inRange(hsv, lower_white, upper_white)  #creo la maschera bianca dell'immagine hsv
	
	return mask   


def match(im, t):
	global top_left
	res = cv2.matchTemplate(t, im, cv2.TM_CCOEFF_NORMED)
	min_val, max_val, min_loc, max_loc=cv2.minMaxLoc(res)
	top_left = max_loc
	if (max_val>=0.90):
		#print ("beccato!")
		#print(max_val)
		return True
	#print ("grullo...")
	#print(max_val)
	return False
	
def match_debug(im, t):
	global top_left
	res = cv2.matchTemplate(t, im, cv2.TM_CCOEFF_NORMED)
	min_val, max_val, min_loc, max_loc=cv2.minMaxLoc(res)
	top_left = max_loc
	if (max_val>=0.80):
		print ("beccato!")
		print(max_val)
		return True
	print ("grullo...")
	print(max_val)
	return False

def getContours(img):
	medianFiltered=cv2.medianBlur(img,5)
	contours, _ = cv2.findContours(medianFiltered, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
	contour_list = []
	for contour in contours:
		area = cv2.contourArea(contour)
		if area>5 and area <150:
			contour_list.append(contour)
	return contour_list

# Written by Antonio Napolitano <nap@napaalm.xyz>
def find_angle(center: complex, needle: complex, target: complex) -> float:
	"""Calculates the angle between the needle and the target in radians, given the center of the skillcheck.

	Parameters
	----------
	center : complex
	The position of the skillcheck's center.
	needle : complex
	The position of the needle.
	target : complex
	The position of the target.

	Returns
	-------
	float
	The angle between the needle and the target in radians.

	Examples
	--------
	>>> center = complex(200, 300)
	>>> needle = complex(300, 300)
	>>> target = complex(200, 200)
	>>> find_angle(center, needle, target)
	1.5707963267948966
	"""

	angle = cmath.phase((needle - center) / (target - center))

	if angle < 0:
		return 2 * math.pi + angle
	else:
		return angle	

#active = True

def listener():
	global active
	while True:
		if is_pressed("z"):
			active = not active
			time.sleep(0.5)
		time.sleep(0.01)
	
middle = (100,100)
omega = 5.453669148864465
monitor = {"top": 440, "left": 860, "width": 200, "height": 200}
monitor2 = {"top": 840, "left": 831, "width": 43, "height": 14}
monitor3 = {"top": 824, "left": 746, "width": 53, "height": 55}
monitor4 = {"top": 823, "left": 743, "width": 62, "height": 59}
heal = cv2.cvtColor(cv2.imread("./heal.png"), cv2.COLOR_BGR2GRAY)
medikit = cv2.cvtColor(cv2.imread("./medikit.png"), cv2.COLOR_BGR2GRAY)
ranger = cv2.cvtColor(cv2.imread("./ranger.png"), cv2.COLOR_BGR2GRAY)
maschera = cv2.bitwise_not(cv2.imread("./mask2.png", 0))
space = cv2.cvtColor(cv2.imread("./space.png"), cv2.COLOR_BGR2GRAY)
#lower_grey = np.array([0,0,100])
#upper_grey = np.array([255,30,200])
#start = time.time()
#count = 0
#flag = False
#408
#while(1):
	#count += 1
#while True:
	#if is_pressed("k"):
		#break
#cv2.imshow("sus", maschera)
#cv2.waitKey(0)
#match(cv2.cvtColor(np.array(mss().grab(monitor)), cv2.COLOR_BGR2GRAY), space)
#screen = cv2.bitwise_and(np.array(mss().grab(monitor)), np.array(mss().grab(monitor)), mask=maschera)
#screen = returnImage(screen)
#cts = getContours(screen)
#coeffs = []
#for c in cts:
	#M = cv2.moments(c)
	#cX = int(M["m10"] / M["m00"])
	#cY = int(M["m01"] / M["m00"])
	#coeffs.append(((middle[1]-cY)/(middle[0]-cX))*(-1))
#angolo = (atan(coeffs[0]) + atan(coeffs[1]))*180/pi
#wait = angolo/omega

#print(angolo)
#cv2.imshow("sus", screen)
#cv2.waitKey(0)

is_heal = False
first = True
predicted_times = []
next_frame = time.time()
#thr1 = Thread(target=listener)
#thr1.start()

for i in range(10):
	press_and_release("space")

while True:
	try:
		now = time.time()
		while now < next_frame:
			time.sleep(0.001)
			now = time.time()
		next_frame = now + 1/60
		screen = np.array(mss().grab(monitor))
		if match(cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY), space):
			if first:
				hnd = cv2.cvtColor(np.array(mss().grab(monitor2)), cv2.COLOR_BGR2GRAY)
				med = cv2.cvtColor(np.array(mss().grab(monitor3)), cv2.COLOR_BGR2GRAY)
				med_rng = cv2.cvtColor(np.array(mss().grab(monitor4)), cv2.COLOR_BGR2GRAY)
				if match(hnd, heal) or match(med, medikit) or match(med_rng, ranger):
					is_heal = True
					print("Healing skillcheck detected")
				else:
					print("Generator skillcheck detected")
					pass
			first = False
			if len(predicted_times) > 0 and now >= sum(predicted_times)/len(predicted_times):
				press_and_release("space")
				continue
			#start = datetime.now()
			#for i in range(5):
			ctsRed = []
			ctsWhite = []
			while (len(ctsRed) + len(ctsWhite)) != 2:
				now = time.time()
				screen = np.array(mss().grab(monitor))
				screen = cv2.bitwise_and(screen, screen, mask=maschera)
				processedRed = returnRedImage(screen)
				processedWhite = returnWhiteImage(screen)
				#cv2.imshow("sus", processed)
				#cv2.waitKey(1)
				ctsRed = getContours(processedRed)
				ctsWhite = getContours(processedWhite)
			M = cv2.moments(ctsRed[0])
			cXr = int(M["m10"] / M["m00"])
			cYr = int(M["m01"] / M["m00"])
			M = cv2.moments(ctsWhite[0])
			cXw = int(M["m10"] / M["m00"])
			cYw = int(M["m01"] / M["m00"])
			#print("cXR: " + str(cXr))
			#print("cYR: " + str(cYr))
			#print("cXW: " + str(cXw))
			#print("cYW: " + str(cYw))
			angolo = find_angle(complex(middle[0],middle[1]),complex(cXr, 200-cYr),complex(cXw, 200-cYw))
			#print("Angolo: " + str(angolo*180/math.pi))
			predicted_times.append((now + angolo/omega-1/60*5) + (0.032 if is_heal else 0.0))
			#predicted_times.append(datetime.now() - start + timedelta(seconds=wait))
			#somma = timedelta()
			#for i in range(len(predicted_times)):
				#somma += predicted_times[i]
			#media = somma/len(predicted_times)
			#time.sleep(media.total_seconds())
		else:
			predicted_times = []
			first = True
			is_heal = False
			time.sleep(0.01)
	except KeyboardInterrupt:
		exit(0)
	except Exception as e:
		print(str(e))
		continue

'''flag = False
while True:
	if is_pressed("z"):
		flag = not flag
		time.sleep(0.15)
	img = returnImage(mss().grab(monitor))
#detector = cv2.SimpleBlobDetector_create()
	img = cv2.erode(img, (21,21), iterations = 1)
	img = cv2.dilate(img, (21,21), iterations = 2)
	img = cv2.bitwise_not(img)
#img = cv2.resize(img, (760,696))
#_, img = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)
#58.5
#159.5
	cts = getContours(img)
	cv2.imshow("sus", img)
	cv2.waitKey(1)
	if len(cts) == 1 and flag:
		press_and_release("space")
		cv2.imwrite("suqi.png", img)
		print("Pressed space!")
		time.sleep(1)
	#elif len(cts) == 2:
		#print("Waiting to press space")
#print(cts)
#print(len(cts))
#for c in cts:
	#img2 = cv2.drawContours(np.array(mss().grab(monitor)), [c], 0, (0,255,0), 2)
	#print(cv2.contourArea(c))
#cv2.imshow("sus", img)
#cv2.waitKey(0)
#if len(cts) == 1:
	#flag = True
#if len(cts) == 0 and flag:
	#flag = False
	#press_and_release("space")
	#print("pressed space")

		#if cv2.contourArea(cts[0]) > 100:
			#press_and_release("space")
#print("pressed space" + "\t" + str(cv2.contourArea(cts[0])))
#print(str(time.time() - start) + "\t" + str(count))
	#print(str(mss().grab(monitor)))'''

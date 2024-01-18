from transform import four_point_transform
import cv2
import numpy as np
import math
import time
import RPi.GPIO as GPIO
#import RPistepper as stp
from time import sleep
from gpiozero import LED
from gpiozero import PWMLED
from gpiozero import Button
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

#motor_pins = [17, 27, 22, 23]
###
IN1 = 17
IN2 = 27
IN3 = 22
IN4 = 23

GPIO.setmode(GPIO.BCM)
GPIO.setup(IN1, GPIO.OUT)
GPIO.setup(IN2, GPIO.OUT)
GPIO.setup(IN3, GPIO.OUT)
GPIO.setup(IN4, GPIO.OUT)

sequence = [
    [1, 0, 0, 0],
    [1, 1, 0, 0],
    [0, 1, 0, 0],
    [0, 1, 1, 0],
    [0, 0, 1, 0],
    [0, 0, 1, 1],
    [0, 0, 0, 1],
    [1, 0, 0, 1]
]
###

button = Button(24)
led = PWMLED(25)

camera = cv2.VideoCapture(0)  # Puede ser necesario ajustar el número según la cámara utilizada
#camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)  # Ancho de la imagen (720p)
#camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)  # Altura de la imagen (720p)
#camera.set(cv2.CAP_PROP_FPS, 25)  # Configurar la velocidad de fotogramas a 25 fps

speed = 0.001 ###
i = 0

GPIO.setmode(GPIO.BCM)

"""
for pin in motor_pins:
    GPIO.setup(pin, GPIO.OUT)
"""

class vertex:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def write(self):
        return "v " + str(self.x) + " " + str(self.y) + " " + str(self.z)

class face:
    def __init__(self, v1, v2, v3):
        self.v1 = v1
        self.v2 = v2
        self.v3 = v3

    def write(self):
        return "f " + str(self.v1) + " " + str(self.v2) + " " + str(self.v3)

def getVertex(pCoord):
    H = pCoord.x
    t = pCoord.y
    d = pCoord.z
    x = d * math.cos(t)
    y = d * math.sin(t)
    z = H
    return vertex(int(x), int(y), int(z))

"""
def step(x, i):
    global motor_pins

    for _ in range(x):
        for halfstep in range(8):
            for pin in range(4):
                GPIO.output(motor_pins[pin], (halfstep >> pin) & 1)
            sleep(0.01)

    return i
"""

###
def set_step(w1, w2, w3, w4):
    GPIO.output(IN1, w1)
    GPIO.output(IN2, w2)
    GPIO.output(IN3, w3)
    GPIO.output(IN4, w4)

def move_steps(steps, direction):
	if direction == "backward":
		sequence.reverse()
	for _ in range(steps):
		for step in sequence:
			set_step(step[0], step[1], step[2], step[3])
			time.sleep(speed)
		if direction == "backward":
			sequence.reverse()
	
###
camera.release()

while (1):
	numItt = 100

	theta = 0
	thetaInc = 360.0/numItt

	motorPos = 0
	motorPosI = 400.0/numItt

	meshPoints = []
	lineLenth = []

	while (not button.is_pressed):
		sleep(0.1)

	led.pulse()

	while(theta < 360):
		ret,frame = camera.read()
		cv2.imwrite('lineDetection.jpg',frame)
		#camera.release()
		img = cv2.imread('lineDetection.jpg')

		"""
		tlp = (375.0,275.0)
		trp = (1090.0,420.0)
		brp = (1090.0,915.0)
		blp = (375.0,1060.0)
		"""
		tlp = (0.0, 0.0)
		trp = (1080.0, 0.0)
		brp = (1080.0, 720.0)
		blp = (0.0, 720.0)
		
		pts = np.array([tlp,trp,brp,blp])
		img = four_point_transform(img, pts)

		# Detección de líneas
		lowerb = np.array([50, 0, 0])
		upperb = np.array([255, 255, 255])
		red_line = cv2.inRange(img, lowerb, upperb)

		# Filtrado adicional
		blurred = cv2.GaussianBlur(red_line, (5, 5), 0)  # Suavizado de imagen
		kernel = np.ones((5, 5), np.uint8)
		morph = cv2.morphologyEx(blurred, cv2.MORPH_OPEN, kernel)  # Eliminación de ruido

		h,w = np.shape(red_line)
		backG = np.zeros((h, w))

		bottomR = 0

		r = 0
		for cIndex in np.argmax(red_line, axis=1):
			if red_line[r,cIndex] != 0:
				backG[r,cIndex] = 1
				bottomR = r
			r += 1

		tempV = []
		r = 0
		centerC = 420.0
		for cIndex in np.argmax(backG,axis=1):
			if(backG[r,cIndex] == 1):
				H = r-bottomR
				dist = cIndex - centerC
				coord = vertex(H,np.radians(theta),dist)
				tempV.append(coord)
			r += 1

		intv = 5
		intv = len(tempV)/intv

		if(len(tempV) != 0 and intv != 0):
			V = []
			V.append(tempV[0])

			for ind in range(1,len(tempV)-2):
				if(ind % intv == 0):
					V.append(tempV[ind])

			V.append(tempV[(len(tempV)-1)])
			meshPoints.append(V)
			print(str(len(V)))
			lineLenth.append(-1*len(V))
		
		theta += thetaInc
		#i = step(int(motorPosI), i)
		i = move_steps(int(motorPosI), "forward")###
		time.sleep(0.3)
    
	shortest = len(meshPoints[np.argmax(lineLenth)])
	print (shortest)
	for line in meshPoints:
		while(len(line) > shortest):
			line.pop(len(line)-2)

	points = []
	faces = []
	firstRow = []
	prevRow = []
	for index in range(1,len(meshPoints[0])+1):

		points.append(getVertex(meshPoints[0][index-1]))
		firstRow.append(index)

	prevRow = firstRow
	for col in range(0,len(meshPoints)):
		if col != 0:
			indexS = prevRow[-1]
			currentRow = []
			for point in range(0,len(meshPoints[col])-1):
				tl = indexS + point + 1
				bl = tl + 1
				tr = prevRow[point]
				br = prevRow[point + 1]

				f1 = face(tl,tr,bl)
				f2 = face(bl,tr,br)
				faces.append(f1)
				faces.append(f2)

				points.append(getVertex(meshPoints[col][point]))
				currentRow.append(tl)
				if(point == len(meshPoints[col])-2):
					points.append(getVertex(meshPoints[col][point+1]))
					currentRow.append(bl)

				if col == (len(meshPoints)-1):
					tr = tl
					br = bl
					tl = firstRow[point]
					bl = firstRow[point+1]
					f1 = face(tl,tr,bl)
					f2 = face(bl,tr,br)
					faces.append(f1)
					faces.append(f2)
			prevRow = currentRow

	filetowrite='3d.obj'
	with open(filetowrite, 'w') as file:
		for point in points:
			file.write(point.write() + "\n")
		for f in faces:
			file.write(f.write() + "\n")
		file.close()

	#email_user = 'cd.antonio.martinez.99@gmail.com'
	#email_password = '+Antonio10'
	#email_send = 'martinez.cortes.antonio.99@gmail.com'

	"""
	subject = '3D File :) !'

	msg = MIMEMultipart()
	msg['From'] = email_user
	msg['To'] = email_send
	msg['Subject'] = subject

	body = 'Hi there, here is your 3D mesh file!'
	msg.attach(MIMEText(body,'plain'))

	filename='3d.obj'
	attachment  =open(filename,'rb')

	part = MIMEBase('application','octet-stream')
	part.set_payload((attachment).read())
	encoders.encode_base64(part)
	part.add_header('Content-Disposition',"attachment; filename= "+filename)

	msg.attach(part)
	text = msg.as_string()
	server = smtplib.SMTP('smtp.gmail.com',465)
	server.starttls()
	server.login(email_user,email_password)

	server.sendmail(email_user,email_send,text)
	server.quit()
	"""

	led.off()

camera.release()
cv2.destroyAllWindows()
GPIO.cleanup()

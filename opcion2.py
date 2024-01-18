from transform import four_point_transform
import cv2
import numpy as np
import math
import time

j=1
#vertex class
class vertex:
	def __init__(self, x,y,z):
		self.x = x
		self.y = y
		self.z = z

	def write(self):
		return "v " + str(self.x) + " " + str(self.y) + " " +str(self.z)
		#return  str(self.x) + "," + str(self.y) + "," +str(self.z)
#face class
class face:
	def __init__(self, v1,v2,v3):
		self.v1 = v1
		self.v2 = v2
		self.v3 = v3

	def write(self):
		return "f " + str(self.v1) + " " + str(self.v2) + " " +str(self.v3)

# transforms cylindrical coordinates into rectangular coordinates
def getVertex(pCoord):
	#pass
	H = pCoord.x
	t = pCoord.y
	d = pCoord.z
	x = d*math.cos(t)
	y = d*math.sin(t)
	z = H
	return vertex(int(x),int(y),int(z))

###
# specify the directory containing images
image_folder = "/home/pi/AA-Scan/Photos/"

# create a list of image paths using list comprehension
images = [f"{image_folder}/Imagen{i}.jpg" for i in range(1, 201)]

# angular resolution
numItt = 200
theta = 0
thetaInc = 360.0 / numItt

# data
meshPoints = []
lineLength = []

# loop over image files in the specified directory
for img_path in images:
	img = cv2.imread(img_path)

	###
	#---------- Preview de la imagen----------------
	cv2.imshow("Imagen", img)
	cv2.waitKey(0)  # Espera hasta que se presione una tecla
	cv2.destroyAllWindows()

	#print(f"Ruta: {img_path}, Forma: {img.shape}, Tipo de Datos: {img.dtype}")
	###

	#get perspective
	tlp = (0.0, 0.0)
	trp = (1080.0, 0.0)
	brp = (1080.0, 720.0)
	blp = (0.0, 720.0)

	pts = np.array([tlp,trp,brp,blp])
	img = four_point_transform(img, pts)

	#---------- Preview the PERSPECTIVE picture ----------------
	cv2.imshow("perspective", img)
	cv2.waitKey(0)


	# filter
	lowerb = np.array([0, 0, 100])
	upperb = np.array([50, 50, 255])
	
	red_line = cv2.inRange(img, lowerb, upperb)
	##red_line = cv2.resize(red_line, (60,80), interpolation = cv2.INTER_AREA)

	#---------- Preview the filtered picture ----------------
	cv2.imshow("perspective", red_line)
	cv2.waitKey(0)
	print (red_line.shape)

	h,w = np.shape(red_line)
	backG = np.zeros((h, w))

	#---------- Preview fondo ----------------
	print (backG)

	bottomR = 0

	r = 0
	for cIndex in np.argmax(red_line, axis=1):
		if red_line[r,cIndex] != 0:
			backG[r,cIndex] = 1
			bottomR = r
		r += 1

	#---------- Preview the processed picture ----------------
	cv2.imshow("perspective", backG)
	cv2.waitKey(0)

	tempV = []
	r = 0
	centerC = 640.0 #center column
	for cIndex in np.argmax(backG,axis=1):
		if(backG[r,cIndex] == 1):
			#intvi = 0
			H = r-bottomR
			dist = cIndex - centerC
			coord = vertex(H,np.radians(theta),dist)
			tempV.append(coord)
		r += 1

	# vertical resolution
	intv = 10
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
		lineLength.append(-1*len(V))

	print(f"Procesadas {j}/{len(images)} imágenes.")
	j += 1
	theta += thetaInc

###
shortest = len(meshPoints[np.argmax(lineLength)])
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

#for i in range(min(50, len(points))):
    #print(f"Punto {i + 1}: {points[i].write()}")

#for i in range(min(50, len(faces))):
    #print(f"Cara {i + 1}: {faces[i].write()}")

#---------- debugging prints ----------------
# for point in points:
# 	print(point.write())
# for face in faces:
# 	print(face.write())

# writing the file
filetowrite='3d.obj'
with open(filetowrite, 'w') as file:
	for point in points:
		file.write(point.write() + "\n")
	print(f"Se han escrito {len(points)} puntos en el archivo obj.")
	for f in faces:
		file.write(f.write() + "\n")
	#
	print(f"Se han escrito {len(faces)} caras en el archivo obj.")
	file.close()
###

print("Archivo guardado!")

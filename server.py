import socket
import cv2
import numpy as np

serverAddress = "192.168.0.9"  # Put your Raspberry Pi IP here
serverPort = 8080
bufferSize = 12
photoStoragePath = '/home/pi/AA-Scan/Photos/Imagen'  # Change the path as needed

socketSendCommands = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socketSendCommands.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
socketSendCommands.bind((serverAddress, serverPort))
socketSendCommands.listen(1)
print("Server {ip} opened at port {port}\n".format(ip=serverAddress, port=serverPort))
(connection, address) = socketSendCommands.accept()
print("Connection established {addr}\n".format(addr=address))

try:
    camera = cv2.VideoCapture(0)  # Use 0 for the default camera
    i = 1
    while True:
        dataReceived = connection.recv(bufferSize).decode()
        if dataReceived != "":
            if dataReceived == "chez":
                ret,frame = camera.read()
                #cv2.imwrite('lineDetection.jpg',frame)
                path = photoStoragePath + str(i) + '.jpg'
                cv2.imwrite(path, frame)
                print("{count} photos taken!".format(count=i))
                i += 1
            if dataReceived == "quit":
                break
except Exception as e:
    print(f"Error: {e}")
finally:
    camera.release()

socketSendCommands.close()
print("DONE! The photos are stored at {path}!".format(path=photoStoragePath))

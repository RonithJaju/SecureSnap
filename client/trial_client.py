from PIL import Image
import numpy as np
from matplotlib.pyplot import imshow
import cv2
from math import log
import hmac
import socket
import struct
import pickle
import time
import os

#HMAC
def generate_hmac(key, data):
    h = hmac.new(key, data, "sha3_256")
    return h.digest()

# DIFFIEE HELLMANN
def generate_public_key(g, x, p):
    # return pow(g, x) % p
    return pow(g, x, p)

def generate_secret_key(y, x, p):
    # return pow(y, x) % p
    return pow(y, x, p)

# HENON
def dec(bitSequence):
    decimal = 0
    for bit in bitSequence:
        decimal = decimal * 2 + int(bit)
    return decimal

def getImageMatrix(imageName):
    im = Image.open(imageName) 
    pix = im.load()
    color = 1
    if type(pix[0, 0]) == int:
        color = 0
    image_size = im.size 
    image_matrix = []
    for width in range(int(image_size[0])):
        row = []
        for height in range(int(image_size[1])):
            row.append(pix[width, height])
        image_matrix.append(row)
    #print(image_size[0], image_size[1], len(image_matrix[0]), len(image_matrix))
    return image_matrix, image_size[0], image_size[1], color

def genHenonMap(dimensionX, dimensionY, key):
    x = key[0]
    y = key[1]
    sequenceSize = dimensionX * dimensionY * 8  # Total Number of bitSequence produced
    bitSequence = []  # Each bitSequence contains 8 bits
    byteArray = []  # Each byteArray contains m( i.e 512 in this case) bitSequence
    TImageMatrix = []  # Each TImageMatrix contains m*n byteArray( i.e 512 byteArray in this case)
    for i in range(sequenceSize):
        xN = y + 1 - 1.4 * x**2
        yN = 0.3 * x

        x = xN
        y = yN

        if xN <= 0.4:
            bit = 0
        else:
            bit = 1

        try:
            bitSequence.append(bit)
        except:
            bitSequence = [bit]

        if i % 8 == 7:
            decimal = dec(bitSequence)
            try:
                byteArray.append(decimal)
            except:
                byteArray = [decimal]
            bitSequence = []

        #byteArraySize = dimensionX * 8
        byteArraySize = dimensionY * 8
        if i % byteArraySize == byteArraySize - 1:
            try:
                TImageMatrix.append(byteArray)
            except:
                TImageMatrix = [byteArray]
            byteArray = []
    return TImageMatrix

def HenonEncryption(imageName, key):
    imageMatrix, dimensionX, dimensionY, color = getImageMatrix(imageName)
    transformationMatrix = genHenonMap(dimensionX, dimensionY, key)
    resultantMatrix = []
    for i in range(dimensionX):
        row = []
        for j in range(dimensionY):
            try:
                if color:
                    row.append(tuple([transformationMatrix[i][j] ^ x for x in imageMatrix[i][j]]))
                else:
                    row.append(transformationMatrix[i][j] ^ imageMatrix[i][j])
            except:
                if color:
                    row = [tuple([transformationMatrix[i][j] ^ x for x in imageMatrix[i][j]])]
                else:
                    row = [transformationMatrix[i][j] ^ x for x in imageMatrix[i][j]]
        try:    
            resultantMatrix.append(row)
        except:
            resultantMatrix = [row]
    if color:
        im = Image.new("RGB", (dimensionX, dimensionY))
    else: 
        im = Image.new("L", (dimensionX, dimensionY)) # L is for Black and white pixels

    pix = im.load()
    for x in range(dimensionX):
        for y in range(dimensionY):
            pix[x, y] = resultantMatrix[x][y]
    im.save(imageName.split('.')[0] + "_HenonEnc.png", "PNG")


def send_image():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('127.0.0.1', 12345))

    #DIFFIE HELLMANN for HENON MAP
    P1 = int(client_socket.recv(1024).decode())
    client_socket.sendall(b"Ack")  # Acknowledge

    G1 = int(client_socket.recv(1024).decode())
    client_socket.sendall(b"Ack")  # Acknowledge

    y2 = int(client_socket.recv(1024).decode())
    x2 = int(input("Enter the private key of User 2: "))
    y1 = generate_public_key(G1, x2, P1)

    client_socket.sendall(str(y1).encode())

    k1 = generate_secret_key(y2, x2, P1)
    print(f"\nSecret Key for User 2 is {k1}\n")

    scaled_secret_1 = k1 / P1

    #DIFFIE HELLMANN for HMAC
    P2 = int(client_socket.recv(1024).decode())
    client_socket.sendall(b"Ack")  # Acknowledge

    G2 = int(client_socket.recv(1024).decode())
    client_socket.sendall(b"Ack")  # Acknowledge

    y2 = int(client_socket.recv(1024).decode())
    x2 = int(input("Enter the private key of User 2: "))
    y1 = generate_public_key(G2, x2, P2)

    client_socket.sendall(str(y1).encode())

    k2 = generate_secret_key(y2, x2, P2)
    print(f"\nSecret Key for User 2 is {k2}\n")

    # HENON

    image_path=r"orig.png"
    key = (scaled_secret_1, scaled_secret_1)

    # Read and encrypt the image
    HenonEncryption(image_path, key)

    image_path_new = image_path.split('.')[0] + "_HenonEnc.png"  # Replace with the path to your image file
 
    image_enc = cv2.imread(image_path_new)

    # Serialize the frame
    data = pickle.dumps(image_enc)
    size = struct.pack(">L", len(data))

    # Send the frame size
    client_socket.sendall(size)

    # Send the serialized frame
    client_socket.sendall(data)
    
    #del the received enc image
    try:
        os.remove(image_path_new)
        print(f"File {image_path_new} deleted successfully.")
    except FileNotFoundError:
        print(f"File {image_path_new} not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

    #hmac
    time.sleep(0.1)
    key = str(k2)
    message_digest1 = hmac.digest(key.encode(), msg=data, digest="sha3_256")
    print("Message Digest 1 : {}".format(message_digest1.hex()))

    #Send the hmac
    client_socket.sendall(message_digest1)

    client_socket.close()

if __name__ == "__main__":
    send_image()
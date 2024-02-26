from PIL import Image
import numpy as np
#import os
from matplotlib.pyplot import imshow
import matplotlib.pyplot as plt
import cv2
#import random
from math import log
import socket
import struct
import pickle
import hmac

#HMAC
def generate_hmac(key, data):
    h = hmac.new(key, data, "sha3_256")
    return h.digest()

#DIFFIE HELLMANN
def prime_checker(p):
    # Checks if the number entered is a Prime Number or not
    if p < 1:
        return False
    elif p > 1:
        if p == 2:
            return True
        for i in range(2, p):
            if p % i == 0:
                return False
        return True


def primitive_check(g, p):
    seen = set()
    for i in range(1, p):
        result = pow(g, i, p)
        if result in seen:
            return -1  # Not a primitive root
        seen.add(result)
    return 1  # Primitive root

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
    return image_matrix, image_size[0], image_size[1], color

def genHenonMap(dimensionX, dimensionY, key):
    x = key[0]
    y = key[1]
    sequenceSize = dimensionX * dimensionY * 8  # Total Number of bitSequence produced
    bitSequence = []  # Each bitSequence contains 8 bits
    byteArray = []  # Each byteArray contains m (i.e 512 in this case) bitSequence
    TImageMatrix = []  # Each TImageMatrix contains m*n byteArray (i.e 512 byteArray in this case)
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

        byteArraySize = dimensionX * 8
        if i % byteArraySize == byteArraySize - 1:
            try:
                TImageMatrix.append(byteArray)
            except:
                TImageMatrix = [byteArray]
            byteArray = []
    return TImageMatrix

def HenonDecryption(imageMatrixEnc, key):
    dimensionX, dimensionY, color = len(imageMatrixEnc), len(imageMatrixEnc[0]), True
    transformationMatrix = genHenonMap(dimensionX, dimensionY, key)
    henonDecryptedImage = []
    for i in range(dimensionX):
        row = []
        for j in range(dimensionY):
            try:
                if color:
                    row.append(tuple([transformationMatrix[i][j] ^ x for x in imageMatrixEnc[i][j]]))
                else:
                    row.append(transformationMatrix[i][j] ^ imageMatrixEnc[i][j])
            except:
                if color:
                    row = [tuple([transformationMatrix[i][j] ^ x for x in imageMatrixEnc[i][j]])]
                else:
                    row = [transformationMatrix[i][j] ^ x for x in imageMatrixEnc[i][j]]
        try:
            henonDecryptedImage.append(row)
        except:
            henonDecryptedImage = [row]
    if color:
        im = Image.new("RGB", (dimensionX, dimensionY))
    else:
        im = Image.new("L", (dimensionX, dimensionY))  # L is for Black and white pixels

    pix = im.load()
    for x in range(dimensionX):
        for y in range(dimensionY):
            pix[x, y] = henonDecryptedImage[x][y]
    return im

def receive_image():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('127.0.0.1', 12345))
    server_socket.listen(1)

    print("Waiting for a connection...")
    client_socket, client_address = server_socket.accept()
    print("Connected to", client_address)

    # DIFFIE HELLMANN
    P = int(input("Enter P (prime): "))
    while not prime_checker(P):
        print("Number is not prime, please enter again!")
        P = int(input("Enter P (prime): "))

    G = int(input(f"Enter the primitive root of {P}: "))
    while not primitive_check(G, P):
        print(f"Number is not a primitive root of {P}, please try again!")
        G = int(input(f"Enter the primitive root of {P}: "))

    x1 = int(input("Enter the private key of User 1: "))
    y1 = generate_public_key(G, x1, P)

    client_socket.sendall(str(P).encode())
    client_socket.recv(1024)  # Acknowledge

    client_socket.sendall(str(G).encode())
    client_socket.recv(1024)  # Acknowledge

    client_socket.sendall(str(y1).encode())

    y2 = int(client_socket.recv(1024).decode())

    k1 = generate_secret_key(y2, x1, P)
    print(f"\nSecret Key for User 1 is {k1}\n")

    scaled_secret = k1 / P

    key = (scaled_secret, scaled_secret)

    data = b""
    payload_size = struct.calcsize(">L")

    while True:
        while len(data) < payload_size:
            data += client_socket.recv(4096)

        packed_msg_size = data[:payload_size]
        data = data[payload_size:]
        msg_size = struct.unpack(">L", packed_msg_size)[0]

        while len(data) < msg_size:
            data += client_socket.recv(4096)

        frame_data = data[:msg_size]
        data = data[msg_size:]

        frame = pickle.loads(frame_data)
        cv2.imshow("Received Henon-Encrypted Image", frame)

        # Decrypt the image
        decrypted_image = HenonDecryption(frame, key)

        # Display the decrypted image
        im_arr = np.array(decrypted_image)
        if im_arr.ndim == 3:  # Check if it's a color image
            im_arr = cv2.cvtColor(im_arr, cv2.COLOR_RGB2BGR)
        cv2.imshow("Henon-Decrypted Image", im_arr)
        cv2.waitKey(0)  # Wait until a key is pressed to close the window

        break

    server_socket.close()

if __name__ == "__main__":
    receive_image()


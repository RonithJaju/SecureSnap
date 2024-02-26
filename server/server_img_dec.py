from PIL import Image
import numpy as np
from matplotlib.pyplot import imshow
import matplotlib.pyplot as plt
import cv2
from math import log
import socket
import struct
import pickle
import hmac
import os
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
    if type(pix[0,0]) == int:
        color = 0
    image_size = im.size 
    image_matrix = []
    for width in range(int(image_size[0])):
        row = []
        for height in range(int(image_size[1])):
                row.append((pix[width,height]))
        image_matrix.append(row)
    return image_matrix, image_size[0], image_size[1], color

def genHenonMap(dimensionX, dimensionY, key):
    x = key[0]
    y = key[1]
    sequenceSize = dimensionX * dimensionY * 8  # Total Number of bitSequence produced
    bitSequence = []    # Each bitSequence contains 8 bits
    byteArray = []      # Each byteArray contains m( i.e 512 in this case) bitSequence
    TImageMatrix = []   # Each TImageMatrix contains m*n byteArray( i.e 512 byteArray in this case)
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

        byteArraySize = dimensionY * 8
        if i % byteArraySize == byteArraySize-1:
            try:
                TImageMatrix.append(byteArray)
            except:
                TImageMatrix = [byteArray]
            byteArray = []
    return TImageMatrix

def HenonDecryption(imageNameEnc, key):
    imageMatrix, dimensionX, dimensionY, color = getImageMatrix(imageNameEnc)
    transformationMatrix = genHenonMap(dimensionX, dimensionY, key)
    pil_im = Image.open(imageNameEnc, 'r')
    imshow(np.asarray(pil_im))
    henonDecryptedImage = []
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
                else :
                    row = [transformationMatrix[i][j] ^ x for x in imageMatrix[i][j]]
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
    im.save(imageNameEnc.split('_')[0] + "_HenonDec.png", "PNG")

def receive_image():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('127.0.0.1', 12345))
    server_socket.listen(1)

    print("Waiting for a connection...")
    client_socket, client_address = server_socket.accept()
    print("Connected to", client_address)

    # DIFFIE HELLMANN for HENON

    while True:
        P1 = int(input("Enter P (prime): "))
        if not prime_checker(P1):
            print("Number is not prime, please enter again!")
            continue
        break

    while True:
        G1 = int(input(f"Enter the primitive root of {P1}: "))
        #if not primitive_check(G, P, l):
        if not primitive_check(G1, P1):
            print(f"Number is not a primitive root of {P1}, please try again!")
            continue
        break

    x1 = int(input("Enter the private key of User 1: "))
    y1 = generate_public_key(G1, x1, P1)

    client_socket.sendall(str(P1).encode())
    client_socket.recv(1024)  # Acknowledge

    client_socket.sendall(str(G1).encode())
    client_socket.recv(1024)  # Acknowledge

    client_socket.sendall(str(y1).encode())

    y2 = int(client_socket.recv(1024).decode())

    k1 = generate_secret_key(y2, x1, P1)
    print(f"\nSecret Key for User 1 is {k1}\n")

    scaled_secret_1 = k1 / P1

    # DIFFIE HELLMANN for HMAC

    while True:
        P2 = int(input("Enter P (prime): "))
        if not prime_checker(P2):
            print("Number is not prime, please enter again!")
            continue
        break

    while True:
        G2 = int(input(f"Enter the primitive root of {P2}: "))
        #if not primitive_check(G, P, l):
        if not primitive_check(G2, P2):
            print(f"Number is not a primitive root of {P2}, please try again!")
            continue
        break

    x1 = int(input("Enter the private key of User 1: "))
    y1 = generate_public_key(G2, x1, P2)

    client_socket.sendall(str(P2).encode())
    client_socket.recv(1024)  # Acknowledge

    client_socket.sendall(str(G2).encode())
    client_socket.recv(1024)  # Acknowledge

    client_socket.sendall(str(y1).encode())

    y2 = int(client_socket.recv(1024).decode())

    k2 = generate_secret_key(y2, x1, P2)
    print(f"\nSecret Key for User 1 is {k2}\n")

    key = (scaled_secret_1, scaled_secret_1)

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
        
        #Client
        key_hmac = str(k2)
        hmac_hash = client_socket.recv(256)
        message_digest2 = hmac.digest(key_hmac.encode(), msg=frame_data, digest="sha3_256")
        print("Message Digest 2 : {}".format(message_digest2.hex()))

        #Authentication
        print("\nIs message digest 1 is equal to message digest 2? : {}".format(hmac.compare_digest(hmac_hash, message_digest2)))

        if (hmac.compare_digest(hmac_hash, message_digest2)):
            frame = pickle.loads(frame_data)
            cv2.imshow("Received Henon-Encrypted Image", frame)

            received_image_path = "received_HenonEnc.png" 
            cv2.imwrite(received_image_path, frame)
            #cv2.waitKey(0)  # Wait until a key is pressed to close the window

            #decrypt the image
            HenonDecryption(received_image_path, key)

            # Display the decrypted image
            im = Image.open("received_HenonDec.png", 'r')
            imshow(np.asarray(im))
            plt.title('Henon-Decrypted Image', fontsize=20)
            plt.show()

            #del the received enc image
            try:
                os.remove(received_image_path)
                print(f"File {received_image_path} deleted successfully.")
            except FileNotFoundError:
                print(f"File {received_image_path} not found.")
            except Exception as e:
                print(f"An error occurred: {e}")

        else:
            print("Authentication failed. Data integrity compromised.")
        break

    server_socket.close()

if __name__ == "__main__":
    receive_image()

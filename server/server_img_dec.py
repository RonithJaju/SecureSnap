# Import necessary modules
from PIL import Image
import numpy as np
from matplotlib.pyplot import imshow
import matplotlib.pyplot as plt
import cv2
import socket
import struct
import pickle
import os
import sys
import time

# Adding parent directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

# Importing custom modules
from modules.diffie_hellman import diffie_hellman_server
from modules.henon import HenonDecryption
from modules.hmac_hash import *

def receive_image():

    if not os.path.exists('decrypted'):
        os.makedirs('decrypted')

    # Socket connection
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('127.0.0.1', 12345))
    server_socket.listen(1)
    print("Waiting for a connection...")
    client_socket, client_address = server_socket.accept()
    print("Connected to", client_address)


    # Diffie Hellman Key Exchange for Henon Map
    # print("\nHenon Map Key:")
    k1, P1 = diffie_hellman_server(client_socket, "henon")
    scaled_secret = k1 / P1
    
    # Diffie Hellman Key Exchange for HMAC
    # print("HMAC Key:")
    k2, P2 = diffie_hellman_server(client_socket)
    
    payload_size = struct.calcsize(">L")

    while True:

        data = b""
        # Receive filename and extension
        filename, extension = pickle.loads(client_socket.recv(4096))
        
        # Recieve Encrypted Image
        while len(data) < payload_size:
            data += client_socket.recv(4096)

        packed_msg_size = data[:payload_size]
        data = data[payload_size:]
        msg_size = struct.unpack(">L", packed_msg_size)[0]
        
        while len(data) < msg_size:
            data += client_socket.recv(4096)

        frame_data = data[:msg_size]
        data = data[msg_size:]

        # HMAC Generation and Authentication
        hmac_key = str(k2)
        computed_hmac_hash = generate_hmac(hmac_key, frame_data)
        recieved_hmac_hash = client_socket.recv(256)
        isAuthentic = hmac_authentication(recieved_hmac_hash, computed_hmac_hash)

        # Authentication successfull, proceed with decryption
        if (isAuthentic):
            # Read and Display the image
            frame = pickle.loads(frame_data)
            received_image_path = f"decrypted\{filename}_HenonEnc{extension}"
            cv2.imwrite(received_image_path, frame)

            #Henon Decryption
            henon_key = (scaled_secret, scaled_secret)
            HenonDecryption(received_image_path, henon_key)

            #Delete the received encrypted image
            try:
                os.remove(received_image_path)
                #print(f"File {received_image_path} deleted successfully.")
            except Exception as e:
                print(f"An error occurred: {e}")

            # Display the decrypted image
            im = Image.open(f"decrypted\{filename}_HenonDec{extension}", 'r')
            imshow(np.asarray(im))
            plt.title(filename + "_HenonDec" + extension, fontsize=20)
            plt.show()
            print(filename)

        # Authentication failed
        else:
            print("Authentication failed. Data integrity compromised.")
        # break
    server_socket.close()

if __name__ == "__main__":
    receive_image()
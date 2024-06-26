# Import necessary modules
import cv2
import socket
import struct
import pickle
import time
import os
import sys
import zipfile

# Adding parent directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

# Importing custom modules
from modules.diffie_hellman import diffie_hellman_client, calculate_brute_force_time
from modules.henon import HenonEncryption
from modules.hmac_hash import generate_hmac

def send_image():
    # Socket connection
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('127.0.0.1', 12345))

    # Diffie Hellman Key Exchange for Henon Map
    k1, P1 = diffie_hellman_client(client_socket)
    scaled_secret = k1 / P1
    henon_key = (scaled_secret, scaled_secret)

    # Diffie Hellman Key Exchange for HMAC
    k2, P2 = diffie_hellman_client(client_socket)

    # Key space and Brute force time
    calculate_brute_force_time()


    # Henon encryption
    image_path=r"images\orig.png"
    filename, extension = os.path.splitext(image_path)


    HenonEncryption(image_path, henon_key)

    image_path_new = filename + "_HenonEnc"+extension
    image_enc = cv2.imread(image_path_new)

    # Send filename and extension
    client_socket.sendall(pickle.dumps((filename.split('\\')[-1], extension)))

    # Send encrypted image to server
    data = pickle.dumps(image_enc)
    size = struct.pack(">L", len(data))
    client_socket.sendall(size) # Send the frame size
    client_socket.sendall(data) # Send the serialized frame

    
    # Delete the encrypted image
    try:
        os.remove(image_path_new)
        #print(f"File {image_path_new} deleted successfully.")
    except Exception as e:
        print(f"An error occurred: {e}")

    # HMAC generation
    time.sleep(0.1)
    hmac_key = str(k2)
    computed_hmac_hash = generate_hmac(hmac_key, data)

    #Send HMAC to server
    client_socket.sendall(computed_hmac_hash)

    client_socket.close()

if __name__ == "__main__":
    send_image()
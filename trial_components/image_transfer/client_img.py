import cv2
import socket
import struct
import pickle

def send_image():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('127.0.0.1', 12345))

    image_path = r"C:\Users\ronit\projects\crypto paper\orig.png"  # Replace with the path to your image file
    image = cv2.imread(image_path)

    # Serialize the frame
    data = pickle.dumps(image)
    size = struct.pack(">L", len(data))

    # Send the frame size
    client_socket.sendall(size)

    # Send the serialized frame
    client_socket.sendall(data)

    client_socket.close()

if __name__ == "__main__":
    send_image()

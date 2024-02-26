'''
    # Open the encrypted image
    im = Image.open(image_path.split('.')[0] + "_HenonEnc.png", 'r')
    #imshow(np.asarray(im))
    #plt.show()

    # Convert the image to a NumPy array
    img_array = np.asarray(im)

    # Get the size of the image array
    image_size = len(img_array.tobytes())

    # Serialize the image array and send it to the server
    data = pickle.dumps(img_array)
    size = struct.pack(">L", image_size)

    # Send the size
    client_socket.sendall(size)

    # Send the serialized image array
    client_socket.sendall(data)

    client_socket.close()

if __name__ == "__main__":
    send_image()
'''
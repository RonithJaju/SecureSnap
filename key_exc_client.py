import socket

def generate_public_key(g, x, p):
    return pow(g, x) % p

def generate_secret_key(y, x, p):
    return pow(y, x) % p

def diffie_hellman_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('127.0.0.1', 12345))

    P = int(client_socket.recv(1024).decode())
    client_socket.sendall(b"Ack")  # Acknowledge

    G = int(client_socket.recv(1024).decode())
    client_socket.sendall(b"Ack")  # Acknowledge

    y2 = int(client_socket.recv(1024).decode())
    x2 = int(input("Enter the private key of User 2: "))
    y1 = generate_public_key(G, x2, P)

    client_socket.sendall(str(y1).encode())

    k2 = generate_secret_key(y2, x2, P)
    print(f"\nSecret Key for User 2 is {k2}\n")

    client_socket.close()

if __name__ == "__main__":
    diffie_hellman_client()

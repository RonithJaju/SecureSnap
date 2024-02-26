import socket

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

def primitive_check(g, p, L):
    # Checks if the entered number is a Primitive Root or not
    for i in range(1, p):
        L.append(pow(g, i) % p)
    for i in range(1, p):
        if L.count(i) > 1:
            L.clear()
            return False
    return True

def generate_public_key(g, x, p):
    return pow(g, x) % p

def generate_secret_key(y, x, p):
    return pow(y, x) % p

def diffie_hellman_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('127.0.0.1', 12345))
    server_socket.listen(1)

    print("Waiting for a connection...")
    client_socket, client_address = server_socket.accept()
    print("Connected to", client_address)

    l = []

    while True:
        P = int(input("Enter P (prime): "))
        if not prime_checker(P):
            print("Number is not prime, please enter again!")
            continue
        break

    while True:
        G = int(input(f"Enter the primitive root of {P}: "))
        if not primitive_check(G, P, l):
            print(f"Number is not a primitive root of {P}, please try again!")
            continue
        break

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
    
    server_socket.close()

if __name__ == "__main__":
    diffie_hellman_server()

import socket
import random

# Helper functions
def generate_public_key(g, x, p):
    return pow(g, x, p)

def generate_secret_key(y, x, p):
    return pow(y, x, p)

def calculate_brute_force_time():
    prime_modulus_bits = 128
    key_space = pow(2, prime_modulus_bits)
    print("Key space: 2**128 = {:.3e}".format(key_space))
    
    key_trials_per_second = pow(10, 11)
    brute_force_time  = key_space / key_trials_per_second
    brute_force_time_hours = brute_force_time / 3600
    print("Estimated time for brute-force attack: {:.3e} hours".format(brute_force_time_hours))



# def prime_checker(p):
#     if p < 1:
#         return False
#     elif p > 1:
#         if p == 2:
#             return True
#         for i in range(2, p):
#             if p % i == 0:
#                 return False
#         return True
    
# def primitive_check(g, p):
#     seen = set()
#     for i in range(1, p):
#         result = pow(g, i, p)
#         if result in seen:
#             return 0 
#         seen.add(result)
#     return 1

# Server
def diffie_hellman_server(client_socket, callFunc = "HMAC"):

    # User inputs modulus value (prime)
    # while True:
    #     P = int(input("Enter P (prime): "))
    #     if not prime_checker(P):
    #         print(f"{P} is not prime, please enter again!")
    #         continue
    #     break

    # # User inputs primitive root of prime
    # while True:
    #     G = int(input(f"Enter the primitive root of {P}: "))
    #     if G >= P or not primitive_check(G, P):
    #         print(f"{G} is not a primitive root of {P}, please try again!")
    #         continue
    #     break
    
    if callFunc == "henon":
        P = 229363825134802087656724050579412084897
        G = 229363825134802087656724050579412084782
    else:
        P = 257367189589445470019423629510774663711
        G = 257367189589445470019423629510774663661

    # User inputs private key, public key is generated

    #x1 = int(input("Enter the private key of User 1: "))
    x1 = random.randint(10, 1000000)
    #print("x1:", x1)
    y1 = generate_public_key(G, x1, P)

    # Key exchange between client and server
    client_socket.sendall(str(P).encode())
    client_socket.recv(1024)  # Acknowledge

    client_socket.sendall(str(G).encode())
    client_socket.recv(1024)  # Acknowledge

    client_socket.sendall(str(y1).encode())

    y2 = int(client_socket.recv(1024).decode())

    # Secret key is generated
    k = generate_secret_key(y2, x1, P)
    #print(f"\nSecret Key for User 1 is {k}\n")
    
    return k, P

# Client
def diffie_hellman_client(client_socket):
    
    # Key exchange between client and server
    P = int(client_socket.recv(1024).decode())
    client_socket.sendall(b"Ack")  # Acknowledge

    G = int(client_socket.recv(1024).decode())
    client_socket.sendall(b"Ack")  # Acknowledge

    y2 = int(client_socket.recv(1024).decode())
    
    # User inputs private key, public key is generated
    #x2 = int(input("Enter the private key of User 2: "))
    x2 = random.randint(10, 1000000)
    #print("x2:", x2)
    y1 = generate_public_key(G, x2, P)

    client_socket.sendall(str(y1).encode())

    # Secret key is generated
    k = generate_secret_key(y2, x2, P)
    #print(f"\nSecret Key for User 2 is {k}\n")
   
    return k, P
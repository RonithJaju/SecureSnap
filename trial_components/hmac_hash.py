import hmac

message = "Welcome to CoderzColumn."
key = "abracadabra"

print("10".encode())

#Server
message_digest1 = hmac.digest("10".encode(), msg=message.encode(), digest="sha3_256")
print("Message Digest 1 : {}".format(message_digest1.hex()))

#Client
message_digest2 = hmac.digest("10".encode(), msg=bytes(message, encoding="utf-8"), digest="sha3_256")
print("Message Digest 2 : {}".format(message_digest2.hex()))

#Authentication
print("\nIs message digest 1 is equal to message digest 2? : {}".format(hmac.compare_digest(message_digest1, message_digest2)))

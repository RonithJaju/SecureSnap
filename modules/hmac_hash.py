import hmac

def generate_hmac(key, data):
    h = hmac.new(key.encode(), data, "sha3_256")
    message_digest = h.digest()
    #print("Message Digest: {}".format(message_digest.hex()))
    return message_digest

def hmac_authentication(recieved, computed):
    result = hmac.compare_digest(recieved, computed)
    #print("Server-Client message digest equal? : {}".format(result))
    return result
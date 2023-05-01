import socket
import pickle
import hmac
import hashlib

def getKey():
    with open('key.txt', 'r') as keyfile:
        for line in keyfile:
            return line

def sendmsg(DATA, HOST="192.168.1.7", PORT=9999):
    pickled_data = pickle.dumps(DATA)

    key = getKey()

    print(pickled_data)
    digest = hmac.new(bytearray(key, 'utf-8'), pickled_data, hashlib.sha1).hexdigest()
    header = '%s' % (digest)
    print(digest)
    # Create a socket (SOCK_STREAM means a TCP socket)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        # Connect to server and send data
        sock.connect((HOST, PORT))
        #sock.sendall(bytes(DATA + "\n", "utf-8"))
        sock.sendall(bytes(header, 'utf-8') + bytes(' ', 'utf-8') + pickled_data)

        # Receive data from the server and shut down
        received = str(sock.recv(1024), "utf-8")

    print("Sent:     {}".format(DATA))
    print("Received: {}".format(received))

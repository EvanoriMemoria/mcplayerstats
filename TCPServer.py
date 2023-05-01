import socketserver
import hmac
import pickle
import hashlib

def getKey():
    with open('key.txt', 'r') as keyfile:
        for line in keyfile:
            return line

class MyTCPHandler(socketserver.BaseRequestHandler):
    """
    The request handler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    def handle(self):
        # self.request is the TCP socket connected to the client
        self.data = self.request.recv(1024)
        recvd_digest, pickled_data = self.data.split(bytes(' ', 'utf-8'))
        recvd_digest = recvd_digest.decode()

        key = getKey()

        print(pickled_data)
        new_digest = hmac.new(bytearray(key, 'utf-8'), pickled_data, hashlib.sha1).hexdigest()
        if recvd_digest != new_digest:
            print('Integrity Check Failed')
        else:
            unpickled_data = pickle.loads(pickled_data)
            print(unpickled_data)
        # just send back the same data, but upper-cased
        self.request.sendall(bytearray("Thanks!", 'utf-8'))

if __name__ == "__main__":
    HOST, PORT = "192.168.1.7", 9999

    # Create the server, binding to localhost on port 9999
    with socketserver.TCPServer((HOST, PORT), MyTCPHandler) as server:
        # Activate the server; this will keep running until you
        # interrupt the program with Ctrl-C
        server.serve_forever()
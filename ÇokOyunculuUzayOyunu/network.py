import socket
import pickle

class Network:
    def __init__(self): 
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = "server ipv4 adresi"  # KENDİ IP'n ile değiştir
        self.port = 5555
        self.addr = (self.server, self.port)
        self.id = None
        self.connect()

    def connect(self):
        try:
            self.client.connect(self.addr)
            self.id = int(self.client.recv(8).decode())
        except:
            pass

    def send(self, data):
        try:
            self.client.send(pickle.dumps(data))
            return pickle.loads(self.client.recv(4096))
        except socket.error as e:
            print(e)

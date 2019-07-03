import sys
import zmq
import json
import os
import hashlib
import re, uuid

"""
Registro=
	{
	hash_file : [parts in this server]
	}

Succesor=
	{
	"hash" : hash
	"ip": ip:port
	}
"""
sizePart = 1024*1024*10  #bytes
m = 256

class Node:
	def __init__(self):
		"""
		self.mac = str(uuid.getnode())
		print(int(self.mac, 10))
		self.hash_calc = hashlib.sha256()
		self.hash_calc.update(int(self.mac, 10))
		print(self.hash_calc)
		"""

		#self.hash = str(hash_calc.hexdigest())
		#self.successor = {}
	def ident(self):
		x = ""
		s = self.mac.split(":")
		for i in s:
			x = x + i
		print(x)
		self.hash_calc = hashlib.sha256()
		self.hash_calc.update(x.encode())
		self.hash_calc = self.hash_calc.hexdigest()
		print(self.hash_calc)

	def Start(self):
		print("\n-- Welcome to UltraServerChord¢2019 --\n")
		print("To initialize Chord provide the your ip,port and then a node ip:port for connect")
		print("\tpython3 node.py ip port<node> ip:port<ring> <folderName> \n")
		print("Example: python3 node.py 192.168.0.0 8001 127.255.255.0:8080 folder")

		if len(sys.argv) != 6:
			print("\n-- Error --\n")
			print("\tInvalid sintax")
			exit()

		ip=sys.argv[1]
		port=sys.argv[2]
		self.web=sys.argv[3]
		self.loc=sys.argv[4]
		self.register={}
		self.first=False

		#para pruebas locales
		self.mac = sys.argv[5]
		
		Node.ident()

		if os.path.isdir('./'+self.loc) == False:
			print("\nThis folder doesn't exist ")
			print("Creating the new directory /{}".format(self.loc))
			os.mkdir('./'+self.loc)

		#this is a first connection into two nodes
		# there is listening
		context = zmq.Context()
		self.socket = context.socket(zmq.REP)
		self.socket.bind("tcp://*:"+ port)

		# there is calling other nodes
		socket_s = context.socket(zmq.REQ) # socket al sucesor

		# if the web direction is the same of my ip address that means it's the first node
		if self.web == str(ip+":"+port):
			print("i am the first u.u")
			self.first = True
			self.successor = {"hash":self.hash_calc,"ip":str(ip+port)}
		else:
			print ("Connecting to web now ...")
			socket_s.connect("tcp://" + self.web)
			socket_s.send_multipart([b"add_successor",self.hash_calc.encode(),ip.encode(),port.encode()])
			response = socket_s.recv_multipart()
			while response[0].decode() == "this way":
				other_socket = eval(response[1].decode())
				print("Asking again to "+other_socket.get("hash")+":( ")
				response = ""
				#socket_s.connect("tcp://" + )
				#socket_s.send_multipart([b"add_successor", self.hash.encode(), ip.encode(), port.encode()])

			if response[0].decode() == "welcome":
				print("I know my place =D")
				if response[1].decode() == "successor":
					print("I am him successor")
					
					rta = socket_s.recv_multipart()
					print(rta)

				#socket_s.send_multipart([b"set_successor",self.hash.encode(),ip.encode(),port.encode()])
				#recv_successor = self

		while True:
			print("\nListening in "+ip+":"+port+" ...")
			query = self.socket.recv_multipart()

			if query[0].decode() == "upload":

"""
	def connect(self):
		contextP = zmq.Context()
		socketP = contextP.socket(zmq.REQ)
		#a = input()
		node = "tcp://" + self.ip_other_Node + ":" + self.port_other_Node
		socketN.connect(node)
		#   socketN.send_multipart([b"server",self.IP_SERVER.encode(),self.PORT_SERVER.encode(),str(self.f_space).encode()])
		req = socketP.recv()
		if req.decode()=="NEXT":
			socketP.send_json(self.register)

		response = socketN.recv()
		if response.decode()=="OK":
			print ("\nNodo is connected ")
		else:
			print("Error!")

"""

if __name__ == '__main__':
	Node = Node()
	Node.Start()
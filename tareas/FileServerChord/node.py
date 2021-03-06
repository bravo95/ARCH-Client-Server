import sys
import zmq
import json
import os
import hashlib
import re, uuid
import random
from os import listdir

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
		print("Hello new node")
		"""
		#para pruebas locales
		self.hash_calc = hashlib.sha256()
		self.hash_calc.update(str(random.randrange(0, 101, 2)).encode()) 
		self.hash_calc = self.hash_calc.hexdigest()
		print(self.hash_calc)
		"""
		self.ident()

	def ident(self): 
		self.mac = str(uuid.getnode())
		x = ""
		s = self.mac.split(":") 
		for i in s:
			x = x + i
		print(x)
		self.hash_calc = hashlib.sha256()
		self.hash_calc.update(x.encode())
		self.hash_calc = self.hash_calc.hexdigest()
		print(self.hash_calc)

	def find (self, x, y, z):
		if x < z:
			if x < y and y < z:
				return True
			else:
				return False
		if x > z:
			if x < y or y < z :
				return True
			else:
				return False

	def share(self, y):
		files = listdir(self.loc)
		sharelist = []
		count = len(files)
		z=self.successor.get("hash") # mi sucesor
		for i in files:
			if self.find(y,i,z):
				sharelist.append(i)
				count-=1
		print("Se quedan "+str(count)+" archivos, se envian "+str(len(files)-count) )
		return str(sharelist).encode()

	def Start(self):
		print("\n-- Welcome to UltraServerChord¢2019 --\n")
		print("To initialize Chord provide the your ip,port and then a node ip:port for connect")
		print("\tpython3 node.py ip<node> port<node> ip:port<ring> <folderName> \n")
		print("Example: python3 node.py 192.168.0.0 8001 127.255.255.0:8080 folder")

		if len(sys.argv) != 5:
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
		#self.mac = sys.argv[5]
		

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

		# if the web direction is the same of my ip address that means it's the first node
		if self.web == str(ip+":"+port):
			print("i am the first u.u")
			self.first = True
			self.successor = {"hash":self.hash_calc,"ip":str(ip+":"+port)}
			print(self.successor)
		else:
			print ("Connecting to web now ...")
			socket_s = context.socket(zmq.REQ) # socket al sucesor
			socket_s.connect("tcp://" + self.web)
			socket_s.send_multipart([b"add_successor",self.hash_calc.encode(),ip.encode(),port.encode()])
			response = socket_s.recv_multipart()
			while response[0].decode() == "this way":
				print("Ask again to "+response[1].decode()+":( ")
				socket_s.close()
				socket_s = context.socket(zmq.REQ) # socket al sucesor
				socket_s.connect("tcp://" + response[1].decode())
				socket_s.send_multipart([b"add_successor", self.hash_calc.encode(), ip.encode(), port.encode()])
				response = ""
				response = socket_s.recv_multipart()

			if response[0].decode() == "welcome":
				print("I know my place =D")
				self.successor={"hash":response[1].decode(),"ip":response[2].decode()}
				print("my succesor is ",self.successor)
				files = eval(response[3].decode())
				print(len(files)," parts for discharge")
				for i in files:
					socket_s.send_multipart([b"discharge",i.encode()])
					response = socket_s.recv_multipart()
					with open(self.loc+'/'+i,"xb") as f:
						f.write(response[1])
					print(response[0].decode())

		while True:
			print("\nListening in "+ip+":"+port+" ...")
			query = self.socket.recv_multipart()

			if query[0].decode() == "add_successor" and self.first == False:
				print("Ask for new node\n"+query[1].decode()+"\nip "+query[2].decode()+":"+query[3].decode()+" O.O")
				x=self.hash_calc # mi hash
				y=query[1].decode() # hash del que habla
				z=self.successor.get("hash") # mi sucesor
				#print(y+"<"+x+"::"+y+">"+z)
				if self.find(x,y,z):
					print ("this node comes here")
					self.socket.send_multipart([b"welcome",self.successor.get("hash").encode(),str(self.successor.get("ip")).encode(),self.share(query[1].decode())])
					self.successor.update({"hash":query[1].decode(),"ip":str(query[2].decode()+":"+query[3].decode())})
					print("now is my successor")
					print(self.successor)
				else:
					print ("redirection node ")
					self.socket.send_multipart([b"this way",self.successor.get("ip").encode()])
			
			if query[0].decode() == "add_successor" and self.first == True:
				print("Ask for first node\n"+query[1].decode()+"\nip "+query[2].decode()+":"+query[3].decode()+" O.O")
				x=self.hash_calc # mi hash
				y=query[1].decode() # hash del que habla
				print ("this node is my first partner ")
				self.socket.send_multipart([b"welcome",self.successor.get("hash").encode(),self.successor.get("ip").encode(),self.share(query[1].decode())])
				self.successor.update({"hash":query[1].decode(),"ip":str(query[2].decode()+":"+query[3].decode())})
				print("now is my successor")
				print(self.successor)
				self.first=False

			if query[0].decode() == "discharge":
				print("new discharge request ",query[1].decode())
				newName = self.loc+'/'+query[1].decode()
				with open(newName, "rb") as f:			
					bt = f.read(sizePart)
				self.socket.send_multipart([b"OK",bt])
				os.system("rm -r "+newName)
				print("file discharged")
			
			if query[0].decode() == "upload":
				print("new upload request ",query[1].decode())
				x=self.hash_calc # mi hash
				y=query[1].decode() # hash de la parte
				z=self.successor.get("hash") # mi sucesor
				#print(y+"<"+x+"\n"+y+">"+z)
				if self.find(x,y,z):
					print ("comes here")
					sha256 = query[1]
					newName = self.loc+'/'+query[1].decode()
					with open(newName,"xb") as f:
						f.write(query[2])
					print("file saved")
					self.socket.send_multipart([b"OK"])
				else:
					print ("redirection client")
					self.socket.send_multipart([b"NOT",self.successor.get("ip").encode()])

			if query[0].decode() == "download":
				print("new download request ",query[1].decode())
				x=self.hash_calc # mi hash
				y=query[1].decode() # hash de la parte
				z=self.successor.get("hash") # mi sucesor
				if self.find(x,y,z):
					print ("is here")
					print(query[1].decode())
					newName = self.loc+'/'+query[1].decode()
					with open(newName, "rb") as f:			
						bt = f.read(sizePart)
					self.socket.send_multipart([b"OK",bt])
					print("file sended")
				else:
					print ("redirection client")
					self.socket.send_multipart([b"NOT",self.successor.get("ip").encode()])
			
	#socket.send(b"OK")
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

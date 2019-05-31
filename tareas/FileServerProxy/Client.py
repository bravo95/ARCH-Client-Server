"""
Created on Tue May 09 2019
@author: Esteban Grisales && Andres Felipe Bravo
Arquitectura Cliente Servidor - UTP 
"""
import zmq
import hashlib
import json
import os
import sys

sizePart = 1024*1024*10
ip="localhost"
sizeBuf = 65536
PORT = "8002"

class Client:
	def Start(self):
		os.system("clear")
		print("\n\n-- Welcome to UltraServer¢2019 --\n")
		print("Use <id> <function> <route> to acces interface")
		print("\t<id> \n\t   Please use the same id for all your consults")
		print("\t<function> there is 2 options:\n\t   \"upload\"\n\t   \"download\"")
		print("\t<route>\n \t\trute of the file, </home/images> \n")
		print("\t<filename>\n \t\tthe name of the file <ejemplo.jpg> \n")
		print("##################################\n")

		if len(sys.argv) != 5:
			print("\n-- Error --\n")
			print("\tInvalid sintax")
			exit()

		self.ident= sys.argv[1].encode()
		self.operation = sys.argv[2].encode()
		self.route = sys.argv[3].encode()
		self.filename=sys.argv[4].encode()

		context = zmq.Context()
		self.socket_proxy = context.socket(zmq.REQ)
		self.socket_proxy.connect("tcp://"+ip+":"+PORT)
		print("Establishing connection to proxy")

		self.proxy_negotiations()

		if self.operation.decode()=='upload':
		    self.upload(self.filename,self.socket_servers, self.ident)
		elif operation.decode()=='download':
			self.download(self.filename,self.socket_proxy,self.ident)
		print("Operation complete ")
	
	def proxy_negotiations(self):
		parts = []
		with open(self.route.decode()+self.filename.decode(), 'rb') as f:
			while True:
				byte = f.read(sizePart)
				if not byte:
					break

				sha2 = hashlib.sha256()
				sha2.update(byte)
				parts.append(sha2.hexdigest())

		print("El archivo tiene el siguiente numero de partes: ",len(parts))

		self.socket_proxy.send_multipart([b"client",self.get_hash(), self.operation, parts])
		response = socket_proxy.recv()
		if response.decode()=="OK":
			print("Proxy conect succesfully\n")
		else:
			print("Error conecting proxy!")

		#self.socket_servers.connect("tcp://"+ip+":"+PORT)
		print("Preparing to send parts")
		#return {"filename" : sha256.hexdigest(),"parts" :parts}

	def writeBytes(self,route,info):
		newName='new-'+route
		print("Writing file...[{}]".format(newName))

		with open(newName,"wb") as f:
		    f.write(info)
		print("Downloaded [{}]".format(newName))

	def get_hash(self):
		with open(self.route.decode()+self.filename.decode(), 'rb') as f :
			sha256 = hashlib.sha256()
			while True:
				file = f.read(sizeBuf)
				if not file :
					break
				sha256.update(file)
		hashfile = sha256.hexdigest().encode()
		return hashfile

	def upload(self, socket, ID):
		with open(self.route.decode()+self.filename.decode(), "rb") as f:
			finished = False
			part = 0
			while not finished:
				f.seek(part*sizePart)
				bt = f.read(sizePart)
				print("Uploading part {}".format(part+1))
				socket.send_multipart([self.get_hash(),ID, b"upload",self.filename, bt])
				part+=1
				if len(bt) < sizePart:
					finished = True
				response = socket.recv()
				if response.decode()=="OK":
					print("Part send succesfully\n")
				else:
					print("Error!")

	def download(self,filename,socket,ID):
		#print("Download not implemented yet!!!!")
		socket.send_multipart([ID,b'download',filename])
		response=socket.recv_multipart()
		filename,info=response
		print("write[{}]".format(filename))
		self.writeBytes(filename.decode(),info)

if __name__ == '__main__':
	Cliente = Client()
	Cliente.Start()

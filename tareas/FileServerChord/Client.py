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
PORT = "9000"
red = "localhost:8000"
sizeBuf = 65536


class Client:
	def start(self):
		os.system("clear")
		print("\n-- Welcome to UltraServer¢2019 Chord--\n")
		print("Use <function> <route> <filename> to acces interface")
		print("<function> there is 2 options:\n\t   \"upload\"\n\t   \"download\"")
		print("<route>\trute of the file, </home/images> \n")
		print("<filename>\tthe name of the file <ejemplo.jpg> \n")

		if len(sys.argv) != 4:
			print("\n-- Error --")
			print("\t Invalid syntax, try again please")
			exit()

		self.operation = sys.argv[1].encode()
		self.route = sys.argv[2].encode()
		self.filename = sys.argv[3].encode()

		context = zmq.Context()
		self.socket_node = context.socket(zmq.REQ)
		self.socket_node.connect("tcp://"+"red")
		self.node_negotiations()

	def node_negotiations(self):
		print("Establishing connection to node ...")
		if self.operation == b"upload":
			self.upload()
		elif self.operation == b"download":
			self.download()

	def upload(self):
		#parte el archivo y pone cada uno de los hash en una lista
		self.parts = []
		with open(self.route.decode()+self.filename.decode(), 'rb') as f:
			while True:
				byte = f.read(sizePart)
				if not byte:
					break
				sha_part = hashlib.sha256()
				sha_part.update(byte)
				self.parts.append(sha_part.hexdigest())

		#crea .json con hash de archivo, hash de archivo como llave.
		register={self.get_hash().decode():{"parts":self.parts}}
		#crea el archivo para la descarga
		with open(str(self.get_hash.decode()+".json"),"x") as f: 	
			json.dump(self.register,f)

		#ejecuta upload_part con la direccion entregada por find
		self.upload_part()
		

	def upload_part(self):
		with open(self.route.decode()+self.filename.decode(), "rb") as f:
			finished = False
			part = 0
			while not finished:
				f.seek(part*sizePart)
				bt = f.read(sizePart)

				if len(bt) < sizePart:
					finished = True

				print("Uploading part {}".format(part+1))
				#hace upload de la parte directamente en el nodo para verificar si lo acepta o no
				self.socket_node.send_multipart([self.operation, self.parts[part].encode(), bt])
				response = self.socket_node.recv_multipart()

				if response[0].decode()=="OK":
					print("Part send succesfully\n")
					self.socket_node.close()
					if len(bt) < sizePart:
						finished = True
					part+=1
				elif response[0].decode()=="NOT":
					#change the socket
					self.socket_node.close()
					self.socket_node = context.socket(zmq.REQ)
					self.socket_node.connect("tcp://"+response[1].decode())


	def download(self):

		reg_down = self.filename.decode()

		print(reg_down)
		parts = reg_down.get("parts")
		print("Conecting to Node ...")
		finished = False

		for i in range(0,len(parts)):
		#while not finished:
			#self.socket_node.send_multipart([self.operation,self.])
			#self.socket_node.connect("tcp://"+servers[i])
			while not finished:
				self.socket_node.send_multipart([self.operation,parts[i].encode()])
				response = self.socket_node.recv_multipart()

				if response[0].decode()=="OK":
					print("Part download succesfully\n")
					with open(self.route.decode()+"/"+self.filename.decode(), "ab") as f:
						#self.socket_node = context.socket(zmq.REQ)
						#self.socket_node.connect("tcp://"+servers[i])
						f.seek(i*sizePart)
						f.write(response[1])
						self.socket_node.close()
						print("Part download succesfully\n")
					#self.socket_node.send(b"OK")
					#self.socket_node.close()
					if len(bt) < sizePart:
						finished = True
					part+=1
				elif response[0].decode()=="NOT":
					#change the socket
					self.socket_node.close()
					self.socket_node = context.socket(zmq.REQ)
					self.socket_node.connect("tcp://"+response[1].decode())


if __name__ == '__main__':
	Cliente = Cliente()
	Cliente.start()
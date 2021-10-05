#!/usr/bin/env python
import socket, time
import getpass
import hashlib
from Crypto.Cipher import AES

def Tcp_connect( HostIp, Port ):
    global s
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HostIp, Port))
    return

def Tcp_Write(D):
   s.send(D + '\n'.encode())
   return

def Tcp_Read( ):
	a = ' '.encode()
	b = ''.encode()
	# import pdb
	# pdb.set_trace()
	# print('a')
	while a != b'\n':
		a = s.recv(1)
		b = b + a
	return b

def Tcp_Close( ):
   s.close()
   return

def PasswordCreate():
    user_in = getpass.getpass()
    password = hashlib.md5()
    password.update(user_in.encode("utf-8"))
    return password.hexdigest()

def main():
	Tcp_connect('127.0.0.1',12345)

	option = input("Enter 1 for login, 0 registration: ")
	# print (option)
	Tcp_Write(option.encode())

	#print username, password

	#type_process = Tcp_Read()

	if(option == '0'):
		print (Tcp_Read())
		username = input("Enter your login username: ")
		password = PasswordCreate()
		Tcp_Write(username.encode())
		#print Tcp_Read()
		Tcp_Write(password.encode())
		#print Tcp_Read()
	elif(option == '1'):
		print (Tcp_Read())

		username = input("Enter your login username: ")
		# print(username)
		password = PasswordCreate()
		print (password)
		Tcp_Write(username.encode())
		#print Tcp_Read()
		Tcp_Write(password.encode())

		existence = Tcp_Read()
		existence = existence.strip(b'\n')


		if(existence == b'0'):
			print("Username does not exist")
		else:
			random_token = Tcp_Read()
			random_token = random_token.strip(b'\n')
			obj = AES.new(random_token, AES.MODE_CBC, 'This is an IV456'.encode())
			ciphertext = obj.encrypt(password.encode())
			Tcp_Write(ciphertext)
			auth_stat = Tcp_Read()
			auth_stat = auth_stat.strip(b'\n')
			print(auth_stat)
			if(auth_stat == b'Wrong Password'):
				print ("Error, Cannot Log in!")
			else:
				print("Logged In!")
	print ("Closing Connection")
	Tcp_Close()


if __name__ == '__main__':
	while(True):
		print("--- New connection ---")
		main()

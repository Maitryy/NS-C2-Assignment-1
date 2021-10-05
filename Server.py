#!/usr/bin/env python
import socket, time, string
import sqlite3
import random
from Crypto.Cipher import AES

#things to begin with
def Tcp_connect(HostIp, Port):
	global s
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	s.connect((HostIp, Port))
	#SocketServer.TCPServer.allow_reuse_address = True
	return

def Tcp_server_wait(numofclientwait, port, HostIp):
	global s2
	s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s2.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	s2.bind((HostIp, port))
	s2.listen(numofclientwait)

def Tcp_server_next ( ):
	global s
	s = s2.accept()[0]

def Tcp_Write(D):
	s.send(D.encode() + '\n'.encode())
	return

def Tcp_Read( ):
	a = ' '.encode()
	b = ''.encode()
	#import pdb
	#pdb.set_trace()
	# print('a')
	while a != b'\n':
		a = s.recv(1)
		b = b + a
	return b

def Tcp_Close( ):
	s.close()
	return

def random_token_generator(size=16, chars=string.ascii_uppercase + string.digits):
	return ''.join(random.choice(chars) for _ in range(size))

def create_connection(db_file):
	""" create a database connection to the SQLite database
	specified by db_file
	:param db_file: database file
	:return: Connection object or None
	"""
	try:
		conn = sqlite3.connect(db_file)
		return conn
	except:
		print("Cannot Create Connection")

	return None

def create_table(conn, create_table_sql):
	""" create a table from the create_table_sql statement
	:param conn: Connection object
	:param create_table_sql: a CREATE TABLE statement
	:return:
	"""
	try:
		c = conn.cursor()
		c.execute(create_table_sql)
	except:
		print("Cannot Create Table")

def main():
	database = "sqlite_users.db"

	sql_create_usernames_table = """ CREATE TABLE IF NOT EXISTS usernames(
                                        id integer primary key AUTOINCREMENT,
                                        name nvarchar(40) not null,
                                        password nvarchar(32) not null
                                    ); """


	# create a database connection
	conn = create_connection(database)
	if conn is not None:
	# create projects table
		create_table(conn, sql_create_usernames_table)
	else:
		print("Error! cannot create the database connection.")
	#Tcp_connect("127.0.0.1", 12345)
	while(True):
		print ("Waiting for a client")
		Tcp_server_wait (1,12345, '127.0.0.1')
		
		Tcp_server_next()
		option = Tcp_Read()
		#print repr(option)

		option = option.strip(b'\n')
		print(option)
		if(option == b'0'):
			print("Creating new user")
			Tcp_Write("Registering...")
			username = Tcp_Read()
			username = username.strip(b'\n')
			password = Tcp_Read()
			password = password.strip(b'\n')
			print (username, password)
			cursor = conn.cursor()
			cursor.execute('insert into usernames (name, password) values (?, ?)', (username, password,))
			conn.commit()
			print ("Inserted")

		elif(option == b'1'):
			print("Login process")
			Tcp_Write("Logging in...")
			username = Tcp_Read()
			username = username.strip(b'\n')
			password = Tcp_Read()
			password = password.strip(b'\n')
			cursor = conn.cursor()
			cursor.execute('select password from usernames where name = ?', (username,))
			rows = cursor.fetchall()
			#print rows
			#for row in rows:
        		#	password_in_db = row
			if(not rows):
				print("Invalid!")
				Tcp_Write("0")
			else:
				Tcp_Write("1")
				password_in_db = rows[0];
				password_in_db = password_in_db[0]
				random_token = random_token_generator()
				Tcp_Write(random_token)

				obj = AES.new(random_token.encode(), AES.MODE_CBC, 'This is an IV456'.encode())
				ciphertext = obj.encrypt(password_in_db)

				read_encrypted_hash = Tcp_Read()
				#print read_encrypted_hash
				read_encrypted_hash = read_encrypted_hash.strip(b'\n')

				#print read_encrypted_hash

				if(read_encrypted_hash == ciphertext):
					print("Authentication successful!")
					print( read_encrypted_hash, ciphertext)
					Tcp_Write("Successful")
				else:
					print("Password mismatch!")
					Tcp_Write("Wrong Password")
		else:
			pass
			#print("Pass")

		Tcp_Close()
		print("--- New connection ---")

if __name__ == '__main__':
	main()

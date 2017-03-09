# usr/bin/env_python
# coding = utf-8

import sys
import signal
import os
import socket
import thread

serverPort = 8000
cachePort = 8001

DEBUG = True

def log(s):
	if DEBUG:
		print s


def sighandler(signal, frame):
    print '\nCTRL+C detected! Exiting Server...'
    sys.exit(0)


def createsocket(port):
    # Criar socket TCP
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Receber nome
    host = socket.gethostname()

    # Conectar
    sock.connect((host, port))
    return sock


def recv_fn(connection):
	print 'A receber...'
	temp = connection.recv(128)
	file_name = temp.splitlines()
	file_name = file_name[0]

	return file_name


def listar(sock_sv, conn): 	# listar ficheiros do user default
	log('dentro do listar... a enviar op ao server')
	sock_sv.send('3\ndefault\ndefault\n')

	log('a espera de confirmacao...')
	confirm = eval(sock_sv.recv(1))

	if confirm == 0:
		print '-- LISTA VAZIA --'
		conn.send('0')
	elif confirm == 1:
		conn.send('1')
		
		tmp = sock_sv.recv(1024)
		lista = tmp
		temp = tmp.splitlines()

		while temp[-1] != '1':
		    tmp = sock_sv.recv(1024)
		    lista += tmp
		    temp = tmp.splitlines()

		tmp = lista.splitlines()
		print '-- LISTA --'
		for i in range(0,len(tmp)-1):
		    print 'Ficheiro',i+1,' =', tmp[i]

		# ENVIAR AO CLIENTE
		for i in range(0,len(tmp)-1):
			conn.send(tmp[i]+'\n')
		conn.send('1')
	return confirm


# Fazer de Cliente para o SV
#receber do cliente o ficheiro enviado e envio para o servidor
def server_upload(sock_sv, fn): #upload
	print("Uploading to server\n")

	if os.path.isfile(fn): # Verificacao do q veio do client
		sock_sv.send('5\ndefault\ndefault\n')
		sock_sv.send(fn+'\n')

		confirm = sock_sv.recv(1)

		f = open(fn,'rb')
		s = f.read(1024)

		while s:
			log('Sending file...')
			sock_sv.send(s)
			s = f.read(1024)
		sock_sv.send('\nfim\n')
		print('Sent.\n')

		f.close()
		return 0
	else:
		return 1

# Fazer de SV para o Cliente
def upload(sock_sv, connection):
	print '** CLIENT UPLOADING **\n'

	file_name = recv_fn(connection)
	print 'File name = ', file_name

	connection.send('1')
	log('after send')

	f = open(file_name, 'wb')
	l = connection.recv(1024)

	tmp = l.splitlines()


	while tmp[-1] != 'fim':
		f.write(l)
		l = connection.recv(1024)
		tmp = l.splitlines()

	log('Ficheiro recebido do cliente... A enviar para o SV...')
	f.close()

	if server_upload(sock_sv, file_name) == 1:
		print("Erro upload (server)")

	os.remove(file_name);

	print '** Fim upload **'
	return repr(0)


# Server -> Cache
def server_download(sock_sv, fn): #download
	print("Downloading from server")

	sock_sv.send('4\ndefault\ndefault')
	sock_sv.send(fn+'\n')

	confirm = eval(sock_sv.recv(1))

	if confirm != 0:
	    with open(fn, 'wb') as f:
	        log('File opened')

	        data = sock_sv.recv(1024)
	        tmp = data.splitlines()
	        f.write(tmp[0])

            while tmp[-1] != '1':
                log('inside download write!!')
                f.write(data)
                data = sock_sv.recv(1024)
                tmp = data.splitlines()
	    print 'Ficheiro obtido do SV com sucesso!'
	    return 0
	else:
		print '- ERRO DOWNLOAD -\nFicheiro inexistente no servidor.'
		return 1


# Cache -> Cliente
def download(sock_sv, connection):
	print '** DOWNLOAD **'

	file_name = recv_fn(connection)

	print 'Ficheiro pedido =', file_name

	if os.path.isfile(file_name) or server_download(sock_sv, file_name) == 0:   # Se ficheiro existir
	    connection.send('1')

	    f = open(file_name, 'rb')
	    l = f.read(1024)

	    while l:
	        print 'A enviar ao cliente...'
	        connection.send(l)
	        l = f.read(1024)
	    f.close()
	    connection.send('\n1')

	    print 'Envio pela cache concluido.'
	else:   # Ficheiro nao existente
	    print 'Ficheiro nao existente!'
	    connection.send('0')


def receive(connection):
	log('A receber......')
	tmp = connection.recv(128)
	tmp = tmp.splitlines()
	operation = eval(tmp[0])
	username = tmp[1]
	password = tmp[2]
	return operation, username, password


def operations(conn,addr):
	log('A espera de login...')
	option, username, password = receive(connection)
	sock_sv = createsocket(serverPort)
	sock_sv.send('3\ndefault\ndefault')
	option = 0
	while option != 6:
		print 'A espera para receber operacao...'
		option, username, password = receive(connection)
		print 'Operacao recebida = ', option
		if option == 3:	 # LISTAR
			listar(sock_sv, conn)
		elif option == 4:	# DOWNLOAD
			download(sock_sv, conn)
		elif option == 5:	# UPLOAD
			upload(sock_sv, conn)
	print 'A fechar ligacao...'
	sock_sv.send('6\ndefault\ndefault')
	sock_sv.close()
	conn.close()
	thread.exit()


if __name__ == '__main__':
	signal.signal(signal.SIGINT, sighandler)

	# Criar socket TCP
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

	host = socket.gethostname()

	sock.bind((host, cachePort))
	sock.listen(5)	

	while True:
		print 'Cache server listening at port', cachePort, '...'
		connection, addr = sock.accept()
		thread.start_new_thread(operations, tuple([connection,addr]))
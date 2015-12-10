# usr/bin/env_python
# coding = utf-8

import sys
import signal
import os
import socket
import cPickle as pickle

serverPort = 8000

users = {}  # quando for preciso mudar -> global users
file_list = []


# fazer print list na funcao listar...

def sighandler(signal, frame):
    print '\nCTRL+C detected! Exiting Server...'
    sys.exit(0)


def upload(connection, userpath):
    global file_list
    print '** UPLOAD **'

    temp = connection.recv(128)
    temp = temp.splitlines()
    print '- Ficheiro Recebido =', temp[0]

    file_name = temp[0]

    # print 'input recebido =', file_name

    if file_list.count(file_name) == 0:
        print '- Ficheiro ainda nao existente'
        file_list.append(file_name)
        with open(userpath+'list.pkl', 'wb') as f:
            pickle.dump(file_list, f)
            print '- Ficheiro adicionado a lista'
        file_name = userpath+file_name
    else:
        print '- Ficheiro ja presente no diretorio do user.'
        file_name = userpath+file_name+'(1)'

    print 'before send'
    connection.send('1')

    f = open(file_name, 'wb')

    l = connection.recv(1024)
    print 'after receive'
    f.write(l)

    f.close()
    print '** Fim upload **'

    return repr(0)


# Server -> Cliente
def download(connection, userpath):
    print '** DOWNLOAD **'

    connection.send('1')
    temp = connection.recv(128)
    file_name = temp.splitlines()
    print 'file_name =', file_name
    file_name = file_name[0]
    print 'Ficheiro pedido =', file_name
    file_name = userpath+'/'+file_name

    if os.path.isfile(file_name):   # Se ficheiro existir
        f = open(file_name, 'rb')
        l = f.read(1024)
        while l:
            print 'A enviar ao cliente...'
            connection.send(l)
            l = f.read(1024)
        f.close()
        print 'Envio concluido.'
    else:   # Ficheiro nao existente
        print 'Ficheiro nao existente!'
        connection.send('0')


def listar(connection):
    print '-- LISTAR --'
    for p in file_list:
        print p
    l = len(file_list)
    if l == 0:
        print 'LISTA VAZIA...'
        connection.send('0')
    else:
        connection.send('1')
        for i in range(len(file_list)):
            # print 'inside for'
            connection.send(file_list[i]+'\n')
        print 'Fim da listagem.\n'
        connection.send('1\n')


def login(option, username, password):
    global users
    if username in users.keys(): # Se utilizador existe
        if users[username] == password and option != 2: # Dados login corretos
            print '\nUser', username, 'logged in!\n'
            return 1
        else: # Password errada e utilizador existe
            if option == 1:
                print 'WRONG password'
            else:
                print 'USER ja existente'
            return 2
    else:  # Se utilizador nao existe
        if option == 2:  # new user
            users[username] = password
            with open('users.pkl', 'wb') as output:
                pickle.dump(users, output, pickle.HIGHEST_PROTOCOL)
            print '\n*** New USER created: ***\nUsername =',username,'\nPassword = ',password,'\n'
        else:
            print '\nUtilizador nao existente.\n'
        return 0


def receive(connection):
    print 'A receber.........'
    tmp = connection.recv(128)
    # print 'RECEIVED = ', tmp
    if not tmp:
        print 'VAZIO.'
        return repr(0)
    tmp = tmp.splitlines()
    operation = eval(tmp[0])
    username = tmp[1]
    password = tmp[2]
    return operation, username, password


def receive_option(connection):
    print 'A espera de receber opcao...'
    tmp = connection.recv(1)
    while not tmp:
        tmp = connection.recv(10)
    tmp = eval(repr(tmp))
    return tmp


def operations(connection):
    option, username, password = receive(connection)

    if option in [1, 2]:  # login/check if user exists
        confirm = login(option, username, password)
        print '[SERVER] confirm = ', confirm
        connection.send(repr(confirm))
        if confirm != 1:
            option = 2
    while option not in [0, 2, 6]:  # Login feito com sucesso
        print 'AFTER LOGIN...'
        option, username, password = receive(connection)
        # print 'option =', option
        if option == 0:
            return 0

        if not os.path.exists(username+'/'):
            os.makedirs(username+'/')

        global file_list
        if os.path.isfile(username+'/list.pkl') and (os.path.getsize(username+'/list.pkl') > 0):
            # Ficheiro existe e nao esta vazio
            with open(username+'/list.pkl', 'rb') as f:
                file_list = pickle.load(f)
        else:
            file_list = []

        if option == 3:  # list
            if file_list:
                listar(connection)
            else:
                print 'Lista vazia!!!'
                connection.send('0')
            print 'fim'
        elif option == 4:
            if file_list:
                download(connection, username+'/')
            else:
                print 'Sem ficheiros para fazer download.'
                connection.send('0')
        elif option == 5:
            upload(connection, username+'/')
        connection.close()


if __name__ == '__main__':
    signal.signal(signal.SIGINT, sighandler)

    # Criar socket TCP
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Receber nome
    host = socket.gethostname()

    sock.bind((host, serverPort))
    sock.listen(2)

    if os.path.isfile('users.pkl') and (os.path.getsize('users.pkl') > 0):  #se o ficheiro existir tiver alguma coisa
        with open('users.pkl', 'rb') as input:
            users = pickle.load(input)

    while True:
        print "Server listening at port", serverPort, "..."
        connection, addr = sock.accept()
        operations(connection)
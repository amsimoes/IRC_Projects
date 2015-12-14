import sys
import signal
import os
import socket
import cPickle as pickle
import thread
import time

serverPort = 8000

users = {}  
file_list = []

DEBUG = True


def log(s):
    if DEBUG:
        print s


def sighandler(signal, frame):
    print '\nCTRL+C detected! Exiting Server...'
    sys.exit(0)


def upload(connection, userpath):
    global file_list
    print '\n** UPLOAD **\n'

    temp = connection.recv(128)
    temp = temp.splitlines()
    print '- Ficheiro a receber =', temp[0]

    file_name = temp[0]

    if file_list.count(file_name) == 0:
        print '- Ficheiro ainda nao existente'
        file_list.append(file_name)
        with open(userpath+'list.pkl', 'wb') as f:
            pickle.dump(file_list, f)
            print '- Ficheiro adicionado a lista'
    else:
        print '- Ficheiro ja presente no diretorio do user.'
        connection.send('0')
    file_name = userpath+file_name

    log('before send')
    connection.send('1')
    log('after send')

    f = open(file_name, 'wb')

    l = connection.recv(1024)
    tmp = l.splitlines()
    print 'tmp=', tmp
    while tmp[-1] != 'fim':
        f.write(l)
        l = connection.recv(1024)
        tmp = l.splitlines();
    log('after receive')

    f.close()

    print '\n** Fim upload **'

    return repr(0)


# Server -> Cliente
def download(connection, userpath):
    print '** DOWNLOAD **'

    temp = connection.recv(128)
    file_name = temp.splitlines()
    file_name = file_name[0]
    print 'Ficheiro pedido =', file_name
    file_name = userpath+'/'+file_name

    if os.path.isfile(file_name):   # Se ficheiro existir
        connection.send('1')

        f = open(file_name, 'rb')
        l = f.read(1024)
        while l:
            print 'a enviar!!!'
            connection.send(l)
            l = f.read(1024)
        f.close()
        connection.send('\n1')
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
        connection.send('0')    # confirm
    else:
        connection.send('1')    # confirm
        for i in range(len(file_list)):
            connection.send(file_list[i]+'\n')
        print 'Fim da listagem.\n'
        connection.send('1')  # enviado para marcar fim da lista


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
    print '\nA receber.........\n'
    tmp = connection.recv(128)
    if not tmp:
        print 'VAZIO.'
        return repr(0)
    tmp = tmp.splitlines()
    operation = eval(tmp[0])
    username = tmp[1]
    password = tmp[2]
    return operation, username, password


def receive_option(connection):
    log('A espera de receber opcao...')
    tmp = connection.recv(1)
    while not tmp:
        tmp = connection.recv(10)
    tmp = eval(repr(tmp))
    return tmp


def operations(connection, addr):
    print '\n# ----------------------------------------------------- #'
    print '# Cliente da maquina', addr[0],'ligado pela porta', addr[1],'!#'
    print '# ----------------------------------------------------- #\n'
    option, username, password = receive(connection)
    print 'Operacao recebida = ', option
    if option in [1, 2]:  # login/check if user exists
        confirm = login(option, username, password)
        print 'Confirm enviado =', confirm
        connection.send(repr(confirm))
        if confirm != 1:
            option = 2
    while option not in [0, 2, 6]:  # Login feito com sucesso
        log('AFTER LOGIN...')
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
        elif option == 4:
            if file_list:
                download(connection, username+'/')
            else:
                print 'Sem ficheiros para fazer download.'
                connection.send('0')
        elif option == 5:
            upload(connection, username+'/')
    print 'CLIENTE A TERMINAR...'
    print "..... Server listening at port", serverPort, "....."
    connection.close()
    sys.exit(0)


if __name__ == '__main__':
    signal.signal(signal.SIGINT, sighandler)

    # Criar socket TCP
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    host = socket.gethostname()

    sock.bind((host, serverPort))
    sock.listen(2)

    if os.path.isfile('users.pkl') and (os.path.getsize('users.pkl') > 0):  #se o ficheiro existir tiver alguma coisa
        with open('users.pkl', 'rb') as input:
            users = pickle.load(input)

    while True:
        print "..... Server listening at port", serverPort, "....."
        connection, addr = sock.accept()
        thread.start_new_thread(operations, tuple([connection,addr]))
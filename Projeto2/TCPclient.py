# usr/bin/env_python
# coding = utf-8

import sys
import os
import signal
import socket
import time

serverPort = 8000
cachePort = 8001


def sighandler(signal, frame):
    print '\nCTRL+C detected. Exiting client...'
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


def upload(sockfd, username, password):
    print '-- UPLOAD --\n'
    file_name = raw_input('Nome do ficheiro:')

    # Verificar se o ficheiro existe no diretorio
    if os.path.isfile(file_name) and (os.path.getsize(file_name) > 0):
        sockfd.send('5\n'+username+'\n'+password)
        sockfd.send(file_name+'\n')
        print 'file sent =', file_name

        sockfd.recv(1)

        f = open(file_name, 'rb')
        s = f.read(1024)
        while s:
            print 'Sending file...\n'
            sockfd.send(s)
            s = f.read(1024)
        print 'Sent\n'
        f.close()
    else:
        print 'Erro! Ficheiro vazio ou inexistente!\n'
    raw_input('\nPrima para voltar ao Menu Cliente.')


def download(sockfd, username, password):
    sockfd.send('4\n'+username+'\n'+password)

    tmp = eval(sockfd.recv(1))
    if tmp != 0:
        file_name = raw_input('Nome do ficheiro:')
        sockfd.send(file_name+'\n')

        with open(file_name, 'wb') as f:
            print 'File opened'
            data = sockfd.recv(1024)
            print "data =", data
            # write data to a file
            f.write(data)
        print 'Sucessfully got the file!'
    else:
        print '- ERRO DOWNLOAD -\nLista esta vazia.'
    raw_input('\nPrima para voltar ao Menu Cliente.')


def listar(sockfd, username, password):
    sockfd.send('3\n'+username+'\n'+password)
    tmp = sockfd.recv(1)
    confirm = eval(tmp)
    # print 'confirm recebido =', confirm
    if confirm == 0:
        print '-- LISTA VAZIA --'
    else:
        tmp = sockfd.recv(1024)
        tmp = tmp.splitlines()
        print '-- LISTA --'
        for i in range(0,len(tmp)-1):
            print 'Ficheiro',i+1,' =', tmp[i]
        while tmp[-1] != '1':
            tmp = sockfd.recv(1024)
            tmp = tmp.splitlines()
            print 'tmp =', tmp

    raw_input('\nPrima para voltar ao Menu Cliente.')


def user_menu(sockfd, port, username, password):
    option = 0
    while option != 4:
        # sockfd.send('0')
        os.system('clear')
        print '** MENU CLIENTE **'
        print '[1] LIST\n' \
              '[2] UPLOAD\n' \
              '[3] DOWNLOAD\n' \
              '[4] LOGOUT \n' \
              '[5] EXIT CLIENT'
        option = eval(raw_input('Escolha uma operacao: '))
        while not option or option not in [1, 2, 3, 4, 5]:
            option = eval(raw_input('Escolha invalida. Tente outra vez: '))

        os.system('clear')
        if option == 1:  # listar
            listar(sockfd, username, password)
        elif option == 2:
            upload(sockfd, username, password)
        elif option == 3:
            download(sockfd, username, password)
        elif option == 4:
            sockfd.send('6\n'+username+'\n'+password)
        elif option == 5:
            sockfd.send('0\nbye\nbye')
            # print 'EXITING...'
            sys.exit(0)


def login(sockfd, option, username, password):
    if option == 1:
        sockfd.send('1\n'+username+'\n'+password+'\n')
    elif option == 2:
        sockfd.send('2\n'+username+'\n'+password+'\n')

    confirm = eval(sockfd.recv(1))
    # print 'Confirm recebido = ', confirm

    if confirm == 0:
        if option == 2:
            print '\nUtilizador criado com sucesso!\n'
        else:
            print '\nUtilizador', username,'nao existente. Crie um.\n'
        raw_input('Pressione para voltar ao menu inicial.')
        return 1
    elif confirm == 2:
        if option == 1:
            print '\nErro! Password errada!\n'
        else:
            print '\nErro! Utilizador ja existente!\n'
        raw_input('Pressione para voltar ao menu inicial.')
        return 1
    elif confirm == 1:  # Login sucesso
        return user_menu(sockfd, serverPort, username, password)


def user(sockfd, option):
    username = raw_input('Nome do utilizador: ')
    while not username:
        username = raw_input('Nome vazio e invalido. Tente outra vez: ')
    password = raw_input('Password: ')
    while not password:
        password = raw_input('Password vazia e invalida. Tente outra vez: ')
    return login(sockfd, option, username, password)


def menu():
    while 1:
        os.system('clear')
        print '** MENU INICIAL **'
        print ('[1] - LOGIN\n[2] - Novo Utilizador\n[0] - EXIT')
        option = eval(raw_input("Escolha uma das opcoes: "))
        while option not in [0, 1, 2]:
            option = eval(raw_input('Erro. Escolha uma das opcoes anteriores: '))
        os.system('clear')

        if option == 0:
            print 'EXITING...'
            sys.exit(0)

        sockfd = createsocket(serverPort)

        if option == 1:
            print '   ** LOGIN **'
            option = user(sockfd, 1)
            sockfd.close()
        elif option == 2:   # NEW USER
            print '** NOVO Utilizador **'
            option = user(sockfd, 2)
            sockfd.close()


if __name__ == '__main__':
    signal.signal(signal.SIGINT, sighandler)
    print 'Bem vindo ao cliente!'
    menu()

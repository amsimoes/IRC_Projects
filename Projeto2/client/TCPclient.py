import sys
import os
import socket


serverPort = 8000
cachePort = 8001

DEBUG = False

def log(s):
    if DEBUG:
        print s


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
    file_name = raw_input('Nome do ficheiro: ')

    # Verificar se o ficheiro existe no diretorio
    if os.path.isfile(file_name) and (os.path.getsize(file_name) > 0):
        sockfd.send('5\n'+username+'\n'+password)
        sockfd.send(file_name+'\n')
        print 'file sent =', file_name

        confirm = sockfd.recv(1)

        if confirm == '0':
            log('Ficheiro ja existente no servidor.')

        f = open(file_name, 'rb')
        s = f.read(1024)
        print s
        while s:
            log('Sending file...')
            sockfd.send(s)
            log('sent!!')
            s = f.read(1024)
        sockfd.send('\nfim')
        print 'Sent\n'
        
        f.close()
    else:
        'Erro! Ficheiro vazio ou inexistente!\n'
    raw_input('\nPrima para voltar ao Menu Cliente.')


def download(sockfd, username, password):
    print '-- DOWNLOAD --'
    sockfd.send('4\n'+username+'\n'+password)

    file_name = raw_input('Nome do ficheiro: ')
    sockfd.send(file_name+'\n')

    tmp = eval(sockfd.recv(1))
    if tmp != 0:
        with open(file_name, 'wb') as f:
            log('File opened')
            data = sockfd.recv(1024)
            tmp = data.splitlines()
            f.write(tmp[0])
            while tmp[-1] != '1':
                log('Inside download write!!')
                f.write(data)
                data = sockfd.recv(1024)
                tmp = data.splitlines()
            # write data to a file
        print 'Sucessfully got the file!'
    else:
        print '- ERRO DOWNLOAD -\nFicheiro inexistente.'
    raw_input('\nPrima para voltar ao Menu Cliente.')


def listar(sockfd, username, password):
    log('A enviar operacao...')
    sockfd.send('3\n'+username+'\n'+password)
    log('A espera de confirm...')
    tmp = sockfd.recv(1)

    while not tmp:
        tmp = sockfd.recv(1)

    confirm = eval(tmp)
    

    if confirm == 0:
        print '-- LISTA VAZIA --'
    elif confirm == 1:
        tmp = sockfd.recv(1024)
        lista = tmp
        temp = tmp.splitlines()
        print temp

        while temp[-1] != '1':
            tmp = sockfd.recv(1024)
            lista += tmp
            temp = tmp.splitlines()

        tmp = lista.splitlines()
        print '-- LISTA --'
        for i in range(0,len(tmp)-1):
            print 'Ficheiro',i+1,' =', tmp[i]


    raw_input('\nPrima para voltar ao Menu Cliente.')
    return confirm


# OPERACOES CACHE APENAS
def user_menu(sockfd, username, password):
    option = 0
    vazia = 1
    while option != 4:
        os.system('clear')
        print '** MENU CLIENTE **'
        print '[1] LIST\n' \
              '[2] UPLOAD\n' \
              '[3] DOWNLOAD\n' \
              '[4] BACK \n' \
              '[5] QUIT CLIENT'
        option = eval(raw_input('Escolha uma operacao: '))
        while option not in [1, 2, 3, 4, 5]:
            option = eval(raw_input('Escolha invalida. Tente outra vez: '))

        os.system('clear')
        if option == 1:  # listar
            vazia = listar(sockfd, username, password)
        elif option == 2:
            upload(sockfd, username, password)
        elif option == 3:
            if vazia == 1:
                download(sockfd, username, password)
            else:
                print 'Lista vazia. Impossivel fazer download.'
                raw_input('\nPrima para voltar ao Menu Cliente.')
        elif option == 4:
            sockfd.send('6\n'+username+'\n'+password)
        elif option == 5:
            sockfd.send('6\nbye\nbye')
            sys.exit(0)


def login(sockfd, option, username, password):
    if option == 1:
        sockfd.send('1\n'+username+'\n'+password)
    elif option == 2:
        sockfd.send('2\n'+username+'\n'+password)

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
        return user_menu(sockfd, username, password)


def user(sockfd, option):
    username = raw_input('Nome do utilizador: ')
    while not username or username == 'default':
        username = raw_input('Nome vazio ou invalido. Tente outra vez: ')
    password = raw_input('Password: ')
    while not password:
        password = raw_input('Password vazia e invalida. Tente outra vez: ')
    return login(sockfd, option, username, password)


def menu():
    option = 1
    while option != 0:
        os.system('clear')
        print '** MENU INICIAL **'
        print ('[1] - LOGIN\n[2] - Novo Utilizador\n[3] - Guest\n[0] - EXIT')
        option = eval(raw_input("Escolha uma das opcoes: "))
        while option not in [0, 1, 2, 3]:
            option = eval(raw_input('Erro. Escolha uma das opcoes anteriores: '))
        os.system('clear')

        if option == 1:
            sockfd = createsocket(serverPort)
            print '   ** LOGIN **'
            option = user(sockfd, 1)
            sockfd.close()
        elif option == 2:   # NEW USER
            sockfd = createsocket(serverPort)
            print '** NOVO Utilizador **'
            option = user(sockfd, 2)
            sockfd.close()
        elif option == 3:
            sock_cache = createsocket(cachePort)
            sock_cache.send('1\ndefault\ndefault')
            user_menu(sock_cache, 'default', 'default')


if __name__ == '__main__':
    print 'Bem vindo ao cliente!'
    menu()
    print 'Bye-bye!'
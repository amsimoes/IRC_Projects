/*******************************************************************
* SERVIDOR no porto 9000, à escuta de novos clientes. Quando surjem
* novos clientes os dados por eles enviados são lidos e descarregados no ecran.
*******************************************************************/
#include <sys/socket.h>
#include <sys/types.h>
#include <netinet/in.h>
#include <unistd.h>
#include <stdlib.h>
#include <stdio.h>
#include <netdb.h>
#include <string.h>

#define SERVER_PORT 9000
#define BUF_SIZE 1024

void process_client(int fd);
void erro(char *msg);

int main(int argc, char* argv[]) {
	int fd, client;
	struct sockaddr_in addr, client_addr;
	int client_addr_size;

	if(argc != 2) {
		printf("Erro! Usage: ./main <port>\n");
		exit(1);
	}

	bzero((void *) &addr, sizeof(addr));
	addr.sin_family = AF_INET;
	addr.sin_addr.s_addr = htonl(INADDR_ANY);
	addr.sin_port = htons((short) atoi(argv[1]));

	if ( (fd = socket(AF_INET, SOCK_STREAM, 0)) < 0)
		erro("Funcao socket");
	if ( bind(fd,(struct sockaddr*)&addr,sizeof(addr)) < 0)
		erro("Funcao bind");
	if( listen(fd, 5) < 0)
		erro("Funcao listen");

	while (1) {
		printf("\n-- A espera de mensagem --\n");

		client_addr_size = sizeof(client_addr);
		client = accept(fd,(struct sockaddr *)&client_addr,&client_addr_size);

		printf("\nLigacao aceite!\n");
		if (client > 0) {
			if (fork() == 0) {
				close(fd);
				process_client(client);
				exit(0);
			} else {
				wait(NULL);
			}
			close(client);
		}
	}
	return 0;
}

void process_client(int client_fd) {
	int nread = 0, i = 0, j = 0;
	char buffer[BUF_SIZE];
	char aux[BUF_SIZE];
	
	nread = read(client_fd, buffer, BUF_SIZE-1);
	buffer[nread] = '\0';

	printf("\nMensagem recebida = %s\n", buffer);
	fflush(stdout);
	
	while(buffer[i]!='\0'){
	    if(buffer[i]!='a'&& buffer[i]!='e'&& buffer[i]!='i'&& buffer[i]!='o'&& buffer[i]!='u'&& buffer[i]!='A' && buffer[i]!='E' && buffer[i]!='I'&& buffer[i]!='O'&& buffer[i]!='U'){
			aux[j]=buffer[i];
			j++;
	    }
	    i++;	
  	}
  	aux[j] = '\0';

  	strcpy(buffer, aux);
	printf("Mensagem enviada = %s\n", buffer);
	fflush(stdout);

	write(client_fd, buffer, 1 + strlen(buffer));
	
	close(client_fd);
}

void erro(char *msg) {
	perror(msg);
	exit(-1);
}
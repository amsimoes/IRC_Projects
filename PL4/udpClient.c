#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <arpa/inet.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <netinet/in.h>
#include <unistd.h>
#include <netdb.h>

#define BUFLEN 512	// Tamanho do buffer
#define PORT 9875

void erro(char *s) {
	perror(s);
	exit(1);
}

// Usage: ./cliente <IP Servidor> <porto> <mensagem>
int main(int argc, char *argv[]){
	struct sockaddr_in si_minha, si_outra;
	char endServer[100];
	int s,recv_len;

	struct hostent *hostPtr;
	socklen_t slen = sizeof(si_minha);
	char buf[BUFLEN];

	if(argc != 4) {
		printf("Erro.\nUsage: ./cliente <IP Servidor> <porto> <mensagem>\n");
		exit(1);
	}

	// Servidor
	strcpy(endServer, argv[1]);
    if ((hostPtr = gethostbyname(endServer)) == 0)
 		erro("Nao consegui obter endereço");
	
	// Mensagem
	strcpy(buf,argv[3]);

	// Cria um socket para recepção de pacotes UDP
	if((s=socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)) == -1) {
		erro("Erro na criação do socket");
	}
	
	si_minha.sin_family = AF_INET;
	si_minha.sin_port = htons(PORT);
	si_minha.sin_addr.s_addr = htonl(INADDR_ANY);
	
	si_outra.sin_family = AF_INET;
	si_outra.sin_port = htons(atoi(argv[2]));
	si_outra.sin_addr.s_addr = ((struct in_addr *)(hostPtr->h_addr))->s_addr;
	
	// Envio de mensagem
	if(sendto(s, buf, BUFLEN, 0, (struct sockaddr *) &si_minha, slen) == -1) {
		erro("Erro no sendto");
	}

	printf("Mensagem enviada: %s\n" , buf);

	// Fecha socket e termina programa
	close(s);
	return 0;
}
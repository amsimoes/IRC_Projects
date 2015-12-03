#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <arpa/inet.h>
#include <sys/socket.h>
#include <unistd.h>

#define BUFLEN 512	// Tamanho do buffer
//#define PORT 23000	// Porto para recepção das mensagens

void erro(char *s) {
	perror(s);
	exit(1);
}

int main(int argc, char* argv[]) {
	struct sockaddr_in si_minha, si_outra;
	int s,recv_len;
	socklen_t slen = sizeof(si_outra);
	char buf[BUFLEN];
	
	if(argc != 2) {
		printf("Erro! Usage: ./server <PORT>\n");
		exit(1);
	}

	// Cria um socket para recepção de pacotes UDP
	if((s = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)) == -1) {
		erro("Erro na criação do socket");
	}

	si_minha.sin_family = AF_INET;
	si_minha.sin_port = htons(atoi(argv[1]));
	si_minha.sin_addr.s_addr = htonl(INADDR_ANY);
	
	// Associa o socket à informação de endereço
	if(bind(s,(struct sockaddr*)&si_minha, sizeof(si_outra)) == -1) {
		erro("Erro no bind");
	}

	while(1) {
		printf("\n\n -- A espera de receber mensagem na porta %d --\n", atoi(argv[1]));

		// Espera recepção de mensagem (a chamada é bloqueante)
		if((recv_len = recvfrom(s, buf, BUFLEN, 0, (struct sockaddr *) &si_outra, &slen)) == -1) {
			erro("Erro no recvfrom");
		}

		// Para ignorar o restante conteúdo (anterior do buffer)
		buf[recv_len]='\0';
			
		printf("\nRecebi uma mensagem do sistema com o endereço %s e o porto %d.\n", inet_ntoa(si_outra.sin_addr), ntohs(si_outra.sin_port));
		printf("Mensagem recebida: %s\n" , buf);
	}

	// Fecha socket e termina programa
	close(s);

	return 0;
}

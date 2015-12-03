#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>

#define SIZE 50

int main() {
	char msg1[SIZE], msg2[SIZE], msg3[SIZE];
	char buffer[SIZE];

	int pai_filho[2];	// [1] -> ESCRITA || [0] -> LEITURA
	int filho_pai[2];

	pid_t childpid;

	if(pipe(pai_filho) == 0 && pipe(filho_pai) == 0) {
		if ((childpid = fork()) == 0) {
			close(filho_pai[0]);
			sprintf(msg2, "Ola pai o meu pid é %d", getpid());
			write(filho_pai[1], msg2, sizeof(msg2));
			//waitpid(dadpid, NULL, 0);
			close(filho_pai[1]);
			close(pai_filho[1]);
			read(pai_filho[0], buffer, sizeof(buffer));
			printf("[FILHO] Recebido do pai = %s\n", buffer);
			printf("[FILHO] Pid do pai = %d\n", getppid());
			sprintf(msg3, "%d", getppid());
			if(strcmp(msg3,buffer) != 0) {
				printf("Erro: PID recebido nao corresponde ao pid do pai!\n");
				return 1;
			}
			close(pai_filho[0]);
		} else {
			waitpid(childpid, NULL, 0);
			printf("[PAI] INIT\n");
			close(pai_filho[0]);
			sprintf(msg1, "%d", getpid());
			write(pai_filho[1], msg1, sizeof(msg1));
			close(pai_filho[1]);
			close(filho_pai[1]);
			read(filho_pai[0], buffer, sizeof(buffer));
			printf("[PAI] Recebido do filho = %s\n", buffer);
			close(filho_pai[0]);
		}
	}

	return 0;
}
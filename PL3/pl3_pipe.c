#include <stdio.h>
#include <sys/types.h>

int main() {
	pid_t childpid;

	if((childpid = fork()) == -1) {
		fprintf(stderr, "Erro na criação do filho!\n");
	} else if (childpid == 0) {
		printf("Eu sou o processo filho, o meu pid é %d e o pid do meu pai é %d.\n", getpid(), getppid());
	} else {
		printf("Eu sou o processo pai e o meu pid é %d.\n", getpid());
	}


	return 0;
}
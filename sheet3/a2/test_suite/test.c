#include <stdio.h>
#include <unistd.h>

#include <stdlib.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>

int main () {
	char c;
	printf("puts is wrapped everytime I call printf ;)\n");

	// open and write test
	printf("### open and write test ###\n");
	int fd = open("test_suite/dont_read.txt", O_CREAT, O_RDWR);
	if(fd != -1) {
		write(fd, "write wrapping test\n", 20);
		close(fd);
	}
	else
		printf("[main] Error in open.\n");

	// openat and read test
	printf("### openat and read test ###\n");
	int fd2 = openat(AT_FDCWD, "test_suite/dont_read2.txt", O_CREAT, O_RDWR);
	if(fd2) {
		read(fd2, &c, 1);
		write(0, &c, 1);
		close(fd2);
	}

	// fopen, fprintf (fwrite) and fread test
	printf("### fopen and fprint (fwrite) test ###\n");
	FILE * fp = fopen("build/fopen_test.txt", "wr+");
	if(fp) {
		fprintf(fp, "fprint wrapping test");
		fread(&c, 1, 1, fp);
		fclose(fp);
	}

	return(0);
}
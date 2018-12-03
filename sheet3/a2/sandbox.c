#define _GNU_SOURCE
#include <dlfcn.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

/* Function pointers to hold the value of the glibc functions */
static int (*real_open)(const char *pathname, int flags) = NULL;
static int (*real_openat)(int dirfd, const char *pathname, int flags) = NULL;
static FILE *(*real_fopen)(const char*, const char*) = NULL;
static ssize_t (*real_write)(int fd, const void *buf, size_t count) = NULL;
static size_t (*real_fwrite)(const void *ptr, size_t size, size_t nmemb, FILE *stream) = NULL;
static ssize_t (*real_read)(int fd, void *buf, size_t count) = NULL;
static size_t (*real_fread)(void *ptr, size_t size, size_t nmemb, FILE *stream) = NULL;

int inBlacklist(const char * pathname) {
    FILE *blacklist;
    char *line = NULL;
    size_t len = 0;
    ssize_t read;

    real_fopen = dlsym(RTLD_NEXT, "fopen");
    blacklist = real_fopen("blacklist.txt", "r");

    if(blacklist) {
        while ((read = getline(&line, &len, blacklist)) != -1) {
            if (line[read-1] == '\n')
               line[read-1] = '\0';

            if(strcmp(line, pathname) == 0)
                return 1;
        }

        fclose(blacklist);
        
        if (line)
            free(line);
    }

    return 0;
}

void fdPathname(int fd, char **pathname) {
    /* Misuse of strcat, strcpy and sprintf are the heart of 
       unstable/insecure software ;) let's use them! */

    int len;
    char fd_s[10];
    char *path = malloc(100);

    /* Finds the path to file descriptor */
    char *str = "/proc/self/fd/";
    sprintf(fd_s, "%d", fd);
    strcpy(path, str);
    strcat(path, fd_s);

    /* Finds the path to the file itself */
    if ((len = readlink(path, *pathname, 255)) != -1)
        (*pathname)[len] = '\0';
    else {
        *pathname = NULL;
        printf("[sandbox] ERROR: Couldn't find file name to file descriptor: %d\n", fd);
    }
}

/** OPEN family **/

int open(const char *pathname, int flags, ...) {
    char *absolute_pathname = malloc(256);
    realpath(pathname, absolute_pathname);

    if(inBlacklist(absolute_pathname)) {
        printf("[sandbox] ERROR in open: File belongs to blacklist: %s\n", pathname);
        return 0;
    }
    
    real_open = dlsym(RTLD_NEXT, "open");
    return real_open(pathname, flags);
}

int openat(int dirfd, const char *pathname, int flags, ...) {
    char *absolute_pathname = malloc(256);
    realpath(pathname, absolute_pathname);

    if(inBlacklist(absolute_pathname)) {
        printf("[sandbox] ERROR in openat: File belongs to blacklist: %s\n", pathname);
        return 0;
    }

    real_openat = dlsym(RTLD_NEXT, "openat");
    return real_openat(dirfd, pathname, flags);
}

FILE *fopen(const char *pathname, const char *mode) {
    char *absolute_pathname = malloc(256);
    realpath(pathname, absolute_pathname);

    if(inBlacklist(absolute_pathname)) {
        printf("[sandbox] ERROR in fopen: File belongs to blacklist: %s\n", pathname);
        return 0;
    }

    real_fopen = dlsym(RTLD_NEXT, "fopen");
    return real_fopen(pathname, mode);
}

/** WRITE family **/

ssize_t write(int fd, const void *buf, size_t count) {
    /* Finds the absolute file path */
    char *pathname = malloc(256);
    fdPathname(fd, &pathname);

    if(pathname)
        if(inBlacklist(pathname)) {
            printf("[sandbox] ERROR in write: File belongs to blacklist: %s\n", pathname);
            return 0;
        }

    real_write = dlsym(RTLD_NEXT, "write");
    return real_write(fd, buf, count);
}

size_t fwrite(const void *ptr, size_t size, size_t nmemb, FILE *stream) {
    /* Finds the absolute file path */
    int fd = fileno(stream);
    char *pathname = malloc(256);
    fdPathname(fd, &pathname);

    if(pathname)
        if(inBlacklist(pathname)) {
            printf("[sandbox] ERROR in fwrite: File belongs to blacklist: %s\n", pathname);
            return 0;
        }

    real_fwrite = dlsym(RTLD_NEXT, "fwrite");
    return real_fwrite(ptr, size, nmemb, stream);
}

/** READ family **/

ssize_t read(int fd, void *buf, size_t count) {
    /* Finds the absolute file path */
    char *pathname = malloc(256);
    fdPathname(fd, &pathname);

    if(pathname)
        if(inBlacklist(pathname)) {
            printf("[sandbox] ERROR in read: File belongs to blacklist: %s\n", pathname);
            return 0;
        }

    real_read = dlsym(RTLD_NEXT, "read");
    return real_read(fd, buf, count);
}

size_t fread(void *ptr, size_t size, size_t nmemb, FILE *stream) {
    /* Finds the absolute file path */
    int fd = fileno(stream);
    char *pathname = malloc(256);
    fdPathname(fd, &pathname);

    if(pathname)
        if(inBlacklist(pathname)) {
            printf("[sandbox] ERROR in fread: File belongs to blacklist: %s\n", pathname);
            return 0;
        }

    real_fread = dlsym(RTLD_NEXT, "fread");
    return real_fread(ptr, size, nmemb, stream);
}
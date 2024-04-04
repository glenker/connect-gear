#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

int main(int argc, char **argv) {
  char buf[10];
  read(0, buf, 11);
  exit(0);
}

#include <stdio.h>
#include <string.h>

int main (int argc, char **argv) {
  char cmdline[4096];
  cmdline[0] = '\0';

  for(int i = 1; i < argc; ++i) {
    strcat (cmdline, argv[i]);
    strcat (cmdline, " ");
  }
  //
  printf("cmdline: %s\n", cmdline);
  return 0;
}

#!/usr/bin/env python3
import sys, re
import subprocess

BLOCKSIZE = 0x1000


def create_cmd(cmd):
     return ["adb", "shell", "su -c '{}'".format(cmd)]

def dump_memory(pid):
     cmd = create_cmd("cat /proc/{}/maps".format(pid))
     memlayout = subprocess.check_output(cmd).decode("utf-8")
     print(memlayout)

     with open('dump.bin', 'wb') as fp:
          # for each mapped region
          dump = b""
          for line in memlayout.strip().split('\n'):
               m = re.match(r'([0-9A-Fa-f]+)-([0-9A-Fa-f]+) ([-r])', line)

               # only consider readable regions
               if m.group(3) != 'r': continue
               print(line)

               start = int(m.group(1), 16)
               end = int(m.group(2), 16)
               size = end - start
               assert start % BLOCKSIZE == 0
               assert size % BLOCKSIZE == 0

               cmd = create_cmd('dd bs={} skip={} count={} if=/proc/{}/mem'.format(BLOCKSIZE, start // BLOCKSIZE, size // BLOCKSIZE, pid))
               output = subprocess.check_output(cmd)
               fp.write(output)



def main():
     if len(sys.argv) != 2:
          print("Usage: {} pid", sys.argv[0])
          quit(1)

     try:
          pid = int(sys.argv[1])
          dump_memory(pid)
     except ValueError:
          print("pid must be a number")

if __name__ == "__main__":
     main()


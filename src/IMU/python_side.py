import sys
from subprocess import *


proc = Popen('./SAUVC' , bufsize=1024 ,stdin =PIPE ,stdout = PIPE)

while True:
     print(proc.stdout.readline())




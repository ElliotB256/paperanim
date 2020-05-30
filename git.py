# -*- coding: utf-8 -*-
import subprocess

p = subprocess.Popen("git log --pretty=\"%h\"", shell=True, stdout=subprocess.PIPE)
for line in p.stdout.readlines():
    print(line)
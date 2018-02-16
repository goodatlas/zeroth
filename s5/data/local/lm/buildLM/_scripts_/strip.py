#!/usr/bin/env python3
import fileinput
import re

for line in fileinput.input():
    if not line.strip():
        continue
    tline = re.sub(r'(\ )+', ' ', line).strip()
    print(tline)

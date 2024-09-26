
import sys

while True:
    command = sys.stdin.readline().strip()
    if command == 'players':
        print('success!')
    else:
        print('another?')
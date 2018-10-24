from enum import Enum
import copy
import sortedcontainers

stack = []


# deep copy wrapper for recursive copy dynamic structures (recursive nodes, trees, etc)
def copy_instance(obj):
    return copy.deepcopy(obj)


class Incrementor:
    def __init__(self, state=0):
        self.state = state

    def inc(self, step=1):
        self.state += step
        return self.state


class FileMode(Enum):
    ORDONLY = 0,
    OWRONLY = 1,
    ORDWR = 2,
    O_CLONEXEC = 0,
    O_CREAT = 400,
    O_EXCL = 2000,
    O_TRUNC = 1000,
    O_APPEND = 10,
    O_SYNC = 20


Common_container = sortedcontainers.SortedList

SG_container = sortedcontainers.SortedDict


def normalize_str(line):
    for idx in range(len(line) - 1):
        if ((line[idx]).isdigit() and line[idx + 1] == '[') or ((line[idx]).isdigit() and line[idx + 1] == ']') or (
                line[idx] == '[' and line[idx + 1] == ']') or ((line[idx + 1]).isdigit() and line[idx] == '[') or (
                (line[idx + 1]).isdigit() and line[idx] == ']') or (line[idx] == ']' and line[idx + 1] == ']') or \
                (line[idx] == ']' and line[idx + 1].isdigit()) or (line[idx].isdigit() and line[idx + 1] == '['):
            line = line[:idx+1] + ' ' + line[idx+1:]
    return line


def test():
    s = SG_container()
    s[1] = sortedcontainers.SortedDict()
    s[1] = 1
    if 1 not in s.keys():
        print('False')
    print(s.keys())


test()

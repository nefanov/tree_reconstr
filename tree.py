from pytz import timezone
import pytz

from atriact import *
from stuff import Incrementor

default_inc = Incrementor()


class Node:
    def __init__(self, data=(None, None, None, []), parent=None, visited=False):
        self.visited = visited
        self.parent = parent
        self.children = [] #list of dependencies - contains nodes, because of Python's binding feature
        self.I = Inh()
        self.S = Synth()
        self.index = default_inc.inc()
        (self.I.ptr, self.I.names, self.I.act, self.S.num) = data  # attributes
        self.deps = []  #list of dependencies - contains nodes, because of Python's binding feature

    def add_child(self, child):
        child.parent = self
        self.children.append(child)
        return self

    def set_parent(self, parent):
        self.parent = parent
        return self

    def __repr__(self):
        print('Current node:', self.index)

    def delete_child(self, index=None, sig=None):  # delete the state;
        if not index:
            if not sig:
                self.children.__delitem__(-1)
            else:
                pass
        else:
            for i,o in enumerate(self.children):
                if o.index == index:
                    del self.children[i]
        return self.children

    # deps routines

    def add_dep(self, dep):
        self.deps.append(dep)
        return self
    # search routines

    # Облегчённая имплементация обхода в глубину (SEC(R)-2018)
    # recursive 1d-dfs: в каждой вершине запускается функция action, возвращающая статус и состояние вершины
    # если статуc==True, процедура обхода завершается.
    # задача: обобщить процедуру (написать свою) для n-местных проверок, построения графа зависимостей и т.д.
    def dfs(self, action=action_check_attr, **kwargs):
        tracer = False # т
        current = self
        
        chk, current = action(current, **kwargs)
        # frame-pointer mode is excluded from code for more compactivity.
        try:
            for en, node in enumerate(current.children):
                try:
                    (chk, crnt) = node.dfs(action, **kwargs) # run this routine for each of children
                except Exception as e:
                    print("Exception during the inner traversal in subtree from node #:", node.index, e)
                    pass

                if chk:
                    return chk, crnt
        except Exception as e:
            print("Exception in node #", current.index, e)

        return chk, current  # ret from recursion

    # upward branch checking from current node to some global root - проход вверх, необходимый для "сквозного" восстановления наследования от предыдущих состояний процессов
    def upbranch(self, action=action_check_attr, **kwargs):
        chk, current = False, self
        while current != None:
            chk, current = action(current, **kwargs)
            if chk:
                break
            current = current.parent
        return chk, current

    #обход, возвращающий список вершин, в которых выполнились некоторые налагаемые на обход условия
    #позволяет свести проверку n-атрибутов от условного O(N^n) к O(N^2), где N-число вершин в проверяемом дереве.
    #inprogress
    def n_dfs(self, action=action_check_attr, **kwargs):
        tracer = False  # т
        current = self

        chk, current = action(current, **kwargs)
        # frame-pointer mode is excluded from code for more compactivity.
        try:
            for en, node in enumerate(current.children):
                try:
                    (chk, crnt) = node.dfs(action, **kwargs)  # run this routine for each of children
                except Exception as e:
                    print("Exception during the inner traversal in subtree from node #:", node.index, e)
                    pass

                if chk == True:
                    return chk, crnt
        except Exception as e:
            print("Exception in node #", current.index, e)

        return chk, current  # ret from recursion

# DFS routine to make dotfile from linked Node objects;
# usage: pass dotfile fileobj via kwargs
def make_dot(current=Node(), **kwargs):
    fileobj = kwargs.get('dotfile', None)
    if not fileobj:
        print('open a file previously!')
        return False, current

    label=''
    edge_labled = kwargs.get('edge_labels', False)

    for child in current.children:
        if edge_labled:
            label = "[label=" + str(child.I.act)+']'
        s = '\t"'+str(current.S.num).replace('[]', '').replace('[', '').replace(']', '') + '" -> ' +\
            '"'+str(child.S.num).replace('[]', '').replace('[', '').replace(']', '') + '"'+label+';\n'
        # and don't forget the 'labeltooltip'- it's useful graphic primitive too
        fileobj.write(s)

    return False, current


def print_dot(fname, root, head="PSTREE", edge_labels=False):
    fileobj = open(fname, 'w')
    fileobj.write("digraph "+head+' {\n')
    root.dfs(make_dot, dotfile=fileobj, edge_labels=edge_labels)
    fileobj.write("}")
    fileobj.close()
    return


def unittest():
    dummy = [1, 2, 3, 4, [], [], [], []]
    dummy2 = [5, 6, 7, 8, [], [], [], []]
    dummy3 = [9, 10, 11, 12, [], [], [], []]

    t = Node(data=(None, {'p': 0,
                                       'g': 1,
                                       's': 2,
                                       'pp': 3,
                                       'socket': 4,
                                       'pipe': 5,
                                       'fifo': 6,
                                       'files': 7}, None, dummy))
    t.add_child(Node(data=(None, {'p': 0,
                                       'g': 1,
                                       's': 2,
                                       'pp': 3,
                                       'socket': 4,
                                       'pipe': 5,
                                       'fifo': 6,
                                       'files': 7}, None, dummy2)))
    t.add_child(Node(data=(None, {'p': 0,
                                  'g': 1,
                                  's': 2,
                                  'pp': 3,
                                  'socket': 4,
                                  'pipe': 5,
                                  'fifo': 6,
                                  'files': 7}, None, dummy3)))
    print(t.S.num)
    print(t.children[1].S.num)
    print(id(t.children), id(t.children[1].children))


if __name__ == '__main__':
    unittest()

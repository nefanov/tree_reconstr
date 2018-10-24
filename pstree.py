# self-made procfs python API for process-tree getting
# supports pid, setsid, setpgid, hierarchy, file descriptors/info

# see into splitting different procfs API
import psutil
import collections
import sys
import os
import glob
import pickle
from stuff import Common_container, SG_container
from tree import *
from atriact import *
import datetime

sys.setrecursionlimit(100000)
_base_path = os.getcwd()
parentdir_of_file = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(parentdir_of_file)


# construct tree with attributes recursively
def construct_tree(node, tree, indent='  ', output_dir='./', permanent=False, filler=False, fill_struct=None,
                   fs=False, use_cache=False, **kwargs):
    pgid = sid = pid = 1
    fds = []
    try:
        name = psutil.Process(node).name()
        pgid = os.getpgid(psutil.Process(node).pid)
        pid = psutil.Process(node).pid
        sid = os.getsid(psutil.Process(node).pid)
        fds = []  # list of results from file descriptors
        if fs:
            fd_procfs = glob.glob('/proc/' + str(psutil.Process(node).pid) + '/fd/*')
            for line in fd_procfs:
                try:
                    with open('/proc/' + str(psutil.Process(node).pid) + '/fdinfo/' + line.split('/')[-1], 'rt+') as finfo:
                        liner = False
                        for l in finfo:
                            if l.split(':')[0] == 'flags':
                                val = l.replace(':', ' ').replace('\t', ' ').split(' ')[-1].replace('\n', '')
                                fds.append({os.path.realpath(line): val})
                                liner = True
                        if liner == False:
                            fds.append({os.path.realpath(line): 'n/a'})

                except Exception as e:
                    print(e)
                    fds.append({os.path.realpath(line): 'n/a'})

    except psutil.Error:
        name = "?"
#    print(name, node, sid, pgid)

    # write additional resources , like fds, into fs
    if fs:
        if permanent:
            if not os.path.exists(output_dir + str(pid)):
                os.makedirs(output_dir + str(pid))
            files = open(output_dir + str(pid) + '/files.pstree', 'w+')
            sockets = open(output_dir + str(pid) + '/sockets.pstree', 'w+')
            pipes = open(output_dir + str(pid) + '/pipes.pstree', 'w+')
            fifos = open(output_dir + str(pid) + '/fifos.pstree', 'w+')

            for it in fds:
                for k, v in it.items():
                    if 'socket' in k.replace(':', ' ').replace('[', ' ').replace(']', ' ').split(' '):
                        sockets.write('{}_-_{}\n'.format(k, v))
                    elif 'pipe' in k.replace(':', ' ').replace('[', ' ').replace(']', ' ').split(' '):
                        pipes.write('{}_-_{}\n'.format(k, v))
                    elif 'fifo' in k.replace(':', ' ').replace('[', ' ').replace(']', ' ').split(' '):
                        fifos.write('{}_-_{}\n'.format(k, v))
                    else:
                        files.write('{}_-_{}\n'.format(k, v))
            files.close()
            sockets.close()
            pipes.close()
            fifos.close()



    if fill_struct and filler:
        fill_struct.S.num[fill_struct.I.names['p']] = pid
        fill_struct.S.num[fill_struct.I.names['g']] = pgid
        fill_struct.S.num[fill_struct.I.names['s']] = sid
        try:
            fill_struct.S[fill_struct.I.names['pp']] = psutil.Process(node).ppid()
        except:
            fill_struct.S[fill_struct.I.names['pp']] = 0

        for it in fds:
            for k, v in it.items():
                if 'socket' in k.replace(':', ' ').replace('[', ' ').replace(']', ' ').split(' '):
                    fill_struct.S.num[fill_struct.I.names['socket']].append({k, v})
                elif 'pipe' in k.replace(':', ' ').replace('[', ' ').replace(']', ' ').split(' '):
                    fill_struct.S.num[fill_struct.I.names['pipe']].append({k, v})
                elif 'fifo' in k.replace(':', ' ').replace('[', ' ').replace(']', ' ').split(' '):
                    fill_struct.S.num[fill_struct.I.names['fifo']].append({k, v})
                else:
                    fill_struct.S.num[fill_struct.I.names['files']].append({k, v})

        if use_cache:
            if not kwargs['P_container']:
                kwargs['P_container'] = Common_container()
            if not kwargs['SPG_container']:
                kwargs['SPG_container'] = SG_container()
            kwargs['P_container'].add(pid)
            if sid not in kwargs['SPG_container'].keys():
                kwargs['SPG_container'][sid] = Common_container
            kwargs['SPG_container'][sid].add(pgid)

    children = tree[node]

    if node not in tree:
        print('ret as disjoint!')
        return fill_struct

    for cnt, child in enumerate(children):
        name = psutil.Process(child).name()
        pgid = os.getpgid(psutil.Process(child).pid)
        pid = psutil.Process(child).pid
        sid = os.getsid(psutil.Process(child).pid)
        dummy = [pid, pgid, sid, psutil.Process(child).ppid(), [], [], [], []]
        node_entry = Node(data=(None, {'p': 0,
                                       'g': 1,
                                       's': 2,
                                       'pp': 3,
                                       'socket': 4,
                                       'pipe': 5,
                                       'fifo': 6,
                                       'files': 7}, None, dummy))

        fill_struct.add_child(node_entry)
        construct_tree(child, tree, indent + '| ', output_dir, permanent, filler, node_entry, use_cache, **kwargs)

    return fill_struct

# make pstree as data structure
# now this is a dict of lists: 'ppid': [pids]
def get_pstree(use_cache=False, permanent=False, fpath='res_pstree', save_tree_fmt='linear',**kwargs):
    tree = collections.defaultdict(list)
    for p in psutil.process_iter():
        try:
            tree[p.ppid()].append(p.pid)
        except (psutil.NoSuchProcess, psutil.ZombieProcess):
            pass
    # on systems supporting PID 0 (kernel PID), PID 0's parent is usually 0
    if 0 in tree and 0 in tree[0]:
        tree[0].remove(0)

    dummy = [None, None, None, None, [], [], [], []]
    root = Node(data=(None, {'p': 0,
                             'g': 1,
                             's': 2,
                             'pp': 3,
                             'socket': 4,
                             'pipe': 5,
                             'fifo': 6,
                             'files': 7}, None, dummy), parent=None)

    construct_tree(1, tree, indent='|- ', permanent=False, filler=True, fill_struct=root, use_cache=use_cache,
                   **kwargs)
    s = kwargs.get('__noprint__lin_log', None)
    if s is not None:
        root.dfs(action_print, K='p', __noprint__prefix='|- ', mode='print', __noprint__lin_log=s)
    f = fpath + '.pkl'
    if save_tree_fmt == 'pkl':
        save_serialized(f, root)

    return root


def save_serialized(fname, obj):
    with open(fname, 'wb') as f:
        print('Writing to file', fname)
        print(obj.children[0])
        pickle.dump(obj, f)


if __name__ == '__main__':
    # if need, pass caches and other stuff into kwargs
    suf = '0'
    try:
        suf = sys.argv[2]
    except:
        suf = str(datetime.datetime.now())
    path = 'pstree_dump_' + suf
    if sys.argv[1] == 'txt':
        fmt = sys.argv[1]
        linear_log_fp = open(path + '.txt', 'w+')
    else:
        fmt = 'pkl'
        linear_log_fp = None

    get_pstree(SPG_container=None, P_container=None, save_tree_fmt=fmt, __noprint__lin_log=linear_log_fp, fpath=path)
#    linear_log_fp.close()


import copy
# 'atriact': actions with attributes
default_inh={'p': 0,
             'g': 1,
             's': 2,
             'pp': 3,
             'socket': 4,
             'pipe': 5,
             'fifo': 6,
             'files': 7}
class Inh:
    def __init__(self, ptrs=None, names=None, act=None):
        self.ptr = ptrs
        self.names = names
        self.act = act

    def __str__(self):
        print('Node inherited attributes')
        print('lists:')
        try:
            print(self.ptr)
        except:
            print('No lists')
        try:
            print(self.names)
        except:
            print('No variables names')
        try:
            print(self.act)
        except:
            print('None')


class Synth:
    def __init__(self, values=[]):
        self.num = copy.copy(values)

    def __getitem__(self, key):
        return self.num[key]

    def __setitem__(self, key, value):
        self.num[key] = value

    def __str__(self):
        print(self.num)


def action_reconstruct(current, **kwargs):

    if current.visited:
        return False, current
    current.visited = True
    handle_exits = kwargs.get('handle_exits', True)
    if current.S[current.I.names['p']] == 1:
        return False, current
    """

    :type current: class Node
    """

    from tree import Node
    if not current.parent: # maybe Init process
        return False, current

    # 2 1 1

    if current.S[current.I.names['g']] == current.parent.S[current.parent.I.names['g']] and \
       current.S[current.I.names['s']] == current.parent.S[current.parent.I.names['s']]:
        current.I.act = 'fork' + '(' + str(current.S[current.I.names['pp']]) + ')'
        if 'check_fds' in kwargs:
            pass

    # 2 2 2
    # setsid
    elif current.S[current.I.names['p']] == current.S[current.I.names['g']] == current.S[current.I.names['s']]:
        new_state = Node(data=(None, default_inh, None, [current.S[current.I.names['p']],
                                    current.parent.S[current.parent.I.names['g']],
                                    current.parent.S[current.parent.I.names['s']],
                                    current.S[current.I.names['pp']],
                                    current.S[4], current.S[5], current.S[6], current.S[7]]), parent=current.parent, visited=True)
        current.parent.add_child(new_state)
        current.parent.delete_child(index=current.index)
        new_state.parent = current.parent
        current.parent = new_state
        new_state.I.act = 'fork'+'('+str(new_state.S[new_state.I.names['pp']])+')'
        current.I.act = 'setsid()'
        new_state.add_child(current)

    # 1 2 1
    # setsid(self)
    if current.S[current.I.names['p']] == current.S[current.I.names['g']] and \
            current.S[current.I.names['g']] != current.S[current.I.names['s']]:
        new_state = Node(data=(None, default_inh, None, [current.S[current.I.names['p']],
                                    current.parent.S[current.parent.I.names['g']],
                                    current.parent.S[current.parent.I.names['s']],
                                    current.S[current.I.names['pp']],
                                    current.S[4], current.S[5], current.S[6], current.S[7]]), parent=current.parent)

        current.parent.add_child(new_state)
        current.parent.delete_child(index=current.index)
        current.parent = new_state

        new_state.I.act = 'fork'+'('+str(new_state.S[new_state.I.names['pp']])+')'
        current.I.act = 'setpgid'+'(self:'+str(new_state.S[new_state.I.names['p']])+')'
        new_state.add_child(current)

    # check cs:
    # correct_session_picker
    # pass this elif or not - think after sleep :)
    elif handle_exits and current.parent.S[current.parent.I.names['p']] == 1:
        res = False
        current.parent.delete_child(current.index)
        # see the tree in previous articles
        res, target = current.parent.dfs(action=action_check_attr_eq, name='g', val=current.S[current.I.names['g']]) # if Ex group
        if res:
            res, target = current.parent.dfs(action=action_check_attr_eq, name='s', val=current.S[current.I.names['s']])
            if res:
                node = Node(data=(None, default_inh, 'fork('+str(target.S[target.I.names['p']])+'),exit()',
                                    [current.S[current.I.names['p']], # refill this
                                    current.S[current.I.names['g']],
                                    current.S[current.I.names['s']],
                                    target.S[target.I.names['p']],
                                    current.S[4], current.S[5], current.S[6], current.S[7]]), parent=target, visited=True)
                target.add_child(node)
                current.parent.delete_child(current.index)
                node.add_child(current)
                #current.parent = node
                current.S[current.I.names['pp']] = current.parent.S[current.parent.I.names['p']]
                current.I.act = 'fork'+'('+str(current.parent.S[current.I.names['pp']])+')'
            else:
                print('parsing error')
                import sys
                sys.exit(-1)
        else:
            res, target = current.parent.dfs(action=action_check_attr_eq, name='s',
                                      val=current.S[current.I.names['s']])  # if Ex session
            if res:
                node_par = Node(data=(None, default_inh, 'fork(' + str(target.S[target.I.names['p']]) + ')',
                                  [current.S[current.I.names['g']],  # refill this
                                   current.S[target.I.names['g']],
                                   current.S[target.I.names['s']],
                                   target.S[target.I.names['p']],
                                   current.S[4], current.S[5], current.S[6], current.S[7]]), parent=current.parent,
                            visited=True)
                node_ch = Node(data=(None, default_inh, 'setpgid(' + str(current.S[current.I.names['g']]) + '),exit()',
                                      [current.S[current.I.names['g']],  # refill this
                                       current.S[current.I.names['g']],
                                       current.S[target.I.names['s']],
                                       target.S[node_par.I.names['p']],
                                       current.S[4], current.S[5], current.S[6], current.S[7]]), parent=node_par,
                                visited=True)
                node_par.add_child(node_ch)
                target.add_child(node_par)
                current.parent.delete_child(current.index)
                node_ch.add_child(current)
                current.S[current.I.names['pp']] = current.parent.S[current.parent.I.names['p']]
            else:
                node_par = Node(data=(None, default_inh, 'fork(' + str(current.parent.S[current.parent.I.names['p']]) + ')',
                                      [current.S[current.I.names['s']],  # refill this
                                       current.parent.S[current.parent.I.names['g']],
                                       current.parent.S[current.parent.I.names['s']],
                                       current.parent.S[current.parent.I.names['p']],
                                       current.S[4], current.S[5], current.S[6], current.S[7]]), parent=current.parent,
                                visited=True)
                node_ch = Node(
                    data=(None, default_inh, 'setsid(), exit()',
                          [current.S[current.I.names['s']],
                           current.S[current.I.names['s']],
                           current.S[current.I.names['s']],
                           node_par.S[node_par.I.names['p']],
                           current.S[4], current.S[5], current.S[6], current.S[7]]), parent=node_par,
                    visited=True)

                node_br = Node(
                    data=(None, default_inh,'fork(' + str(node_ch.S[node_ch.I.names['p']]) + ')',
                          [current.S[current.I.names['g']],
                           current.S[current.I.names['s']],
                           current.S[current.I.names['s']],
                           node_ch.S[node_ch.I.names['p']],
                           current.S[4], current.S[5], current.S[6], current.S[7]]), parent=node_ch,
                    visited=True)

                node_br2 = Node(
                    data=(None, default_inh, 'setpgid(self,' + str(current.S[current.I.names['g']]) + '), exit()',
                          [current.S[current.I.names['g']],
                           current.S[current.I.names['g']],
                           current.S[current.I.names['s']],
                           node_br.S[node_br.I.names['p']],
                           current.S[4], current.S[5], current.S[6], current.S[7]]), parent=node_br,
                    visited=True)

                node_par.add_child(node_ch)
                current.parent.add_child(node_par)
                current.parent.delete_child(current.index)
                node_ch.add_child(node_br)
                node_br.add_child(node_br2)
                node_br2.add_child(current)
                current.S[current.I.names['pp']] = node_ch.S[node_ch.I.names['p']]

    else:
        res = False
        if current.parent.I.act == 'setsid()':
        # triple - see article - up of current's parent is reconstructed, which parent is target value
            res, _ = current.parent.parent.parent.upbranch(action=action_check_attr_eq, name='p', val=current.S[current.I.names['s']])
        elif 'setpgid' in current.parent.I.act:
            res, _ = current.parent.parent.parent.upbranch(action=action_check_attr_eq, name='p',
                                                           val=current.S[current.I.names['s']])
        if res:
#            current.parent.children = current.parent.delete_child(current.index)
            current.parent.delete_child(current.index) # redundancy - needs dynamic refilling of children list!
            current.parent = current.parent.parent

            current.parent.add_child(current)

            # look for group if not id is not suitable
            if current.S[current.I.names['g']] != current.parent.S[current.parent.I.names['g']]: ##loc_group(noself)
                print('starting upbranch')
                resg, root = current.upbranch(action=action_check_attr_eq, name='p', val=current.S[current.I.names['s']])
                print('upbranch is ok')
                if resg:
                    print('resg')
                    r, _ = root.dfs(action=action_check_attr_eq, name='p', name2='g', val=current.S[current.I.names['g']])
                    if r:
                        print('recons')
                        new_state = Node(data=(None, default_inh, None, [current.S[current.I.names['p']],
                                                                         current.parent.S[current.parent.I.names['g']],
                                                                         current.parent.S[current.parent.I.names['s']],
                                                                         current.S[current.I.names['pp']],
                                                                         current.S[4], current.S[5], current.S[6],
                                                                         current.S[7]]), parent=current.parent)
                        current.parent.add_child(new_state)
                        current.parent.delete_child(index=current.index)
                        current.parent = new_state
                        new_state.I.act = 'fork' + '(' + str(new_state.S[new_state.I.names['pp']]) + ')'
                        current.I.act = 'setpgid' + '(' + str(new_state.S[new_state.I.names['p']]) +';' + str(current.S[current.I.names['g']])+ ')'
                        new_state.add_child(current)

            else:
                print('forku')
                current.I.act = 'fork' + ' (' + str(current.S[current.I.names['pp']]) + ')'


    return False, current


# action fmt: get attributes from tree, return True if cond, else false

def action_stub(current, **kwargs):
    return False, current

def action_check_attr(current, **kwargs):
    if current.S[kwargs.pop('name')] == kwargs.pop('value'):
        return True, current
    return False, current


# the most base checker
def action_check_attr_eq(current, **kwargs):
    val = kwargs.pop('val')
    for _, v in kwargs.items():
        if current.S[current.I.names[v]] != val:
            return False, current
    return True, current


def action_print(current, **kwargs):
    mode = kwargs.pop('mode')
    prefix = kwargs.pop('__noprint__prefix')
    s = ''
    s += prefix + str(current.index)+':'
    if mode == 'parsed':
        try:
            s += current.I.act + '-->'
        except:
            s += 'Init' + '--> '
    for k, v in kwargs.items():
        if '__noprint__' not in k:
            s += str(v) + ' = ' + str(current.S[current.I.names[v]]) + '; '
    lin_log=kwargs.get('lin_log', None)
    if lin_log is not None:
        lin_log += ' '.join(current.S[:2])
    #print(s)
    return False, current

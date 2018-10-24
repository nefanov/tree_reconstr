import sys
import pickle
from tree import *

def run_pstree_loadtest(fpath):
    _pstree = Node()
    with open(fpath, 'rb') as fileobj:
        _pstree = pickle.load(fileobj)
        return  _pstree


if __name__ == "__main__":
    loaded_obj = run_pstree_loadtest(sys.argv[1])
    # example of usage:
    print(loaded_obj.S[1])
    

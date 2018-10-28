from graphviz import Source
path = 'dotfile.dot'
s = Source.from_file(path)
s.view()
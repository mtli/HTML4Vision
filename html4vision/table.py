from __future__ import print_function
from codecs import open

from collections import namedtuple
from glob import glob

import dominate
from dominate.tags import *
from dominate.util import text

Col = namedtuple('Col', 'name, pattern, range')

def imagetable(cols, outfile='index.html', title='', imsize=None, imscale=1):
    # parse the columns
    match_col = None
    if imsize:
        if isinstance(imsize, (int)) and imsize >= 0:
            match_col = imsize
            imsize = None
        elif not(isinstance(imsize, list) and len(imsize) == 2 and imsize[0] > 0 and imsize[1] > 0):
            raise ValueError('"imsize" needs to be None, a column index, or a list of size 2 specifying the width and the height')

    n_col = len(cols)
    col_src = [None]*n_col
    col_n_row = [None]*n_col
    for i, col in enumerate(cols):
        if col.pattern == '<id_0>' or col.pattern == '<id_1>':
            col_n_row[i] = 0
        else:
            col_src[i] = glob(col.pattern)
            if len(col_src[i]) == 0:
                print('Warning: Col %d: no files found matching "%s"' % (i, col.pattern))
            if col.range:
                col_src[i] = col_src[i][col.range[0]:col.range[1]]
            col_n_row[i] = len(col_src[i])
    n_row = max(col_n_row)

    # generate html
    with dominate.document(title=title) as doc:
        with table(style='text-align:center; zoom=50%', cls='html4vision'):
            with thead():
                with tr():
                    for col in cols:
                        td(col.name)
            with tbody():
                for r in range(n_row):
                    with tr():
                        for i, col in enumerate(cols):
                            if col.pattern == '<id_0>':
                                td(r)
                            elif col.pattern == '<id_1>':
                                td(r+1)
                            else:
                                if r < col_n_row[i]:
                                    if imsize:
                                        td(img(src=col_src[i][r], width=imsize[0], height=imsize[1]))
                                    else:
                                        td(img(src=col_src[i][r]))
                                else:
                                    td()
        if match_col:
            import os
            filedir = os.path.dirname(os.path.realpath(__file__))
            tablejs = open(os.path.join(filedir, 'table.js')).read()
            tablejs += '\naddImgSize(%d, %g);\n' % (match_col, imscale)
            script(text(tablejs, escape=False))

    with open(outfile, 'w', encoding='utf-8') as f:
        f.write(doc.render())
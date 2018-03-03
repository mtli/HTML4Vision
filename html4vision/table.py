from __future__ import print_function
from codecs import open

from collections import namedtuple
from glob import glob

import dominate
from dominate.tags import *
from dominate.util import text

Col = namedtuple('Col', 'type, name, content, subset, style')
Col.__new__.__defaults__ = ('img',) + (None,) * (len(Col._fields) - 1)

def _subsetsel(content, subset):
    if isinstance(subset, int):
        return content[:subset]
    if type(subset) is tuple: # namedtuple is not allowed here
        if len(subset) == 2:
            return content[subset[0]:subset[1]]
        elif len(subset) == 3:
            return content[subset[0]:subset[1]:subset[2]]
    if isinstance(subset, list):
        return [content[i] for i in subset]
    raise ValueError('Unrecognized subset value')

def imagetable(cols, outfile='index.html', title='', imsize=None, imscale=1, style=None):
    # parse the columns
    match_col = None
    if imsize != None:
        if isinstance(imsize, int) and imsize >= 0:
            match_col = imsize
            imsize = None
            if cols[match_col].type != 'img':
                raise ValueError('Invalid column type "' + cols[match_col].type + '" when "imsize" is interpreted as size matching column given index')
        elif not((isinstance(imsize, list) or type(imsize) is tuple) and len(imsize) == 2 and imsize[0] > 0 and imsize[1] > 0):
            raise ValueError('"imsize" needs to be None, a column index, or a list/tuple of size 2 specifying the width and the height')

    if imsize != None and imscale != 1:
        imsize = (imsize[0]*imscale, imsize[1]*imscale)

    n_col = len(cols)
    col_src = [None]*n_col
    col_n_row = [None]*n_col

    col_bug = [None]*n_col

    use_overlay = False
    col_pre_overlay = [False]*n_col
    col_idx_no_overlay = [None]*n_col
    col_idx = 0

    for i, col in enumerate(cols):
        col_idx_no_overlay[i] = col_idx
        col_idx += 1
        if col.type == 'id0' or col.type == 'id1':
            col_n_row[i] = 0
        elif col.type == 'text':
            if col.subset:
                cols[i] = col._replace(content=_subsetsel(col.content, col.subset))
            col_n_row[i] = len(cols[i].content)
        elif col.type == 'img' or col.type == 'overlay':
            if isinstance(col.content, list):
                col_src[i] = col.content
            else:
                col_src[i] = sorted(glob(col.content))
                if len(col_src[i]) == 0:
                    print('Warning: Col %d: no files found matching "%s"' % (i, col.content))
            if col.subset:
                col_src[i] = _subsetsel(col_src[i], col.subset)
            col_n_row[i] = len(col_src[i])
            if col.type == 'overlay':
               if i == 0 or cols[i-1].type != 'img':
                   raise ValueError('The column preceding "overlay" type must be of "img" type')
               else:
                   use_overlay = True
                   col_pre_overlay[i-1] = True
                   col_idx -= 1
                   col_idx_no_overlay[i] -= 1

    n_row = max(col_n_row)
    match_col = col_idx_no_overlay[match_col] if match_col else match_col

    # generate html
    with dominate.document(title=title) as doc:
        with doc.head:
            css = 'table.html4vision {text-align: center}\n'
            css += '.html4vision td {vertical-align: middle}\n'
            css += '.html4vision td img {display:table-cell}\n'
            if use_overlay:
                css += '.html4vision div {position: relative; display: table-cell}\n'
                css += '.overlay {position: absolute; left: 0; top: 0}\n'
            if style:
                css += style + '\n'
            for i, col in enumerate(cols):
                if col.style:
                    if col.type == 'overlay':
                        css += 'td:nth-child(%d) img.overlay {%s}\n' % (col_idx_no_overlay[i] + 1, col.style)
                    else: # css uses 1-based indexing
                        css += 'td:nth-child(%d) {%s}\n' % (col_idx_no_overlay[i] + 1, col.style)
            dominate.tags.style(text(css, escape=False))
        with table(cls='html4vision'):
            with thead():
                with tr():
                    for col in cols:
                        if col.type == 'overlay':
                            continue
                        if col.name:
                            td(col.name)
                        else:
                            td()
            with tbody():
                for r in range(n_row):
                    with tr():
                        for i, col in enumerate(cols):
                            if col.type == 'id0':
                                td(r)
                            elif col.type == 'id1':
                                td(r+1)
                            elif col.type == 'text':
                                if r < col_n_row[i]:
                                    td(col.content[r])
                                else:
                                    td()
                            elif col.type == 'overlay':
                                continue
                            elif col_pre_overlay[i]:
                                with td():
                                    with div():
                                        if imsize:
                                            if r < col_n_row[i]:
                                                img(src=col_src[i][r], width=imsize[0], height=imsize[1])
                                            if r < col_n_row[i+1]:
                                                img(src=col_src[i+1][r], cls='overlay', width=imsize[0], height=imsize[1])
                                        else:
                                            if r < col_n_row[i]:
                                                img(src=col_src[i][r])
                                            if r < col_n_row[i+1]:
                                                img(src=col_src[i+1][r], cls='overlay')
                            else:
                                if r < col_n_row[i]:
                                    if imsize:
                                        td(img(src=col_src[i][r], width=imsize[0], height=imsize[1]))
                                    else:
                                        td(img(src=col_src[i][r]))
                                else:
                                    td()

        if match_col != None:
            import os
            filedir = os.path.dirname(os.path.realpath(__file__))
            jscode = open(os.path.join(filedir, 'matchCol.js')).read()
            jscode += '\nmatchCol(%d, %g);\n' % (match_col, imscale)
            script(text(jscode, escape=False))
        elif imsize == None and imscale != 1:
            import os
            filedir = os.path.dirname(os.path.realpath(__file__))
            jscode = open(os.path.join(filedir, 'scaleImg.js')).read()
            jscode += '\nscaleImg(%g);\n' % (imscale)
            script(text(jscode, escape=False))

    with open(outfile, 'w', encoding='utf-8') as f:
        f.write(doc.render())
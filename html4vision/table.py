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

# wrapper classes to remove empty attributes
class _img(html_tag):
    tagname = 'img'
    def __init__(self, *args, **kwargs):
        empty_attrs = []
        for attr, value in kwargs.items():
            if not value:
                empty_attrs.append(attr)
        for attr in empty_attrs:
            del kwargs[attr]
        super(_img, self).__init__(*args, **kwargs)

def imagetable(
        # contents
        cols,
        out_file='index.html',
        title='',
        summary_row=None,
        copyright=True,

        # modifiers
        pathrep=None,
        sortcol=None,

        # style
        imsize=None,
        imscale=1,
        summary_color=None,
        sticky_header=False,
        sort_style=None,
        zebra=False,
        style=None,

        # interaction
        overlay_toggle=False,
        sortable=False,
    ):

    n_col = len(cols)

    match_col = None
    if imsize != None:
        if isinstance(imsize, int) and imsize >= 0 and imsize < n_col:
            match_col = imsize
            imsize = None
            if cols[match_col].type != 'img':
                raise ValueError('Invalid column type "' + cols[match_col].type + '" when "imsize" is interpreted as size matching column given index')
        elif not((isinstance(imsize, list) or type(imsize) is tuple) and len(imsize) == 2 and imsize[0] > 0 and imsize[1] > 0):
            raise ValueError('"imsize" needs to be a column index, or a list/tuple of size 2 specifying the width and the height')
    if imsize != None and imscale != 1:
        imsize = (imsize[0]*imscale, imsize[1]*imscale)
    if not imsize:
        imsize = [None, None]

    if sortcol != None:
        if not isinstance(sortcol, int) or sortcol < 0 or sortcol >= n_col:
            raise ValueError('"sortcol" needs to be a column index')
        if cols[sortcol].type != 'text':
            raise ValueError('The type of the column specified by "sortcol" should be "text"')

    # variables to store the processed contents
    col_content = [None]*n_col
    col_n_row = [None]*n_col

    use_overlay = False
    col_pre_overlay = [False]*n_col
    col_idx_no_overlay = [None]*n_col
    col_idx = 0

    if pathrep:
        if type(pathrep) is tuple or isinstance(pathrep, list):
            pathrep_old = pathrep[0].replace('\\', '/')
            pathrep_new = pathrep[1]
        else:
            pathrep_old = pathrep.replace('\\', '/')
            pathrep_new = ''

    for i, col in enumerate(cols):
        col_idx_no_overlay[i] = col_idx
        col_idx += 1
        if col.type == 'id0' or col.type == 'id1':
            col_n_row[i] = 0
        elif col.type == 'text':
            if col.subset:
                col_content[i] = _subsetsel(col.content, col.subset)
            else:
                col_content[i] = col.content
            col_n_row[i] = len(col_content[i])
        elif col.type == 'img' or col.type == 'overlay':
            if isinstance(col.content, list):
                col_content[i] = col.content
            else:
                col_content[i] = sorted(glob(col.content))
                if len(col_content[i]) == 0:
                    print('Warning: Col %d: no files found matching "%s"' % (i, col.content))
            if col.subset:
                col_content[i] = _subsetsel(col_content[i], col.subset)
            if pathrep:
                col_content[i] = [s.replace('\\', '/').replace(pathrep_old, pathrep_new) for s in col_content[i]]
            col_n_row[i] = len(col_content[i])
            if col.type == 'overlay':
               if i == 0 or cols[i-1].type != 'img':
                   raise ValueError('The column preceding "overlay" type must be of "img" type')
               else:
                   use_overlay = True
                   col_pre_overlay[i-1] = True
                   col_idx -= 1
                   col_idx_no_overlay[i] -= 1
        else:
            raise ValueError('Col %d: unrecognized column type "%s"' % (i, col.type))

    n_row = max(col_n_row)
    match_col = col_idx_no_overlay[match_col] if match_col else match_col

    if sortcol != None:
        sort_list = col_content[sortcol]
        n_item = len(sort_list)
        sorted_idx = sorted(list(range(n_item)), key=sort_list.__getitem__)
        sorted_idx += list(range(n_item, n_row)) # in case the sort list is shorter than others
        for i in range(n_col):
            if col_n_row[i]:
                col_content[i] = [col_content[i][x] if x < col_n_row[i] else '' for x in sorted_idx]
                col_n_row[i] = max(n_item, col_n_row[i]) # the sort list can be longer than others

    cdn = 'https://cdnjs.cloudflare.com/ajax/libs/'
    cdn_ts = 'https://cdnjs.cloudflare.com/ajax/libs/jquery.tablesorter/2.30.7/'

    ts_widgets = []
    
    if sticky_header:
        ts_widgets.append('stickyHeaders')
    if zebra:
        ts_widgets.append('zebra')
    if sortable and summary_row:
        ts_widgets.append('staticRow')
    use_tablesorter = sortable or ts_widgets

    # generate html
    with dominate.document(title=title) as doc:
        with doc.head:
            if sort_style:
                link(href=cdn_ts + 'css/theme.' \
                    + sort_style + '.min.css', rel='stylesheet')
            if use_tablesorter:
                script(src=cdn + 'jquery/3.3.1/jquery.slim.min.js')
                script(src=cdn_ts + 'js/jquery.tablesorter.min.js')
                for w in ts_widgets:
                    if w != 'zebra':
                        script(src=cdn_ts + 'js/widgets/widget-' + w + '.min.js')

                ts_opts = ''
                if not sortable:
                    ts_opts += 'headers: {"th": {sorter: false}},\n'
                ts_opts += 'widgets: [' + (', '.join('"' + w + '"' for w in ts_widgets)) + '],\n'
                if ts_opts:
                    ts_opts = '{\n' + ts_opts + '}'
                script(text('$(function(){$(".tablesorter").tablesorter(' + ts_opts + ');});', escape=False))

            css = '' # custom CSS
            css += 'table.html4vision {text-align: center}\n'
            css += '.html4vision td {vertical-align: middle !important}\n'
            css += '.html4vision td img {display: table-cell}\n'
            if copyright:
                css += '.copyright {margin-top: 0.5em; font-size: 85%}'

            # style fix
            if sticky_header and sort_style == 'materialize':
                css += '.html4vision {border-collapse: collapse}\n'
                css += '.html4vision th,td {border: 1px solid #DDD}\n'

            if use_overlay:
                css += '.html4vision div {position: relative; display: table-cell}\n'
                css += '.overlay {position: absolute; left: 0; top: 0}\n'
            if summary_color:
                css += '.html4vision tr.static td {background-color: ' + summary_color + ' !important}\n'
            if style:
                css += style + '\n'

            for i, col in enumerate(cols):
                if col.style:
                    if col.type == 'overlay':
                        css += 'td:nth-child(%d) img.overlay {%s}\n' % (col_idx_no_overlay[i] + 1, col.style)
                    else: # css uses 1-based indexing
                        css += 'td:nth-child(%d) {%s}\n' % (col_idx_no_overlay[i] + 1, col.style)
            dominate.tags.style(text(css, escape=False))
        tablecls = 'html4vision'
        if sortable or sticky_header:
            tablecls += ' tablesorter'
        if sort_style:
            tablecls += ' tablesorter-' + sort_style
        with table(cls=tablecls):
            with thead():
                with tr():
                    for col in cols:
                        if col.type == 'overlay':
                            continue
                        if col.name:
                            th(col.name)
                        else:
                            th()
            with tbody():
                if summary_row:
                    with tr(cls='static'):
                        for i, col in enumerate(cols):
                            if col.type == 'overlay':
                                continue
                            else:
                                td(summary_row[i])
                for r in range(n_row):
                    with tr():
                        for i, col in enumerate(cols):
                            if col.type == 'id0':
                                td(sorted_idx[r] if sortcol != None else r)
                            elif col.type == 'id1':
                                td(sorted_idx[r]+1 if sortcol != None else r+1)
                            elif col.type == 'text':
                                if r < col_n_row[i]:
                                    td(col_content[i][r])
                                else:
                                    td()
                            elif col.type == 'overlay':
                                continue
                            elif col_pre_overlay[i]:
                                with td():
                                    with div():
                                        if r < col_n_row[i]:
                                            _img(src=col_content[i][r], width=imsize[0], height=imsize[1])
                                        if r < col_n_row[i+1]:
                                            _img(src=col_content[i+1][r], cls='overlay', width=imsize[0], height=imsize[1])
                            else:
                                if r < col_n_row[i]:
                                    td(_img(src=col_content[i][r], width=imsize[0], height=imsize[1]))
                                else:
                                    td()
        if copyright:
            with div(cls='copyright'):
                text('Genereted by')
                a('HTML4Vision', href='https://github.com/mtli/HTML4Vision')
                from . import __version__
                text(' v' + __version__)
            
        def getjs(filename):
            import os
            filedir = os.path.dirname(os.path.realpath(__file__))
            jscode = open(os.path.join(filedir, filename)).read()
            return jscode
            
        if match_col != None:
            jscode = getjs('matchCol.js')
            jscode += '\nmatchCol(%d, %g);\n' % (match_col, imscale)
            script(text(jscode, escape=False))
        elif imsize[0] == None and imscale != 1:
            jscode = getjs('scaleImg.js')
            jscode += '\nscaleImg(%g);\n' % (imscale)
            script(text(jscode, escape=False))
        if overlay_toggle:
            jscode = getjs('overlayToggle.js')
            script(text(jscode, escape=False))

    with open(out_file, 'w', encoding='utf-8') as f:
        f.write(doc.render())
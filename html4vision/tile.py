from __future__ import print_function
from codecs import open

from math import ceil
from glob import glob

import dominate
from dominate.tags import *
from dominate.util import text

from .common import *

def imagetile(
        # contents
        content,
        n_col=3,
        out_file='index.html',
        title='',
        caption=None,
        href=None,
        subset=None,
        copyright=True,

        # modifiers
        pathrep=None,

        # style
        imsize=None,
        imscale=1,
        caption_bottom=True,
        style=None,
    ):
    
    if imsize is None:
        imsize = [None, None]
    else:
        if not((isinstance(imsize, list) or type(imsize) is tuple) and len(imsize) == 2 and imsize[0] > 0 and imsize[1] > 0):
            raise ValueError('"imsize" needs to be a column index, or a list/tuple of size 2 specifying the width and the height')
        if imscale != 1:
            imsize = (imsize[0]*imscale, imsize[1]*imscale)

    pathrep = parse_pathrep(pathrep)
    items = parse_content(content, subset, pathrep, 'tile content')
    n_item = len(items)
    if n_item == 0:
        raise ValueError('Empty content')
    use_caption = caption is not None and caption
    if use_caption:
        caption = subsetsel(caption, subset)
    if href is not None:
        href = parse_content(href, subset, pathrep, 'tile href')
    
    n_row = ceil(float(n_item) / n_col)
    # generate html

    def add_caption(r):
        with tr():
            for c in range(n_col):
                idx = r*n_col + c
                if idx < len(caption):
                    td(text(caption[idx]))
                else:
                    td()

    with dominate.document(title=title) as doc:
        with doc.head:
            css = '' # custom CSS
            css += 'table.html4vision {text-align: center}\n'
            css += '.html4vision td {vertical-align: middle !important}\n'
            css += '.html4vision td img {display: block; margin: auto;}\n'
            if use_caption:
                css += '.html4vision tr:nth-child(even) td {padding-bottom: 0.8em}\n'
            if copyright:
                css += '.copyright {margin-top: 0.5em; font-size: 85%}'
            if style:
                css += style + '\n'
            dominate.tags.style(text(css, escape=False))

        with table(cls='html4vision'):
            with tbody():
                for r in range(n_row):
                    if use_caption and not caption_bottom:
                        add_caption(r)
                    with tr():
                        for c in range(n_col):
                            idx = r*n_col + c
                            if idx < n_item:
                                tda(href, idx, img_(src=items[idx], width=imsize[0], height=imsize[1]))
                            else:
                                td()
                    if use_caption and caption_bottom:
                        add_caption(r)

        if copyright:
            copyright_html()
            
        if imsize[0] == None and imscale != 1:
            jscode = getjs('scaleImg.js')
            jscode += '\nscaleImg(%g);\n' % (imscale)
            script(text(jscode, escape=False))


    with open(out_file, 'w', encoding='utf-8') as f:
        f.write(doc.render())
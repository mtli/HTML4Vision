from __future__ import print_function
from codecs import open

from math import ceil

import dominate  # type: ignore
from dominate.tags import meta, script, table, tbody, tr, td  # type: ignore
from dominate.util import text  # type: ignore

from .common import (
    copyright_html,
    getjs,
    imsize_attrs,
    img_,
    parse_pathrep,
    parse_content,
    subsetsel,
    tda,
)


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
    inline_js=None,

    # style
    imsize=None,
    imscale=1,
    preserve_aspect=True,
    caption_bottom=True,
    style=None,
):
    if imsize is None:
        imsize = [None, None]
    else:
        if not (
            (isinstance(imsize, list) or type(imsize) is tuple)
            and len(imsize) == 2 and imsize[0] > 0 and imsize[1] > 0
        ):
            raise ValueError(
                '"imsize" needs to be a column index, or a list/tuple of size 2 specifying '
                'the width and the height'
            )
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
            meta(charset='utf-8')

            css = ''
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
                                if imsize[0] is None or imsize[1] is None:
                                    kw = {}
                                else:
                                    kw = imsize_attrs(imsize, preserve_aspect)
                                tda(href, idx, img_(src=items[idx], **kw))
                            else:
                                td()
                    if use_caption and caption_bottom:
                        add_caption(r)

        if copyright:
            copyright_html()

        if imsize[0] is None and imscale != 1:
            jscode = getjs('scaleImg.js')
            jscode += '\nscaleImg(%g);\n' % (imscale)
            script(text(jscode, escape=False))

        if inline_js:
            script(text(inline_js, escape=False))

    with open(out_file, 'w', encoding='utf-8') as f:
        f.write(doc.render())

from __future__ import print_function

import os
from codecs import open  # For Python 2 compatibility
from collections import namedtuple
from functools import partial

import dominate  # type: ignore
from dominate.tags import meta, link, script, table, thead, tbody, tr, th, td, div  # type: ignore
from dominate.util import text  # type: ignore

from .common import (
    copyright_css,
    copyright_html,
    getjs,
    imsize_attrs,
    img_,
    model_,
    parse_pathrep,
    parse_content,
    subsetsel,
    tda,
)

from .thumbs import make_thumbnail


Col = namedtuple('Col', 'type, name, content, subset, style, href')
Col.__new__.__defaults__ = ('img',) + (None,) * (len(Col._fields) - 1)


def imagetable(
    # contents
    cols,
    out_file='index.html',
    title='',
    summary_row=None,
    copyright=True,
    thumbs_dir=None,

    # modifiers
    pathrep=None,
    sortcol=None,
    precompute_thumbs=False,
    thumb_quality=95,
    inline_js=None,
    escape_summary_row=True,

    # style
    imsize=None,
    imscale=1,
    preserve_aspect=True,
    hori_center_img=False,
    summary_color=None,
    sticky_header=False,
    sort_style=None,
    zebra=False,
    style=None,

    # interaction
    overlay_toggle=False,
    sortable=False,

    # 3d model viewer
    auto_rotate=False,
    camera_controls=True,
    mesh_opt=False,

    # performance
    max_image_load_concurrency=None,
):
    img_.use_data_src = max_image_load_concurrency is not None

    n_col = len(cols)

    match_col = None
    if imsize is not None:
        if isinstance(imsize, int) and imsize >= 0 and imsize < n_col:
            match_col = imsize
            imsize = None
            if cols[match_col].type != 'img':
                raise ValueError(
                    'Invalid column type "' + cols[match_col].type + '" when "imsize" is '
                    'interpreted as size matching column given index'
                )
        elif not (
            (isinstance(imsize, list) or type(imsize) is tuple)  # noqa: E721
            and len(imsize) == 2 and imsize[0] > 0 and imsize[1] > 0
        ):
            raise ValueError(
                '"imsize" needs to be a column index, or a list/tuple of size 2 specifying '
                'the width and the height'
            )
    if imsize is not None and imscale != 1:
        imsize = (imsize[0]*imscale, imsize[1]*imscale)
        imscale = 1
    if imsize is None:
        imsize = [None, None]

    if precompute_thumbs:
        if thumbs_dir is None:
            thumbs_dir = os.path.splitext(out_file)[0] + '_thumbs'
        if not os.path.isdir(thumbs_dir):
            os.makedirs(thumbs_dir)
        thumb_func = partial(
            make_thumbnail,
            thumbs_dir=thumbs_dir,
            imsize=imsize,
            imscale=imscale,
            preserve_aspect=preserve_aspect,
            quality=thumb_quality,
        )
        imscale = 1
    else:
        thumb_func = None

    if sortcol is not None:
        if not isinstance(sortcol, int) or sortcol < 0 or sortcol >= n_col:
            raise ValueError('"sortcol" needs to be a column index')
        if cols[sortcol].type != 'text':
            raise ValueError('The type of the column specified by "sortcol" should be "text"')

    # variables to store the processed contents
    col_content = [None]*n_col
    col_href = [None]*n_col
    col_n_row = [None]*n_col

    use_overlay = False
    use_model_viewer = False
    col_pre_overlay = [False]*n_col
    col_idx_no_overlay = [None]*n_col
    col_idx = 0

    pathrep = parse_pathrep(pathrep)

    for i, col in enumerate(cols):
        col_idx_no_overlay[i] = col_idx
        col_idx += 1
        is_img_col = False
        if col.type == 'id0' or col.type == 'id1':
            col_n_row[i] = 0
        elif col.type == 'text':
            col_content[i] = subsetsel(col.content, col.subset)
            col_n_row[i] = len(col_content[i])
        elif col.type == 'img' or col.type == 'overlay':
            is_img_col = True
            col_content[i] = parse_content(
                col.content,
                col.subset,
                pathrep,
                'Col %d' % i,
                thumb_func=thumb_func,
            )
            col_n_row[i] = len(col_content[i])
            if col.type == 'overlay':
                if i == 0 or cols[i-1].type != 'img':
                    raise ValueError('The column preceding "overlay" type must be of "img" type')
                else:
                    use_overlay = True
                    col_pre_overlay[i-1] = True
                    col_idx -= 1
                    col_idx_no_overlay[i] -= 1
        elif col.type == 'model':
            use_model_viewer = True
            col_content[i] = parse_content(col.content, col.subset, pathrep, 'Col %d' % i)
            col_n_row[i] = len(col_content[i])
        else:
            raise ValueError('Col %d: unrecognized column type "%s"' % (i, col.type))

        if col.href:
            col_href[i] = parse_content(col.href, col.subset, pathrep, 'Col %d href' % i)
        elif is_img_col and precompute_thumbs:
            # For thumbnails, we want hrefs to point to the high-resolution
            # images (after path replacement), not the thumbnail files.
            col_href[i] = parse_content(col.content, col.subset, pathrep, 'Col %d href' % i)

    n_row = max(col_n_row)
    match_col = col_idx_no_overlay[match_col] if match_col else match_col

    if sortcol is not None:
        sort_list = col_content[sortcol]
        n_item = len(sort_list)
        sorted_idx = sorted(list(range(n_item)), key=sort_list.__getitem__)
        sorted_idx += list(range(n_item, n_row))  # in case the sort list is shorter than others
        for i in range(n_col):
            if col_n_row[i]:
                col_content[i] = [col_content[i][x] if x < col_n_row[i] else '' for x in sorted_idx]
                if col_href[i]:
                    col_href[i] = [
                        col_href[i][x] if x < len(col_href[i]) else '' for x in sorted_idx
                    ]
                col_n_row[i] = max(n_item, col_n_row[i])  # the sort list can be longer than others

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
            meta(charset='utf-8')

            if sort_style:
                link(href=cdn_ts + 'css/theme.' + sort_style + '.min.css', rel='stylesheet')
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
                script(text(
                    '$(function(){$(".tablesorter").tablesorter(' + ts_opts + ');});', escape=False
                ))

            if use_model_viewer:
                model_viewer_opts = {'auto-rotate': auto_rotate, 'camera-controls': camera_controls}
                if mesh_opt:
                    script(text("""
    self.ModelViewerElement = self.ModelViewerElement || {};
    self.ModelViewerElement.meshoptDecoderLocation = 'https://cdn.jsdelivr.net/npm/meshoptimizer/meshopt_decoder.js';
                    """, escape=False))  # noqa
                script(
                    type="module",
                    src="https://unpkg.com/@google/model-viewer/dist/model-viewer.min.js",
                )

            css = ''
            css += 'table.html4vision {text-align: center}\n'
            css += '.html4vision td {vertical-align: middle !important}\n'
            if hori_center_img:
                css += '.html4vision td img {display: block; margin: auto}\n'
            else:
                css += '.html4vision td img {display: table-cell}\n'
            if copyright:
                css += copyright_css()

            # style fix
            if sticky_header and sort_style == 'materialize':
                css += '.html4vision {border-collapse: collapse}\n'
                css += '.html4vision th,td {border: 1px solid #DDD}\n'

            if use_overlay:
                css += '.html4vision div {position: relative; display: table-cell}\n'
                css += '.overlay {position: absolute; left: 0; top: 0}\n'
            if summary_color:
                css += (
                    '.html4vision tr.static td {background-color: ' +
                    summary_color + ' !important}\n'
                )
            if style:
                css += style + '\n'

            for i, col in enumerate(cols):
                if col.style:
                    if col.type == 'overlay':
                        css += (
                            'td:nth-child(%d) img.overlay {%s}\n'
                            % (col_idx_no_overlay[i] + 1, col.style)
                        )
                    else:   # CSS uses 1-based indexing
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
                                td(text(str(summary_row[i]), escape=escape_summary_row))
                for r in range(n_row):
                    with tr():
                        for i, col in enumerate(cols):
                            if col.type == 'id0':
                                idx = sorted_idx[r] if sortcol is not None else r
                                tda(col_href[i], r, idx)
                            elif col.type == 'id1':
                                idx = sorted_idx[r] if sortcol is not None else r
                                tda(col_href[i], r, idx + 1)
                            elif col.type == 'text':
                                if r < col_n_row[i]:
                                    tda(col_href[i], r, col_content[i][r])
                                else:
                                    td()
                            elif col.type == 'model':
                                if r < col_n_row[i]:
                                    tda(
                                        col_href[i], r,
                                        model_(src=col_content[i][r], **model_viewer_opts)
                                    )
                                else:
                                    td()
                            elif col.type == 'overlay':
                                continue
                            elif col_pre_overlay[i]:
                                with tda(col_href[i], r):
                                    with div():
                                        if r < col_n_row[i]:
                                            img_(
                                                src=col_content[i][r],
                                                width=imsize[0],
                                                height=imsize[1],
                                            )
                                        if r < col_n_row[i+1]:
                                            img_(
                                                src=col_content[i+1][r],
                                                cls='overlay',
                                                width=imsize[0],
                                                height=imsize[1],
                                            )
                            else:
                                if r < col_n_row[i]:
                                    if imsize[0] is None or imsize[1] is None:
                                        kw = {}
                                    else:
                                        kw = imsize_attrs(imsize, preserve_aspect)
                                    tda(col_href[i], r, img_(src=col_content[i][r], **kw))
                                else:
                                    td()
        if copyright:
            copyright_html()

        if match_col is not None:
            jscode = getjs('matchCol.js')
            jscode += '\nmatchCol(%d, %g);\n' % (match_col, imscale)
            script(text(jscode, escape=False))
        elif imsize[0] is None and imscale != 1:
            jscode = getjs('scaleImg.js')
            jscode += '\nscaleImg(%g);\n' % imscale
            script(text(jscode, escape=False))
        if overlay_toggle:
            jscode = getjs('overlayToggle.js')
            script(text(jscode, escape=False))
        if max_image_load_concurrency is not None:
            jscode = getjs('limitImgLoad.js')
            jscode += '\nlimitImgLoad(%d);\n' % max_image_load_concurrency
            script(text(jscode, escape=False))
        if inline_js:
            script(text(inline_js, escape=False))

    with open(out_file, 'w', encoding='utf-8') as f:
        f.write(doc.render())

    # Reset the global flag to avoid side effects for subsequent calls
    img_.use_data_src = False

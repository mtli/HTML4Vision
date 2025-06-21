from collections.abc import Sequence

import dominate
from dominate.tags import meta, script, table, tbody, tr, td
from dominate.util import text

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
    content: str | Sequence[str],
    n_col: int = 3,
    out_file: str = 'index.html',
    title: str = '',
    caption: Sequence[str] | None = None,
    href: str | Sequence[str] | None = None,
    subset: int | tuple[int] | list[int] | None = None,
    copyright: bool = True,
    # modifiers
    pathrep: str | tuple[str, str] | list[str] | None = None,
    inline_js: str | None = None,
    # style
    imsize: tuple[int, int] | list[int] | None = None,
    imscale: float = 1,
    preserve_aspect: bool = True,
    caption_bottom: bool = True,
    style: str | None = None,
) -> None:
    if imsize is None:
        imsize_list: list[int | None] = [None, None]
    else:
        if not (
            (isinstance(imsize, list) or type(imsize) is tuple)  # noqa: E721
            and len(imsize) == 2
            and imsize[0] > 0
            and imsize[1] > 0
        ):
            raise ValueError(
                '"imsize" needs to be a column index, or a list/tuple of size 2 specifying '
                'the width and the height'
            )
        im_w, im_h = imsize[0], imsize[1]
        if imscale != 1:
            im_w = round(im_w * imscale)
            im_h = round(im_h * imscale)
        imsize_list = [int(im_w), int(im_h)]

    pathrep_parsed = parse_pathrep(pathrep)

    if isinstance(content, str):
        content_desc: str | list[str] = content
    else:
        content_desc = list(content)

    items = parse_content(content_desc, subset, pathrep_parsed, 'tile content')
    n_item = len(items)
    if n_item == 0:
        raise ValueError('Empty content')
    captions: list[str] = (
        subsetsel(list(caption), subset) if caption else []  # type: ignore[arg-type]
    )
    use_caption: bool = bool(captions)
    if href is not None:
        href_desc: str | list[str] = href if isinstance(href, str) else list(href)
        href = parse_content(href_desc, subset, pathrep_parsed, 'tile href')

    n_row = -(-n_item // n_col)

    def add_caption(r: int) -> None:
        """Insert caption row *r* (0-based) into the table body."""
        with tr():  # type: ignore[misc]
            for c in range(n_col):
                idx = r * n_col + c
                if idx < len(captions):
                    td(text(captions[idx]))
                else:
                    td()

    with dominate.document(title=title) as doc:  # type: ignore[misc]
        with doc.head:  # type: ignore[misc]
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
                            idx = r * n_col + c
                            if idx < n_item:
                                if imsize_list[0] is None or imsize_list[1] is None:
                                    kw = {}
                                else:
                                    kw = imsize_attrs(
                                        (int(imsize_list[0]), int(imsize_list[1])), preserve_aspect
                                    )
                                tda(href, idx, img_(src=items[idx], **kw))
                            else:
                                td()
                    if use_caption and caption_bottom:
                        add_caption(r)

        if copyright:
            copyright_html()

        if imsize_list[0] is None and imscale != 1:
            jscode = getjs('scaleImg.js')
            jscode += f'\nscaleImg({imscale:g});\n'
            script(text(jscode, escape=False))

        if inline_js:
            script(text(inline_js, escape=False))

    with open(out_file, 'w', encoding='utf-8') as f:
        f.write(doc.render())

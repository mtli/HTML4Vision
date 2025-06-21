from __future__ import print_function

import os
from glob import glob
try:
    from concurrent.futures import ThreadPoolExecutor
except ImportError:
    # For Python 2
    from futures import ThreadPoolExecutor  # type: ignore

from dominate.tags import html_tag, td, a, div  # type: ignore
from dominate.util import text  # type: ignore


def subsetsel(content, subset):
    """Subset selection for various syntaxes"""
    if subset is None:
        return content
    if isinstance(subset, int):
        return content[:subset]
    if type(subset) is tuple:  # namedtuple is not allowed here
        if len(subset) == 2:
            return content[subset[0]:subset[1]]
        elif len(subset) == 3:
            return content[subset[0]:subset[1]:subset[2]]
    if isinstance(subset, list):
        return [content[i] for i in subset]
    raise ValueError('Unrecognized subset value')


def parse_pathrep(pathrep):
    """Parse path replacer"""
    if pathrep is None:
        return None
    if type(pathrep) is tuple or isinstance(pathrep, list):
        pathrep_old = pathrep[0].replace('\\', '/')
        pathrep_new = pathrep[1]
    else:
        pathrep_old = pathrep.replace('\\', '/')
        pathrep_new = ''
    return (pathrep_old, pathrep_new)


def parse_content(descriptor, subset=None, pathrep=None, message=None, thumb_func=None):
    """ Parse content descriptor """
    if isinstance(descriptor, list):
        out = descriptor
    elif isinstance(descriptor, str):
        out = sorted(glob(descriptor))
        if len(out) == 0:
            if message is not None:
                print('Warning: %s: no files found matching "%s"' % (message, descriptor))
    else:
        raise ValueError('Invalid type of content descriptor: %s', type(descriptor))
    out = subsetsel(out, subset)
    if not out:
        return out

    if thumb_func is not None:
        with ThreadPoolExecutor() as executor:
            out = list(executor.map(thumb_func, out))

    if pathrep:
        out = [s.replace('\\', '/').replace(pathrep[0], pathrep[1]) for s in out]
    return out


class img_(html_tag):
    """Wrapper that removes empty attributes and supports data-src for lazy loading"""
    tagname = 'img'

    # When True, a provided "src" attribute is moved to "data-src" so that
    # the browser does not automatically start downloading the image. The
    # JavaScript limiter will later copy it back to "src".
    use_data_src = False

    def __init__(self, **kwargs):
        kwargs = {k: v for k, v in kwargs.items() if v}
        if img_.use_data_src and 'src' in kwargs:
            kwargs['data-src'] = kwargs['src']
            del kwargs['src']
        super(img_, self).__init__(**kwargs)


class model_(html_tag):
    tagname = 'model-viewer'


def tda(hrefs, idx, *args, **kwargs):
    """ Wrapper that adds an anchor tag on demand """
    if hrefs and idx < len(hrefs) and hrefs[idx]:
        return td(**kwargs).add(a(*args, href=hrefs[idx], target='_blank'))
    else:
        return td(*args, **kwargs)


def getjs(filename):
    """Read javascript"""
    filedir = os.path.dirname(os.path.realpath(__file__))
    jscode = open(os.path.join(filedir, filename)).read()
    return jscode


def copyright_css():
    return '.copyright {margin-top: 0.5em; font-size: 85%}'


def copyright_html():
    with div(cls='copyright'):
        text('Genereted by')
        a('HTML4Vision', href='https://github.com/mtli/HTML4Vision')
        from . import __version__
        text(' v' + __version__)


def imsize_attrs(imsize, preserve_aspect):
    if not preserve_aspect:
        return {'width': imsize[0], 'height': imsize[1]}
    else:
        return {'style': 'max-width:%dpx; max-height:%dpx;' % (imsize[0], imsize[1])}

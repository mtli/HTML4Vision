import os
from glob import glob
from dominate.tags import *
from dominate.util import text

   
def subsetsel(content, subset):
    ''' Subset selection for various syntaxes '''
    if subset is None:
        return content
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

def parse_pathrep(pathrep):
    ''' Parse path replacer '''
    if pathrep is None:
        return None
    if type(pathrep) is tuple or isinstance(pathrep, list):
        pathrep_old = pathrep[0].replace('\\', '/')
        pathrep_new = pathrep[1]
    else:
        pathrep_old = pathrep.replace('\\', '/')
        pathrep_new = ''
    return (pathrep_old, pathrep_new)

def parse_content(descriptor, subset=None, pathrep=None, message=None):
    ''' Parse content descriptor '''
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
    if pathrep:
        out = [s.replace('\\', '/').replace(pathrep[0], pathrep[1]) for s in out]
    return out

class img_(html_tag):
    ''' Wrapper that removes empty attributes '''
    tagname = 'img'
    def __init__(self, *args, **kwargs):
        empty_attrs = []
        for attr, value in kwargs.items():
            if not value:
                empty_attrs.append(attr)
        for attr in empty_attrs:
            del kwargs[attr]
        super(img_, self).__init__(*args, **kwargs)

def tda(hrefs, idx, *args, **kwargs):
    ''' Wrapper that adds an anchor tag on demand '''
    if hrefs and idx < len(hrefs) and hrefs[idx]:
        return td(**kwargs).add(a(*args, href=hrefs[idx], target='_blank'))
    else:
        return td(*args, **kwargs)

            
def getjs(filename):
    ''' Read javascript '''
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
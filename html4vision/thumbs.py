
from PIL import Image
import os

class ThumbnailGenerator:
    def __init__(self, thumbs_dir, imsize, imscale, preserve_aspect, quality):
        self.thumbs_dir = thumbs_dir
        self.imsize = imsize
        self.imscale = imscale
        self.preserve_aspect = preserve_aspect
        self.quality = quality

    def make_thumb(self, filename):
        thumb_filename = os.path.join(self.thumbs_dir, filename.replace(os.sep, '___'))
        thumb_ok = True
        st_filename = os.stat(filename)
        try:
            st_thumb = os.stat(thumb_filename)
            if st_thumb.st_mtime < st_filename.st_mtime:
                thumb_ok = False
        except FileNotFoundError:
            thumb_ok = False
        
        if not thumb_ok:
            I = Image.open(filename)
            w0, h0 = I.width, I.height
            if self.imsize is None:
                w, h = w0, h0
            else:
                assert len(self.imsize) == 2
                if self.preserve_aspect:
                    if w0 * 1.0 / h0 > self.imsize[0] * 1.0 / self.imsize[1]:
                        w = self.imsize[0]
                        h = int(h0 * 1.0 / w0 * self.imsize[1] + 0.5)
                    else:
                        h = self.imsize[1]
                        w = int(w0 * 1.0 / h0 * self.imsize[0] + 0.5)
                else:
                    w, h = self.imsize
            
            if self.imscale != 1:
                w = int(w * self.imscale + 0.5)
                h = int(h * self.imscale + 0.5)
            
            I = I.resize((w, h), Image.BILINEAR)
            
            I.save(thumb_filename, quality=self.quality)

        return thumb_filename


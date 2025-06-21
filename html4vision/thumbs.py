"""Thumbnail generation utilities."""

import os
import hashlib

from PIL import Image


def make_thumbnail(
    filepath,
    thumbs_dir,
    imsize,
    imscale,
    preserve_aspect,
    quality,
):
    """Create a thumbnail and return the thumbnail path."""

    if not filepath:
        return ""

    digest = hashlib.sha1(filepath.encode('utf-8')).hexdigest()
    thumb_filename = os.path.join(thumbs_dir, digest + '.webp')

    # Check modification time - regenerate only when outdated or missing.
    thumb_ok = True
    st_filename = os.stat(filepath)
    try:
        st_thumb = os.stat(thumb_filename)
        if st_thumb.st_mtime < st_filename.st_mtime:
            thumb_ok = False
    except (IOError, OSError):  # Python 2 compatibility: FileNotFoundError is not defined
        thumb_ok = False

    if not thumb_ok:
        img = Image.open(filepath)
        w0, h0 = img.width, img.height

        if None in imsize:
            w, h = w0, h0
        else:
            assert len(imsize) == 2
            if preserve_aspect:
                if w0 * 1.0 / h0 > imsize[0] * 1.0 / imsize[1]:
                    w = imsize[0]
                    h = int(h0 * 1.0 / w0 * imsize[1] + 0.5)
                else:
                    h = imsize[1]
                    w = int(w0 * 1.0 / h0 * imsize[0] + 0.5)
            else:
                w, h = imsize

        if imscale != 1:
            w = int(w * imscale + 0.5)
            h = int(h * imscale + 0.5)

        # Pillow introduced the `Resampling` enum in 9.1.0.
        if hasattr(Image, 'Resampling'):
            resample = Image.Resampling.BILINEAR  # type: ignore
        else:
            resample = Image.BILINEAR  # type: ignore
        img = img.resize((w, h), resample)

        img.save(thumb_filename, quality=quality)

    return thumb_filename

"""Thumbnail generation utilities."""

import os
import hashlib
from PIL import Image
from collections.abc import Sequence


def make_thumbnail(
    filepath: str,
    thumbs_dir: str,
    imsize: Sequence[int | float | None],
    imscale: float,
    preserve_aspect: bool,
    quality: int,
) -> str:
    """Create a thumbnail and return the thumbnail path."""

    if not filepath:
        return ''

    digest = hashlib.sha1(filepath.encode('utf-8')).hexdigest()
    thumb_filename = os.path.join(thumbs_dir, digest + '.webp')

    # Check modification time - regenerate only when outdated or missing.
    thumb_ok = True
    st_filename = os.stat(filepath)
    try:
        st_thumb = os.stat(thumb_filename)
        if st_thumb.st_mtime < st_filename.st_mtime:
            thumb_ok = False
    except FileNotFoundError:
        thumb_ok = False

    if not thumb_ok:
        img = Image.open(filepath)
        if None in imsize:
            w, h = img.width, img.height
        else:
            assert len(imsize) == 2
            # Help type checker: elements are not None here
            assert imsize[0] is not None and imsize[1] is not None
            if preserve_aspect:
                if img.width / img.height > imsize[0] / imsize[1]:
                    w = int(imsize[0])
                    h = round(img.height / img.width * float(imsize[0]))
                else:
                    h = int(imsize[1])
                    w = round(img.width / img.height * float(imsize[1]))
            else:
                w = int(imsize[0])
                h = int(imsize[1])
        if imscale != 1:
            w = round(w * imscale)
            h = round(h * imscale)
        img = img.resize((w, h), Image.Resampling.BILINEAR)  # type: ignore[assignment]
        img.save(thumb_filename, quality=quality)

    return thumb_filename

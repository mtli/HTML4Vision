from html4vision import Col, imagetable

cols = [
    Col('id1', 'ID'), # 1-based indexing
    Col('img', 'Detections', 'images/det_*.jpg'),
]

imagetable(
    cols,
    'auto_thumbs.html',
    'Auto Thumbnails',
    precompute_thumbs=True,
    imscale=0.25,
    thumbs_dir='images/thumbs',
    # Optionally limit the number of images loaded in parallel to work around server rate-limiting.
    max_image_load_concurrency=1,
)
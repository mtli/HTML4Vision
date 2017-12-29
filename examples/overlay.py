from html4vision import Col, imagetable

cols = [
    Col('id1', 'ID'), # 1-based indexing
    Col('img', 'Image', 'images/*_image.jpg'),
    Col('img', 'Label', 'images/*_label.png', [0]), # [0] is used to select only the first item
    Col('img', 'Image + Label', 'images/*_image.jpg'),
    Col('overlay', '', 'images/*_label.png', [0], 'opacity: 0.4'),
]

imagetable(cols, 'overlay.html', 'Image Overlay', imscale=1.5)

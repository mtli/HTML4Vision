from html4vision import Col, imagetable

cols = [
    Col('img', 'Image', 'images/road_*_image.jpg'),
    Col('img', 'Label', 'images/road_*_label.png', 1), # 1 is used to select only the first item
    Col('img', 'Image + Label', 'images/road_*_image.jpg'),
    Col('overlay', '', 'images/road_*_label.png', 1, 'opacity: 0.4'),
]

imagetable(cols, 'overlay.html', 'Image Overlay', imscale=1.5, overlay_toggle=True)

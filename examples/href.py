from html4vision import Col, imagetable

cols = [
    # href can even be used on id columns, and uses the same glob pattern as for the content in img column
    Col('id1', 'ID', subset=1, href='images/road_*_image.jpg'),
    Col('img', 'Image + Label', 'images/road_*_image.jpg', 1, href='images/road_*_image.jpg'),
    # for overlay columns, href should be attached to the preceding img column
    Col('overlay', '', 'images/road_*_label.png', 1, 'opacity: 0.4'),
    # href supports a list of URLs, each one for each row
    Col('img', 'Amodel Road Mask', 'images/road_*_amodelroad.png', 1, href=['https://github.com/mtli/HTML4Vision']),
]

imagetable(cols, 'href.html', 'Hyperlink Example')
# Note for image overaly, href conflicts with overlay_toggle=True, since they are both triggered by the mouse click

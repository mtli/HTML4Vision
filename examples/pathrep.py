from os import makedirs
from html4vision import Col, imagetable

cols = [
    Col('id1', 'ID'), # 1-based indexing
    Col('img', 'Label Map', 'images/road_*_label.png'),
    Col('img', 'Road Object Map', 'images/road_*_roadobj.png'),
    Col('img', 'Amodel Road Mask', 'images/road_*_amodelroad.png'),
]

makedirs('another-dir', exist_ok=True)
imagetable(cols, 'another-dir/pathrep.html', 'Path Replace Example', pathrep=('images', '../images'))

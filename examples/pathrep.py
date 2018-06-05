from html4vision import Col, imagetable

cols = [
    Col('id1', 'ID'), # 1-based indexing
    Col('img', 'Label Map', 'images/*_label.png'),
    Col('img', 'Road Object Map', 'images/*_roadobj.png'),
    Col('img', 'Amodel Road Mask', 'images/*_amodelroad.png'),
]

imagetable(cols, 'another-dir/pathrep.html', 'Path Replace Example', pathrep=('images', '../images'))

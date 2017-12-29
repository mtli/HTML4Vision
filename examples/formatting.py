from html4vision import Col, imagetable

cols = [
    Col('id1', 'ID'), # 1-based indexing
    Col('img', 'Label Map', 'images/*_label.png'),
    Col('img', 'Road Object Map', 'images/*_roadobj.png'),
    Col('img', 'Amodel Road Mask', 'images/*_amodelroad.png', None, 'background: yellow'),
]

imagetable(cols, 'formatting.html', style='tbody tr:nth-child(2) {background: green}')

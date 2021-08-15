from html4vision import Col, imagetable

cols = [
    Col('id1', 'ID'), # 1-based indexing
    Col('model', 'Models', '3dmodels/*.glb'),
]

imagetable(cols, 'model.html', 'Interactive 3D Models')

print('If you cannot see the 3D models, please check out README.md for troubleshooting')

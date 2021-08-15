from html4vision import Col, imagetable

cols = [
    Col('id1', 'ID'), # 1-based indexing
    Col('model', 'Models', '3dmodels/*.glb'),
    Col('text', 'Notes', ['If you see empty contents, please check out README.md', '']),
]

imagetable(cols, 'model.html', 'Interactive 3D Models',
    auto_rotate=True, camera_controls=True)

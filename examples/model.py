from html4vision import Col, imagetable

cols = [
    Col('id1', 'ID'), # 1-based indexing
    Col('model', 'Models', 'models/*.glb'),
]

imagetable(
    cols,
    auto_rotate=True,
    camera_controls=True
)

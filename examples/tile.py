from html4vision import imagetile

content = [
    'images/sketch_1_1.svg',
    'images/sketch_1_2.svg',
    'images/sketch_1_3.svg',
    'images/sketch_2_1.svg',
    'images/sketch_2_2.svg',
    'images/sketch_2_3.svg',
]

# get filename without extensions
caption = [path.split('/')[1][:-4] for path in content]

# set hrefs so that clicking an image views it in full size in another tab
href = content               

imagetile(
    content, 3, 
    'tile.html', 'Tiling Example',
    caption=caption, href=href,
    imscale=0.5,
)


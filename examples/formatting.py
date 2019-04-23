from html4vision import Col, imagetable

cols = [
    Col('img', 'Image', 'images/sketch_img_*'),
    Col('img', 'Sketch 1', 'images/sketch_*_1.svg'),
    Col('img', 'Sketch 2', 'images/sketch_*_2.svg'),
    Col('img', 'Sketch 3', 'images/sketch_*_3.svg',
        None, 'background: #e9f9fe'), # set background to light blue for this column
]

imagetable(
    cols,               
    'formatting.html',
    imsize=0,      # resize sketch svg to match corresponding image size (column 0)
    imscale=0.5,   # scale all images to 50%
    # adding image border and box shadows to the entire table
    style='img {border: 1px solid black;-webkit-box-shadow: 2px 2px 1px #ccc; box-shadow: 2px 2px 1px #ccc;}',
)

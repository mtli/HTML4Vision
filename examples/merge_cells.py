from html4vision import Col, imagetable
from itertools import chain

img_paths = ['images/natural_1.jpg', 'images/natural_2.jpg']
num_examples = len(img_paths)

results = [
    [
        ['Exp 1', '0.3', '0.4'],
        ['Exp 2', '0.2', '0.3'],
        ['Exp 3', '0.5', '0.6'],
    ],
    [
        ['Exp 1', '0.7', '0.4'],
        ['Exp 2', '0.1', '0.2'],
        ['Exp 3', '0.9', '0.6'],
    ],
]
num_experiments = len(results[0])
flattened = list(chain(*results))

def pad_empty_rows(items, n):
    return [elem for item in items for elem in ([item] + [''] * n)]

ids = [str(i + 1) for i in range(num_examples)]
multirow_cols = [
    Col('text', 'ID', pad_empty_rows(ids, num_experiments - 1)),
    Col('img', 'Image', pad_empty_rows(img_paths, num_experiments - 1)),
]

regular_cols = [
    Col('text', 'Experiment', [row[0] for row in flattened]),
    Col('text', 'Metric 1', [row[1] for row in flattened]),
    Col('text', 'Metric 2', [row[2] for row in flattened]),
]

table_style = """
    table, th, td {
        border: 1px solid DarkGray;
        border-collapse: collapse;
    }
"""

# Using "{{" and "}}" to escape the f-string syntax.
inline_js = f"""
    document.addEventListener("DOMContentLoaded", function() {{
        var multirowCols = {len(multirow_cols)};
        var rowsToMerge = {num_experiments};

        var tbody = document.querySelector("table.html4vision tbody");
        var rows = tbody.querySelectorAll("tr");

        for (var i = 0; i < rows.length; i += rowsToMerge) {{
            var baseRow = rows[i];

            for (var j = multirowCols - 1; j >= 0; j--) {{
                baseRow.cells[j].rowSpan = rowsToMerge;

                for (var k = 1; k < rowsToMerge; k++) {{
                    if (rows[i + k]) {{
                        rows[i + k].removeChild(rows[i + k].cells[j]);
                    }}
                }}
            }}
        }}
    }});
"""

imagetable(
    cols=multirow_cols + regular_cols,
    out_file='merged_cells.html',
    title='Compare Experiments',
    imsize=(300, 300),  # Define the maximum display size of the image.
    hori_center_img=True,  # Center images horizontally within their cells.
    sort_style="materialize",  # Apply materialize theme from tablesorter.
    style=table_style,  # Enable table borders.
    inline_js=inline_js,  # Merge cells in the table after the page loads.
)

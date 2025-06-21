from html4vision import Col, imagetable

class_names = ['Person', 'Dog', 'Frisbee']
n_class = len(class_names)

pref = open('stats/det-perf.txt').readlines()
n = len(pref) - 1   # discount the header row
ave_perf = n*[None]
class_perf = [n*[None] for i in range(n_class)]
summary_info = (n_class + 1)*[None]

for i, s in enumerate(pref):
    items = s.split(' ')
    if i == 0:      # the header contains dataset summary
        for j in range(n_class + 1):
            summary_info[j] = float(items[j])
    else:           # each row contains result for each data point
        ave_perf[i - 1] = float(items[0])
        for j in range(n_class):
            class_perf[j][i - 1] = float(items[j + 1])

cols = [
    Col('id1', 'ID'),  # 1-based indexing
    Col('img', 'Detection', 'images/det_*.jpg'),
    Col('text', 'Class Average', ave_perf),
]
for i in range(n_class):
    cols.append(Col('text', class_names[i], class_perf[i]))

summary_row = ['S', ''] + summary_info

imagetable(
    cols,
    'sort.html',
    'Sorting Example',
    summary_row=summary_row,    # add a summary row showing overall statistics of the dataset
    summary_color='#fff9b7',    # highlight the summary row
    imscale=0.4,                # scale images to 0.4 of the original size
    sortcol=2,                  # initially sort based on column 2 (class average performance)
    sortable=True,              # enable interactive sorting
    sticky_header=True,         # keep the header on the top
    sort_style='materialize',   # use the theme "materialize" from jquery.tablesorter
    zebra=True,                 # use zebra-striped table
)


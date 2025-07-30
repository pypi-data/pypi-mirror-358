import pandas as pd
import numpy as np
from datetime import datetime
from lushalytics.plotting.DatePlotingClasses import DateLinePlotter, LegendPlotter

import plotly.io as pio
pio.renderers.default = "browser"

labels = ['A', 'B','D','E','F','G','C','X','Z']
all_possible_labels = ['A', 'B', 'C','D','E','F','G','H','I']

# Toy dataset
np.random.seed(0)
date_range = pd.date_range(end=datetime.today(), periods=90)
data = {
    'date': np.random.choice(date_range, 500),
    'category': np.random.choice(all_possible_labels, 500),
    'value_1': np.random.normal(1900, 100, 500),
    'value_2': np.random.normal(200, 20, 500),
    'count_1': np.random.randint(1, 10, 500),
    'count_2': np.random.randint(1, 20, 500),
}
df = pd.DataFrame(data)

# Common config
title = "Sample Weighted Avg Demo"
date_col = 'date'
segment_col = None

legend = LegendPlotter(labels, all_possible_labels).get_legend_figure()
legend.show()

# segments
plotter1 = DateLinePlotter(df.copy(), title, all_possible_labels=all_possible_labels)
f1 = plotter1.plot(
    date_col=date_col,
    filters={'category':labels},
    segment_col='category',
    target_col='value_1',
    count_col='count_1',
    aggregator='weighted_avg',
    granularity='daily',
)
f1.show()

# Weighted avg plot: daily, 1 target, 1 weight
plotter1 = DateLinePlotter(df.copy(), title)
f1 = plotter1.plot(
    date_col=date_col,
    filters={'category':labels},
    target_col='value_1',
    count_col='count_1',
    aggregator='weighted_avg',
    granularity='daily',
)
f1.show()

# Weighted avg plot: weekly, 2 targets, 1 weight
plotter2 = DateLinePlotter(df.copy(), title)
f2 = plotter2.plot(
    date_col=date_col,
    filters={'category':labels},
    target_col=['value_1', 'value_2'],
    count_col='count_1',
    aggregator='weighted_avg',
    granularity='weekly',
)
f2.show()

# Weighted avg plot: monthly, 2 targets, 2 weights
plotter3 = DateLinePlotter(df.copy(), title)
f3 = plotter3.plot(
    date_col=date_col,
    filters={'category':labels},
    target_col=['value_1', 'value_2'],
    count_col=['count_2','count_1'],
    aggregator='weighted_avg',
    granularity='weekly',
)
f3.show()
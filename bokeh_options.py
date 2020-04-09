
import pandas as pd

from bokeh.io import output_file, show
from bokeh.models import BasicTicker, ColorBar, LinearColorMapper, ColumnDataSource, PrintfTickFormatter, LogColorMapper, LogTicker
from bokeh.plotting import figure
from bokeh.transform import transform
import numpy as np
from random import random
from bokeh.palettes import magma

strikes_float = list(np.arange(1.0, 40.0, 0.5))
strikes = [str(s) for s in strikes_float]
expirations = ['20200403',
                    '20200409',
                    '20200417',
                    '20200424',
                    '20200501',
                    '20200508',
                    '20200515',
                    '20200619',
                    '20200918',
                    '20210115',
                    '20220121']

matrix_data = pd.DataFrame(columns=strikes, index=expirations)
for e in expirations:
    matrix_data.loc[e] = np.sin(strikes_float) * random()

matrix_data.columns.name = 'Strike'
matrix_data.index.name = 'Expiration'
p = figure(x_range=(0, len(strikes)), y_range=(0, len(expirations)))


print(str(matrix_data.values.min()))
print(str(matrix_data.values.max()))
# Prepare data.frame in the right format
matrix_data = matrix_data.stack().rename("value").reset_index()



# here the plot :
output_file("myPlot.html")

# You can use your own palette here
colors = ['#a50026', '#d73027', '#f46d43', '#fdae61', '#fee08b', '#d9ef8b', '#a6d96a', '#66bd63', '#1a9850', '#006837']
color_mapper = LinearColorMapper(palette='Magma256', low=-1.0, high=1.0)
colors2 = colors[::-1]

# mapper = LinearColorMapper(
#     palette=colors, low=0, high=255)
# Define a figure


p = figure(
    plot_width=1800,
    plot_height=600,
    title="My plot",
    #x_range=[str(i) for i in strikes],
    x_range=list(matrix_data.Strike.drop_duplicates()),
    y_range=list(matrix_data.Expiration.drop_duplicates()),
    toolbar_location=None,

    x_axis_location="above",
    tools="hover", tooltips=[('bid:', '@value')])
# Create rectangle for heatmap
p.rect(
    x="Strike",
    y="Expiration",
    width=0.9,
    height=0.9,
    # height_units="screen",
    # width_units="screen",
    source=ColumnDataSource(matrix_data),
    line_color=None,
    fill_color=transform('value', color_mapper))
# Add legend
color_bar = ColorBar(color_mapper=color_mapper, ticker=LogTicker(),
                     label_standoff=12, border_line_color=None, location=(0,0),
                     orientation="horizontal")

p.add_layout(color_bar, 'above')

show(p)
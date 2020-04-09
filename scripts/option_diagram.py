from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, Panel, Slope, PreText
from bokeh.layouts import column, row
import numpy as np
import pandas as pd
from bokeh.io import output_file, show
from bokeh.models import BasicTicker, ColorBar, LinearColorMapper, ColumnDataSource, PrintfTickFormatter
from bokeh.plotting import figure
from bokeh.transform import transform
from bokeh.io import output_file, show
from bokeh.layouts import widgetbox
from bokeh.models.widgets import CheckboxGroup
from random import random

class Option_diagram:
    def __init__(self, corr_data):

        self.matrix_data = pd.DataFrame(columns=self.strikes, index=self.expirations)
        for e in self.expirations:
            self.matrix_data.loc[e] = np.sin(self.strikes) * random()


        self.matrix_data.columns.name = 'STRIKES'
        self.matrix_data.index.name = 'EXPIRATIONS'
        p = figure(x_range=(0, len(self.strikes)), y_range=(0, len(self.expirations)))


        self.matrix_data = self.matrix_data.stack().rename("value").reset_index()
        #self.matrix_data.to_pickle("/Users/Uriel/Documents/Python/Ibis/Gemini/matrix_data.pkl")

        #create plot
        colors = ["#75968f", "#a5bab7", "#c9d9d3", "#e2e2e2", "#dfccce", "#ddb7b1", "#cc7878", "#933b41", "#550b1d"]
        mapper = LinearColorMapper(palette=colors, low=-1, high=1)
        colors2 = colors[::-1]

        self.p = figure(plot_width=600, plot_height=600, title="My plot", x_range=list(self.matrix_data.A.drop_duplicates()),y_range=list(self.matrix_data.B.drop_duplicates())[::-1], toolbar_location=None, tools="hover", tooltips=[('coef:', '@value')], x_axis_location="above")

        self.p.rect(
            x="A",
            y="B",
            width=1,
            height=1,
            source=ColumnDataSource(self.matrix_data),
            line_color=None,
            fill_color=transform('value', mapper))

        self.p.text(
            x="A",
            y="B",
            text=str("value"),
            source=ColumnDataSource(self.matrix_data),
            text_color='black',
            text_font_size='8pt',
            x_offset=-15,
            text_align="left")

        color_bar = ColorBar(
            color_mapper=mapper,
            location=(0, 0),
            ticker=BasicTicker(desired_num_ticks=len(colors)))

        def checkbox_group_callback(attr, old, new):
            print(corr_data.columns[new])

        self.checkbox_group = CheckboxGroup(
            labels=list(corr_data.columns), active=[0, 1])

        #show(widgetbox(checkbox_group))
        self.checkbox_group.on_change('active', checkbox_group_callback)

        self.p.add_layout(color_bar, 'right')

        layout = row(self.p, widgetbox(self.checkbox_group))


    def update(self, data):
        pass
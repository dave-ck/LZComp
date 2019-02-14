import plotly.offline as po
import plotly.graph_objs as go
import colorsys

import numpy as np


# pass a dictionary {"groupname1":{"xs":[], "ys":[]}, ... "groupnameN":{"xs":[], "ys":[]}}
def scatter_grouped(data_object):
    data = []
    N = len(data_object)
    index = 0
    for group_name in data_object:
        data.append(go.Scatter(
            x=data_object[group_name]["xs"],
            y=data_object[group_name]["ys"],
            name=group_name,
            mode='markers',
            marker=dict(
                size=10,
                color='rgba({}, {}, {}, .8)'.format(255 * ((0.7 + index / N) % 1), 255 * ((0.7 + index / N) % 1),
                                                    255 * ((0.9 + index / N) % 1)),
                line=dict(
                    width=2,
                    color='rgba({}, {}, {}, .8)'.format(255 * ((0.7 + index / N) % 1), 255 * ((0.7 + index / N) % 1),
                                                    255 * ((0.9 + index / N) % 1))
                )
            )
        ))
        index += 1
    layout = dict(title='Styled Scatter',
                  yaxis=dict(zeroline=False),
                  xaxis=dict(zeroline=False)
                  )
    plotly_fig = go.Figure(data=data, layout=layout)
    po.plot(plotly_fig, show_link=False, filename='basic-scatter-plot.html', )


scatter_grouped({
    "Set A": {"xs": np.random.randn(100), "ys": np.random.randn(100)},
    "Set B": {"xs": np.random.randn(100) - 0.5, "ys": np.random.randn(100) - 0.5},
    "Set C": {"xs": np.random.randn(100) + 0.5, "ys": np.random.randn(100) + 0.5}
})

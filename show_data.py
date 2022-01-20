
import base64
import functools
import mimetypes
from os import sendfile
from flask import (
    Blueprint, flash, redirect, render_template, url_for, request
)
#matlplot based
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import random
import io
import plotly as px

#plotly based
import pandas as pd
import json
import plotly
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.io as pio

#creo un blueprint chiamato auth
#definisco url suo, che verrà preposto ad ogni view 
#che appartiene alla stessa blueprint
bp = Blueprint('show_data', __name__, url_prefix='/show_data')


@bp.route('/<string:s>/show', methods=('GET', 'POST'))
def show(s):
    return render_template('show_data/print.html', string_data=s)


#---------------MATPLOTLIB/SEABORN BASED GRAPH-------#
@bp.route('/plot')
def plot():
    set={}
    plot_img1 = create_figure()
    plot_img2 = create_figure()
    printable = makeimagedata(plot_img1)
    printable2 = makeimagedata(plot_img2)
    return render_template('show_data/print_plot.html', set={'imgdata' : printable, 'imgdata2':printable2 })
    #return Response(output.getvalue(), mimetype='image/png')

#trasforma l'immagine generata da create_figure in uno stream di byte 
def makeimagedata(plot_img):
    img = io.BytesIO()
    plot_img.savefig(img, format ='PNG')
    img.seek(0)
    return base64.b64encode(img.getvalue()).decode()
    #decode('ascii')

def create_figure():
    fig = Figure()
    axis = fig.add_subplot(1, 1, 1)
    xs = range(100)
    ys = [random.randint(1, 50) for x in xs]
    axis.plot(xs, ys)
    return fig

def create_figure_plotly():
    df = pd.DataFrame({
        "Fruit": ["Apples", "Oranges", "Bananas", "Apples", "Oranges", "Bananas"],
        "Amount": [4, 1, 2, 2, 4, 5],
        "City": ["SF", "SF", "SF", "Montreal", "Montreal", "Montreal"]
    })

    df2 = pd.DataFrame({
        "Fruit": ["kiwi", "lime", "Bananas", "kiwi", "lime", "Bananas"],
        "Amount": [4, 1, 2, 2, 4, 5],
        "City": ["SF", "SF", "SF", "Montreal", "Montreal", "Montreal"]
    })

    fig = make_subplots(rows=2, cols=1, shared_xaxes=False)
    fig1 = px.bar(df, x="Fruit", y="Amount", color="City", barmode="group")
    fig2 = px.bar(df2, x="Fruit", y="Amount", color="City", barmode="group")
    fig1.update_xaxes(rangeslider_visible=True)
    fig2.update_xaxes(rangeslider_visible=True)
    
    fig.add_trace(fig1['data'][0], row=1, col=1)
    fig.add_trace(fig2['data'][0], row=2, col=1)

    return fig
    

    #------------------------#
    #You can either render_template('page.html', value_1='something 1', value_2='something 2')
    #and in the template: {{ value_1 }} and {{ value_2}}
    #Or you can pass a dict called e.g. result:
    #render_template('page.html, result={'value_1': 'something 1', 'value_2': 'something 2'})
    #and in the template {{ result.value_1 }} and {{ result.value_2 }}
    #------------------------#


    #---------------MATPLOTLIB/SEABORN BASED GRAPH-------#
@bp.route('/plot2') 
def plot2():
    fig = create_figure_plotly()
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    #return render_template('show_data/print_plotly.html', graphJSON=graphJSON)
    
    return render_template('show_data/print_plotly.html', out=graphJSON)
 



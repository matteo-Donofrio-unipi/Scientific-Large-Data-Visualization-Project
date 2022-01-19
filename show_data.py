
import base64
import functools
import mimetypes
from os import sendfile
from flask import (
    Blueprint, flash, redirect, render_template, url_for, request
)
from flask import Response, make_response
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import random
import io

#creo un blueprint chiamato auth
#definisco url suo, che verrà preposto ad ogni view 
#che appartiene alla stessa blueprint
bp = Blueprint('show_data', __name__, url_prefix='/show_data')



@bp.route('/<string:s>/show', methods=('GET', 'POST'))
def show(s):
    return render_template('show_data/print.html', string_data=s)

@bp.route('/plot')
def plot():
    plot_img = create_figure()
    printable = makeimagedata(plot_img)
    return render_template('show_data/print_plot.html', imgdata = printable)
    #return Response(output.getvalue(), mimetype='image/png')

#trasforma l'immagine generata da create figure in uno stream di byte 
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
    

    #------------------------#
    #You can either render_template('page.html', value_1='something 1', value_2='something 2')
    #and in the template: {{ value_1 }} and {{ value_2}}
    #Or you can pass a dict called e.g. result:
    #render_template('page.html, result={'value_1': 'something 1', 'value_2': 'something 2'})
    #and in the template {{ result.value_1 }} and {{ result.value_2 }}
    #------------------------#
import functools
from flask import (
    Blueprint, flash, redirect, render_template, url_for, request
)

import base64
from io import BytesIO
from flask import Flask
from matplotlib.figure import Figure

#creo un blueprint chiamato auth
#definisco url suo, che verrà preposto ad ogni view 
#che appartiene alla stessa blueprint
bp = Blueprint('get_data', __name__, url_prefix='/get_data')


# @bp.route associates the URL /register with the register view function. When Flask
# receives a request to /auth/register, it will call the register view and use the
# return value as the response
@bp.route('/get_strings', methods=('GET', 'POST'))
def get_strings():
    if request.method == 'POST':
        string = request.form['string']
        error = None

        if not string:
            error = 'String is required.'
            
        if error is None:
            return redirect(url_for('show_data.show', s=string)) #creates the url to go next

        flash(error) #memorizza l'errore che in seguito può essere acceduto e stampato allutente

    return render_template('get_data/gather.html') #POTREI PASSARE PARAMETRI



@bp.route('/plot')
def plot():
# Generate the figure **without using pyplot**.
    fig = Figure()
    ax = fig.subplots()
    ax.plot([1, 2])
    # Save it to a temporary buffer.
    buf = BytesIO()
    fig.savefig(buf, format="png")
    # Embed the result in the html output.
    data = base64.b64encode(buf.getbuffer()).decode("ascii")
    return f"<img src='data:image/png;base64,{data}'/>"





@bp.route('/logout')
def logout():
    return redirect(url_for('index'))

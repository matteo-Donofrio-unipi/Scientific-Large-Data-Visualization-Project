
import functools
from flask import (
    Blueprint, flash, redirect, render_template, url_for, request
)


#creo un blueprint chiamato auth
#definisco url suo, che verrà preposto ad ogni view 
#che appartiene alla stessa blueprint
bp = Blueprint('show_data', __name__, url_prefix='/show_data')



@bp.route('/<string:s>/show', methods=('GET', 'POST'))
def show(s):
    return render_template('show_data/print.html', string_data=s)
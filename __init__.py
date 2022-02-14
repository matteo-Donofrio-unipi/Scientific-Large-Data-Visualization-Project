
import os

from flask import Flask
from flask import (
    Blueprint, flash, redirect, render_template, url_for, request
)

# create and configure the app
def create_app(test_config=None):
    app = Flask(__name__)

    from . import show_data
    app.register_blueprint(show_data.bp)

    # a simple page that says hello
    @app.route('/', methods = ['GET', 'POST'])
    def index():
        
        if request.method == 'POST':
            country_chosen = request.form['country']
            error = None

            if not country_chosen:
                error = 'Country is required.'

            if error is None:
                return redirect(url_for("show_data.standard_topic_selection", country=country_chosen))
        else:
            return render_template('Home.html') #POTREI PASSARE PARAMETRI

    

    return app
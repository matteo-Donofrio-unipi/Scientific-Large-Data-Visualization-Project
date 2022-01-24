
import os

from flask import Flask
from flask import (
    Blueprint, flash, redirect, render_template, url_for, request
)


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)

    # a simple page that says hello
    @app.route('/')
    def index():
        return render_template('Home.html') #POTREI PASSARE PARAMETRI

    from . import get_data
    app.register_blueprint(get_data.bp)

    from . import show_data
    app.register_blueprint(show_data.bp)

    return app
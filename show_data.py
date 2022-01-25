
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


@bp.route('/<string:country>/standard_topic_selection')
def standard_topic_selection(country):
    return render_template('show_data/standard_topic_selection.html', country=country)

@bp.route('/<string:country>/<string:topic>/standard_year_selection')
def standard_year_selection(country, topic):
    return render_template('show_data/standard_year_selection.html', country=country, topic=topic)

@bp.route('/<string:country>/topic3')
def topic3(country):
    return render_template('show_data/topic3.html', country=country)

#rimuovere passaggio di var topic in topic1 e 2

@bp.route('/<string:country>/<string:topic>/<string:year>/topic1')
def topic1(country, topic, year):
    df = pd.read_csv('progetto/datasets/how_produce_energy/'+country+'_how_produce_energy.csv')
    df1 = df[['SIEC',year]] #take only the 2 columns needed 

    df1 = df1.rename(columns={year: "Amount", 'SIEC' : 'Source_of_Energy'}) #rename those columns

    df1 = df1[df1.Source_of_Energy != 'Total'] #remove the row with the total amount
    df1.reset_index(inplace = True, drop = True)

    #define a static list about the type of the source energy (defined manually by looking at the source)
    type_list=['non_renwable','renwable','non_renwable','non_renwable','renwable','non_renwable','non_renwable','renwable','renwable','renwable','non_renwable','non_renwable','non_renwable','non_renwable','non_renwable','non_renwable','non_renwable','non_renwable','non_renwable','non_renwable','non_renwable','non_renwable','non_renwable','renwable','renwable','non_renwable','non_renwable','non_renwable','non_renwable','non_renwable','non_renwable','non_renwable','non_renwable','non_renwable','renwable','non_renwable','non_renwable','non_renwable','renwable','non_renwable','non_renwable','non_renwable','non_renwable','non_renwable','non_renwable','renwable','renwable','renwable','renwable','non_renwable','non_renwable','renwable','renwable','renwable','non_renwable','renwable','non_renwable','renwable']
    df1['Type'] = type_list #add this new column

    #transform the Amount column from strings to float, done using a temporary list
    value_list = df1['Amount']
    value_list = [w.replace(',', '') for w in value_list]
    value_list2=[float(i) for i in value_list]

    df1['Amount'] = value_list2 #assign the column of float
    df1 = df1[df1.Amount > 0] #remove energy source having Amount=0

    fig_funnel = px.funnel(df1, x='Amount', y='Source_of_Energy', color='Type')
    fig_pie = px.pie(df1, values='Amount', names='Type', title='Energy use')

    graphJSON_funnel = json.dumps(fig_funnel, cls=plotly.utils.PlotlyJSONEncoder)
    graphJSON_pie = json.dumps(fig_pie, cls=plotly.utils.PlotlyJSONEncoder)


    return render_template('show_data/topic1.html', country=country, topic=topic, year=year, graphJSON_funnel=graphJSON_funnel, graphJSON_pie=graphJSON_pie)




@bp.route('/topic4')
def topic4():
    return render_template('show_data/topic4.html')

@bp.route('/<string:country>/<string:topic>/<string:year>/topic2')
def topic2(country, topic, year):
    df = pd.read_csv('progetto/datasets/how_energy_is_used/'+country+'_how_energy_is_used.csv')
    df = df[df.Use != 'energy use'] #remove first row (containing total energy used for each year)
    df.reset_index(inplace = True, drop = True)
    df = df[['Use',year]] #take only the 2 columns needed 
    
    type_list = [] #create a new column with the main category for each different use
    for i in range (len(df)):
        if (df.iloc[i]['Use'].startswith('industry')):
            type_list.append('Industry')
        if (df.iloc[i]['Use'].startswith('transport')):
            type_list.append('Transport')
        if (df.iloc[i]['Use'].startswith('other')):
            type_list.append('Other')

        df.iloc[i][year]=df.iloc[i][year].replace(",","") #replace the comma in values in order to convert them to float

        split_string = df.iloc[i]['Use'].split("-", 3) #take only the core of "Use" description
        if(split_string[1]==' non'):
            df.iloc[i]['Use']=split_string[2]
        else:
            df.iloc[i]['Use']=split_string[1]

    df['Type']=type_list #add the new category column 
    df = df.rename(columns={year: "Amount"})

    fig_tree = px.treemap(df, path=['Type','Use'], values = 'Amount', width=800, height=800)

    fig_pie = px.pie(df, values='Amount', names='Type', title='Energy use: aggregated data')


    graphJSON_tree = json.dumps(fig_tree, cls=plotly.utils.PlotlyJSONEncoder)
    graphJSON_pie = json.dumps(fig_pie, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template('show_data/topic2.html', country=country, topic=topic, year=year, graphJSON_tree=graphJSON_tree, graphJSON_pie=graphJSON_pie)




def create_figure_plotly2():
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



@bp.route('/plot2') 
def plot2():
    fig = create_figure_plotly()
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    #return render_template('show_data/print_plotly.html', graphJSON=graphJSON)
    
    return render_template('show_data/print_plotly.html', out=graphJSON)





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



 




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
import numpy as np
import json

#creo un blueprint chiamato auth
#definisco url suo, che verrà preposto ad ogni view 
#che appartiene alla stessa blueprint
bp = Blueprint('show_data', __name__, url_prefix='/show_data')


@bp.route('/info')
def info():
    return render_template('show_data/info.html')


@bp.route('/<string:country>/standard_topic_selection')
def standard_topic_selection(country):
    return render_template('show_data/standard_topic_selection.html', country=country)

@bp.route('/<string:country>/<string:topic>/standard_year_selection')
def standard_year_selection(country, topic):
    return render_template('show_data/standard_year_selection.html', country=country, topic=topic)

@bp.route('/<string:country>/topic3')
def topic3(country):
    #input: chosen country
    #output: plot converted in json (passed to html page)  
    df = pd.read_csv('progetto/datasets/how_produce_energy/'+country+'_how_produce_energy.csv')

    df = df.rename(columns={'SIEC' : 'Source_of_Energy'})#rename the column 
    df = df[df.Source_of_Energy != 'Total'] #remove the total row, not used

    #define if a source of energy is or not Renewable (defined manually, so it's static)
    type_list=['Non Renewable','Renewable','Non Renewable','Non Renewable','Renewable','Non Renewable','Non Renewable','Renewable','Renewable','Renewable','Non Renewable','Non Renewable','Non Renewable','Non Renewable','Non Renewable','Non Renewable','Non Renewable','Non Renewable','Non Renewable','Non Renewable','Non Renewable','Non Renewable','Non Renewable','Renewable','Renewable','Non Renewable','Non Renewable','Non Renewable','Non Renewable','Non Renewable','Non Renewable','Non Renewable','Non Renewable','Non Renewable','Renewable','Non Renewable','Non Renewable','Non Renewable','Renewable','Non Renewable','Non Renewable','Non Renewable','Non Renewable','Non Renewable','Non Renewable','Renewable','Renewable','Renewable','Renewable','Non Renewable','Non Renewable','Renewable','Renewable','Renewable','Non Renewable','Renewable','Non Renewable','Renewable']
    df['Type'] = type_list

    df=df.replace(",","", regex=True) #remove comma from values in order to cast them to float (regex allow to substitute even substrings)

    df_for_area=produce_table_for_topic3(df)

    fig_area = px.area(df_for_area, x="year", y=['Renewable','Non Renewable'], color_discrete_sequence=px.colors.qualitative.Dark2, color_discrete_map={ # replaces default color mapping by value
                "Non Renewable": 'Orange', 'Renewable':'green'}, title='Percentage'  )
    graphJSON_area = json.dumps(fig_area, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template('show_data/topic3.html', country=country, graphJSON_area=graphJSON_area)


#define the new df used by topic3 (a df tracking for each year, the % of Renewable and not Renewable source of energy converted to electricity)
def produce_table_for_topic3(df):
    #input: table containing, for a country, as many rows as many source of energy converted in electricity & as many col as many year considered (1990-2020)
    #       each value is the amount of that source converted in that year
    #output: table containing, for a country, as many rows as years considered & col = tot energy converted, % renewable, % non-renewable
     

    df2 = pd.DataFrame(columns=['year','tot','Renewable','Non Renewable'], index=np.arange(0,(len(df.columns)-2),1)) 
    k=0 #iterator for df2
    tot=0 #for each year, store the total energy produced
    tot_r=0 #for each year, store the total energy produced from Renewable sources
    tot_n=0 #for each year, store the total energy produced from Non Renewable sources
    
    for i in range(len(df.columns)): #for each column in the df 
        
        if(i==0 or i==len(df.columns)-1): #skip the first & last col, since they're Source_of_energy and Type
                pass
        else:

            df[df.columns[i]] = pd.to_numeric(df[df.columns[i]], downcast="float") #cast the year column values into float
            tot = df[df.columns[i]].sum() #compute the total for the year
            
            for j in range(len(df)): #for each row of a year column, count total energy from Renewable and Non Renewable
                if(df.iloc[j]['Type']=='Renewable'): 
                    tot_r+=df.iloc[j][df.columns[i]]
                else:
                    tot_n+=df.iloc[j][df.columns[i]]
            
            #assign the computed values to the k-th row of the new df2
            df2.iloc[k]['tot']=tot
            df2.iloc[k]['year']=df.columns[i]
            df2.iloc[k]['Renewable']=tot_r/tot
            df2.iloc[k]['Non Renewable']=tot_n/tot
            #update variables and iterators
            k=k+1
            tot=0
            tot_r=0
            tot_n=0
    
    return df2

@bp.route('/<string:country>/<string:topic>/<string:year>/topic1')
def topic1(country, topic, year):
    df = pd.read_csv('progetto/datasets/how_produce_energy/'+country+'_how_produce_energy.csv')
    df1 = df[['SIEC',year]] #take only the 2 columns needed 

    df1 = df1.rename(columns={year: "Amount", 'SIEC' : 'Source of Energy'}) #rename those columns

    df1 = df1[df1['Source of Energy'] != 'Total'] #remove the row with the total amount
    df1.reset_index(inplace = True, drop = True)

    #define a static list about the type of the source energy (defined manually by looking at the source)
    type_list=['Non Renewable','Renewable','Non Renewable','Non Renewable','Renewable','Non Renewable','Non Renewable','Renewable','Renewable','Renewable','Non Renewable','Non Renewable','Non Renewable','Non Renewable','Non Renewable','Non Renewable','Non Renewable','Non Renewable','Non Renewable','Non Renewable','Non Renewable','Non Renewable','Non Renewable','Renewable','Renewable','Non Renewable','Non Renewable','Non Renewable','Non Renewable','Non Renewable','Non Renewable','Non Renewable','Non Renewable','Non Renewable','Renewable','Non Renewable','Non Renewable','Non Renewable','Renewable','Non Renewable','Non Renewable','Non Renewable','Non Renewable','Non Renewable','Non Renewable','Renewable','Renewable','Renewable','Renewable','Non Renewable','Non Renewable','Renewable','Renewable','Renewable','Non Renewable','Renewable','Non Renewable','Renewable']
    df1['Type'] = type_list #add this new column

    #transform the Amount column from strings to float (if needed), done using a temporary list
    if(isinstance(df1.iloc[0]['Amount'], str)):
        value_list = df1['Amount']
        value_list = [w.replace(',', '') for w in value_list]
        value_list2=[float(i) for i in value_list]
        df1['Amount'] = value_list2 #assign the column of float

    df1 = df1[df1.Amount > 0] #remove energy source having Amount=0

    fig_funnel = px.funnel(df1, x='Amount', y='Source of Energy', color='Type', color_discrete_sequence=px.colors.qualitative.Dark2, color_discrete_map={ # replaces default color mapping by value
                "Renewable": 'Green', "Non Renewable": 'Orange'})
    fig_pie = px.pie(df1, values='Amount', names='Type', color = 'Type', title='Renewable vs Non Renewable sources of energy comparison', color_discrete_sequence=px.colors.qualitative.Dark2, color_discrete_map={'Renewable':'green','Non Renewable':'orange'})

    graphJSON_funnel = json.dumps(fig_funnel, cls=plotly.utils.PlotlyJSONEncoder)
    graphJSON_pie = json.dumps(fig_pie, cls=plotly.utils.PlotlyJSONEncoder)


    return render_template('show_data/topic1.html', country=country, topic=topic, year=year, graphJSON_funnel=graphJSON_funnel, graphJSON_pie=graphJSON_pie)


def produce_table_for_topic4(df_countries,year):
    #input: year chosen & df empty whose col are = ['Name','Renewable percentage']
    #output: table containing, as many rows as many countries in EU, col = % of renewable energy converted in electricity in the year considered


    #here we build a df st: for each country we def the % of Renewable source of energy used 
    
    #here we build a list of names that will be taken from the json file, a list of country of interest, since the json contains name 
    #of all countries of the world

    name_list_json = ['Albania', 'Austria', 'Belgium', 'Bosnia and Herzegovina', 'Bulgaria', 'Croatia', 'Cyprus', 'Czech Republic', 'Denmark', 'Estonia',
            'Finland', 'France', 'Georgia', 'Germany', 'Greece', 'Hungary', 'Iceland', 'Ireland', 'Italy', 'Latvia', 'Lithuania', 'Luxembourg',
            'Malta', 'Montenegro', 'Netherlands', 'Montenegro', 'The former Yugoslav Republic of Macedonia', 'Norway', 'Poland', 'Portugal',
            'Romania', 'Serbia', 'Slovakia', 'Slovenia', 'Spain', 'Sweden', 'Turkey', 'Ukraine', 'United Kingdom']

    #list of countries of interest, written in the same way of csv datasets, in order to scan the list and access datasets

    name_list_csv = ['Albania', 'Austria', 'Belgium', 'Bosnia_and_Herzegovina', 'Bulgaria', 'Croatia', 'Cyprus', 'Czech_Rep', 'Denmark', 'Estonia',
            'Finland', 'France', 'Georgia', 'Germany', 'Greece', 'Hungary', 'Iceland', 'Ireland', 'Italy', 'Latvia', 'Lithuania', 'Luxembourg',
            'Malta', 'Montenegro', 'Netherlands', 'Montenegro', 'Macedonia', 'Norway', 'Poland', 'Portugal',
            'Romania', 'Serbia', 'Slovakia', 'Slovenia', 'Spain', 'Sweden', 'Turkey', 'Ukraine', 'United_Kingdom']

    #list defined manually to track which source of energy is Renewable or isn't
    type_list=['Non Renewable','Renewable','Non Renewable','Non Renewable','Renewable','Non Renewable','Non Renewable','Renewable','Renewable','Renewable','Non Renewable','Non Renewable','Non Renewable','Non Renewable','Non Renewable','Non Renewable','Non Renewable','Non Renewable','Non Renewable','Non Renewable','Non Renewable','Non Renewable','Non Renewable','Renewable','Renewable','Non Renewable','Non Renewable','Non Renewable','Non Renewable','Non Renewable','Non Renewable','Non Renewable','Non Renewable','Non Renewable','Renewable','Non Renewable','Non Renewable','Non Renewable','Renewable','Non Renewable','Non Renewable','Non Renewable','Non Renewable','Non Renewable','Non Renewable','Renewable','Renewable','Renewable','Renewable','Non Renewable','Non Renewable','Renewable','Renewable','Renewable','Non Renewable','Renewable','Non Renewable','Renewable']

    #this list will contain the % for each country
    value_list=[]

    #initialize the column of countrie's names (use as country name the same name of the json file)
    df_countries['Name']=name_list_json

    for i in (name_list_csv): #for each country
        df = pd.read_csv('progetto/datasets/how_produce_energy/'+i+'_how_produce_energy.csv')
        df = df[['SIEC',year]] #choose only the year of interest
        df=df.replace(",","", regex=True) #prepare data to be cast from string to float
        
        df[year] = pd.to_numeric(df[year], downcast="float")#cast
        df = df[df.SIEC != 'Total'] #remove total col, since not significative
        df['Type'] = type_list #add type col
        
        tot=0
        tot_r=0
        perc_r =0
        
        
        tot = df[year].sum() #take the sum of energy produced in a year
        if(tot > 0):
            for j in range(len(df)):
                if(df.iloc[j]['Type']=='Renewable'):
                    tot_r+=df.iloc[j][year] #take the sum of Renewable energy produced in a year
        
            perc_r = tot_r / tot #compute %
        else:
            perc_r = -1
        value_list.append(perc_r) #add percentage to list
    
    df_countries['Renewable percentage']=value_list #add list to df (now the list has as many % as many countries)

    return df_countries



@bp.route('/<string:country>/<string:topic>/<string:year>/topic4')
def topic4(country, topic, year):
    #input: country and topic are not used (but needed due to simplicity), year is the year chosen by user
    #output: choropleth in json format (passed to html)

    df_countries = pd.DataFrame(columns=['Name','Renewable percentage'])

    df_for_choropleth= produce_table_for_topic4(df_countries,year)

    #here is used a json file defining the european structure, used for build the map,
    #each country in the json file is associated with a set of metadata,
    #metadata of a country i is given by "data['features'][i].keys()",
    #initially, for each country, metadata is only-> ['type', 'properties', 'geometry'],
    #then we add manually another one called 'Name' containing the name of the country, it will be used by the choropleth to find the country
    
    file_json = open('progetto/datasets/countries.json', 'r')

    data_json = json.load(file_json)
    for features in data_json['features']:
        features['Name'] = features['properties']['NAME']

    #now for each country, metadata is-> ['type', 'properties', 'geometry', 'Name']

    #locations & color, refer to the attribute in the dataframe from which take values
    #featureidkey="Name" is used to match the name of the country in the dataframe with the name of the country in the json(they've same attribute name)
    fig_choropleth = px.choropleth(df_countries, geojson=data_json, locations='Name', color='Renewable percentage',
                           color_continuous_scale="speed",
                           range_color=(0, 1),
                           scope="europe",
                           labels={'unemp':'unemployment rate'},
                           featureidkey="Name"
                          )
    fig_choropleth.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

    graphJSON_choropleth = json.dumps(fig_choropleth, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template('show_data/topic4.html', year=year, graphJSON_choropleth=graphJSON_choropleth )

@bp.route('/<string:country>/<string:topic>/<string:year>/topic2')
def topic2(country, topic, year):
    #input: country, topic and year chosen by user
    #output: plot converted in json (passed to html)


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
        if(isinstance(df.iloc[i][year],str)):
            df.iloc[i][year]=df.iloc[i][year].replace(",","") #replace the comma in values in order to convert them to float

        split_string = df.iloc[i]['Use'].split("-", 3) #take only the core of "Use" description
        if(split_string[1]==' non'):
            df.iloc[i]['Use']=split_string[2]
        else:
            df.iloc[i]['Use']=split_string[1]

    df['Type']=type_list #add the new category column 
    df = df.rename(columns={year: "Amount"})

    fig_tree = px.treemap(df, path=['Type','Use'], values = 'Amount', color='Type', color_discrete_sequence=px.colors.qualitative.Dark2, color_discrete_map={ # replaces default color mapping by value
                "Industry": 'Orange', "Other": '#2E91E5', 'Transport':'green'})

    fig_pie = px.pie(df, values='Amount', names='Type', title='Sectors comparison', color='Type', color_discrete_sequence=px.colors.qualitative.Dark2, color_discrete_map={ # replaces default color mapping by value
                "Industry": 'Orange', "Other": '#2E91E5', 'Transport':'green'} )


    graphJSON_tree = json.dumps(fig_tree, cls=plotly.utils.PlotlyJSONEncoder)
    graphJSON_pie = json.dumps(fig_pie, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template('show_data/topic2.html', country=country, topic=topic, year=year, graphJSON_tree=graphJSON_tree, graphJSON_pie=graphJSON_pie)









 



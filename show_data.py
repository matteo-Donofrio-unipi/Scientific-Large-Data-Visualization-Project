from flask import (
    Blueprint, flash, redirect, render_template, url_for, request
)

import pandas as pd
import json
import plotly
import plotly.express as px
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import numpy as np

#bp is a container of views, each of the following bp.route are
#views (functions that produce an output that can be sent to the corresponding html page  ) 
bp = Blueprint('show_data', __name__, url_prefix='/show_data')

#EACH ROUTE IS ASSOCIATED WITH AN HTML PAGE, THIS PAGE CAN BE REACHED BY TYPING THE
# URL OF THAT ROUTE 
# NB: SINCE THE ROUTE BELONG TO THE BLUEPRINT, EACH ROUTE URL IS PREPRENDED BY THE BLUEPRINT URL  

@bp.route('/info')
def info():
    #IS THE VIEW OF THE INFO PAGE 
    return render_template('show_data/info.html')


@bp.route('/ErrorPage')
def ErrorPage():
    #IS THE VIEW OF THE INFO PAGE 
    return render_template('show_data/ErrorPage.html')



#a view can have some input args, they must be the same of the function handling the view
@bp.route('/<string:country>/standard_topic_selection')
def standard_topic_selection(country):
    #IS THE VIEW OF THE TOPIC SELECTION 

    #here the view doesen't have a proper code, just render the proper html page
    #NB: HERE A VARIABLE (OUTPUT) IS PASSED TO THE HTML PAGE
    return render_template('show_data/standard_topic_selection.html', country=country)

@bp.route('/<string:country>/<string:topic>/standard_year_selection', methods=('GET', 'POST'))
def standard_year_selection(country, topic):
    #IS THE VIEW OF THE YEAR SELECTION 

    if request.method == 'POST':
        year_chosen = request.form['year']
        error = None

        if not year_chosen:
            error = 'Year is required.'

        if error is None:
            return redirect(url_for("show_data.topic"+str(topic), year = year_chosen, country = country, topic=topic)) #creates the url to go next

        flash(error) #memorizza l'errore che in seguito può essere acceduto e stampato allutente

    else:
        return render_template('show_data/standard_year_selection.html', country=country, topic=topic)




@bp.route('/<string:country>/<string:topic>/<string:year>/topic1')
def topic1(country, topic, year):
    #IS THE VIEW OF THE GRAPH SHOWING, GIVEN A COUNTRY AND YEAR, HOW IS PRODUCED ELECTRICITY
    #input: country and year chosen (and topic)
    #output: plot converted in json (passed to html page)
    df = pd.read_csv('progetto/datasets/how_produce_energy/'+country+'_how_produce_energy.csv')
    df1 = df[['SIEC',year]] #take only the 2 columns needed

    df1 = df1.rename(columns={year: "Amount", 'SIEC' : 'Source of Energy'}) #rename those columns

    df1 = df1[df1['Source of Energy'] != 'Total'] #remove the row with the total amount
    df1.reset_index(inplace = True, drop = True)

    #define a static list about the type of the source energy (defined manually by looking at the source)
    type_list=['Non Renewable','Renewable','Non Renewable','Non Renewable','Renewable','Non Renewable','Non Renewable','Renewable','Renewable','Renewable','Non Renewable','Non Renewable','Non Renewable','Non Renewable','Non Renewable','Non Renewable','Non Renewable','Non Renewable','Non Renewable','Non Renewable','Non Renewable','Non Renewable','Non Renewable','Renewable','Renewable','Non Renewable','Non Renewable','Non Renewable','Non Renewable','Non Renewable','Non Renewable','Non Renewable','Non Renewable','Non Renewable','Renewable','Non Renewable','Non Renewable','Non Renewable','Renewable','Non Renewable','Non Renewable','Non Renewable','Non Renewable','Non Renewable','Non Renewable','Renewable','Renewable','Renewable','Renewable','Non Renewable','Non Renewable','Renewable','Renewable','Renewable','Non Renewable','Renewable','Non Renewable','Renewable']
    df1['Type'] = type_list #add this new column

    df1=df1.replace(",","", regex=True)
    df1['Amount'] = pd.to_numeric(df1['Amount'], downcast="float")
    df1['Amount']=df1['Amount'].round(0).astype(int)

    df1 = df1[df1.Amount > 0] #remove energy source having Amount=0

    if(len(df1)>0):

        fig_funnel = px.funnel(df1, x='Amount', y='Source of Energy', color='Type', color_discrete_sequence=px.colors.qualitative.Dark2, color_discrete_map={ # replaces default color mapping by value
                    "Renewable": 'Green', "Non Renewable": 'Orange'})
        fig_funnel.update_layout( margin_autoexpand=True, 
        font=dict(
            size=10,
         )) 



        fig_pie = px.pie(df1, values='Amount', names='Type', color = 'Type', color_discrete_sequence=px.colors.qualitative.Dark2, color_discrete_map={'Renewable':'green','Non Renewable':'orange'})
        fig_pie.update_layout(showlegend=False, margin_b=0, margin_t=0,margin_l=0,margin_r=0 )


        graphJSON_funnel = json.dumps(fig_funnel, cls=plotly.utils.PlotlyJSONEncoder)
        graphJSON_pie = json.dumps(fig_pie, cls=plotly.utils.PlotlyJSONEncoder)


        return render_template('show_data/topic1.html', country=country, topic=topic, year=year, graphJSON_funnel=graphJSON_funnel, graphJSON_pie=graphJSON_pie)
    else:
        return render_template('show_data/ErrorPage.html')



def produce_table_for_topic2(df):
    #input: table containing, for a country, as many rows as many source of energy converted in electricity & as many col as many year considered (1990-2020)
    #       each value is the amount of that source converted in that year
    #output: table containing, for a country, as many rows as years considered & col = tot energy converted, % renewable, % non-renewable


    df2 = pd.DataFrame(columns=['year','tot','perc_r','perc_n', 'Renewable', 'Non Renewable'], index=np.arange(0,(len(df.columns)-2),1))
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

            if(tot>0):

                df2.iloc[k]['perc_r']=round(tot_r/tot,2)
                df2.iloc[k]['perc_n']=round(tot_n/tot,2)
                df2.iloc[k]['tot']=int(round(tot,2))
                df2.iloc[k]['year']=df.columns[i]
                df2.iloc[k]['Renewable']=int(round(tot_r,2))
                df2.iloc[k]['Non Renewable']=int(round(tot_n,2))
                #update variables and iterators
                k=k+1
            tot=0
            tot_r=0
            tot_n=0

    return df2



@bp.route('/<string:country>/topic2')
def topic2(country):
    #IS THE VIEW OF THE GRAPH SHOWING, GIVEN A COUNTRY, THE TREND OVER YEARS OF % OF RENWABLE ENERGY
    #input: chosen country
    #output: plot converted in json (passed to html page)
    df = pd.read_csv('progetto/datasets/how_produce_energy/'+country+'_how_produce_energy.csv')

    df = df.rename(columns={'SIEC' : 'Source_of_Energy'})#rename the column
    df = df[df.Source_of_Energy != 'Total'] #remove the total row, not used

    #define if a source of energy is or not Renewable (defined manually, so it's static)
    type_list=['Non Renewable','Renewable','Non Renewable','Non Renewable','Renewable','Non Renewable','Non Renewable','Renewable','Renewable','Renewable','Non Renewable','Non Renewable','Non Renewable','Non Renewable','Non Renewable','Non Renewable','Non Renewable','Non Renewable','Non Renewable','Non Renewable','Non Renewable','Non Renewable','Non Renewable','Renewable','Renewable','Non Renewable','Non Renewable','Non Renewable','Non Renewable','Non Renewable','Non Renewable','Non Renewable','Non Renewable','Non Renewable','Renewable','Non Renewable','Non Renewable','Non Renewable','Renewable','Non Renewable','Non Renewable','Non Renewable','Non Renewable','Non Renewable','Non Renewable','Renewable','Renewable','Renewable','Renewable','Non Renewable','Non Renewable','Renewable','Renewable','Renewable','Non Renewable','Renewable','Non Renewable','Renewable']
    df['Type'] = type_list

    df=df.replace(",","", regex=True) #remove comma from values in order to cast them to float (regex allow to substitute even substrings)

    df_for_area=produce_table_for_topic2(df)

    fig_for_area = go.Figure()

    fig_for_area.add_trace(go.Bar(
        y=df_for_area["Renewable"],
        x=df_for_area.year,
        name="Renewable",
        text=df_for_area['perc_r'],
        textposition='inside',
        marker=dict(
            color='rgba(131,245,44, 0.6)',
            line=dict(color='rgba(131,245,44, 0.5)', width=0.05)
        )
    ))

    fig_for_area.add_trace(go.Bar(
        y=df_for_area["Non Renewable"],
        x=df_for_area.year,
        name="Non Renewable",
        text=df_for_area['perc_n'],
        textposition='inside',
        marker=dict(
            color='rgba(255,117,20, 0.6)',
            line=dict(color='rgba(255,117,20, 0.5)', width=0.05)
        )
    ))

    fig_for_area.update_layout(
        margin_autoexpand=True,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        title=country,
        barmode='stack')


    graphJSON_area = json.dumps(fig_for_area, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template('show_data/topic2.html', country=country, graphJSON_area=graphJSON_area)



@bp.route('/<string:country>/<string:topic>/<string:year>/topic3')
def topic3(country, topic, year):
    #IS THE VIEW OF A GRAPH SHOWING, GIVEN A COUNTRY AND YEAR, HOW ENERGY IS USED (IN WHICH SECTORS)
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

    df['Amount'] = pd.to_numeric(df['Amount'], downcast="float")
    df['Amount']=df['Amount'].round(0).astype(int)

    if(df.Amount.sum() > 0):

        fig_tree = px.treemap(df, path=['Type','Use'], values = 'Amount', color='Type', color_discrete_sequence=px.colors.qualitative.Dark2, color_discrete_map={ # replaces default color mapping by value
                    "Industry": 'Orange', "Other": '#2E91E5', 'Transport':'green'})
        fig_tree.update_layout( margin_l=0) 

        fig_pie = px.pie(df, values='Amount', names='Type', color='Type', color_discrete_sequence=px.colors.qualitative.Dark2, color_discrete_map={ # replaces default color mapping by value
                    "Industry": 'Orange', "Other": '#2E91E5', 'Transport':'green'} )
        fig_pie.update_layout(showlegend=False, margin_b=0, margin_t=0,margin_l=0,margin_r=0) 


        graphJSON_tree = json.dumps(fig_tree, cls=plotly.utils.PlotlyJSONEncoder)
        graphJSON_pie = json.dumps(fig_pie, cls=plotly.utils.PlotlyJSONEncoder)

        return render_template('show_data/topic3.html', country=country, topic=topic, year=year, graphJSON_tree=graphJSON_tree, graphJSON_pie=graphJSON_pie)
    else:
        return render_template('show_data/ErrorPage.html')



@bp.route('/<string:country>/topic4')
def topic4(country):
    #IS THE VIEW OF THE GRAPH SHOWING, GIVEN A COUNTRY, THE TREND OVER YEARS OF HOW ENERGY IS USED, DIVIDED INTO SECTORS
    #input: chosen country
    #output: plot converted in json (passed to html page)

    #create the new dataframe, it will be used in the plot
    # as many rows as many years, cols are overall energy used in each sector
    df_plot = pd.DataFrame(columns=['year','Industry','Other','Transport'], index = range(0,31,1)) #index size = number of years considered

    df = pd.read_csv('progetto/datasets/how_energy_is_used/'+country+'_how_energy_is_used.csv')
    df = df[df.Use != 'energy use'] #remove a not significative row

    #create and fill the Type column (track the sector of each row)
    df['Type']=''

    type_list=[]
    for i in range (len(df)):
        if (df.iloc[i]['Use'].startswith('industry')):
            type_list.append('Industry')
        elif (df.iloc[i]['Use'].startswith('transport')):
            type_list.append('Transport')
        elif (df.iloc[i]['Use'].startswith('other')):
            type_list.append('Other')

    df['Type']=type_list

    df=df.replace(",","", regex=True) #make all values suitable to be cast from string to float

    k=0 #iterator of df_plot

    #for each year, compute the mean consumption of each sector
    for y in range(1990,2021,1):
        year=str(y)
        df[year] = pd.to_numeric(df[year], downcast="float") #cast values
        df[year]=df[year].round(0).astype(int)


        Industry_mean= float( round(df[df.Type == 'Industry'][year].sum(),2) )
        Other_mean = float( round(df[df.Type == 'Other'][year].sum(),2) )
        Transport_mean = float( round(df[df.Type == 'Transport'][year].sum(),2) )

        #fill df_plot by putting for each row: the year, the mean consumption of each sector
        df_plot.iloc[k]['year']=year
        df_plot.iloc[k]['Industry']=Industry_mean
        df_plot.iloc[k]['Other']=Other_mean
        df_plot.iloc[k]['Transport']=Transport_mean
        k+=1


    fig_area = fig_area = px.area(df_plot, x="year", y=['Industry','Other','Transport'], color_discrete_sequence=px.colors.qualitative.Dark2, color_discrete_map={ # replaces default color mapping by value
                    "Industry": 'Orange', "Other": '#2E91E5', 'Transport':'green'},labels={"variable": "Sector: "}   )
    fig_area.update_layout(showlegend=True, margin_l=0, 
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1,
        xanchor="right",
        x=1
    ))

    fig_subplots = make_subplots(rows=3, cols=1)

    fig_subplots.append_trace(go.Scatter(
        x=df_plot["year"],
        y=df_plot['Industry'],
        name='Industry',
        fill='tozeroy',
        marker=dict(
                color='Orange',
                line=dict(color='Orange', width=0.05)
            ),
    ), row=1, col=1)

    fig_subplots.append_trace(go.Scatter(
        x=df_plot["year"],
        y=df_plot['Other'],
        fill='tozeroy',
        name='Other',
        marker=dict(
                color='#2E91E5',
                line=dict(color='#2E91E5', width=0.05)
            ),
    ), row=2, col=1)

    fig_subplots.append_trace(go.Scatter(
        x=df_plot["year"],
        y=df_plot['Transport'],
        fill='tozeroy',
        name='Transport',
        marker=dict(
                color='green',
                line=dict(color='green', width=0.05)
            ),
    ), row=3, col=1)

    fig_subplots.update_layout(showlegend=False, margin_b=0, margin_t=0,margin_l=0,margin_r=0 )

    graphJSON_area = json.dumps(fig_area, cls=plotly.utils.PlotlyJSONEncoder)
    graphJSON_subplots = json.dumps(fig_subplots, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template('show_data/topic4.html', country=country, graphJSON_area=graphJSON_area, graphJSON_subplots=graphJSON_subplots )





def produce_table_for_topic5(df_countries,year):
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

            perc_r = float(str(round(tot_r / tot, 2))) #compute %
        else:
            perc_r = -1
        value_list.append(perc_r) #add percentage to list

    df_countries['Renewable percentage']=value_list #add list to df (now the list has as many % as many countries)

    return df_countries


@bp.route('/<string:country>/<string:topic>/<string:year>/topic5')
def topic5(country, topic, year):
    #IS THE VIEW OF THE GRAPH SHOWING, GIVEN A YEAR, THE % OF RENEWABLE SOURCES OF ENERGY CONVERTED BY ALL EUROPEAN COUNTRIES
    #input: country and topic are not used (but needed due to simplicity), year is the year chosen by user
    #output: choropleth in json format (passed to html)

    df_countries_5 = pd.DataFrame(columns=['Name','Renewable percentage'])

    df_for_choropleth_5= produce_table_for_topic5(df_countries_5,year)

    df_topic6 = pd.DataFrame(columns=['Name','Total Consumption'])

    df_for_choropleth_6= produce_table_for_topic6(df_topic6,year)

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
    fig_choropleth_5 = px.choropleth(df_for_choropleth_5, geojson=data_json, locations='Name', color='Renewable percentage',
                           color_continuous_scale="speed",
                           range_color=(0, 1),
                           scope="europe",
                           featureidkey="Name"
                          )
    fig_choropleth_5.update_layout(
        title='Percentage of renwable energy converted',
        margin_autoexpand=True,
        font=dict(size=10),
    )


    fig_choropleth_6 = px.choropleth(df_for_choropleth_6, geojson=data_json, locations='Name', color='Total Consumption',
                           color_continuous_scale="matter",
                           range_color=(0, 100000),
                           scope="europe",
                           labels={'Total Consumption':'Total Consumption'},
                           featureidkey="Name"
                          )
    fig_choropleth_6.update_layout(
        title='Total amount of energy used',
        margin_autoexpand=True,
        font=dict(size=10),
    )

    graphJSON_choropleth_5 = json.dumps(fig_choropleth_5, cls=plotly.utils.PlotlyJSONEncoder)
    graphJSON_choropleth_6 = json.dumps(fig_choropleth_6, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template('show_data/topic5.html', year=year, country=country, graphJSON_choropleth_5=graphJSON_choropleth_5, graphJSON_choropleth_6=graphJSON_choropleth_6 )


def produce_table_for_topic6(df_countries, year):
    #input: year chosen & df empty whose col are = ['Name','Total Consumption']
    #output: table containing, as many rows as many countries in EU, col = Total Consumption of energy


    #here we build a df st: for each country we def the Total Consumption of energy

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

    #this list will contain the Total Consumption of energy for each country
    value_list=[]


    df_countries['Name']=name_list_json

    for i in (name_list_csv):
        df = pd.read_csv('progetto/datasets/how_energy_is_used/'+i+'_how_energy_is_used.csv')
        df = df[['Use',year]]
        df=df.replace(",","", regex=True)

        df[year] = pd.to_numeric(df[year], downcast="integer")
        df = df[df.Use != 'energy use']

        tot=0

        tot = int(df[year].sum())
        if(tot==0):
            tot = -1
        value_list.append(tot)

    df_countries['Total Consumption']=value_list
    return df_countries


@bp.route('/<string:country>/<string:topic>/<string:year>/topic6')
def topic6(country, topic, year):
    #IS THE VIEW OF THE GRAPH SHOWING, GIVEN A YEAR, THE OVERALL ENERGY CONSUMED BY ALL EUROPEAN COUNTRIES
    #input: country and topic are not used (but needed due to simplicity), year is the year chosen by user
    #output: choropleth in json format (passed to html)

    df_topic6 = pd.DataFrame(columns=['Name','Total Consumption'])

    df_for_choropleth_6= produce_table_for_topic6(df_topic6,year)

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
    fig_choropleth = px.choropleth(df_for_choropleth, geojson=data_json, locations='Name', color='Total Consumption',
                           color_continuous_scale="matter",
                           range_color=(0, 100000),
                           scope="europe",
                           labels={'Total Consumption':'Total Consumption'},
                           featureidkey="Name"
                          )
    fig_choropleth.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

    graphJSON_choropleth = json.dumps(fig_choropleth, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template('show_data/topic6.html', year=year, graphJSON_choropleth=graphJSON_choropleth )









 



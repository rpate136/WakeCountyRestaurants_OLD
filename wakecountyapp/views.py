from django.shortcuts import render
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import requests

#-------------------------------------------------------------------------------------------------------
# Functions to set up Dataframes. 

def getRestaurantsDf():
    print('Fetching restaurants data...')
    val = 'https://opendata.arcgis.com/datasets/124c2187da8c41c59bde04fa67eb2872_0.geojson'

    # Sending get request and saving the response as response object
    # extracting data in json 
    r = requests.get(url = val)
    rows = []
    data = r.json()['features']
    for d in data:
        rows.append(d['properties'])
    df = pd.DataFrame(rows)
    df['CITY'] = df['CITY'].str.strip()
    df = df.apply(lambda x: x.astype(str).str.upper())
    df = df.replace("FUQUAY-VARINA", "FUQUAY VARINA")
    df['year'] = pd.DatetimeIndex(df['RESTAURANTOPENDATE']).year
    df['month'] = pd.DatetimeIndex(df['RESTAURANTOPENDATE']).month
    print('restaurants df shape:', df.shape)
    return df

def getOneRestaurantInspDf(id):
    print('Fetching restaurants data...')
    id = "04092016133"
    val = f"https://maps.wakegov.com/arcgis/rest/services/Inspections/RestaurantInspectionsOpenData/MapServer/2/query?where=HSISID='{id}'&where=1%3D1&outFields=*&outSR=4326&f=json"


    # Sending get request and saving the response as response object
    # extracting data in json 
    r = requests.get(url = val)
    rows = []
    data = r.json()['features']
    for d in data:
        rows.append(d['attributes'])
    df = pd.DataFrame(rows)
    print('restaurants df shape:', df.shape)
    return df


#-------------------------------------------------------------------------------------------------------
# Django views to display elements on the website

# Methods that return the base HTML's
def home (request):
    return render(request,"navbar.html")

def searchRestuarents(request):
    return render(request,"search.html")

def oneRestaurant(request):
    return render(request,"oneRest.html")

def overallAnalysis(request):
    return render(request,"overallAnalysis.html")

# Methods that return the elements when forms are submitted

def plot (request):
    fig = go.Figure(
        data=[go.Bar(y=[2, 1, 3])],
        layout_title_text="A Figure Displayed with fig.show()"
    )
    fig =px.scatter(x=range(10), y=range(10))
    graph = fig.to_html(full_html=False, default_height=500, default_width=700)
    context = {'graph': graph}
    return render(request,"home.html",context)

def searchRestuarentsOutput(request):
    restaurants = getRestaurantsDf()
    inp1 = request.POST.get('CityName')
    inp2 = request.POST.get('param1')
    print(inp1, "  ", inp2)
    df_search = restaurants.loc[(restaurants['CITY'] == inp1) & (restaurants['year'] == int(inp2))]
    df_search = df_search.drop(["OBJECTID","RESTAURANTOPENDATE","X","Y","GEOCODESTATUS","month"] , axis =1)
    df_search_html =  df_search.to_html()

    return render(request,"search.html",{"df_search_html":df_search_html})

def oneRestaurantOutput(request):
    #get the input
    inp1 = request.POST.get('HSISIDparm1')
    #set the dataframe with HSISID input
    df = getOneRestaurantInspDf(inp1)
    dfCriticalYes = df[df['CRITICAL'] == "Yes"]
    #category pie chart
    categoryDF = pd.DataFrame(dfCriticalYes['CATEGORY'].value_counts())
    categoryDF = categoryDF.reset_index()
    fig = px.pie(categoryDF, values='CATEGORY', names='index', title='Breakdown of Category of risk factor for Critical Inspections')
    graph = fig.to_html(full_html=False, default_height=500, default_width=700)
    #number of critical inspections
    criticalDF = (pd.DataFrame(df['CRITICAL'].value_counts()))
    criticalDF = criticalDF.to_html()
    graphs = {'graph': graph , 'critical': criticalDF}

    return render(request,"oneRest.html",graphs)


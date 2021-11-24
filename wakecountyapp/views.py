from django.shortcuts import render
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import requests
# Create your views here.


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

restaurants = getRestaurantsDf()


#-------------------------------------------------------------------------------------------------------

def searchRestuarents(request):
    #city = City
    df_Incity = restaurants.loc[(restaurants['CITY'] == "RALEIGH") & (restaurants['year'] == 2020)]
    df_Incity_html =  df_Incity.to_html()

    return render(request,"search.html",{"df_Incity_html":df_Incity_html})

def oneRestaurant(request):

    return render(request,"oneRest.html",{})

def home (request):
    print("hello")
    return render(request,"navbar.html")

def search (request):
    print("hello")
    return render(request,"search.html")

def plot (request):
    fig = go.Figure(
        data=[go.Bar(y=[2, 1, 3])],
        layout_title_text="A Figure Displayed with fig.show()"
    )
    fig =px.scatter(x=range(10), y=range(10))
    graph = fig.to_html(full_html=False, default_height=500, default_width=700)
    context = {'graph': graph}
    return render(request,"home.html",context)
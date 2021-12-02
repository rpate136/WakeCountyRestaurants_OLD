from django.shortcuts import render
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import requests

#-------------------------------------------------------------------------------------------------------
# Methods to set up Dataframes. 

# API call to get the restaurants in wake county [Table title : Restaurants in Wake County]
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

# API call to get the inspection data for a specific restaurants in wake county [Table title : Food Inspection Violations]
def getOneRestaurantInspDf(id):
    print('Fetching restaurants data...')
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

# API call to get the inspection data for all restaurants in wake county [Table title : Food Inspection Violations](reading 420K~ rows)
def getInspectionDf(forceFetch=False):
    print('Fetching restaurants data...')
    val = 'https://opendata.arcgis.com/datasets/9b04d0c39abd4e049cbd4656a0a04ba3_2.geojson'

    # Sending get request and saving the response as response object
    # extracting data in json 
    r = requests.get(url = val)
    rows = []
    data = r.json()['features']
    for d in data:
        rows.append(d['properties'])
    df = pd.DataFrame(rows)
    print('restaurants df shape:', df.shape)
    print('Done')
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

# Methods that return the elements when forms are submitted

# return the form submitted on the Search restaurants page
def searchRestuarentsOutput(request):
    restaurants = getRestaurantsDf()
    inp1 = request.POST.get('CityName')
    inp2 = request.POST.get('year')
    df_search = restaurants.loc[(restaurants['CITY'] == inp1) & (restaurants['year'] == int(inp2))]
    df_search = df_search.drop(["OBJECTID","RESTAURANTOPENDATE","X","Y","GEOCODESTATUS","month"] , axis =1)
    df_search = df_search.sort_values(by=['NAME'])
    df_search_html =  df_search.to_html(index=False)

    return render(request,"search.html",{"df_search_html":df_search_html})

# return the form submitted on the One restaurant inspection page
def oneRestaurantOutput(request):
    #get the input
    inp1 = request.POST.get('HSISIDparm1')
    #set the dataframe with HSISID input
    df = getOneRestaurantInspDf(inp1)
    dfCriticalYes = df[df['CRITICAL'] == "Yes"]
    
    #category pie chart
    categoryDF = pd.DataFrame(dfCriticalYes['CATEGORY'].value_counts())
    categoryDF = categoryDF.reset_index()
    fig1 = px.pie(categoryDF, values='CATEGORY', names='index', title='Breakdown of Category of risk factor for Critical Inspections')
    graph = fig1.to_html(full_html=False, default_height=500, default_width=700)
    
    #number of critical inspections
    criticalDF = (pd.DataFrame(df['CRITICAL'].value_counts()))
    criticalDF = criticalDF.to_html()
    
    #description of inspection findings totals
    descDF = pd.DataFrame(dfCriticalYes['SHORTDESC'].value_counts())
    descDF.index.name = 'Description'
    descDF = descDF.to_html()
    
    #violation type total 
    violationDF = pd.DataFrame(df['VIOLATIONTYPE'].value_counts())
    violationDF.index.name = 'Violation Type'
    violationDF = violationDF.rename(columns={"VIOLATIONTYPE":'TOTAL'})
    violationDF = violationDF.reset_index()
    fig2 = px.bar(violationDF, x='Violation Type', y='TOTAL', title='Breakdown of Category of risk factor for Critical Inspections')
    violationBar = fig2.to_html(full_html=False, default_height=500, default_width=700)
 
    graphs = {'graph': graph , 'critical': criticalDF, 'desc': descDF, 'violation':violationBar}
    return render(request,"oneRest.html",graphs)

# return the form submitted on the Restaurant in Wake County Analysis page
def RestaurantAnalysis(request):
    df = getRestaurantsDf()
    #Number of Resturants in city
    df['CITY'] = df['CITY'].str.strip()
    cityDF = pd.DataFrame(df['CITY'].value_counts())
    cityDF = cityDF[cityDF['CITY'] >= 3]
    cityDF = cityDF.reset_index()
    cityDF = cityDF.rename(columns={"index":'City' , "CITY": 'Total'})  
    city_fig = px.bar(cityDF, x='City', y='Total', title='Number of restaurants in each city')
    city_fig = city_fig.to_html()
    
    #Types of Restuarent pie chart 
    facttypeDF = pd.DataFrame(df['FACILITYTYPE'].value_counts())
    facttypeDF = facttypeDF.reset_index()
    facttype_fig = px.pie(facttypeDF, values='FACILITYTYPE', names='index', title='Breakdown of food place types')
    facttype_fig = facttype_fig.to_html(full_html=False, default_height=500, default_width=700)
    
    #Number of restuarants over time in wake county
    numRestWTime = pd.DataFrame(df['year'].value_counts())
    numRestWTime = numRestWTime.reset_index()
    numRestWTime = numRestWTime.rename(columns={"index":'Year' , "year": 'Number Of restaurants'})  
    numRestWTime = numRestWTime.sort_values(by=['Year'])
    numRestWTime_fig = px.line(numRestWTime, x='Year', y="Number Of restaurants",title='Number of Restuarants with time in Wake County')
    numRestWTime_fig = numRestWTime_fig.to_html(full_html=False, default_height=500, default_width=800)
    
    #Map that displays the resturants 
    mapDF = df[['HSISID','NAME','CITY','X','Y','GEOCODESTATUS','FACILITYTYPE']].copy()
    mapDF['X'] = mapDF['X'].astype(float, errors = 'raise')
    mapDF['Y'] = mapDF['Y'].astype(float, errors = 'raise')
    token = "pk.eyJ1Ijoia2FyZGluaTMwMSIsImEiOiJja3dvZG84a2UwMXVwMm5zNm55aTcwcDcyIn0.82Pz65yxgNlgN60FhaS3OQ"
    px.set_mapbox_access_token(token)                    
    mapDF_fig = px.scatter_mapbox(mapDF,lat=mapDF['Y'],lon=mapDF['X'], hover_name="NAME",color = mapDF["FACILITYTYPE"],zoom = 7)
    mapDF_fig = mapDF_fig.to_html(full_html=False, default_height=500, default_width=1500)

    graphs = {'facilityType': facttype_fig , 'numRestinCity':city_fig , 'numOfRest':numRestWTime_fig , 'map': mapDF_fig}
    return render(request,"RestInWakeAnalysis.html",graphs)

# return the form submitted on the Overall Inspection Analysis
def overallAnalysis(request):
    df = getInspectionDf()
    restaurants = getRestaurantsDf()

    #bar graph of number of inspections by inspector
    inspector = pd.DataFrame(df['INSPECTEDBY'].value_counts())
    inspector = inspector.reset_index()
    inspector = inspector.rename(columns={"INSPECTEDBY":'TOTAL' , 'index':'Inspector Name'})
    inspector = inspector.head(20)
    inspector_fig = px.bar(inspector, x='Inspector Name', y='TOTAL', title='Number of inspections by Inspector')
    inspector_fig = inspector_fig.to_html()
    
    #Bar grap of total violation by violation type code
    violationCode = pd.DataFrame(df['VIOLATIONCODE'].value_counts())
    violationCode = violationCode.reset_index()
    violationCode = violationCode.rename(columns={"VIOLATIONCODE":'TOTAL' , 'index':'Violation Code'})
    violationCode = violationCode.head(20)
    violationCode_fig = px.bar(violationCode, x='Violation Code', y='TOTAL', title='Total of Violation Types')
    violationCode_fig = violationCode_fig.to_html()
    
    #Table that shows the top 20 Restuarent with the highest amount of inspections
    dfCriticalYes = df[df['CRITICAL'] == "Yes"]
    criticalDF = pd.DataFrame(dfCriticalYes['HSISID'].value_counts())
    criticalDF = criticalDF.reset_index()
    criticalDF = criticalDF.rename(columns={"HSISID":'TOTAL' , 'index':'HSISID'})
    criticalDF = criticalDF.head(20)
    criticalDF.set_index('HSISID', inplace=True)
    restaurantsBasicInfo = restaurants[["NAME",'HSISID','ADDRESS1','CITY']]
    restaurantsBasicInfo.set_index('HSISID', inplace=True)
    topInspecRestDF = criticalDF.merge(restaurantsBasicInfo, on = 'HSISID' , how='left')
    topInspecRestDF_fig = topInspecRestDF.to_html()

    graphs = {'inspector':inspector_fig , 'violation': violationCode_fig, 'top20Rest': topInspecRestDF_fig}
    return render(request,"overallAnalysis.html",graphs)
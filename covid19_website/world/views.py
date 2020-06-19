from django.shortcuts import render
import numpy as np 
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.offline as opy
import requests
import folium

# Create your views here.
def country_detail(request):
    country = request.POST['country']

    r = requests.get('https://www.trackcorona.live/api/countries')
    df_coun = r.json()
    df_coun = pd.DataFrame(df_coun['data'])

    check = False
    write = False
    country_code = ''

    if country.lower() in 'uk' or country.lower() in 'united kingdom' or country.lower() in 'england' or country.lower() in 'britain':
        check = True
        temp = df_coun[df_coun['location'] == 'UK']
        country = temp['location'].iloc[0]
        country_code = temp['country_code'].iloc[0]

    elif country.lower() in 'america' or country.lower() in 'united states of america' or country.lower() in 'usa':
        check = True
        temp = df_coun[df_coun['location'] == 'United States']
        country = temp['location'].iloc[0]
        country_code = temp['country_code'].iloc[0]

    else:
        for i in range(len(df_coun)):
            if country.lower() in df_coun['location'][i].lower():
                check = True
                country = df_coun['location'][i]
                country_code = df_coun['country_code'][i]

    if check:
        temp = df_coun[df_coun['location'] == country]
        Date = temp.iloc[0,7].split()[0]
        Total = temp.iloc[0,4]
        Discharged = temp.iloc[0,6]
        Deaths = temp.iloc[0,5]
        Active = Total - (Discharged + Deaths)

        r = requests.get('https://www.trackcorona.live/api/cities')
        df_city = r.json()
        df_city = pd.DataFrame(df_city['data'])


        df_city = df_city[df_city['country_code'] == country_code]
        if len(df_city) > 0:
            write = True
        df_city = df_city.sort_values(by=['confirmed','dead'], ascending = False)
        df_city['recovered'].fillna(value = 0, inplace = True)
        df_city['dead'].fillna(value = 0, inplace = True)
        df_city = df_city[:200]

        rows = []
        for i in range(len(df_city)):
            inn = []
            inn.append(df_city.iloc[i,0])
            inn.append(int(df_city.iloc[i,4]))
            inn.append(int(df_city.iloc[i,6]))
            inn.append(int(df_city.iloc[i,5]))
            rows.append(inn)

        temp = df_city[:30]


        fig_total = px.bar(temp, x = 'location', y = 'confirmed', hover_data=['confirmed', 'recovered', 'dead'], template = 'plotly_dark', title = '30 most affected State/City of {}'.format(country))
        fig_total = opy.plot(fig_total, auto_open=False, output_type='div')
        fig_total

        map = folium.Map(location=[df_coun[df_coun['country_code'] == country_code]['latitude'], df_coun[df_coun['country_code'] == country_code]['longitude']], tiles='CartoDB dark_matter', zoom_start=4)
        for lat, lon, value, name in zip(df_city['latitude'], df_city['longitude'], df_city['confirmed'], df_city['location']):
            folium.CircleMarker([lat, lon], radius = 3, popup= ('<strong>State: </strong>'+name+'<br>' '<strong>Confirmed: </strong>'+str(value)), color = 'red', fill_color = 'red', fill_opacity=0.3).add_to(map)
        map = map._repr_html_()
        

        return render(request, 'rest_state.html', {'check': check, 'write': write, 'Country': country, 'Date': Date, 'Total': Total, 'Active': Active, 
                        'Discharged': Discharged, 'Deaths': Deaths, 'rows': rows, 'fig': fig_total, 'map': map})

        
    else:
        return render(request, 'rest_state.html', {'check': check})
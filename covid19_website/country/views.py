from django.shortcuts import render
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import plotly.graph_objects as go
import plotly.offline as opy
import requests
import folium

# Create your views here.
def index(request):
    return render(request, 'index.html')


def india_index(request):

    ind_country = pd.read_json('https://api.rootnet.in/covid19-in/stats/latest')
    ind_regional = ind_country.iloc[0,1]
    ind_regional = pd.DataFrame(ind_regional)


    ind_regional.dropna(thresh=3, inplace = True)
    ind_regional['totalConfirmed'] = ind_regional['totalConfirmed'].astype('int')
    ind_regional['discharged'] = ind_regional['discharged'].astype('int')
    ind_regional['deaths'] = ind_regional['deaths'].astype('int')

    ind_summary = ind_country.iloc[2,1]
    ind_summary = pd.DataFrame(ind_summary, index=[0])

    Date = ind_country['lastRefreshed']['unofficial-summary'][:10]
    Total = str(ind_summary['total'][0])
    Active = str(ind_summary['active'][0])
    Discharged = str(ind_summary['recovered'][0])
    Deaths = str(ind_summary['deaths'][0])

    rows = []
    for i in range(len(ind_regional)):
        inn = []
        inn.append(ind_regional.iloc[i,4])
        inn.append(ind_regional.iloc[i,5])
        inn.append(ind_regional.iloc[i,2])
        inn.append(ind_regional.iloc[i,3])
        rows.append(inn)


    raw_daily = pd.read_json('https://api.rootnet.in/covid19-in/stats/history')

    regional_daily = raw_daily.iloc[0,1]['summary']
    regional_daily = pd.DataFrame(regional_daily, index = [0])
    regional_daily['Date'] = raw_daily.iloc[0,1]['day']
    regional_daily['Daily Confirmed Cases'] = regional_daily['total']
    regional_daily['Daily Cured Cases'] = regional_daily['discharged']
    regional_daily['Daily Deaths'] = regional_daily['deaths']


    for i in range(1,len(raw_daily)):
        temp = raw_daily.iloc[i,1]['summary']
        temp = pd.DataFrame(temp, index = [i])
        temp['Date'] = raw_daily.iloc[i,1]['day']
        if temp['total'][i] is None:
            temp['Daily Confirmed Cases'] = regional_daily['total'][i-1]
            temp['total'] = ind_summary['total'][0]
        else:
            temp['Daily Confirmed Cases'] = temp['total'][i] - regional_daily['total'][i-1]
        if temp['discharged'][i] is None:
            temp['Daily Cured Cases'] = regional_daily['Daily Cured Cases'][i-1]
            temp['discharged'] = ind_summary['recovered'][0]
        else:
            temp['Daily Cured Cases'] = (temp['discharged'][i] - regional_daily['discharged'][i-1])
        if temp['deaths'][i] is None:
            temp['Daily Deaths'] = regional_daily['Daily Deaths'][i-1]
            temp['deaths'] = ind_summary['deaths'][0]
        else:
            temp['Daily Deaths'] = abs(temp['deaths'][i] - regional_daily['deaths'][i-1])
        regional_daily = pd.concat([regional_daily, temp])


    regional_daily = regional_daily.rename(columns={'total':'Total Confirmed Cases', 'discharged':'Discharged', 'deaths':'Deaths'})
    regional_daily.drop(['confirmedCasesIndian', 'confirmedCasesForeign', 'confirmedButLocationUnidentified'], axis = 1, inplace = True)


    fig_total = px.scatter(regional_daily, x = 'Date', y = 'Total Confirmed Cases', title='Growth in COVID19 Cases',
                            color = 'Total Confirmed Cases', color_continuous_scale='Bluered_r', template = 'plotly_dark')
    fig_total = opy.plot(fig_total, auto_open=False, output_type='div')
    fig_total


    fig_daily = px.bar(regional_daily, x = 'Date', y = 'Daily Confirmed Cases', title='Daily Confirmed COVID19 Cases',
                        color = 'Daily Confirmed Cases',color_continuous_scale='Bluered_r',
                        hover_data=['Date', 'Total Confirmed Cases', 'Daily Confirmed Cases'], template = 'plotly_dark')
    fig_daily = opy.plot(fig_daily, auto_open=False, output_type='div')
    fig_daily


    fig_daily_cured = px.bar(regional_daily, x = 'Date', y = 'Daily Cured Cases', title = 'Daily Cured Cases',
                                color = 'Daily Cured Cases',color_continuous_scale='Bluered_r',
                                hover_data=['Date', 'Daily Cured Cases', 'Discharged'], template = 'plotly_dark')
    fig_daily_cured = opy.plot(fig_daily_cured, auto_open=False, output_type='div')
    fig_daily_cured


    fig_daily_death = px.bar(regional_daily, x = 'Date', y = 'Daily Deaths', template = 'plotly_dark', title = 'Daily Deaths',
                                color = 'Daily Deaths',color_continuous_scale='Bluered_r',)
    fig_daily_death = opy.plot(fig_daily_death, auto_open=False, output_type='div')
    fig_daily_death


    fig_daily_all = go.Figure()
    fig_daily_all.add_trace(go.Line(x = regional_daily['Date'], y = regional_daily['Daily Confirmed Cases'], mode = 'markers+lines', name = 'Daily Confirmed Cases'))
    fig_daily_all.add_trace(go.Line(x = regional_daily['Date'], y = regional_daily['Daily Deaths'], mode = 'markers+lines', name = 'Daily Deaths'))
    fig_daily_all.add_trace(go.Line(x = regional_daily['Date'], y = regional_daily['Daily Cured Cases'], mode = 'markers+lines', name = 'Daily Cured Cases'))
    fig_daily_all.update_layout(title = 'Daily Confirmed Cases vs Recoveries vs Deaths', xaxis_title="Date", yaxis_title="Count", template = 'plotly_dark')
    fig_daily_all = opy.plot(fig_daily_all, auto_open=False, output_type='div')
    fig_daily_all


    fig_total_all = go.Figure()
    fig_total_all.add_trace(go.Line(x = regional_daily['Date'], y = regional_daily['Total Confirmed Cases'], mode = 'markers+lines', name = 'Confirmed Cases'))
    fig_total_all.add_trace(go.Line(x = regional_daily['Date'], y = regional_daily['Deaths'], mode = 'markers+lines', name = 'Deaths'))
    fig_total_all.add_trace(go.Line(x = regional_daily['Date'], y = regional_daily['Discharged'], mode = 'markers+lines', name = 'Cured/Discharged'))
    fig_total_all.update_layout(title = 'Total Confirmed Cases vs Recoveries vs Deaths', xaxis_title="Date", yaxis_title="Count", template = 'plotly_dark')
    fig_total_all = opy.plot(fig_total_all, auto_open=False, output_type='div')
    fig_total_all


    fig = [fig_total, fig_daily, fig_daily_cured, fig_daily_death, fig_daily_all, fig_total_all]


    r = requests.get('https://www.trackcorona.live/api/provinces')
    df_state_lev = pd.DataFrame(r.json()['data'])
    df_in = df_state_lev[df_state_lev['country_code'] == 'in'].copy()


    map = folium.Map(location=[22, 80], zoom_start=4.5, tiles='CartoDB dark_matter')
    for lat, lon, value, name in zip(df_in['latitude'], df_in['longitude'], df_in['confirmed'], df_in['location']):
        folium.CircleMarker([lat, lon], radius=value*0.001, popup = ('<strong>State</strong>: ' + str(name).capitalize() + '<br>''<strong>Total Cases</strong>: ' + str(value) + '<br>'),color='red',fill_color='red', fill_opacity=0.3).add_to(map)  
    map = map._repr_html_()


    return render(request, 'india_home.html', {'Date':Date, 'Total':Total, 'Active':Active, 'Discharged':Discharged, 'Deaths':Deaths, 
                        'rows': rows, 'fig':fig, 'map': map})



def country_map(request):
    country = True
    r = requests.get('https://www.trackcorona.live/api/provinces')
    df_state_lev = pd.DataFrame(r.json()['data'])
    df_in = df_state_lev[df_state_lev['country_code'] == 'in'].copy()


    map = folium.Map(location=[20, 80], zoom_start=4.5, tiles='CartoDB dark_matter')
    for lat, lon, value, name in zip(df_in['latitude'], df_in['longitude'], df_in['confirmed'], df_in['location']):
        folium.CircleMarker([lat, lon], radius=value*0.001, popup = ('<strong>State</strong>: ' + str(name).capitalize() + '<br>''<strong>Total Cases</strong>: ' + str(value) + '<br>'),color='red',fill_color='red', fill_opacity=0.3).add_to(map)  
    map = map._repr_html_()

    return render(request, 'country.html', {'map': map, 'country': country})



def world_index(request):
    r = requests.get('https://www.trackcorona.live/api/countries')
    df_coun = pd.DataFrame(r.json()['data'])


    Total = df_coun['confirmed'].sum()
    Discharged = df_coun['recovered'].sum()
    Deaths = df_coun['dead'].sum()


    df_temp = df_coun.sort_values(by=['confirmed','dead'], ascending = False)
    df_temp = df_temp[:20]


    fig_bar = px.bar(df_temp, x = 'location', y = 'confirmed', color = 'confirmed', color_continuous_scale='Bluered_r',
             hover_data=['location','confirmed','recovered','dead'], title='20 most affected Countries',
            template='plotly_dark')
    fig_bar = opy.plot(fig_bar, auto_open=False, output_type='div')
    fig_bar


    fig_line = go.Figure()
    fig_line.add_trace(go.Line(x = df_temp['location'], y = df_temp['confirmed'], mode = 'markers+lines', name = 'Confirmed Cases'))
    fig_line.add_trace(go.Line(x = df_temp['location'], y = df_temp['dead'], mode = 'markers+lines', name = 'Death Cases'))
    fig_line.add_trace(go.Line(x = df_temp['location'], y = df_temp['recovered'], mode = 'markers+lines', name = 'Recovered Deaths'))
    fig_line.update_layout(title = 'Confirmed Cases vs Recoveries vs Deaths', xaxis_title="Date", yaxis_title="Count", template = 'plotly_dark')
    fig_line = opy.plot(fig_line, auto_open=False, output_type='div')
    fig_line


    fig = [fig_bar, fig_line]


    rows = []
    for i in range(len(df_coun)):
        inn = []
        inn.append(df_coun.iloc[i,0])
        inn.append(df_coun.iloc[i,4])
        inn.append(df_coun.iloc[i,6])
        inn.append(df_coun.iloc[i,5])
        rows.append(inn)

    
    r = requests.get('https://www.trackcorona.live/api/countries')
    df_coun = pd.DataFrame(r.json()['data'])
    map = folium.Map(location=[15,0], tiles='CartoDB dark_matter', zoom_start=2.5)
    for lat, lon, value, name in zip(df_coun['latitude'], df_coun['longitude'], df_coun['confirmed'], df_coun['location']):
        folium.CircleMarker([lat, lon], radius = value*0.00005, popup= ('<strong>Country: </strong>'+name+'<br>' '<strong>Confirmed: </strong>'+str(value)), color = 'red', fill_color = 'red', fill_opacity=0.2).add_to(map)
    map = map._repr_html_()


    return render(request, 'rest_home.html', {'Total': Total, 'Discharged': Discharged, 'Deaths': Deaths, 'rows': rows, 'map': map, 'fig': fig})


def world_map(request):
    r = requests.get('https://www.trackcorona.live/api/countries')
    df_coun = pd.DataFrame(r.json()['data'])
    map = folium.Map(location=[0,5], tiles='CartoDB dark_matter', zoom_start=2.5)
    for lat, lon, value, name in zip(df_coun['latitude'], df_coun['longitude'], df_coun['confirmed'], df_coun['location']):
        folium.CircleMarker([lat, lon], radius = value*0.00005, popup= ('<strong>Country: </strong>'+name+'<br>' '<strong>Confirmed: </strong>'+str(value)), color = 'red', fill_color = 'red', fill_opacity=0.2).add_to(map)
    map = map._repr_html_()
    return render(request, 'country.html', {'map': map})
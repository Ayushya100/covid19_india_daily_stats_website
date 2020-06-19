from django.shortcuts import render
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import plotly.graph_objects as go
import plotly.offline as opy

# Create your views here.
def state_details(request):

    state_name = request.POST["state"]

    check = False

    ind_dist = pd.read_json('https://api.covid19india.org/state_district_wise.json')
    for i in ind_dist.columns:
        if state_name.lower() in i.lower():
            check = True
            state_name = i
            temp_dist = pd.DataFrame(ind_dist[i].iloc[0])
            temp_dist.drop(['notes', 'delta'], inplace = True)
            temp_dist = temp_dist.transpose()
    
    if check:
        temp_dist.reset_index(inplace = True)
        temp_dist.rename(columns={'index':'Name of District', 'active':'Active','confirmed':'Confirmed cases', 
                                         'deceased':'Deaths', 'recovered':'Discharged'}, inplace = True)

        temp_dist = temp_dist.sort_values(by='Confirmed cases', ascending = False)

        rows = []
        for i in range(len(temp_dist)):
            inn = []
            inn.append(temp_dist.iloc[i,0])
            inn.append(temp_dist.iloc[i,2])
            inn.append(temp_dist.iloc[i,4])
            inn.append(temp_dist.iloc[i,3])
            rows.append(inn)


        fig_dist = px.bar(temp_dist, x = 'Name of District', y = 'Confirmed cases', hover_data=['Active', 'Discharged', 'Deaths'],
                template = 'plotly_dark')
        fig_dist = opy.plot(fig_dist, auto_open=False, output_type='div')
        fig_dist

        raw_daily = pd.read_json('https://api.rootnet.in/covid19-in/stats/history')

        regional_daily = raw_daily.iloc[0,1]['regional']
        regional_daily = pd.DataFrame(regional_daily)
        regional_daily['Date'] = raw_daily.iloc[0,1]['day']
        for j in range(1, len(raw_daily)):
            temp_df = raw_daily.iloc[j,1]['regional']
            temp_df = pd.DataFrame(temp_df)
            temp_df['Date'] = raw_daily.iloc[j,1]['day']
            regional_daily = pd.concat([regional_daily, temp_df])

        regional_daily.rename(columns = {'totalConfirmed':'Total Confirmed Cases', 'discharged':'Discharged', 'deaths':'Deaths', 'loc': 'Name of State / UT'}, inplace = True)
        regional_daily.drop(['confirmedCasesIndian', 'confirmedCasesForeign'], axis = 1, inplace = True)
        regional_daily = regional_daily[['Date', 'Name of State / UT', 'Total Confirmed Cases', 'Discharged', 'Deaths']]

        state_df = regional_daily[regional_daily['Name of State / UT'] == state_name]

        Date = state_df.iloc[-1,0]
        Total = int(state_df.iloc[-1,2])
        Discharged = int(state_df.iloc[-1,3])
        Deaths = int(state_df.iloc[-1,4])
        Active = int(Total - (Discharged + Deaths))

        fig_all = go.Figure()
        fig_all.add_trace(go.Line(x = state_df['Date'], y = state_df['Total Confirmed Cases'], mode = 'markers+lines', name = 'Daily Confirmed Cases'))
        fig_all.add_trace(go.Line(x = state_df['Date'], y = state_df['Deaths'], mode = 'markers+lines', name = 'Daily Deaths'))
        fig_all.add_trace(go.Line(x = state_df['Date'], y = state_df['Discharged'], mode = 'markers+lines', name = 'Daily Cured Cases'))
        fig_all.update_layout(title = '{} Daily Confirmed Cases vs Recoveries vs Deaths'.format(state_name), xaxis_title="Date", yaxis_title="Count", template = 'plotly_dark')
        fig_all = opy.plot(fig_all, auto_open=False, output_type='div')

        fig = [fig_dist, fig_all]

        return render(request, 'india_state.html', {'check': check, 'State': state_name, 'Date': Date, 'Total': Total, 'Active': Active, 'Discharged': Discharged,
                    'Deaths': Deaths, 'rows': rows, 'fig':fig})    

    else:
        return render(request, 'india_state.html', {'check': check})

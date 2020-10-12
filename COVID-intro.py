"""
Researching COVID
"""

import pandas as pd
import glob
import matplotlib.pyplot as plt
import datetime
import plotly_express

path = '/Users/jasonrubenstein/Desktop/Python/covid/COVID-19/csse_covid_19_data/csse_covid_19_daily_reports_us/*.csv'
covid_files = glob.glob(path)


class COVID:

    def get_csvs(files):
        datas = pd.concat([
            pd.read_csv(datas,
                        dtype=str,
                        error_bad_lines=False,
                        delimiter=',')
            for datas in files], axis=0)
        df = datas.drop_duplicates(keep='first').reset_index(drop=True)
        return df

    # Adjust dtype as necessary
    def to_ints(df):
        df['Last_Update'] = pd.to_datetime(df['Last_Update']).dt.date
        df['Last_Update'] = pd.to_datetime(df['Last_Update'])
        df.rename(columns={'Last_Update': 'Date'}, inplace=True)
        df['Confirmed'] = df['Confirmed'].astype("int")
        df['Deaths'] = df['Deaths'].astype("int")
        # df['People_Tested'].str.replace('.', '').astype(int)
        df['People_Tested'] = pd.to_numeric(df['People_Tested'])
        # df['People_Tested'] = df['People_Tested'].astype("int")
        df['People_Hospitalized'] = pd.to_numeric(df['People_Hospitalized'])
        # df['People_Hospitalized'] = df['People_Hospitalized'].astype("int")
        return df


    def shift_data(df):
        df['Prev_Cases'] = df.groupby("Province_State")["Confirmed"].shift(1)
        df['Prev_Deaths'] = df.groupby("Province_State")["Deaths"].shift(1)
        df['Prev_Tests'] = df.groupby("Province_State")["People_Tested"].shift(1)
        df['Prev_Hospitalizations'] = df.groupby("Province_State")["People_Hospitalized"].shift(1)
        df = df.fillna(0)
        return df


    def daily_data(df):
        df['Daily_Cases'] = df['Confirmed'] - df['Prev_Cases']
        df['Daily_Deaths'] = df['Deaths'] - df['Prev_Deaths']
        df['Daily_Tests'] = df['People_Tested'] - df['Prev_Tests']
        df['Daily_Hospitalizations'] = df['People_Hospitalized'] - df['Prev_Hospitalizations']
        del df['Prev_Hospitalizations'], df['Prev_Deaths'], df['Prev_Cases'], df['Prev_Tests']
        df = df[(df['Date'] > "2020-04-13")]
        return df


    def kpis(df):
        df['Positivity_Rate'] = df['Daily_Cases'] / df['Daily_Tests']
        return df


    def moving_avg(df):
        df['14_Day_Avg_Positivity_Rate'] = df.groupby('Province_State')['Positivity_Rate'].transform(
            lambda x: x.rolling(14, 1).mean())
        df['14_Day_Avg_Tests'] = df.groupby('Province_State')['Daily_Tests'].transform(
            lambda x: x.rolling(14, 1).mean())
        return df


covid_data = get_csvs(covid_files)
covid_data = covid_data[covid_data['Last_Update'].notna()]
covid_data = covid_data.sort_values(by="Last_Update")
covid_data = covid_data.fillna(0)

covid_data = COVID.to_ints(covid_data)
covid_data = COVID.shift_data(covid_data)
covid_data = COVID.daily_data(covid_data)
covid_data = COVID.kpis(covid_data)
covid_data = COVID.moving_avg(covid_data)


states = ["New York", "California", "Texas", "Alabama", "North Carolina", "South Carolina", "Michigan",
          "Florida", "New Jersey", "Arizona", "Illinois", "Georgia", "Ohio", "Colorado", "Massachusetts",
          "Wisconsin", "South Dakota", "North Dakota"]
plot_data = covid_data[(covid_data['Province_State'].isin(states))].sort_values(by=["Province_State", "Date"]).reset_index(drop=True)

plot_data = plot_data[(plot_data['Positivity_Rate'] < 1)]

# Positivity Rate by date
fig = plotly_express.scatter(plot_data, x="Date", y="14_Day_Avg_Positivity_Rate", color="Province_State",
                             hover_data=['Date', 'Province_State']).\
    update_traces(mode="lines+markers")
fig.update_layout(
    title={
        'text': "14 Day µ Positivity Rate by Date",
        'y':0.95,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'})
fig.show()

# Testing by State
fig = plotly_express.scatter(plot_data, x="Date", y="Daily_Tests", color="Province_State",
                             hover_data=['Date', 'Province_State']).\
    update_traces(mode="lines+markers")
fig.update_layout(
    title={
        'text': "Tests by Date",
        'y':0.95,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'})
fig.show()


class PlottingCOVID:

    def plotting(df):
        fig = plotly_express.scatter(df, x="Date", y="Positivity_Rate",
                                     hover_data=['Positivity_Rate', 'Daily_Cases', 'Daily_Tests']). \
            update_traces(mode="lines+markers")
        fig.update_layout(
            title={
                'text': "Positivity Rate by Date Without {}".format(ignore_states),
                'y': 0.95,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top'})
        fig.show()
        return 0

    def without_states(df):
        without_states = df[~(df['Province_State'].isin(ignore_states))]
        df_grp = without_states.groupby(['Date'], as_index=False)['Daily_Cases', 'Daily_Tests'].agg('sum')
        df_final = kpis(df_grp)
        return plotting(df_final)


    # ignore_states = ["New York"]
    # without_states(covid_data)
    #
    # ignore_states = ["Massachusetts", "Connecticut", "Rhode Island", "New Hampshire", "Vermont", "Maine"]
    # without_states(covid_data)
    #
    # ignore_states = ["New York", "New Jersey", "Connecticut"]
    # without_states(covid_data)
    #
    # ignore_states = ["New York", "New Jersey", "Connecticut",
    #                      "New Hampshire", "Vermont", "Maine", "Massachusetts", "Rhode Island"]
    # without_states(covid_data)

    def plotting_keep(df):
        fig = plotly_express.scatter(df, x="Date", y="Positivity_Rate",
                                     hover_data=['Positivity_Rate', 'Daily_Cases', 'Daily_Tests']). \
            update_traces(mode="lines+markers")
        fig.update_layout(
            title={
                'text': "Positivity Rate by Date With Only {}".format(keep_states),
                'y': 0.95,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top'})
        fig.show()
        return 0

    def with_states(df):
        without_states = df[(df['Province_State'].isin(keep_states))]
        df_grp = without_states.groupby(['Date'], as_index=False)['Daily_Cases', 'Daily_Tests'].agg('sum')
        df_final = kpis(df_grp)
        return plotting_keep(df_final)


keep_states = ["Arizona", "Texas", "Missouri", "Alabama", "Florida", "South Carolina"]
PlottingCOVID.with_states(covid_data)

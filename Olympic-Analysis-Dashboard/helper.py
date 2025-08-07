import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st
def Medal_tally(df):
    data = df[['region', 'NOC', 'Year', 'Gold', 'Silver', 'Bronze']]
    medal_tally = data.groupby("region")[['Gold', 'Silver', 'Bronze']].sum().sort_values(by='Gold',
                                                            ascending=False).reset_index()
    medal_tally['Total'] = medal_tally['Gold'] + medal_tally['Silver'] + medal_tally['Bronze']
    return medal_tally
def country_year(df):
    years = df['Year'].sort_values().unique().tolist()
    years.insert(0, 'Overall')

    country = df['region'].dropna().sort_values().unique().tolist()
    country.insert(0, 'Overall')
    return years,country

def fetchingMedalTally(df,year,country):
    flag = 0
    if year == 'Overall' and country == 'Overall':
        temp_df = df
    elif year == 'Overall' and country != 'Overall':
        temp_df  = df[df['region'] == country]
        flag = 1
    elif year != 'Overall' and country == 'Overall':
        temp_df = df[df['Year'] == year]
    elif year != 'Overall' and country != 'Overall':
        temp_df = df[(df['Year'] == year) & (df['region'] == country)]

    if flag ==0:
        x = temp_df.groupby("region")[['Gold', 'Silver', 'Bronze']].sum().sort_values(by='Gold', ascending=False).reset_index()
        x['Total'] = x['Gold'] + x['Silver'] + x['Bronze']
    else:
        x = temp_df.groupby("Year")[['Gold', 'Silver', 'Bronze']].sum().sort_values(by='Year').reset_index()
        x['Total'] = x['Gold'] + x['Silver'] + x['Bronze']
    return x

def titleMedalTally(year,country):
    if year == 'Overall' and country == 'Overall':
        return ("All Nations Olympic Analysis")
    elif year == 'Overall' and country != 'Overall':
        return ("Overall Olympics Analysis of " + country)
    elif year != 'Overall' and country == 'Overall':
        return ("Overall Nations Olympic Analysis in year " + str(year))
    elif year != 'Overall' and country != 'Overall':
        return (country + " Olympic Analysis in Year " + str(year))


def topstats(df):
    editions = df['Year'].nunique() - 1
    cities = df['City'].nunique()
    events = df['Event'].nunique()
    sports = df['Sport'].nunique()
    athelets = df['Name'].nunique()
    nations = df['region'].nunique()

    col1,col2,col3 = st.columns(3)
    with col1:
        st.subheader("Edition")
        st.header(editions)
    with col2:
        st.subheader("Cities")
        st.header(cities)
    with col3:
        st.subheader("Events")
        st.header(events)
    col1,col2,col3 = st.columns(3)
    with col1:
        st.subheader("Sports")
        st.header(sports)
    with col2:
        st.subheader("Athelets")
        st.header(athelets)
    with col3:
        st.subheader("Nations")
        st.header(nations)

def plotSection(df,col):
    data = df.groupby('Year')[col].nunique().reset_index()
    return data

def heatmap(df):
    df_unique_events = df.drop_duplicates(subset=['Year', 'Sport', 'Event'])
    x = df_unique_events.pivot_table(index='Sport', columns='Year', values='Event', aggfunc='count').fillna(0)
    return x

def Top15_Athelets(df,sport):
    temp_df = df.dropna(subset = ['Medal'])

    flag = 0
    if sport != "Overall":
        flag = 1
        temp_df = temp_df[temp_df['Sport'] == sport]
        temp_df = temp_df['Name'].value_counts().reset_index().head(15)

    else:
        temp_df = temp_df['Name'].value_counts().reset_index().head(15)

    top15 = pd.merge(temp_df,df,on = 'Name',how = 'left').drop_duplicates(subset = ['Name'])
    top15.reset_index(drop=True, inplace=True)
    top15.index += 1
    if flag:
        return top15[['Name','Sex','region','count']]
    else:
        return top15[['Name','Sex','Sport','region','count']]

def yearwise_medalTally(df,country):
    countryWise = df[df['region'] == country]
    return countryWise.groupby('Year').count()['Medal'].reset_index()

def heatmap_countryWise(df,country):
    countryWise = df[df['region'] == country]
    countryWise.groupby('Year').count()['Medal'].reset_index()
    x = countryWise.pivot_table(index='Sport', columns='Year', values='Medal', aggfunc='count').fillna(0).astype(int)
    return x

def top10_Athelets_CountryWise(df,country):
    countryWise = df[df['region'] == country]
    player = countryWise['Name'].value_counts().sort_values(ascending=False).head(10)
    top10 = pd.merge(player, countryWise, on='Name', how='left').drop_duplicates(subset=['Name'])
    top10 = top10[['Name', 'Sex', 'Sport', 'count']]
    top10 = top10.rename(columns={'count': 'Medals'})
    top10.reset_index(drop=True, inplace=True)
    top10.index += 1
    return top10

def AthleteWise_Age_dist(ath_df):
    ath_df = ath_df.drop_duplicates(subset=['Name', 'region'])
    age = ath_df['Age'].dropna()
    gold = ath_df[ath_df['Medal'] == 'Gold']['Age'].dropna()
    silver = ath_df[ath_df['Medal'] == 'Silver']['Age'].dropna()
    bronze = ath_df[ath_df['Medal'] == 'Bronze']['Age'].dropna()
    return age,gold,silver,bronze

def wonGold_FamousSports(df):
    df = df.drop_duplicates(subset=['Name', 'region'])
    sports = df['Sport'].value_counts().reset_index().head(30)
    famous_sports = sports['Sport']
    famous_sports = list(famous_sports)
    goldAge = []
    for sport in famous_sports:
        selected_sport = df[df['Sport'] == sport]
        goldAge.append(selected_sport[selected_sport['Medal'] == 'Gold']['Age'].dropna())
    return goldAge,famous_sports

def height_vs_weight(df,sport):
    df = df.drop_duplicates(subset=['Name','region'])
    if sport == "Overall":
        return df
    else:
        df['Medal'].fillna("No Medal",inplace = True)
        temp_df = df[df['Sport'] == sport]
        return temp_df

def men_vs_women(df):
    df = df.drop_duplicates(subset=['Name', 'region'])
    df = df.drop_duplicates(subset=['Name', 'region'])
    male = df[df['Sex'] == 'M'].groupby('Year')['Sex'].count().reset_index()
    male = male.rename(columns={'Sex': 'Male'})

    female = df[df['Sex'] == 'F'].groupby('Year')['Sex'].count().reset_index()
    female = female.rename(columns={"Sex": "Female"})

    male_vs_female = pd.merge(male, female, how='left').fillna(0)
    return male_vs_female
import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.figure_factory as ff
import scipy
import PreprocessingFile, helper

df = pd.read_csv("athlete_events.csv")
reg = pd.read_csv("noc_regions.csv")

cleandf = PreprocessingFile.dataCleaner(df,reg)
medalTally = helper.Medal_tally(cleandf)

st.sidebar.title("Olympic Analysis")
user_menu = st.sidebar.radio('Select an Option Below', ('Medal_Tally', 'Overall_Analysis',
                   'Country_Wise_Analysis','Athelete_Wise_Analysis'))

if user_menu == 'Medal_Tally':
    # st.dataframe(medalTally)
    year,country = helper.country_year(cleandf)

    selectedYear = st.sidebar.selectbox("Select Year", year)
    selectedContry = st.sidebar.selectbox("Select Country",country)
    selcted_country_year = helper.fetchingMedalTally(cleandf,selectedYear,selectedContry)
    title = helper.titleMedalTally(selectedYear,selectedContry)
    st.subheader(title)
    st.dataframe(selcted_country_year)



if user_menu == "Overall_Analysis":
    st.sidebar.title('Overall Analysis')
    st.markdown("<h3 style='text-align: center;'>Top Statistics</h3>", unsafe_allow_html=True)
    helper.topstats(cleandf)

    data = helper.plotSection(cleandf,'region')
    fig = px.line(data,x = 'Year', y = 'region')
    st.markdown("<h3 style='text-align: center;'>Nations Per Edition</h3>", unsafe_allow_html=True)
    st.plotly_chart(fig)

    data = helper.plotSection(cleandf, 'Sport')
    fig = px.line(data, x='Year', y='Sport')
    st.markdown("<h3 style='text-align: center;'>Sport Per Edition</h3>", unsafe_allow_html=True)
    st.plotly_chart(fig)

    data = helper.plotSection(cleandf, 'Event')
    fig = px.line(data, x='Year', y='Event')
    st.markdown("<h3 style='text-align: center;'>Events Per Edition</h3>", unsafe_allow_html=True)
    st.plotly_chart(fig)

    data = helper.plotSection(cleandf, 'Name')
    data.rename(columns = {'Name':'Athelets'},inplace = True)
    fig = px.line(data, x='Year', y='Athelets')
    st.markdown("<h3 style='text-align: center;'>Athelets Per Edition</h3>", unsafe_allow_html=True)
    st.plotly_chart(fig)

    x = helper.heatmap(cleandf)
    fig = plt.figure(figsize=(20,20))
    ax = sns.heatmap(x,annot = True)
    st.markdown("<h3 style='text-align: center;'>No of Events over Year (Per Sport)</h3>", unsafe_allow_html=True)
    st.pyplot(fig)


    data = PreprocessingFile.dataCleaner(df,reg,1)

    st.markdown("<h3 style='text-align: center;'>Most Successful 15 Players </h3>", unsafe_allow_html=True)
    sports = data['Sport'].sort_values().unique().tolist()
    sports.insert(0, 'Overall')
    selected_sport = st.selectbox("Select Sport", sports)
    top15 = helper.Top15_Athelets(data,selected_sport)
    top15.rename(columns = {'count':'Medals'},inplace = True)
    st.dataframe(top15)

if user_menu == 'Country_Wise_Analysis':
    st.sidebar.title('Country Wise Analysis')
    countryWise_df = PreprocessingFile.dataCleaner(df,reg,'cw')
    country = countryWise_df['region'].sort_values().unique().tolist()
    country = country[:-1]

    selected_country = st.sidebar.selectbox('Select a Country', country)
    countryWise_MedalTally = helper.yearwise_medalTally(countryWise_df, selected_country)
    st.markdown(f"<h3 style='text-align: center;'>{selected_country} Medal Tally Over the Years</h3>",unsafe_allow_html=True)
    fig = px.line(countryWise_MedalTally, x='Year', y='Medal')
    st.plotly_chart(fig)

    st.markdown(f"<h3 style='text-align: center;'>{selected_country} Excel in the Following Sports</h3>",
                unsafe_allow_html=True)
    countryWise_heatmap = helper.heatmap_countryWise(countryWise_df,selected_country)
    fig = plt.figure(figsize=(20, 20))
    ax = sns.heatmap(countryWise_heatmap,annot= True)
    st.pyplot(fig)

    st.markdown(f"<h3 style='text-align: center;'>{selected_country} Top 10 Players</h3>",
                unsafe_allow_html=True)
    top10 = helper.top10_Athelets_CountryWise(countryWise_df,selected_country)
    st.dataframe(top10)

if user_menu == 'Athelete_Wise_Analysis':
    ath_df = PreprocessingFile.dataCleaner(df, reg, 'cw')
    age, gold, silver, bronze = helper.AthleteWise_Age_dist(ath_df)
    fig = ff.create_distplot([age, gold, silver, bronze], ['Overall Age', 'Gold Medalist', 'Silver Medalist',
                                                       'Bronze Medalist'], show_hist=False, show_rug=False)
    st.markdown("<h3 style='text-align: center;'>Age Distribution of Athletes by Medal Type </h3>", unsafe_allow_html=True)
    fig.update_layout(
        xaxis_title='Age',
        yaxis_title='Density',)
    st.plotly_chart(fig)

    ath_wise = PreprocessingFile.dataCleaner(df, reg, 'cw')
    goldAge,famous_sports = helper.wonGold_FamousSports(ath_wise)
    fig = ff.create_distplot(goldAge,famous_sports,show_hist=False,show_rug=False)
    st.markdown("<h3 style='text-align: center;'>Age Distribution of Athletes wrt to Sport (Gold Medalist) </h3>", unsafe_allow_html=True)
    fig.update_layout(
        xaxis_title='Age',
        yaxis_title='Density', )
    st.plotly_chart(fig)

    unique_ath_sports = PreprocessingFile.dataCleaner(df,reg,'athWise')
    unique_sports = unique_ath_sports['Sport'].sort_values().unique().tolist()
    unique_sports.insert(0,'Overall')
    selcted_sport = st.sidebar.selectbox("Select a Sport",unique_sports)
    data = helper.height_vs_weight(unique_ath_sports,selcted_sport)
    st.markdown("<h3 style='text-align: center;'>Height Vs Weight for Successful Athlets </h3>",
                unsafe_allow_html=True)
    fig = plt.figure(figsize=(10, 10))
    ax = sns.scatterplot(x = data['Height'],y = data['Weight'], data = data,s = 150,hue = data['Medal'],style = data['Sex'])
    st.pyplot(fig)

    st.markdown("<h3 style='text-align: center;'>Male vs Female Over the Years </h3>",unsafe_allow_html=True)

    male_vs_female  = PreprocessingFile.dataCleaner(df,reg,'athWise')
    male_vs_female = helper.men_vs_women(male_vs_female)
    fig = px.line(male_vs_female, x='Year', y = ['Male','Female'])
    st.plotly_chart(fig)

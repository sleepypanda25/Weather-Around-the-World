import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3

@st.cache_data
def load_weather():
    conn = sqlite3.connect("weather.db")
    df = pd.read_sql_query("SELECT * FROM weather", conn)
    conn.close()
    return df

df = load_weather()

st.write(df.dtypes)
st.write(len(df), df['Temperature'].head())

# --- Dashboard ---
# Sidebar
st.sidebar.title("Filter Options")
graph_options = ['Temperature Distribution', 'Temperature Over Time', 'Hottest and Coldest Cities', 'Usage Guide']
selected_graph = st.sidebar.selectbox("Select Graph", graph_options)
st.sidebar.header("Graph Filter Options")
temperature_filter = st.sidebar.slider("Select Temperature Range Lower Bound", min_value=int(df['Temperature'].min()), max_value=int(df['Temperature'].max()), value=(int(df['Temperature'].min()), int(df['Temperature'].max())), step=1)
time_lower_filter = st.sidebar.slider("Select Time Range Lower Bound", min_value=0, max_value=23, value=(0, 23), step=1)
city_filter = st.sidebar.multiselect("Select Cities", options=df['City'].unique(), default=df['City'].unique())

# Main Page
st.title("Weather Dashboard")

# --- Data Visualization ---
df['Time'] = df['Date/Time'].str.split(n=1).str[1]
df['Time'] = (pd.to_datetime(df['Time'], format='%I:%M %p').dt.floor('h').dt.hour)
df = df[(df['Temperature'] >= temperature_filter[0]) & (df['Temperature'] <= temperature_filter[1])]
df = df[(df['Time'] >= time_lower_filter[0]) & (df['Time'] <= time_lower_filter[1])]
df = df[df['City'].isin(city_filter)]

if selected_graph == 'Temperature Distribution':
    # Temperature Distribution Graph
    st.header("Temperature Distribution")
    bins = st.slider("Select number of bins", min_value=5, max_value=50, value=20, step=5, key="bins_slider")
    temp_dist = px.histogram(df, x='Temperature', nbins=bins, title='Temperature Distribution')
    temp_dist.update_layout(bargap=0.05, xaxis_title="Temperature (°F)", yaxis_title="Count")
    temp_dist.update_traces(xbins=dict(start=df['Temperature'].min(), end=df['Temperature'].max(), size=(df['Temperature'].max() - df['Temperature'].min()) / bins))
    st.plotly_chart(temp_dist)
elif selected_graph == 'Temperature Over Time':
    # Temperature Over Time Graph
    st.header("Temperature Over Time")
    temp_over_time = px.scatter(df, x='Time', y='Temperature', color='Temperature', title='Temperature Over Time')
    temp_over_time.update_layout(xaxis_title="Hour of Day", yaxis_title="Temperature (°F)")
    st.plotly_chart(temp_over_time)
elif selected_graph == 'Hottest and Coldest Cities':
    # Hottest and Coldest Cities Graph
    st.header("Hottest and Coldest Cities")
    topn = st.slider("Select number of top cities on each extreme to display", min_value=1, max_value=20, value=10, step=1, key="topn_slider")
    temp_sorted = df.sort_values(by='Temperature')
    extremes = pd.concat([temp_sorted.head(topn), temp_sorted.tail(topn)])
    extremes_chart = px.bar(extremes, x='City', y='Temperature',  color='Temperature', title='Hottest and Coldest Cities')
    extremes_chart.update_layout(yaxis_title="Temperature (°F)")
    st.plotly_chart(extremes_chart)
else:
    st.header("Usage Guide")
    st.write("This dashboard contains current weather data from cities around the world.")
    st.subheader("Sidebar Filters")
    st.write("Use the sidebar to filter through three different graphs. Select the desired range for temperature and time of day, as well as the cities you want to include in the graph. The graphs will update automatically based on your selections.")
    st.subheader("Graphs")
    st.write("The graph options are as follows:")
    st.write("1. Temperature Distribution: Displays a histogram of the temperature distribution for the selected cities and time range.")
    st.write("2. Temperature Over Time: Displays a scatter plot of the temperature over time for the selected cities and time range.")
    st.write("3. Hottest and Coldest Cities: Displays a bar chart of the top hottest and coldest cities based on the selected temperature range, time of day, and number of top cities.")
    st.write("Two of the three graphs contain a slider to adjust the number of bins or cities displayed.")
    st.write("1. The Temperature Distribution graph allows you to select the number of bins for the histogram.")
    st.write("2. The Hottest and Coldest Cities graph allows you to select how many cities to display in the bar chart.")

#%%
import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.express as px

#%%
st.title("Motor collision")
st.markdown("streamlit dashboard to monitor collision in NYC ")

@st.cache(persist = True)
def load_data(nrows):
    data = pd.read_csv('database.csv', nrows = nrows, parse_dates = [["DATE" , "TIME"]])
    data.dropna(subset=['LATITUDE', "LONGITUDE"], inplace=True)
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase, axis = 'columns', inplace = True)
    data.rename(columns = {"crash_date_crash_time": 'date/time'}, inplace = True)
    return data

data = load_data(100000)

#%%
data.rename(columns = {"persons injured": 'person_injured'}, inplace = True)
#%%
st.header("where are most peapol injured in NYC?")
injured_people = st.slider("Number of persons injured in collisions", 0, 19)
st.map(data.query(" person_injured >= @injured_people")[['longitude', 'latitude']].dropna(how='any'))

st.header("How many collision happern in a single day?")
hour = st.sidebar.selectbox("hour to look at", range(0,24), 1)
data = data[data['date_time'].dt.hour == hour]
st.map(data.query("person_injured == @hour")[['longitude', 'latitude']].dropna(how='any'))


#%%

st.markdown("vehCollision btw %i:00 and %i:00" %(hour, (hour+1) % 24))
midpoint = (np.average(data['latitude']), np.average(data['longitude']))
st.write(pdk.Deck(
    map_style="mapbox://styles/mapbox/light-v9",
    initial_view_state={
        'latitude': midpoint[0],
        'longitude': midpoint[1],
        'zoom': 11,
        'pitch': 50,
    },
    layers=[
        pdk.Layer(
        'HexagonLayer',
        data=data[['date_time', 'latitude', 'longitude']],
        get_position=['longitude', 'latitude'],
        radius = 100,
        extruded=True,
        pickable=True,
        elevation_scale=4,
        elevation_range=[0, 1000],
        ),
    ],
))

st.subheader("between %i:00 and %i:00" %(hour, (hour+1) %24))
filtered = data[
    (data['date_time'].dt.hour >= hour) & (data['date_time'].dt.hour < (hour+1))
    ]
hist = np.histogram(filtered['date_time'].dt.minute, bins=60, range=(0, 60))[0]
chart_data = pd.DataFrame({'minute': range(60), 'crashes':hist})
fig = px.bar(chart_data, x='minute', y= 'crashes', hover_data=['minute', 'crashes'], height =400)
st.write(fig) 
#%%
if st.checkbox("Show data", False):
    st.subheader("Raw Data")
    st.write(data)

# %%

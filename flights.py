import streamlit as st
import folium
from streamlit_folium import st_folium
import requests
from folium.plugins import MarkerCluster
from datetime import datetime

st.set_page_config(layout="wide")
st.title("✈️ Live Airplane Routes - OpenSky Network API")

# Function to fetch live aircraft data
@st.cache_data(ttl=60)
def get_air_traffic_data():
    url = "https://opensky-network.org/api/states/all"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data["states"]
    except Exception as e:
        st.error(f"Failed to fetch data: {e}")
        return []

# Create a folium map
def create_map(flight_data):
    m = folium.Map(location=[20, 0], zoom_start=2, tiles="CartoDB positron")
    marker_cluster = MarkerCluster().add_to(m)

    for flight in flight_data:
        try:
            callsign = flight[1].strip()
            origin_country = flight[2]
            longitude = flight[5]
            latitude = flight[6]
            altitude = flight[7]
            velocity = flight[9]

            if latitude is None or longitude is None:
                continue

            popup_content = f"""
            <b>Callsign:</b> {callsign}<br>
            <b>Country:</b> {origin_country}<br>
            <b>Altitude:</b> {altitude} m<br>
            <b>Speed:</b> {velocity} m/s<br>
            <b>Timestamp:</b> {datetime.utcnow()} UTC
            """

            folium.Marker(
                location=[latitude, longitude],
                popup=popup_content,
                icon=folium.Icon(color="blue", icon="plane", prefix="fa"),
            ).add_to(marker_cluster)
        except Exception:
            continue

    return m

with st.spinner("Fetching live airplane data..."):
    flight_data = get_air_traffic_data()

if flight_data:
    st.markdown(f"**Total flights tracked:** {len(flight_data)}")
    folium_map = create_map(flight_data)
    st_folium(folium_map, width=1300, height=600)
else:
    st.warning("No data to display.")

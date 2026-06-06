import os
import django
import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import plotly.express as px
from django.apps import apps

 Environment Settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nakuru_tourism_project.settings')
os.environ['SECRET_KEY'] = 'local-migration-bypassed-key-123'
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"  # Prevents database thread lock in Streamlit

 Bulletproof Django Initialization
if not apps.ready:
    try:
        django.setup()
    except RuntimeError as e:
       
        if "populate() isn't reentrant" in str(e):
            pass
        else:
            raise

 Import Models safely AFTER setup
from tour_app.models import AttractionSite, Hotel, Pricing, VisitorStat, Category
@st.cache_data
def load_data():
    attractions_df = pd.DataFrame(list(AttractionSite.objects.all().values()))
    hotels_df = pd.DataFrame(list(Hotel.objects.all().values()))
    prices_df = pd.DataFrame(list(Pricing.objects.all().values()))
    category_df = pd.DataFrame(list(Category.objects.all().values()))
    visitors_df = pd.DataFrame(list(VisitorStat.objects.all().values()))
    return attractions_df, hotels_df, prices_df, category_df, visitors_df

attractions, hotels, prices, categories, visitors = load_data()

for df in [attractions, hotels]:
    if not df.empty and 'latitude' in df.columns and 'longitude' in df.columns:
        df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
        df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')

st.set_page_config(page_title="Nakuru Tourism Map", layout="wide")
st.title("Nakuru Tourism Dashboard")

st.subheader("Explore Attractions")
if not attractions.empty and 'name' in attractions.columns:
    attraction_options = sorted(attractions['name'].unique())
    selected_attraction_name = st.selectbox(
        "Search or choose an attraction to auto-center the map and pull visitor metrics:",
        options=attraction_options
    )
else:
    st.error("No attraction records found in the database.")
    st.stop()

selected_row = attractions[attractions['name'] == selected_attraction_name].iloc[0]

map_center = [-0.3031, 36.0800]
zoom_level = 10

if pd.notnull(selected_row['latitude']) and pd.notnull(selected_row['longitude']):
    map_center = [selected_row['latitude'], selected_row['longitude']]
    zoom_level = 13
    
# Split layout: Map on the left (wider), Deep Dive on the right
col_map, col_details = st.columns([2, 1])

with col_map:
    m = folium.Map(location=map_center, zoom_start=zoom_level)
    
    COUNTY_GEOJSON_PATH = "KENYAcounties.geojson"
    if os.path.exists(COUNTY_GEOJSON_PATH):
        folium.GeoJson(
            COUNTY_GEOJSON_PATH,
            name="Nakuru County Boundary",
            style_function=lambda feature: {
                'fillColor': '#2255ff',
                'color': '#0033cc',
                'weight': 2.5,
                'fillOpacity': 0.08
            },
            tooltip="Nakuru County Border Line"
        ).add_to(m)

    if 'latitude' in attractions.columns and 'longitude' in attractions.columns:
        for i, row in attractions.dropna(subset=['latitude', 'longitude']).iterrows():
            folium.Marker(
                location=[row['latitude'], row['longitude']],
                popup=row.get('name', 'Attraction'),
                tooltip=row.get('name', 'Click for details'),
                icon=folium.Icon(color="blue", icon="info-sign")
            ).add_to(m)

    if 'latitude' in hotels.columns and 'longitude' in hotels.columns:
        clean_hotels = hotels.dropna(subset=['latitude', 'longitude'])
        for i, row in clean_hotels.iterrows():
            h_name = str(row.get('name', 'Unknown Hotel'))
            h_web = str(row.get('website', ''))
            
            if h_web and h_web.lower() not in ['nan', 'none', '']:
                popup_html = f"<b>{h_name}</b><br><a href='{h_web}' target='_blank'>Visit Website</a>"
            else:
                popup_html = f"<b>{h_name}</b>"
                
            folium.CircleMarker(
                location=[row['latitude'], row['longitude']],
                radius=5,
                color="red",
                fill=True,
                fill_color="red",
                fill_opacity=0.9,
                popup=folium.Popup(popup_html, max_width=250),
                tooltip=f"Hotel: {h_name}"
            ).add_to(m)

    st_folium(m, width=600, height=600, use_container_width=True) 

with col_details:
    st.subheader("Attraction Deep Dive")
    st.write(f"**{selected_row['name']}**")
    
    desc = str(selected_row.get('description', ''))
    if desc and desc.lower() not in ['nan', 'none', '']:
        st.write(desc)
    
    address = str(selected_row.get('address', ''))
    phone = str(selected_row.get('contact_phone', ''))
    email = str(selected_row.get('contact_email', ''))
    
    contact_box = ""
    if address and address.lower() not in ['nan', 'none', '']:
        contact_box += f" **Address:** {address}\n\n"
    if phone and phone.lower() not in ['nan', 'none', '']:
        contact_box += f"**Phone:** {phone}\n\n"
    if email and email.lower() not in ['nan', 'none', '']:
        contact_box += f"**Email:** {email}\n\n"
        
    if contact_box:
        st.info(contact_box)
    
    # Coordinates and Website
    st.caption(f"**GPS:** {selected_row['latitude']}, {selected_row['longitude']}")
    
    web_link = str(selected_row.get('website', ''))
    if web_link and web_link.lower() not in ['nan', 'none', '']:
        st.markdown(f"**[Visit Official Website]({web_link})**")

    # Pricing
    if 'id' in selected_row and not prices.empty and 'attraction_site_id' in prices.columns:
        site_prices = prices[prices['attraction_site_id'] == selected_row['id']]
        if not site_prices.empty:
            st.write("**Pricing Matrix:**")
            st.dataframe(site_prices[['visitor_type', 'price', 'valid_from']], hide_index=True)

st.markdown("---")
st.subheader("Trend Metrics: Visitor Statistics")

if not visitors.empty:
    col_f1, col_f2, col_f3 = st.columns([1, 1, 2])
    
    with col_f1:
        if 'year' in visitors.columns:
            years_available = sorted(visitors['year'].unique())
            selected_years = st.multiselect("Filter Target Years", options=years_available, default=years_available)
        else:
            selected_years = []

    working_df = visitors.copy()
    
    if 'attraction_site_id' in working_df.columns and 'id' in selected_row:
        working_df = working_df[working_df['attraction_site_id'] == selected_row['id']]

    if selected_years and 'year' in working_df.columns:
        working_df = working_df[working_df['year'].isin(selected_years)]
    
    if not working_df.empty:
        x_axis = 'year' if 'year' in working_df.columns else working_df.columns[0]
        y_axis = 'visitor_count' if 'visitor_count' in working_df.columns else working_df.columns[-1]
        
        if 'year' in working_df.columns:
            working_df = working_df.sort_values(by='year')

        fig = px.bar(
            working_df, 
            x=x_axis, 
            y=y_axis,
            title=f"Comparative Attendance Trends for {selected_attraction_name}",
            labels={x_axis: "Timeline", y_axis: "Total Registered Visitors"},
            text_auto='.2s'
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning(f"No specific timeline metrics found matching your filters for {selected_attraction_name}.")
else:
    st.info("Visitor statistical records are currently empty or unmapped in PostgreSQL.")

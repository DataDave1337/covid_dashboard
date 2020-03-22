import pandas as pd
import numpy as np
import os
import os.path
import streamlit as st
import matplotlib.pyplot as plt
import yaml
import geopandas as gpd
import json

# Bokeh imports
from bokeh.models import ColumnDataSource, GeoJSONDataSource, LogColorMapper
from bokeh.palettes import brewer
from bokeh.plotting import figure
from bokeh.tile_providers import Vendors, get_provider

def country_geoplot(country_data, shp_path):
    def load_country_shapes(country_shp_path):
        #Read shapefile using Geopandas
        gdf = gpd.read_file(country_shp_path)[['ADMIN', 'ADM0_A3', 'geometry']]
        #Rename columns
        gdf.columns = ['country', 'country_code', 'geometry']
        gdf = gdf.drop(gdf.index[159])
        return gdf

    def get_geodatasource(gdf):    
        """ Get getjsondatasource from geopandas object """
        json_data = json.dumps(json.loads(gdf.to_json()))
        return GeoJSONDataSource(geojson = json_data)
    
    gdf = load_country_shapes(shp_path)

    plt_cols = ['country', 'confirmed_cases', 'deaths', 'recovered']
    plt_df = gdf.merge(country_data[plt_cols], on='country')

    tile_provider = get_provider(Vendors.CARTODBPOSITRON)
    geosource = get_geodatasource(plt_df)

    # color mapping
    palette = brewer['OrRd'][8]
    palette = palette[::-1]
    color_col = 'confirmed_cases'
    vals = plt_df[color_col]
    color_mapper = LogColorMapper(palette=palette, low=1, high=vals.max())
    tile_provider = get_provider(Vendors.CARTODBPOSITRON)

    # Tooltip attributes
    TOOLTIPS = [
        ('Country', '@country'),
        ('Confirmed cases', '@confirmed_cases'),
        ('Deaths', '@deaths'),
        ('Recovered', '@recovered')
    ]

    p = figure(tooltips=TOOLTIPS, plot_height=400 , plot_width=850, match_aspect=True)
    p.add_tile(tile_provider)
    # Plot country shapes
    p.patches('xs','ys', source=geosource, fill_alpha=1, line_width=0.5, line_color='black',
              fill_color={'field' :color_col , 'transform': color_mapper})

    return p

def history_plot(data):
    fig = plt.figure(figsize=(10,7))
    ax = fig.gca()
    ax = data.plot(x='date', y=['confirmed_cases', 'deaths', 'recovered'], ax=ax)
    ax.grid(True)
    ax.set_title(f"{country}'s Corona history")
    plt.tight_layout()
    
    return fig

# Load path config
config_file = open('config.yaml', 'r')
config = yaml.safe_load(config_file)
SOURCE_DATA_DIR = config['source_data_dir']
PREP_DATA_DIR = config['prep_data_dir']
COUNTRY_SHP_FILE = config['country_shapefile']

# Load and prepare data
df = pd.read_csv(os.path.join(PREP_DATA_DIR, 'covid_prep.csv'))
df['date'] = pd.to_datetime(df['date'], format='%Y/%m/%d', errors='ignore')

st.title('Corona data visualization')

st.sidebar.title("Filter data")
# Countries ordered by confirmed cases
country_df = df.groupby(['country','date'], as_index=False)[['confirmed_cases', 'deaths', 'recovered']].sum()
latest_df = country_df.loc[country_df.groupby('country').date.idxmax()]
latest_df.sort_values('confirmed_cases', ascending=False, inplace=True)
countries = latest_df['country'].tolist()

# Geoplot
st.subheader('Geoplot with Country shapes')
geoplot = country_geoplot(latest_df, COUNTRY_SHP_FILE)
st.bokeh_chart(geoplot, use_container_width=True)

st.subheader('Country ranking')
st.write(latest_df[['date','country', 'confirmed_cases', 'deaths', 'recovered']])

# Country filter
country = st.sidebar.selectbox("Choose country to look at", countries)
filter_df = df[df['country']==country]

# State filter
state_count = filter_df['state'].notnull().sum()

if state_count > 0:
    # bool for state_filter
    if st.sidebar.checkbox('Filter by state'):
        states = filter_df[filter_df['state'].notnull()]['state'].unique()
        state = st.sidebar.selectbox("Choose state to look at", states)
        filter_df = filter_df[filter_df['state']==state]
    else:
        filter_df = filter_df.groupby(['country', 'date'], as_index=False).sum()

# history plot
st.subheader('Country History')
fig = history_plot(filter_df)
st.write(fig)

# st.map(filter_df)


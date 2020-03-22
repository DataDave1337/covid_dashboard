import pandas as pd
import numpy as np
import os
import os.path
import streamlit as st
import matplotlib.pyplot as plt
import yaml

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

# Load and prepare data
df = pd.read_csv(os.path.join(PREP_DATA_DIR, 'covid_prep.csv'))
df['date'] = pd.to_datetime(df['date'], format='%Y/%m/%d', errors='ignore')

st.title('Corona data visualization')

st.sidebar.title("Filter data")
# country filter
# countries ordered by confirmed cases
country_df = df.groupby(['country','date'], as_index=False)[['confirmed_cases', 'deaths', 'recovered']].sum()
latest_df = country_df.loc[country_df.groupby('country').date.idxmax()]
latest_df.sort_values('confirmed_cases', ascending=False, inplace=True)
countries = latest_df['country'].tolist()

st.subheader('Country ranking')
st.write(latest_df[['date','country', 'confirmed_cases', 'deaths', 'recovered']])

country = st.sidebar.selectbox("Choose country to look at", countries)
filter_df = df[df['country']==country]

# state filter
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
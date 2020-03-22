import pandas as pd
import numpy as np
import os
import os.path
import streamlit as st
import matplotlib.pyplot as plt

# Load and prepare data
df = pd.read_csv('covid_prep.csv')
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

# bool for state_filter
# state filter
state_count = filter_df['state'].notnull().sum()

if state_count > 0:
    if st.sidebar.checkbox('Filter by state'):
        states = filter_df[filter_df['state'].notnull()]['state'].unique()
        state = st.sidebar.selectbox("Choose state to look at", states)
        filter_df = filter_df[filter_df['state']==state]
    else:
        filter_df = filter_df.groupby(['country', 'date'], as_index=False).sum()

# history plot
st.subheader('Country History')
fig = plt.figure(figsize=(10,7))
ax = fig.gca()
ax = filter_df.plot(x='date', y=['confirmed_cases', 'deaths', 'recovered'], ax=ax)
ax.grid(True)
ax.set_title(f"{country}'s Corona history")
plt.tight_layout()
st.write(fig)

# st.map(filter_df)
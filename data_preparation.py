import pandas as pd
import os.path
import os
import yaml

def read_case_file(fname, col_name, ignore_lat_lon=False):
    df = pd.read_csv(fname)
    df.rename(columns={'Province/State': 'state',
                       'Country/Region': 'country',
                       'Lat': 'lat',
                       'Long': 'lon'}, inplace=True)
    stack_cols = [col for col in df.columns if col not in ['state', 'country', 'lat', 'lon']]
    df.set_index(['state', 'country', 'lat', 'lon'], inplace=True)
    ser = df.stack()
    ser.name = col_name
    df_result = ser.reset_index().rename(columns={'level_4': 'date'})
    df_result['date'] = pd.to_datetime(df_result['date'], format='%m/%d/%y', errors='ignore')
    if ignore_lat_lon:
        df_result.drop(columns=['lat', 'lon'], inplace=True)
    return df_result

def prepare_covid_data(folder):
    conf_fname = os.path.join(folder, 'time_series_covid19_confirmed_global.csv')
    death_fname = os.path.join(folder, 'time_series_covid19_deaths_global.csv')
    recov_fname = os.path.join(folder, 'time_series_covid19_recovered_global.csv')

    conf_df = read_case_file(conf_fname, 'confirmed_cases')
    death_df = read_case_file(death_fname, 'deaths', ignore_lat_lon=True)
    recov_df = read_case_file(recov_fname, 'recovered', ignore_lat_lon=True)
    df = conf_df.merge(death_df, on=['state', 'country', 'date'])\
       .merge(recov_df, on=['state', 'country', 'date'])
    
    return df


if __name__ == '__main__':
    # Load path config
    config_file = open('config.yaml', 'r')
    config = yaml.safe_load(config_file)
    SOURCE_DATA_DIR = config['source_data_dir']
    PREP_DATA_DIR = config['prep_data_dir']

    df = prepare_covid_data(SOURCE_DATA_DIR)
    # Create data dir if it doesn't exist
    if not os.path.isdir(PREP_DATA_DIR):
        os.mkdir(PREP_DATA_DIR)
    df.to_csv(os.path.join(PREP_DATA_DIR, 'covid_prep.csv'), index=False)
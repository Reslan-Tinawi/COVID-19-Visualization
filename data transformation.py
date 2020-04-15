import pandas as pd
import numpy as np


def data_preprocessing(confirmed_global_df, deaths_global_df, recovered_global_df, confirmed_us_df, deaths_us_df):

    def drop_irrelevant_columns(df, irrelevant_columns):
        new_df = df.drop(columns=irrelevant_columns)
        return new_df

    def rename_columns(df, columns_mapping):
        new_df = df.rename(columns=columns_mapping)
        return new_df

    def apply_aggregation(df, by_column):
        aggregate_df = df.groupby(by=by_column)\
            .sum()\
            .reset_index()
        return aggregate_df

    def construct_date_df(df, date_column_name, copy_columns, value_column_name):

        data = {}

        data['date'] = date_column_name

        for column in copy_columns:
            data[column] = df[column]

        data[value_column_name] = df[date_column_name]

        date_df = pd.DataFrame(data=data)

        return date_df

    # 1 - Drop irrelevant columns:
    # 1 - a - global data
    irrelevant_columns = ['Lat', 'Long']

    confirmed_global_df = drop_irrelevant_columns(
        confirmed_global_df, irrelevant_columns)
    deaths_global_df = drop_irrelevant_columns(
        deaths_global_df, irrelevant_columns)
    recovered_global_df = drop_irrelevant_columns(
        recovered_global_df, irrelevant_columns)

    # 1 - b - U.S. data
    irrelevant_columns = ['UID', 'iso2', 'iso3', 'code3',
                          'FIPS', 'Admin2', 'Lat', 'Long_', 'Combined_Key']

    confirmed_us_df = drop_irrelevant_columns(
        confirmed_us_df, irrelevant_columns)
    deaths_us_df = drop_irrelevant_columns(deaths_us_df, irrelevant_columns)

    # only deaths data has the column Population, but it should the same for the confirmed data also.
    confirmed_us_df.insert(2, 'Population', deaths_us_df['Population'])

    # 2 - Normalize columns' names:
    columns_mapping = {
        'Province/State': 'State',
        'Province_State': 'State',
        'Country/Region': 'Country',
        'Country_Region': 'Country'
    }

    # global data
    confirmed_global_df = rename_columns(confirmed_global_df, columns_mapping)
    deaths_global_df = rename_columns(deaths_global_df, columns_mapping)
    recovered_global_df = rename_columns(recovered_global_df, columns_mapping)

    # U.S. data
    confirmed_us_df = rename_columns(confirmed_us_df, columns_mapping)
    deaths_us_df = rename_columns(deaths_us_df, columns_mapping)

    # 3 - Drop State column from the global data:
    confirmed_global_df = drop_irrelevant_columns(confirmed_global_df, 'State')
    deaths_global_df = drop_irrelevant_columns(deaths_global_df, 'State')
    recovered_global_df = drop_irrelevant_columns(recovered_global_df, 'State')

    # 4 - Aggregate data by countries for global data:

    # global
    by_column = 'Country'
    confirmed_global_agg_df = apply_aggregation(confirmed_global_df, by_column)
    deaths_global_agg_df = apply_aggregation(deaths_global_df, by_column)
    recovered_global_agg_df = apply_aggregation(recovered_global_df, by_column)

    # U.S.
    by_columns = ['Country', 'State']
    confirmed_us_agg_df = apply_aggregation(confirmed_us_df, by_columns)
    deaths_us_agg_df = apply_aggregation(deaths_us_df, by_columns)

    confirmed_us_agg_df = drop_irrelevant_columns(
        confirmed_us_agg_df, ['Population'])
    deaths_us_agg_df = drop_irrelevant_columns(
        deaths_us_agg_df, ['Population'])

    # 5 - Restructe the Data:
    date_columns = confirmed_global_agg_df.filter(
        regex='\d{1,2}/\d{1,2}/\d{1,4}').columns.values

    # global data
    confirmed_global_date_frames = [construct_date_df(confirmed_global_agg_df, date_column, [
        'Country'], 'confirmed') for date_column in date_columns]
    deaths_global_date_frames = [construct_date_df(deaths_global_agg_df, date_column, [
        'Country'], 'deaths') for date_column in date_columns]
    recovered_global_date_frames = [construct_date_df(recovered_global_agg_df, date_column, [
        'Country'], 'recovered') for date_column in date_columns]

    # U.S. data
    confirmed_us_date_frames = [construct_date_df(confirmed_us_agg_df, date_column, [
        'Country', 'State'], 'confirmed') for date_column in date_columns]
    deaths_us_date_frames = [construct_date_df(deaths_us_agg_df, date_column, [
        'Country', 'State'], 'deaths') for date_column in date_columns]

    # global data
    confirmed_global_time_series = pd.concat(confirmed_global_date_frames)
    deaths_global_time_series = pd.concat(deaths_global_date_frames)
    recovered_global_time_series = pd.concat(recovered_global_date_frames)

    # U.S. data
    confirmed_us_time_series = pd.concat(confirmed_us_date_frames)
    deaths_us_time_series = pd.concat(deaths_us_date_frames)

    return confirmed_global_time_series, deaths_global_time_series, recovered_global_time_series,\
        confirmed_us_time_series, deaths_us_time_series

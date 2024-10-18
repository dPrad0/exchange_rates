import pandas as pd
import requests
import csv
from io import StringIO

def get_cop_usd():

    # Fetch the CSV content from the URL
    url = "https://www.datos.gov.co/api/views/mcec-87by/rows.csv?accessType=DOWNLOAD&bom=true&format=true"
    response = requests.get(url)
    csv_content = response.text

    # Convert csv content to DataFrame
    df = pd.read_csv(StringIO(csv_content), encoding='utf-8')

    # Remove columns "UNIDAD" and "VIGENCIAHASTA"
    df.drop(columns=["UNIDAD", "VIGENCIAHASTA"], inplace=True)

    # Convert "VIGENCIADESDE" column to datetime
    df['VIGENCIADESDE'] = pd.to_datetime(df['VIGENCIADESDE'], dayfirst=True)

    # Create a DataFrame with all continuous dates
    min_date = df['VIGENCIADESDE'].min()
    max_date = df['VIGENCIADESDE'].max()
    date_range = pd.date_range(start=min_date, end=max_date)
    date_df = pd.DataFrame({'VIGENCIADESDE': date_range})

    # Merge the two DataFrames on "VIGENCIADESDE" and forward fill missing values
    merged_df = pd.merge(date_df, df, on='VIGENCIADESDE', how='left')
    merged_df.fillna(method='ffill', inplace=True)

    # Rename columns
    merged_df.rename(columns={'VIGENCIADESDE': 'Fecha', 'VALOR': 'COP/USD'}, inplace=True)

    # Rearrange column order
    merged_df = merged_df[['Fecha', 'COP/USD']]

    merged_df['Fecha'] = pd.to_datetime(merged_df['Fecha'])
    merged_df['COP/USD'] = merged_df['COP/USD'].str.replace(',', '').astype(float)
    merged_df['COP/USD'] = pd.to_numeric(merged_df['COP/USD'])

    # Save df to csv
    merged_df.to_csv('exchange_rates/cop_usd.csv', index=False)

    return merged_df

if __name__ == "__main__":
    get_cop_usd()
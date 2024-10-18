import requests
from bs4 import BeautifulSoup
import pandas as pd
import sys
import os

def get_crc_usd():
    # URL of the website
    url = "https://gee.bccr.fi.cr/indicadoreseconomicos/Cuadros/frmVerCatCuadro.aspx?CodCuadro=400&Idioma=1&FecInicial=2019/01/01&Filtro=0&Exportar=True&Excel=True"

    response = requests.get(url)

    if response.status_code == 200:
    # Parse the HTML content
        soup = BeautifulSoup(response.content, "html.parser")
    else:
        print("Failed to fetch data from the website.")
        pass

    # Find the table
    table = soup.find('table')

    # Extract column headers
    headers = ['Date', 'Tipo Cambio Compra', 'Tipo Cambio Venta']

    # Extract data rows
    data = []
    for row in soup.find_all('tr'):
        row_data = [cell.text.strip() for cell in row.find_all('td')]
        data.append(row_data)

    # Create DataFrame
    df = pd.DataFrame(data, columns=headers)

    # Drop the "Tipo Cambio Compra" column
    df = df.drop(columns=["Tipo Cambio Compra"])

    # Drop first 5 rows that are empty
    df = df.iloc[5:]

    # Change column headers
    df = df.rename(columns={"Date": "Fecha", "Tipo Cambio Venta": "CRC/USD"})

    # Convert blank values in "CRC/USD" column to NaN
    df["CRC/USD"] = df["CRC/USD"].replace("", pd.NA)

    # Drop rows with NaN values in "CRC/USD" column
    df.dropna(subset=["CRC/USD"], inplace=True)

    # Mapping of Spanish month names to English month abbreviations
    month_names_spanish = {
        'Ene': 'Jan',
        'Feb': 'Feb',
        'Mar': 'Mar',
        'Abr': 'Apr',
        'May': 'May',
        'Jun': 'Jun',
        'Jul': 'Jul',
        'Ago': 'Aug',
        'Set': 'Sep',
        'Oct': 'Oct',
        'Nov': 'Nov',
        'Dic': 'Dec'
    }

    # Convert "CRC/USD" column to numeric type
    df['CRC/USD'] = pd.to_numeric(df['CRC/USD'].str.replace(',', '.'))

    # Round the values to two decimal places
    df['CRC/USD'] = df['CRC/USD'].round(2)

    # Replace Spanish month names with English month names
    df['Fecha'] = df['Fecha'].replace(month_names_spanish, regex=True)

    # Convert column Fecha to datetime
    df['Fecha'] = pd.to_datetime(df['Fecha'], format='%d %b %Y', errors='coerce')

    df['Fecha'] = pd.to_datetime(df['Fecha'])

    # Convert column CRC/USD to numeric
    df['CRC/USD'] = pd.to_numeric(df['CRC/USD'])

    # Save df to csv
    df.to_csv('exchange_rates/crc_usd.csv', index=False)

    return df

if __name__ == "__main__":

    get_crc_usd()

    # # Add the parent directory of the exchange_rates package to sys.path
    # current_dir = os.path.dirname(os.path.abspath(__file__))
    # parent_dir = os.path.dirname(current_dir)
    # sys.path.insert(0, parent_dir)

    # import mysql_functions as sql

    # table_name = 'crc_usd'
    # sql.replace_table(df,table_name)

    # df.to_csv('exchange_rates/crc_usd.csv', index=False)
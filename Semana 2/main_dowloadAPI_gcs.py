import datetime
import pandas as pd
from google.cloud import storage
import wbdata
pd.options.display.float_format = '{:.2f}'.format


# Define variables for Cloud Functions
bucket_name = 'fromworldbank_to_bucket'
#blob_name = 'data'

def fetch_world_bank_data():
    # List of indicators
    indicators = {
        "NY.GDP.PCAP.CN": "GDP per Capita, Current US Dollars",
        "FP.CPI.TOTL.ZG": "Inflation, Consumer Prices (Annual %)",
        "NY.GDP.DEFL.KD.ZG": "Inflation, GDP Deflator (Annual %)",
        "NY.GDP.MKTP.KN": "GDP, Nominal (Current US Dollars)",
        "NY.GDP.PCAP.KN": "GDP per Capita, Nominal (Current US Dollars)",
        "BX.TRF.PWKR.DT.GD.ZS": "Personal Remittances, Received (% of GDP)",
        "SP.POP.TOTL": "Population, Total",
        "SL.UEM.TOTL.ZS": "Unemployment, Total (% of Total Labor Force)",
        "SM.POP.NETM": "Net Migration",
        "SL.UEM.TOTL.MA.NE.ZS" : "Unemployment, Male (% of Male Labor Force) (National Estimate)",
        "SL.UEM.TOTL.FE.ZS" : "Unemployment, Female (% of Female Labor Force) (Modeled ILO Estimate)",
        "SL.EMP.WORK.ZS" : "Wage and Salaried Workers, Total (% of Total Employment) (Modeled ILO Estimate)",
        "SL.EMP.WORK.MA.ZS": "Wage and Salaried Workers, Male (% of Male Employment) (Modeled ILO Estimate)",
        "SL.EMP.WORK.FE.ZS": "Wage and Salaried Workers, Female (% of Female Employment) (Modeled ILO Estimate)",
        "NY.GDP.MKTP.KN": "GDP (Constant LCU)",
        "NY.GDP.PCAP.KN": "GDP per Capita (Constant LCU)",
        "SM.POP.TOTL": "International Migrant Stock (% of Population)"
    }

    # List of countries
    countries = ['USA', 'PRY', 'BRA', 'URY', 'CHL', 'BOL', 'VEN', 'PER', 'CAN', 'MEX', 'COL', 'ECU', 'PAN', 'GTM', 'SUR', 'CRI', 'CUB', 'SLV',
        'DOM', 'NIC', 'HND', 'TTO', 'GUY', 'BRB', 'ATG', 'BHS', 'BLZ', 'DMA', 'GRD', 'HTI', 'JAM', 'LCA', 'VCT', 'ARG', 'AUS', 'AUT',
        'BEL', 'CZE', 'DNK', 'EST', 'FIN', 'FRA', 'DEU', 'GRC', 'HUN', 'ISL', 'IRL', 'ISR', 'ITA', 'JPN', 'KOR', 'LVA', 'LTU', 'LUX',
        'NLD', 'NZL', 'NOR', 'POL'
    ]

    # Fetch World Bank data
    data = wbdata.get_dataframe(indicators, country=countries, convert_date=False)

    # Add the "Code Country" column
    data['Code Country'] = data.index.get_level_values('country').str[:3].str.upper() + data.index.get_level_values('date').astype(str)

    # Reorder columns with "Code Country," "Country," and "Year" at the beginning
    column_order = ['Code Country'] + [col for col in data.columns if col not in ['Code Country']] #, 'country', 'date'
    data = data[column_order] 

    # Upload DataFrame to Cloud Storage as a pickle file
    client = storage.Client()
    bucket = client.get_bucket(bucket_name)
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    
    # Save DataFrame as pickle
    pickle_blob = bucket.blob(f'data/world_bank_data_{today}.pkl')
    data.to_pickle('/tmp/data.pkl')  # Save DataFrame as a temporary file
    with open('/tmp/data.pkl', 'rb') as f:
        pickle_blob.upload_from_file(f)
    
    # Save DataFrame as CSV
    csv_blob = bucket.blob(f'data/world_bank_data_{today}.csv')
    csv_string = data.to_csv(index=True)  # Save DataFrame as CSV (adjust other parameters as needed)
    csv_blob.upload_from_string(csv_string)

    return f"World Bank data saved to {pickle_blob.name} (pickle) and {csv_blob.name} (CSV) in {bucket_name}."

def main(event, context): # This is my entry point
    fetch_world_bank_data()

if __name__ == "__main__":
    main('data', 'context')

import pandas as pd
import streamlit as st
from urllib.parse import urlparse
from google.oauth2 import service_account
from googleapiclient.discovery import build
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import DateRange, Dimension, Metric, RunReportRequest

def get_credentials():
    """Carica le credenziali del Service Account."""
    return service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"], # o letto da .env
    )

def fetch_gsc_data(site_url, start_date, end_date):
    """Estrae i dati da Google Search Console (Query e Pagine)."""
    creds = get_credentials()
    service = build('webmasters', 'v3', credentials=creds)
    
    request_body = {
        'startDate': start_date, # Formato YYYY-MM-DD
        'endDate': end_date,
        'dimensions': ['page', 'query'],
        'rowLimit': 25000
    }
    
    # Esecuzione della chiamata API
    response = service.searchanalytics().query(siteUrl=site_url, body=request_body).execute()
    
    if 'rows' not in response:
        return pd.DataFrame()
        
    # Parsing della risposta
    data = []
    for row in response['rows']:
        data.append({
            'page': row['keys'][0],
            'keyword': row['keys'][1],
            'clicks': row['clicks'],
            'impressions': row['impressions'],
            'ctr': row['ctr'],
            'position': row['position']
        })
        
    df_gsc = pd.DataFrame(data)
    
    # NORMALIZZAZIONE: Estraiamo solo il path dall'URL di GSC per fare il join con GA4
    df_gsc['page_path'] = df_gsc['page'].apply(lambda x: urlparse(x).path)
    # Se il path è vuoto (home page), lo impostiamo come "/"
    df_gsc['page_path'] = df_gsc['page_path'].apply(lambda x: "/" if x == "" else x)
    
    return df_gsc

def fetch_ga4_data(property_id, start_date, end_date):
    """Estrae i dati da Google Analytics 4 (Sessioni e Conversioni per Pagina)."""
    creds = get_credentials()
    client = BetaAnalyticsDataClient(credentials=creds)
    
    # Costruzione della richiesta GA4
    request = RunReportRequest(
        property=f"properties/{property_id}",
        dimensions=[Dimension(name="pagePath")],
        metrics=[
            Metric(name="sessions"),
            Metric(name="conversions"),
            Metric(name="activeUsers")
        ],
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
    )
    
    response = client.run_report(request)
    
    data = []
    for row in response.rows:
        data.append({
            'page_path': row.dimension_values[0].value,
            'sessions': int(row.metric_values[0].value),
            'conversions': float(row.metric_values[1].value),
            'active_users': int(row.metric_values[2].value)
        })
        
    return pd.DataFrame(data)

def get_merged_seo_data(site_url, property_id, start_date, end_date):
    """Unisce i dati di GSC e GA4 usando il page_path come chiave di Join."""
    df_gsc = fetch_gsc_data(site_url, start_date, end_date)
    df_ga4 = fetch_ga4_data(property_id, start_date, end_date)
    
    if df_gsc.empty or df_ga4.empty:
        return df_gsc if df_ga4.empty else df_ga4
        
    # Eseguiamo un Left Join: teniamo tutte le keyword/pagine di GSC e attacchiamo i dati di GA4
    df_merged = pd.merge(df_gsc, df_ga4, on='page_path', how='left')
    
    # Riempiamo i valori NaN con 0 per le pagine che non hanno registrato sessioni/conversioni
    df_merged[['sessions', 'conversions', 'active_users']] = df_merged[['sessions', 'conversions', 'active_users']].fillna(0)
    
    return df_merged
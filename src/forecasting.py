from prophet import Prophet
from sklearn.metrics import mean_absolute_percentage_error
import pandas as pd

def train_and_forecast(df, periods=7):
    # Prophet richiede colonne nominate esattamente 'ds' (Data) e 'y' (Valore)
    df_prophet = df[['Data', 'Clic']].rename(columns={'Data': 'ds', 'Clic': 'y'})
    
    # Inizializza e addestra il modello
    model = Prophet(yearly_seasonality=False, weekly_seasonality=True, daily_seasonality=False)
    model.fit(df_prophet)
    
    # Crea il futuro
    future = model.make_future_dataframe(periods=periods)
    forecast = model.predict(future)
    
    return forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]
def perform_backtest(df):
    # Dati: Tutto tranne l'ultimo mese
    train_data = df.iloc[:-30] 
    test_data = df.iloc[-30:] # L'ultimo mese che usiamo come test
    
    # Addestramento su dati passati
    model = Prophet()
    model.fit(train_data.rename(columns={'Data': 'ds', 'Clic': 'y'}))
    
    # Predizione
    future = model.make_future_dataframe(periods=30)
    forecast = model.predict(future)
    
    # Calcolo errore (quanto ci siamo allontanati dalla realtà?)
    predictions = forecast.iloc[-30:]['yhat']
    mape = mean_absolute_percentage_error(test_data['Clic'], predictions)
    
    return mape, forecast
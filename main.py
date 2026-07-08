from src.processor import load_and_clean_gsc

# Percorso del tuo file
file_path = 'data/Query.csv'

# Testiamo la pulizia
try:
    df = load_and_clean_gsc(file_path)
    print("Dati puliti correttamente!")
    print(df.info())
    print(df.head())
except Exception as e:
    print(f"Errore durante l'elaborazione: {e}")
import yfinance as yf
from pymongo import MongoClient
import pandas as pd

# Connexion à MongoDB
client = MongoClient('mongodb+srv://haddadfayssal75:K5mg1DdBUE5OfTS6@cluster0.0xesz.mongodb.net/financial_data?retryWrites=true&w=majority')
db = client['financial_data']
collection = db['sp500_data']  # Nouvelle collection pour le S&P 500

# Récupérer les données historiques du S&P 500 sur 10 ans avec yfinance
ticker = "^GSPC"
stock = yf.Ticker(ticker)

print("Tentative de récupération des données pour le S&P 500 (10 ans)")
data = stock.history(period="10y", interval="1d")  # Récupérer les données sur 10 ans en D1 (quotidiennes)

# Si les données sont valides, on les insère dans MongoDB
if not data.empty:
    data['Ticker'] = ticker
    data.index = pd.to_datetime(data.index)  # Conversion de l'index (Date) en DateTime
    data.reset_index(inplace=True)  # Réinitialisation de l'index avant la conversion en JSON
    stock_data_json = data.to_dict('records')  # Transformer en JSON

    # Insérer dans MongoDB
    collection.insert_many(stock_data_json)
    print("Données S&P 500 insérées dans MongoDB avec succès.")
else:
    print("Aucune donnée trouvée pour le S&P 500.")

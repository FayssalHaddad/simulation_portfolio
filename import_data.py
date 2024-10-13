import yfinance as yf
import pandas as pd
from pymongo import MongoClient

# Connexion à MongoDB
# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

# Récupérer la variable d'environnement pour MongoDB
client = MongoClient(os.getenv("MONGODB_URI"))
db = client['financial_data']
collection = db['stock_data']

# Récupérer la liste des tickers du S&P 500 depuis Wikipedia
url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
sp500_table = pd.read_html(url)
sp500_tickers = sp500_table[0]['Symbol'].tolist()

# Initialiser une liste pour stocker les tickers filtrés
filtered_tickers = []

# Boucle pour filtrer les actions avec une capitalisation boursière > 5 milliards
for ticker in sp500_tickers:
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        if info.get('marketCap', 0) > 5e9:  # Vérifier si la capitalisation est > 5 milliards
            filtered_tickers.append(ticker)
    except Exception as e:
        print(f"Erreur avec le ticker {ticker}: {e}")
        continue

# Récupérer les données historiques pour chaque ticker et les insérer directement dans MongoDB
for ticker in filtered_tickers:
    stock = yf.Ticker(ticker)
    try:
        print(f"Tentative de récupération des données pour {ticker} avec la période 10y.")
        data = stock.history(period="10y", interval="1d")  # Récupérer les données sur 10 ans

        if data.empty:
            print(f"Aucune donnée trouvée pour {ticker} sur 10 ans. Aucune importation ne sera effectuée.")
            continue  # Ne pas importer l'action si elle n'a pas de données sur 10 ans
        
        # Préparer les données pour MongoDB
        data['Ticker'] = ticker
        data.index = pd.to_datetime(data.index)  # Conversion de l'index (Date) en DateTime
        data.reset_index(inplace=True)  # Remettre l'index 'Date' comme une colonne normale
        stock_data_json = data.to_dict('records')  # Transformer les données en JSON pour MongoDB

        # Insérer les données dans MongoDB dans la collection 'stock_data'
        collection.insert_many(stock_data_json)
        print(f"Données pour {ticker} insérées dans MongoDB avec succès.")

    except Exception as e:
        print(f"Erreur lors de la récupération des données pour {ticker}: {e}")

print("Toutes les données boursières ont été insérées dans MongoDB avec succès.")


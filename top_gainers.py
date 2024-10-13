from pymongo import MongoClient
from datetime import datetime, timedelta
import calendar
import pandas as pd
import matplotlib.pyplot as plt

# Connexion à MongoDB Atlas
client = MongoClient('mongodb+srv://haddadfayssal75:K5mg1DdBUE5OfTS6@cluster0.0xesz.mongodb.net/financial_data?retryWrites=true&w=majority')
db = client['financial_data']
collection = db['stock_data']

# Fonction pour afficher les détails des actions et vérifier les données
def get_top_gainers_for_month(year, month):
    start_date = datetime(year, month, 1)
    end_date = datetime(year, month, calendar.monthrange(year, month)[1])

    pipeline = [
        {
            "$match": {
                "Date": {"$gte": start_date, "$lte": end_date}
            }
        },
        {
            "$sort": {"Date": 1}
        },
        {
            "$group": {
                "_id": "$Ticker",
                "start_price": {"$first": "$Close"},
                "end_price": {"$last": "$Close"}
            }
        },
        {
            "$project": {
                "Ticker": "$_id",
                "start_price": 1,
                "end_price": 1,
                "percentage_change": {
                    "$multiply": [
                        {"$divide": [{"$subtract": ["$end_price", "$start_price"]}, "$start_price"]}, 100
                    ]
                }
            }
        },
        {
            "$sort": {"percentage_change": -1}
        },
        {
            "$limit": 3
        }
    ]

    top_gainers = list(collection.aggregate(pipeline))
    
    # Log de debug pour chaque action
    #for gainer in top_gainers:
    #    print(f"Ticker: {gainer['_id']}, Start Price: {gainer['start_price']}, End Price: {gainer['end_price']}")
    
    return top_gainers


# Fonction pour récupérer la performance d'une liste de tickers pour le mois suivant
def get_performance_for_next_month(tickers, year, month):
    # Ajuster l'année et le mois pour le mois suivant
    if month == 12:
        next_month = 1
        next_year = year + 1
    else:
        next_month = month + 1
        next_year = year

    start_date = datetime(next_year, next_month, 1)
    end_date = datetime(next_year, next_month, calendar.monthrange(next_year, next_month)[1])

    # Pipeline pour récupérer les performances des tickers donnés pour le mois suivant
    pipeline = [
        {
            "$match": {
                "Date": {"$gte": start_date, "$lte": end_date},
                "Ticker": {"$in": tickers}
            }
        },
        {
            "$sort": {"Date": 1}
        },
        {
            "$group": {
                "_id": "$Ticker",
                "start_price": {"$first": "$Close"},
                "end_price": {"$last": "$Close"}
            }
        }
    ]

    performance_data = list(collection.aggregate(pipeline))
    
    return performance_data

# Récupérer les top gagnants pour chaque mois à partir de 2 ans en arrière
ten_years_ago = datetime.now().year - 10
current_year = datetime.now().year
current_month = datetime.now().month

for year in range(ten_years_ago, current_year + 1):  # Parcourir les années depuis il y a 2 ans
    start_month = 1 if year > ten_years_ago else datetime.now().month  # Si on est dans une année passée, commencer au mois de janvier
    end_month = current_month if year == current_year else 12  # S'arrêter au mois actuel pour l'année en cours

    for month in range(start_month, end_month + 1):  # Parcourir chaque mois jusqu'au mois actuel
        print(f"\nTop 3 gagnants pour {calendar.month_name[month]} {year} :")
        top_gainers = get_top_gainers_for_month(year, month)

        if top_gainers:
            for gainer in top_gainers:
                print(f"Action : {gainer['_id']}, Variation : {gainer['percentage_change']:.2f}%")
        else:
            print("Aucun résultat pour ce mois.")
            
# Dictionnaire pour stocker les gagnants de chaque mois
gainers_dict = {}

# Récupérer les top gagnants et les stocker dans le dictionnaire
for year in range(ten_years_ago, current_year + 1):
    start_month = 1 if year > ten_years_ago else datetime.now().month
    end_month = current_month if year == current_year else 12

    for month in range(start_month, end_month + 1):
        top_gainers = get_top_gainers_for_month(year, month)
        
        # Stocker les top gagnants dans le dictionnaire sous la forme {'(year, month)': [Tickers]}
        gainers_dict[(year, month)] = top_gainers

# Fonction pour afficher les performances des top gagnants du mois précédent pour le mois suivant
def show_performance_of_previous_gainers(gainers_dict):
    for (year, month), gainers in gainers_dict.items():
        tickers = [gainer['_id'] for gainer in gainers]  # Extraire les tickers

        # Récupérer les performances des tickers pour le mois suivant
        performance_next_month = get_performance_for_next_month(tickers, year, month)

        if not performance_next_month:
            print(f"Aucune donnée pour {calendar.month_name[month + 1]} {year}")
            continue

        print(f"\nPerformances des top gagnantes de {calendar.month_name[month]} {year} pour le mois suivant :")
        
        for gainer in gainers:
            ticker = gainer['_id']
            start_price = gainer['end_price']  # Prix de clôture du mois actuel
            
            # Récupérer la performance pour ce ticker dans le mois suivant
            performance_data = next((item for item in performance_next_month if item['_id'] == ticker), None)

            if performance_data:
                end_price_next_month = performance_data['end_price']
                if start_price > 0:
                    performance = (end_price_next_month - start_price) / start_price * 100
                    print(f"Action : {ticker}, Performance au mois suivant : {performance:.2f}%")
            else:
                print(f"Données manquantes pour {ticker} au mois suivant.")

# Récupération et affichage des performances des gagnants du mois précédent pour le mois suivant
show_performance_of_previous_gainers(gainers_dict)

# Fonction pour simuler la performance du portefeuille avec répartition équipondérée sur les 3 actions gagnantes du mois précédent
# Fonction pour simuler la performance du portefeuille avec répartition équipondérée sur les 3 actions gagnantes du mois précédent
def simulate_portfolio_performance(gainers_dict, initial_investment=10000, monthly_investment=1000):
    portfolio_value = initial_investment  # Montant initial
    portfolio_history = []  # Historique de la valeur du portefeuille pour chaque mois

    # Parcourir chaque mois et année dans l'ordre chronologique
    for (year, month), gainers in sorted(gainers_dict.items()):
        # Si le mois courant n'a pas de gagnants, on passe
        if not gainers:
            continue

        tickers = [gainer['_id'] for gainer in gainers]  # Extraire les tickers des gagnants

        # Récupérer la performance des actions gagnantes pour le mois suivant
        performance_next_month = get_performance_for_next_month(tickers, year, month)

        if not performance_next_month:
            print(f"Aucune donnée pour {calendar.month_name[month + 1]} {year}. Pas de simulation pour ce mois.")
            continue

        # Calculer la performance totale pour le mois
        monthly_return = 0
        for gainer in gainers:
            ticker = gainer['_id']
            start_price = gainer['end_price']  # Prix de clôture du mois actuel
            
            # Récupérer la performance pour ce ticker dans le mois suivant
            performance_data = next((item for item in performance_next_month if item['_id'] == ticker), None)

            if performance_data:
                end_price_next_month = performance_data['end_price']
                if start_price > 0:
                    # Calculer le rendement pour cette action
                    stock_return = (end_price_next_month - start_price) / start_price
                    # Ajouter le rendement pondéré par l'investissement équipondéré (1/3 de l'investissement sur chaque action)
                    monthly_return += stock_return / len(gainers)  # Divisé par le nombre de gagnants (équipondéré)
                else:
                    print(f"Prix de départ invalide pour {ticker}")
            else:
                print(f"Données manquantes pour {ticker} au mois suivant.")

        # Mise à jour de la valeur du portefeuille avec le rendement du mois
        portfolio_value *= (1 + monthly_return)

        # Ajouter 1000€ au portefeuille chaque mois
        portfolio_value += monthly_investment

        # Utiliser la date de fin du mois comme référence pour l'historique (plus précise)
        last_day_of_month = datetime(year, month, calendar.monthrange(year, month)[1])
        
        # Stocker l'historique du portefeuille
        portfolio_history.append({
            'Date': last_day_of_month,
            'portfolio_value': portfolio_value
        })

    return portfolio_history


# Fonction pour simuler la performance du portefeuille S&P 500
def simulate_sp500_performance(initial_investment=10000, monthly_investment=1000):
    collection = db['sp500_data']  # Utiliser la collection S&P 500

    # Pipeline MongoDB pour récupérer les données dans l'ordre chronologique
    pipeline = [
        {"$sort": {"Date": 1}},  # Trier par date croissante
        {
            "$project": {
                "Date": 1,
                "Close": 1,  # Récupérer les prix de clôture
            }
        }
    ]

    # Récupérer toutes les données du S&P 500
    sp500_data = list(collection.aggregate(pipeline))

    # Simulation du portefeuille
    portfolio_value = initial_investment
    portfolio_history = []  # Historique du portefeuille

    for i, day_data in enumerate(sp500_data):
        # Calculer la performance du jour (en supposant que c'est chaque jour de trading)
        if i == 0:
            continue  # On passe le premier jour, car pas de données pour calculer le rendement

        # Calculer la performance entre les jours
        previous_day = sp500_data[i - 1]
        current_close = day_data['Close']
        previous_close = previous_day['Close']

        if previous_close > 0:
            daily_return = (current_close - previous_close) / previous_close
            portfolio_value *= (1 + daily_return)

        # Ajouter 1000€ à chaque mois (approximativement tous les 21 jours de trading)
        if i % 21 == 0:  # Environ un mois de trading
            portfolio_value += monthly_investment

        # Ajouter à l'historique
        portfolio_history.append({
            'Date': day_data['Date'],
            'portfolio_value': portfolio_value
        })

    return portfolio_history











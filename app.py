from fastapi import FastAPI
from top_gainers import get_top_gainers_for_month, simulate_portfolio_performance
from datetime import datetime

app = FastAPI()

# Endpoint pour obtenir les top gagnants d'un mois donné
@app.get("/top-gainers/{year}/{month}")
async def top_gainers(year: int, month: int):
    return get_top_gainers_for_month(year, month)

# Endpoint pour calculer la performance du portefeuille sur deux ans
@app.get("/portfolio-performance")
async def portfolio_performance():
    gainers_dict = {}
    two_years_ago = datetime.now().year - 2
    current_year = datetime.now().year
    current_month = datetime.now().month

    # Collecter les top gagnants pour chaque mois
    for year in range(two_years_ago, current_year + 1):
        start_month = 1 if year > two_years_ago else datetime.now().month
        end_month = current_month if year == current_year else 12

        for month in range(start_month, end_month + 1):
            top_gainers = get_top_gainers_for_month(year, month)
            gainers_dict[(year, month)] = top_gainers

    # Simuler la performance du portefeuille
    portfolio_performance = simulate_portfolio_performance(gainers_dict)
    return portfolio_performance
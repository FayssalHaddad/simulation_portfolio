import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from top_gainers import simulate_portfolio_performance, simulate_sp500_performance, get_top_gainers_for_month
from datetime import datetime

# Section de l'accueil
st.sidebar.title("Navigation")
page = st.sidebar.radio("Aller à", ["Accueil", "Simulation de Portefeuille"])

if page == "Accueil":
    st.title("Bienvenue sur notre Simulateur de Stratégie Boursière")
    st.write("""
        Cette application permet de faire des backtests de stratégie sur les 10 dernières années en investissant 
        dans les 3 actions les plus performantes de chaque mois. Vous pouvez également voir une simulation de 
        portefeuille basée sur cette stratégie et comparer sa performance à celle du S&P 500.
    """)

elif page == "Simulation de Portefeuille":
    st.title("Simulateur de Portefeuille - Top Gagnants vs S&P 500")

    # Demander à l'utilisateur d'entrer les paramètres
    capital_initial = st.number_input("Capital initial (€)", value=10000)
    investissement_mensuel = st.number_input("Investissement mensuel (€)", value=1000)

    # Ajouter un bouton pour déclencher la simulation
    if st.button("Lancer la Simulation"):
        # Récupération de la simulation du portefeuille top 3 gagnantes
        gainers_dict = {}
        ten_years_ago = datetime.now().year - 10
        current_year = datetime.now().year
        current_month = datetime.now().month

        for year in range(ten_years_ago, current_year + 1):
            start_month = 1 if year > ten_years_ago else datetime.now().month
            end_month = current_month if year == current_year else 12

            for month in range(start_month, end_month + 1):
                top_gainers = get_top_gainers_for_month(year, month)
                gainers_dict[(year, month)] = top_gainers

        # Simulation du portefeuille top 3 gagnantes avec les paramètres utilisateur
        portfolio_performance = simulate_portfolio_performance(gainers_dict, capital_initial, investissement_mensuel)

        # Simulation du S&P 500 avec les mêmes paramètres
        sp500_performance = simulate_sp500_performance(capital_initial, investissement_mensuel)

        # Si des données existent, afficher le graphique
        if portfolio_performance and sp500_performance:
            st.write("Historique de la Valeur du Portefeuille")

            # Convertir les résultats en DataFrame pour affichage
            df_portfolio = pd.DataFrame(portfolio_performance)
            df_sp500 = pd.DataFrame(sp500_performance)

            # Convertir les dates en format datetime
            df_portfolio['Date'] = pd.to_datetime(df_portfolio['Date'])
            df_sp500['Date'] = pd.to_datetime(df_sp500['Date'])

            # Création du graphique Plotly
            fig = go.Figure()

            # Ajout de la courbe des top 3 gagnantes
            fig.add_trace(go.Scatter(x=df_portfolio['Date'],
                                     y=df_portfolio['portfolio_value'],
                                     mode='lines+markers',
                                     name='Valeur du Portefeuille - Top 3 Gagnantes',
                                     line=dict(color='blue')))

            # Ajout de la courbe du S&P 500 en rouge
            fig.add_trace(go.Scatter(x=df_sp500['Date'],
                                     y=df_sp500['portfolio_value'],
                                     mode='lines',
                                     name='Valeur du Portefeuille - S&P 500',
                                     line=dict(color='red')))

            # Ajustements du design du graphique
            fig.update_layout(
                title="Historique de la Valeur du Portefeuille vs S&P 500",
                xaxis_title="Date",
                yaxis_title="Valeur (€)",
                showlegend=True
            )

            # Affichage du graphique avec Plotly
            st.plotly_chart(fig)

            # Afficher les résultats sous forme de tableau
            st.write("Portefeuille Top 3 Gagnantes :")
            st.dataframe(df_portfolio)
            st.write("Portefeuille S&P 500 :")
            st.dataframe(df_sp500)
        else:
            st.write("Aucune donnée disponible pour la simulation.")

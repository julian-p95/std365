# Importations
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

# Titre de la page
st.title("Analyse des Tables ERP")

# Lecture des fichiers Excel
erp_relations = pd.read_excel("erp_all_table_relations_finalV2.xlsx", sheet_name='Sheet1')
d365_tables = pd.read_excel("D365FO.xlsx", sheet_name='D365 Table')

# Gestion des valeurs NaN
d365_tables['App module'].fillna("Non spécifié", inplace=True)

# Calcul du nombre total de tables
total_tables = len(d365_tables)

# Création d'une nouvelle colonne combinant App module, Table group et Table type
d365_tables['AppModule-TableGroup-TableType'] = d365_tables['App module'] + " - " + d365_tables['Table group'] + " - " + d365_tables['Table type']

# Compte du nombre de tables pour chaque combinaison unique
table_combination_counts = d365_tables['AppModule-TableGroup-TableType'].value_counts()

# Graphique à barres horizontales
fig, ax = plt.subplots()
table_combination_counts.plot(kind='barh', ax=ax)
plt.title('Répartition des tables par App module, Table group et Table type')
plt.xlabel('Nombre de tables')
plt.ylabel('App module - Table group - Table type')
st.pyplot(fig)

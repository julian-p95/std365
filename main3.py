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
d365_tables['Table group'].fillna("Non spécifié", inplace=True)
d365_tables['Table type'].fillna("Non spécifié", inplace=True)

# Calcul du nombre total de tables
total_tables = len(d365_tables)

# Création d'une nouvelle colonne pour la combinaison "AppModule - TableGroup - TableType"
d365_tables['AppModule-TableGroup-TableType'] = d365_tables['App module'] + " - " + d365_tables['Table group'] + " - " + d365_tables['Table type']

# Sélection de l'App module
selected_app_module = st.selectbox('Sélectionnez un App module:', ['ALL'] + d365_tables['App module'].unique().tolist())
if selected_app_module != 'ALL':
    d365_tables = d365_tables[d365_tables['App module'] == selected_app_module]

# Graphique à barres horizontales pour la combinaison "AppModule - TableGroup - TableType"
combination_counts = d365_tables['AppModule-TableGroup-TableType'].value_counts()
fig, ax = plt.subplots()
combination_counts.plot(kind='barh', ax=ax)
plt.title('Répartition des tables par AppModule - TableGroup - TableType')
plt.xlabel('Nombre de tables')
plt.ylabel('AppModule - TableGroup - TableType')
st.pyplot(fig)

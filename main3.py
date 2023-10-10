import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

# Titre de la page
st.title("Analyse des Tables ERP")

# Lecture des fichiers Excel
d365_tables = pd.read_excel("/path/to/D365FO.xlsx", sheet_name='D365 Table')
erp_relations = pd.read_excel("/path/to/erp_all_table_relations_finalV2.xlsx", sheet_name='Sheet1')

# Gestion des valeurs NaN
d365_tables['App module'].fillna("Non spécifié", inplace=True)
d365_tables['Table group'].fillna("Non spécifié", inplace=True)
d365_tables['Tabletype'].fillna("Non spécifié", inplace=True)

# Création d'une nouvelle colonne pour App module - Table group - Table type
d365_tables['AppModule-TableGroup-TableType'] = d365_tables['App module'] + " - " + d365_tables['Table group'] + " - " + d365_tables['Tabletype']

# Graphique à barres horizontales pour AppModule-TableGroup-TableType
grouped_counts = d365_tables['AppModule-TableGroup-TableType'].value_counts()
fig, ax = plt.subplots()
grouped_counts.plot(kind='barh', ax=ax)
plt.title('Répartition des App module - Table group - Table type')
plt.xlabel('Nombre de tables')
plt.ylabel('App module - Table group - Table type')
st.pyplot(fig)

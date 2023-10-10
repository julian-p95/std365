import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

# Titre de la page
st.title("Analyse des Tables ERP")

# Lecture des fichiers Excel
d365_tables = pd.read_excel("D365FO.xlsx", sheet_name='D365 Table')

# Gestion des valeurs NaN
d365_tables['App module'].fillna("Non spécifié", inplace=True)
d365_tables['Table group'].fillna("Non spécifié", inplace=True)
d365_tables['Table\xa0type'].fillna("Non spécifié", inplace=True)

# Exclude 'Non spécifié' from App module
d365_tables = d365_tables[d365_tables['App module'] != 'Non spécifié']

# Création d'une nouvelle colonne pour App module - Table group - Table type
d365_tables['AppModule-TableGroup-TableType'] = d365_tables['App module'] + " - " + d365_tables['Table group'] + " - " + d365_tables['Table\xa0type']

# Graphique à barres horizontales
grouped_counts = d365_tables['AppModule-TableGroup-TableType'].value_counts()
fig, ax = plt.subplots()
grouped_counts.plot(kind='barh', ax=ax)
plt.title('Répartition des App module - Table group - Table type')
plt.xlabel('Nombre de tables')
plt.ylabel('App module - Table group - Table type')
st.pyplot(fig)

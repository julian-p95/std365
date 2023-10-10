import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

# Titre de la page
st.title("Analyse des Tables ERP")

# Lecture des fichiers Excel
d365_tables = pd.read_excel("D365FO.xlsx", sheet_name='D365 Table')

# Gestion des valeurs NaN
d365_tables = d365_tables.dropna(subset=['App module'])  # Supprime les lignes où 'App module' est NaN
d365_tables['Table group'].fillna("Non spécifié", inplace=True)
d365_tables['Tabletype'].fillna("Non spécifié", inplace=True)

# Création d'une nouvelle colonne pour App module - Table group - Table type
d365_tables['AppModule-TableGroup-TableType'] = d365_tables['App module'] + " - " + d365_tables['Table group'] + " - " + d365_tables['Tabletype']

# Suppression de l'App module "Non spécifié"
d365_tables = d365_tables[d365_tables['App module'] != 'Non spécifié']

# Graphique à barres horizontales pour AppModule-TableGroup-TableType
grouped_counts = d365_tables['AppModule-TableGroup-TableType'].value_counts()
fig, ax = plt.subplots()
grouped_counts.plot(kind='barh', ax=ax)
plt.title('Répartition des App module - Table group - Table type')
plt.xlabel('Nombre de tables')
plt.ylabel('App module - Table group - Table type')
ax.bar_label(ax.containers[0])
st.pyplot(fig)

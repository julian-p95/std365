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
d365_tables['Tabletype'].fillna("Non spécifié", inplace=True)

# Supprimer les App modules indésirables
d365_tables = d365_tables[~d365_tables['App module'].isin(['SystemAdministration', 'General', 'Non spécifié'])]

# Graphique à barres horizontales pour App module
app_module_counts = d365_tables['App module'].value_counts()
fig1, ax1 = plt.subplots()
app_module_counts.plot(kind='barh', ax=ax1)
plt.title('Répartition des App modules')
plt.xlabel('Nombre de tables')
plt.ylabel('App module')
ax1.bar_label(ax1.containers[0])
plt.tight_layout()
st.pyplot(fig1)

# Comptage des préfixes des labels des tables
d365_tables['Prefix'] = d365_tables['Table label'].str.split().str[0].str.upper()
prefix_counts = d365_tables['Prefix'].value_counts()
st.table(prefix_counts.reset_index().rename(columns={'index': 'Prefix', 'Prefix': 'Count'}))
"
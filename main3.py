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

# Filtre pour exclure certains App modules
d365_tables = d365_tables[~d365_tables['App module'].isin(["Non spécifié", "SystemAdministration", "General"])]

# Graphique à barres horizontales
grouped_counts = d365_tables['App module'].value_counts()
fig, ax = plt.subplots()
grouped_counts.plot(kind='barh', ax=ax)
ax.set_title('Répartition des App modules')
ax.set_xlabel('Nombre de tables')
ax.set_ylabel('App modules')
ax.set_yticks(ax.get_yticks()[::2])  # Augmentation de l'espace entre les barres
st.pyplot(fig)

# Tableau des préfixes des labels de table
d365_tables['Table Prefix'] = d365_tables['Table label'].str.split(' ').str[0].str.upper()
prefix_counts = d365_tables['Table Prefix'].value_counts().reset_index()
prefix_counts.columns = ['Table Prefix', 'Count']
st.table(prefix_counts)

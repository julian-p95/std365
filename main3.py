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

# Remove "Non spécifié" from 'App module'
d365_tables = d365_tables[d365_tables['App module'] != "Non spécifié"]

# Graphique à barres horizontales pour AppModule-TableGroup-TableType
grouped_counts = d365_tables['App module'].value_counts()
fig, ax = plt.subplots()
grouped_counts.plot(kind='barh', ax=ax)
ax.set_title('Répartition des App modules')
ax.set_xlabel('Nombre de tables')
ax.set_ylabel('App modules')
ax.set_yticks(ax.get_yticks()[::2])  # Adding more space between bars
st.pyplot(fig)

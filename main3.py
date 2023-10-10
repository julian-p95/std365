import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

# Titre de la page
st.title("Analyse des Tables ERP")

# Lecture du fichier Excel
d365_tables = pd.read_excel("D365FO.xlsx", sheet_name='D365 Table')

# Gestion des valeurs NaN
d365_tables['App module'].fillna("Non spécifié", inplace=True)
d365_tables['Table group'].fillna("Non spécifié", inplace=True)
d365_tables['Tabletype'].fillna("Non spécifié", inplace=True)

# Filtrage des App modules
filtered_tables = d365_tables[~d365_tables['App module'].isin(['SystemAdministration', 'General', 'Non spécifié'])]

# Répartition par App module
app_module_counts = filtered_tables['App module'].value_counts()

# 5 types de graphiques
fig_types = ['bar', 'barh', 'pie', 'area', 'line']
for ftype in fig_types:
    fig, ax = plt.subplots()
    app_module_counts.plot(kind=ftype, ax=ax)
    plt.title(f'Répartition des App modules - {ftype}')
    plt.xlabel('App module')
    plt.ylabel('Nombre de tables')
    st.pyplot(fig)

# Graphique pour tous les App modules
all_app_module_counts = d365_tables['App module'].value_counts()
for ftype in fig_types:
    fig, ax = plt.subplots()
    all_app_module_counts.plot(kind=ftype, ax=ax, autopct='%1.1f%%' if ftype == 'pie' else None)
    plt.title(f'Poids de chaque App module - {ftype}')
    plt.xlabel('App module')
    plt.ylabel('Nombre de tables')
    st.pyplot(fig)

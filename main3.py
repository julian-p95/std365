# main.py

import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from collections import Counter

# Titre pour la page d'accueil
st.title("Accueil")

# Lecture des fichiers Excel
erp_relations = pd.read_excel("erp_all_table_relations_finalV2.xlsx", sheet_name='Sheet1')
d365_tables = pd.read_excel("D365FO.xlsx", sheet_name='D365 Table')

# Gérer les valeurs NaN pour le module d'application
d365_tables['App module'] = d365_tables['App module'].fillna("Non spécifié")

# Conversion en majuscules
erp_relations['Table Parent'] = erp_relations['Table Parent'].astype(str).str.upper()
erp_relations['Table Enfant'] = erp_relations['Table Enfant'].astype(str).str.upper()
d365_tables['Table name'] = d365_tables['Table name'].astype(str).str.upper()

# Calcul du nombre total de tables
total_tables = len(d365_tables)

# Calcul du nombre de tables par module d'application
app_module_counts = d365_tables['App module'].value_counts().sort_values(ascending=False)

# Calcul du ratio en pourcentage pour chaque module d'application
app_module_ratios = (app_module_counts / total_tables) * 100

# Visualisation de la répartition des modules d'application en barres
fig1, ax1 = plt.subplots()
app_module_ratios.plot(kind='bar', ax=ax1)
plt.title('Répartition des App Modules (Barres)')
plt.xlabel('App Module')
plt.ylabel('% du total des tables')
st.pyplot(fig1)

# Visualisation de la répartition des modules d'application en camembert
fig2, ax2 = plt.subplots()
app_module_ratios.plot(kind='pie', ax=ax2, autopct='%1.1f%%')
plt.title('Répartition des App Modules (Camembert)')
st.pyplot(fig2)

# Affichage du tableau avec le nombre de tables par module d'application
st.table(app_module_counts.reset_index().rename(columns={"index": "App Module", "App module": "Nombre de Tables"}))

# Sommaire
st.subheader("Sommaire")
for app_module in app_module_counts.index:
    st.markdown(f"* [{app_module}](#{app_module})")

# Détails pour chaque module d'application
for app_module in app_module_counts.index:
    st.subheader(f"App Module: {app_module}")

    # Anchor pour le sommaire
    st.markdown(f"<a name='{app_module}'></a>", unsafe_allow_html=True)

    # Tables du module d'application
    filtered_tables = d365_tables[d365_tables['App module'] == app_module]
    filtered_tables['Total Associations'] = filtered_tables['Table name'].map(total_counter)

    # 10 tables avec le plus grand nombre de relations
    top_tables = filtered_tables.nlargest(10, 'Total Associations')
    st.write(top_tables[['Table name', 'Total Associations']])

    # Relations avec d'autres modules d'application
    other_module_relations = erp_relations[(erp_relations['Table Parent'].isin(filtered_tables['Table name'])) | (erp_relations['Table Enfant'].isin(filtered_tables['Table name']))]
    other_module_relations = other_module_relations.merge(d365_tables[['Table name', 'App module']], left_on='Table Parent', right_on='Table name', how='left')
    other_module_count = other_module_relations['App module'].value_counts()
    st.write("Relations avec d'autres App Modules:", other_module_count)

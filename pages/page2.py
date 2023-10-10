# page2.py
# Page pour afficher les champs de la table

import pandas as pd
import streamlit as st

def show_page2():
    st.title("Page 2: Informations sur les Tables")

    # Lecture du fichier Excel pour cette page
    field_list = pd.read_excel("Table and Field List.xlsx", sheet_name='Field List')
    field_list['TABLE_NAME'] = field_list['TABLE_NAME'].astype(str).str.upper()

    # Barre de recherche pour les tables (placée sous le graphe)
    search_term_table = st.text_input("Rechercher une table (sous le graphe)")

    # Tableau pour la sélection de la table et l'affichage des champs
    table_choice = st.selectbox('Choisissez une table pour afficher ses champs:', field_list['TABLE_NAME'].unique())
    table_fields = field_list[field_list['TABLE_NAME'] == table_choice]
    st.table(table_fields[['COLUMN_NAME', 'DATA_TYPE']])

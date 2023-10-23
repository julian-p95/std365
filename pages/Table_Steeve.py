# pages/page2.py

import pandas as pd
import streamlit as st


st.title("Tables' Field, Data by Steeve")

# Lecture du fichier Excel
# Changer le nom du fichier et la feuille si nécessaire
field_list = pd.read_excel("Table_Steeve.xlsx")  
field_list['TableName'] = field_list['TableName'].astype(str).str.upper()  # Convertir en majuscules

# Barre de recherche pour les tables
# Utilisez cette fonction si vous souhaitez ajouter une fonction de recherche
search_term_table = st.text_input("Rechercher une table (sous le graphe)")

# Sélection de la table et affichage des champs
# Remplacer 'TABLE_NAME' et 'COLUMN_NAME', 'DATA_TYPE' par les noms des colonnes correspondants
table_choice = st.selectbox('Choisissez une table pour afficher ses champs:', field_list['TableName'].unique())
table_fields = field_list[field_list['TableName'] == table_choice]
st.table(table_fields[['FieldName']])

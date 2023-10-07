# Importation des bibliothèques nécessaires
import streamlit as st
import pandas as pd
import random
from pyvis.network import Network

# Fonction pour générer une couleur aléatoire
def random_color():
    return "#{:02x}{:02x}{:02x}".format(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

# Initialisation de Streamlit
st.title("Visualisation des Relations de Tables dans l'ERP D365")

# Téléchargement des fichiers Excel
uploaded_file_erp = st.file_uploader("Télécharger erp_all_table_relations_finalV2.xlsx", type=['xlsx'])
uploaded_file_d365fo = st.file_uploader("Télécharger D365FO.xlsx", type=['xlsx'])
uploaded_file_field_list = st.file_uploader("Télécharger Table and Field List.xlsx", type=['xlsx'])

if all([uploaded_file_erp, uploaded_file_d365fo, uploaded_file_field_list]):
    # Lecture des fichiers Excel
    erp_relations = pd.read_excel(uploaded_file_erp, sheet_name='Sheet1')
    d365_tables = pd.read_excel(uploaded_file_d365fo, sheet_name='D365 Table')
    field_list = pd.read_excel(uploaded_file_field_list, sheet_name='Field List')
    
    # Création du graphe avec PyVis
    net = Network(height="750px", width="100%", bgcolor="#ffffff", font_color="black")
    
    # Ajout des nœuds avec leurs attributs
    for _, row in d365_tables.iterrows():
        table_name = row['Table name']
        app_module = row['App module']
        color = random_color()
        
        fields = field_list[field_list['TABLE_NAME'] == table_name]
        field_str = "<br>".join(fields['COLUMN_NAME'].astype(str) + ' (' + fields['DATA_TYPE'].astype(str) + ')')
        
        net.add_node(table_name, title=field_str, color=color, label=table_name, group=app_module)
    
    # Ajout des arêtes avec leurs attributs
    for _, row in erp_relations.iterrows():
        parent = row['Table Parent']
        child = row['Table Enfant']
        relation = row['Lien 1']
        
        if parent in net.nodes and child in net.nodes:
            net.add_edge(parent, child, title=relation)
            
    # Affichage du graphe
    net.save_graph("temp.html")
    with open("temp.html", 'r', encoding='utf-8') as f:
        source_code = f.read()
    st.components.v1.html(source_code, height=800)

import streamlit as st
import pandas as pd
import networkx as nx
from pyvis.network import Network
from collections import Counter
import random

# Générer une couleur aléatoire
def random_color():
  return "#{:02x}{:02x}{:02x}".format(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

# Chargement des fichiers
uploaded_file_erp = st.file_uploader("Upload erp_all_table_relations_finalV2.xlsx", type=['xlsx'])
uploaded_file_d365fo = st.file_uploader("Upload D365FO.xlsx", type=['xlsx']) 
uploaded_file_field_list = st.file_uploader("Upload Table and Field List.xlsx", type=['xlsx'])

if uploaded_file_erp and uploaded_file_d365fo and uploaded_file_field_list:
  
  # Lecture des données
  erp_all_table_relations = pd.read_excel(uploaded_file_erp)
  d365fo = pd.read_excel(uploaded_file_d365fo)
  field_list = pd.read_excel(uploaded_file_field_list, sheet_name='Field List')

  # Comptage des relations
  table_counts = erp_all_table_relations['Table Parent'].value_counts() + erp_all_table_relations['Table Enfant'].value_counts()
  table_counts = table_counts.reset_index()
  table_counts.columns = ['Table', 'Count']

  # Jointure avec d365fo
  table_counts = table_counts.merge(d365fo[['Table name','App module']], left_on='Table', right_on='Table name')

  # Sélection du module
  app_module = st.selectbox('App Module:', table_counts['App module'].unique())

  # Filtrage des tables
  filtered_tables = table_counts[table_counts['App module'] == app_module]

  # Slider pour limiter les tables
  num_tables = st.slider('Number of tables:', min_value=1, max_value=len(filtered_tables), value=10)
  
  # Tables à afficher
  top_tables = filtered_tables.nlargest(num_tables, 'Count')['Table'].tolist()

  # Filtrage des relations
  filtered_relations = erp_all_table_relations[
      erp_all_table_relations['Table Parent'].isin(top_tables) |
      erp_all_table_relations['Table Enfant'].isin(top_tables)
  ]

  # Création du graphe
  G = nx.Graph()
  for _, row in filtered_relations.iterrows():
    G.add_edge(row['Table Parent'], row['Table Enfant'], title=row['Lien 1'])

  # Création du graphe PyVis
  net = Network(height="750px", width="100%", bgcolor="#ffffff", font_color="black")
  
  # Ajout des noeuds
  for node in top_tables:
    net.add_node(node)
    
  # Ajout des arêtes  
  for _, row in filtered_relations.iterrows():
    if row['Table Parent'] in top_tables or row['Table Enfant'] in top_tables:
      net.add_edge(row['Table Parent'], row['Table Enfant'])

  # Couleurs et infos bulles
  for node in top_tables:
    
    node_info = filtered_tables[filtered_tables['Table'] == node]
    
    if not node_info.empty:
        
      node_module = node_info['App module'].values[0]
      node_color = random_color()
      net.get_node(node)['color'] = node_color
      
      columns_info = field_list[field_list['TABLE_NAME'] == node]
      title_str = "<br>".join(columns_info['COLUMN_NAME'].astype(str) + ' (' + columns_info['DATA_TYPE'].astype(str) + ')')
      net.get_node(node)['title'] = title_str
  
  # Affichage
  net.show("temp.html")
  with open("temp.html", 'r', encoding='utf-8') as f:
    source_code = f.read()

  st.components.v1.html(source_code, height=800)
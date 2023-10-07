# ... (même code pour les imports et les fonctions)

if uploaded_file_erp and uploaded_file_d365fo and uploaded_file_field_list:
    # ... (même code pour le chargement des fichiers et le filtrage initial)

    # Nombre de tables à afficher
    num_tables = st.slider('Nombre de tables:', min_value=1, max_value=len(filtered_tables), value=min(10, len(filtered_tables)))

    # Tables avec le plus de relations
    top_tables = filtered_tables.nlargest(num_tables, 'Total Associations')['Table'].tolist()

    # Filtrage des relations pour inclure les tables liées à top_tables
    filtered_relations = erp_relations_df[
        erp_relations_df['Table Parent'].isin(top_tables) | 
        erp_relations_df['Table Enfant'].isin(top_tables)
    ]

    # Création du graphe
    G = nx.Graph()
    for _, row in filtered_relations.iterrows():
        G.add_edge(row['Table Parent'], row['Table Enfant'], app_module=row['App module'])

    # Création du graphe PyVis
    net = Network(height="750px", width="100%", bgcolor="#ffffff", font_color="black")
    net.from_nx(G)

    # Couleurs par module
    color_map = {module: random_color() for module in app_modules}
    for node in G.nodes():
        node_info = table_counts.loc[table_counts['Table'] == node, 'App module']
        if not node_info.empty:
            net.get_node(node)['color'] = color_map.get(node_info.iloc[0], "#000000")

    # Affichage du graphe
    net.save_graph("temp.html")
    with open("temp.html", 'r', encoding='utf-8') as f:
        source_code = f.read()
    st.components.v1.html(source_code, height=800)

    # Légende des couleurs
    st.write("Légende des couleurs:")
    for module, color in color_map.items():
        st.write(f"{module} : {color}")

    # Affichage du tableau
    table_to_show = filtered_tables.nlargest(num_tables, 'Total Associations')[['Table', 'Total Associations', 'App module']]
    st.table(table_to_show.sort_values('Total Associations', ascending=False))

# Fin du code

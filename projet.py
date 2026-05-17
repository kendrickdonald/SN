import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns

# Configuration de la page
st.set_page_config(
    page_title="Analyse des prix des voitures",
    page_icon=" ",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Style CSS personnalisé
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #424242;
        margin-top: 1rem;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
    }
    .insight-text {
        background-color: #e3f2fd;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #1E88E5;
    }
</style>
""", unsafe_allow_html=True)

# Chargement des données nettoyées
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('CarPriceDataset_Ne.csv')
        
        return df
    except FileNotFoundError:
        st.error(" Fichier 'CarPriceDataset_Cleaned.csv' non trouvé!")
        st.info(" Assurez-vous que le fichier nettoyé se trouve dans le même dossier que cette application.")
        st.stop()

# Charger les données
df = load_data()

# En-tête principal
st.markdown('<div class="main-header"> Analyse des prix des voitures </div>', unsafe_allow_html=True)
st.markdown("---")

# Sidebar - Filtres
st.sidebar.header(" Selections")
st.sidebar.markdown(" ")

# Création des filtres avec les données nettoyées
companies = st.sidebar.multiselect(
    "Compagnie", 
    df['Company'].unique(), 
    default=df['Company'].unique()[:5] if len(df['Company'].unique()) > 5 else df['Company'].unique()
)

types = st.sidebar.multiselect(
    "Type de véhicule", 
    df['Type'].unique(), 
    default=df['Type'].unique()
)

fuels = st.sidebar.multiselect(
    "Carburant", 
    df['Fuel'].unique(), 
    default=df['Fuel'].unique()
)

# Sliders pour les plages numériques
price_min = float(df['Price (Lakhs)'].min())
price_max = float(df['Price (Lakhs)'].max())
price_range = st.sidebar.slider(
    "Prix (Lakhs)", 
    price_min, 
    price_max, 
    (price_min, price_max)
)

year_min = int(df['Year'].min())
year_max = int(df['Year'].max())
year_range = st.sidebar.slider(
    "Année", 
    year_min, 
    year_max, 
    (year_min, year_max)
)

# Application des filtres
filtered_df = df[
    (df['Company'].isin(companies)) &
    (df['Type'].isin(types)) &
    (df['Fuel'].isin(fuels)) &
    (df['Price (Lakhs)'] >= price_range[0]) &
    (df['Price (Lakhs)'] <= price_range[1]) &
    (df['Year'] >= year_range[0]) &
    (df['Year'] <= year_range[1])
]

# Vérifier si le filtre ne retourne pas de données
if len(filtered_df) == 0:
    st.warning(" Aucune donnée ne correspond aux filtres sélectionnés. Veuillez élargir vos critères.")
    st.stop()

# Section 1: Métriques clés
st.markdown('<div class="sub-header"> Indicateurs Clés (Données Nettoyées)</div>', unsafe_allow_html=True)

# Calcul des métriques
total_cars = len(filtered_df)
avg_price = filtered_df['Price (Lakhs)'].mean()
median_price = filtered_df['Price (Lakhs)'].median()
avg_mileage = filtered_df['Mileage'].mean()
avg_horsepower = filtered_df['Horsepower_kw'].mean()
avg_year = filtered_df['Year'].mean()
most_expensive = filtered_df.loc[filtered_df['Price (Lakhs)'].idxmax(), 'Model']
most_expensive_price = filtered_df['Price (Lakhs)'].max()
cheapest = filtered_df.loc[filtered_df['Price (Lakhs)'].idxmin(), 'Model']
cheapest_price = filtered_df['Price (Lakhs)'].min()
most_common_company = filtered_df['Company'].mode()[0]
most_common_type = filtered_df['Type'].mode()[0]
most_common_fuel = filtered_df['Fuel'].mode()[0]

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(" Total Véhicules", f"{total_cars:,}")
with col2:
    st.metric(" Prix Moyen", f"{avg_price:.2f} Lakhs")
with col3:
    st.metric(" Année Moyenne", f"{avg_year:.0f}")
with col4:
    st.metric(" Puissance Moyenne", f"{avg_horsepower:.1f} kW")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(" Plus chère", f"{most_expensive} ({most_expensive_price:.1f} Lakhs)")
with col2:
    st.metric(" Moins chère", f"{cheapest} ({cheapest_price:.1f} Lakhs)")
with col3:
    st.metric(" Marque populaire", most_common_company)
with col4:
    st.metric(" Carburant populaire", most_common_fuel)

st.markdown(" ")

# Section 2: Visualisations principales
st.markdown('<div class="sub-header">  Graphiques</div>', unsafe_allow_html=True)

# Création d'onglets pour organiser les graphiques
tab1, tab2, tab3, tab4 = st.tabs([" Distribution des prix", " Analyse par marque", " Évolution temporelle", " Corrélations"])

with tab1:
    col1, col2 = st.columns(2)
    
    with col1:
        # Histogramme des prix
        fig_price = px.histogram(filtered_df, x='Price (Lakhs)', nbins=50, 
                                  title='Distribution des prix des Voitures',
                                  color_discrete_sequence=['#1E88E5'])
        fig_price.update_layout(xaxis_title='Prix (Lakhs)', yaxis_title='Nombre de véhicules')
        st.plotly_chart(fig_price, use_container_width=True)
        
        # Boxplot des prix par type
        fig_box_type = px.box(filtered_df, x='Type', y='Price (Lakhs)', 
                              title='Distribution des prix par type de véhicule',
                              color='Type')
        st.plotly_chart(fig_box_type, use_container_width=True)
    
    with col2:
        # Prix par carburant
        fuel_price = filtered_df.groupby('Fuel')['Price (Lakhs)'].agg(['mean', 'median']).reset_index()
        fig_fuel = px.bar(fuel_price, x='Fuel', y='mean', 
                          title='Prix moyen par type de carburant',
                          color='Fuel',
                          text_auto='.2f')
        fig_fuel.update_layout(yaxis_title='Prix moyen (Lakhs)')
        st.plotly_chart(fig_fuel, use_container_width=True)
        
        # Top 10 des voitures les plus chères
        top_expensive = filtered_df.nlargest(10, 'Price (Lakhs)')[['Model', 'Company', 'Price (Lakhs)']]
        fig_top = px.bar(top_expensive, x='Price (Lakhs)', y='Model', 
                         title='Top 10 des voitures les plus chères',
                         orientation='h', color='Company',
                         color_discrete_sequence=px.colors.qualitative.Set3)
        st.plotly_chart(fig_top, use_container_width=True)

with tab2:
    col1, col2 = st.columns(2)
    
    with col1:
        # Nombre de véhicules par marque
        company_count = filtered_df['Company'].value_counts().head(10).reset_index()
        company_count.columns = ['Company', 'Count']
        fig_company = px.bar(company_count, x='Company', y='Count', 
                             title='Top 10 des arques par nombre de éhicules',
                             color='Count', color_continuous_scale='Blues')
        st.plotly_chart(fig_company, use_container_width=True)
        
        # Prix moyen par marque
        company_price = filtered_df.groupby('Company')['Price (Lakhs)'].mean().sort_values(ascending=False).head(10).reset_index()
        fig_company_price = px.bar(company_price, x='Company', y='Price (Lakhs)',
                                   title='Prix moyen par marque ',
                                   color='Price (Lakhs)', color_continuous_scale='Reds')
        st.plotly_chart(fig_company_price, use_container_width=True)
    
    with col2:
        # Répartition des types de véhicules
        type_count = filtered_df['Type'].value_counts().reset_index()
        type_count.columns = ['Type', 'Count']
        fig_type_pie = px.pie(type_count, values='Count', names='Type', 
                              title='répartition des types de véhicules',
                              hole=0.3)
        st.plotly_chart(fig_type_pie, use_container_width=True)
        
        # Prix moyen par type
        type_avg_price = filtered_df.groupby('Type')['Price (Lakhs)'].mean().sort_values().reset_index()
        fig_type_price = px.bar(type_avg_price, x='Type', y='Price (Lakhs)',
                                title='prix moyen par type de véhicule',
                                color='Price (Lakhs)', color_continuous_scale='Greens')
        st.plotly_chart(fig_type_price, use_container_width=True)

with tab3:
    col1, col2 = st.columns(2)
    
    with col1:
        # Évolution du prix moyen par année
        yearly_price = filtered_df.groupby('Year')['Price (Lakhs)'].mean().reset_index()
        fig_yearly = px.line(yearly_price, x='Year', y='Price (Lakhs)',
                             title='Évolution du prix moyen par an',
                             markers=True, line_shape='linear')
        fig_yearly.update_layout(yaxis_title='Prix Moyen (Lakhs)')
        st.plotly_chart(fig_yearly, use_container_width=True)
        
        # Évolution du nombre de véhicules par année
        yearly_count = filtered_df['Year'].value_counts().sort_index().reset_index()
        yearly_count.columns = ['Year', 'Count']
        fig_count = px.area(yearly_count, x='Year', y='Count',
                            title='Nombre de véhicules par an',
                            color_discrete_sequence=['#1E88E5'])
        st.plotly_chart(fig_count, use_container_width=True)
    
    with col2:
        # Évolution du kilométrage moyen
        yearly_mileage = filtered_df.groupby('Year')['Mileage'].mean().reset_index()
        fig_mileage = px.bar(yearly_mileage, x='Year', y='Mileage',
                             title='Évolution du kilométrage moyen (km/l)',
                             color='Mileage', color_continuous_scale='Viridis')
        st.plotly_chart(fig_mileage, use_container_width=True)
        
        # Évolution de la puissance moyenne
        yearly_hp = filtered_df.groupby('Year')['Horsepower_kw'].mean().reset_index()
        fig_hp = px.scatter(yearly_hp, x='Year', y='Horsepower_kw',
                            title='Évolution de la puissance moyenne (kW)',
                            size='Horsepower_kw', color='Horsepower_kw',
                            color_continuous_scale='Plasma')
        st.plotly_chart(fig_hp, use_container_width=True)

with tab4:
    # Matrice de corrélation
    numeric_cols = ['Price (Lakhs)', 'Mileage', 'Engine', 'Km_driven', 'Year', 'Horsepower_kw']
    corr_matrix = filtered_df[numeric_cols].corr()
    
    fig_corr = px.imshow(corr_matrix, 
                         text_auto=True, 
                         aspect="auto",
                         title="Matrice de corrélation ",
                         color_continuous_scale='RdBu',
                         zmin=-1, zmax=1)
    st.plotly_chart(fig_corr, use_container_width=True)
    
    # Analyse des corrélations avec le prix
    st.markdown('<div class="insight-text">', unsafe_allow_html=True)
    st.markdown(" Principales corrélations avec le prix (données nettoyées) :")
    correlations = corr_matrix['Price (Lakhs)'].sort_values(ascending=False)
    for var, corr in correlations.items():
        if var != 'Price (Lakhs)':
            st.write(f"- {var}: {corr:.2f} ({'positive' if corr > 0 else 'negative'})")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Scatter plot prix vs puissance
    fig_scatter = px.scatter(filtered_df, x='Horsepower_kw', y='Price (Lakhs)',
                             color='Type', size='Engine', hover_data=['Model', 'Company'],
                             title='Prix vs Puissance (taille = Cylindrée)',
                             trendline="ols")
    st.plotly_chart(fig_scatter, use_container_width=True)

# Section 3: Données détaillées
st.markdown("---")
st.markdown('<div class="sub-header">données et affichage détaillé</div>', unsafe_allow_html=True)

# Affichage du tableau avec pagination
rows_per_page = st.selectbox("Lignes par page", [10, 25, 50, 100])
page_number = st.number_input("Page", min_value=1, max_value=max(1, len(filtered_df)//rows_per_page + 1), value=1)

start_idx = (page_number - 1) * rows_per_page
end_idx = start_idx + rows_per_page

st.dataframe(
    filtered_df.iloc[start_idx:end_idx],
    use_container_width=True,
    height=400
)

# Section 4: Statistiques supplémentaires sur les données nettoyées
st.markdown(" ")
st.markdown('<div class="sub-header"> Statistiques </div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.write("**Aperçu des valeurs uniques après nettoyage:**")
    st.write(f"- **Types de carburant:** {', '.join(df['Fuel'].unique())}")
    st.write(f"- **Types de véhicules:** {', '.join(df['Type'].unique())}")
    st.write(f"- **Marques:** {len(df['Company'].unique())} marques différentes")
    st.write(f"- **Modèles:** {len(df['Model'].unique())} modèles différents")

with col2:
    st.write("Plages de valeurs:")
    st.write(f"- **Prix:** {df['Price (Lakhs)'].min():.2f} - {df['Price (Lakhs)'].max():.2f} Lakhs")
    st.write(f"- **Année:** {df['Year'].min()} - {df['Year'].max()}")
    st.write(f"- **Kilométrage:** {df['Mileage'].min():.1f} - {df['Mileage'].max():.1f} km/l")
    st.write(f"- **Puissance:** {df['Horsepower_kw'].min():.0f} - {df['Horsepower_kw'].max():.0f} kW")


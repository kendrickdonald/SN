import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns


st.set_page_config(
    page_title="Analyse des prix des voitures",
    page_icon=" ",
    layout="wide",
    initial_sidebar_state="expanded"
)


st.markdown("""""
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


@st.cache_data
def load_data():
    
        df = pd.read_csv('CarPriceDataset_Ne.csv')
        
        return df
   
df = load_data()


st.markdown('<div class="main-header"> Analyse des prix des voitures </div>', unsafe_allow_html=True)
st.markdown(" ")

st.sidebar.header(" Selections")
st.sidebar.markdown(" ")

compagnies = st.sidebar.multiselect(
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

prix_min = float(df['Price (Lakhs)'].min())
prix_max = float(df['Price (Lakhs)'].max())
prix_range = st.sidebar.slider(
    "Prix (Lakhs)", 
    prix_min, 
    prix_max, 
    (prix_min, prix_max)
)

annee_min = int(df['Year'].min())
annee_max = int(df['Year'].max())
year_range = st.sidebar.slider(
    "Année", 
    annee_min, 
    annee_max, 
    (annee_min, annee_max)
)


colonnes = df[
    (df['Company'].isin(compagnies)) &
    (df['Type'].isin(types)) &
    (df['Fuel'].isin(fuels)) &
    (df['Price (Lakhs)'] >= prix_range[0]) &
    (df['Price (Lakhs)'] <= prix_range[1]) &
    (df['Year'] >= year_range[0]) &
    (df['Year'] <= year_range[1])
]


if len(colonnes) == 0:
    st.warning(" Aucune donnée ne correspond aux filtres sélectionnés. Veuillez élargir vos critères.")
    st.stop()


st.markdown('<div class="sub-header"> Indicateurs Clés (Données Nettoyées)</div>', unsafe_allow_html=True)

total_voitures = len(colonnes)
moy_prix = colonnes['Price (Lakhs)'].mean()
median_prix = colonnes['Price (Lakhs)'].median()
moy_mileage = colonnes['Mileage'].mean()
moy_horsepower = colonnes['Horsepower_kw'].mean()
moy_year = colonnes['Year'].mean()
plus_cher = colonnes.loc[colonnes['Price (Lakhs)'].idxmax(), 'Model']
plus_cherp = colonnes['Price (Lakhs)'].max()
moins = colonnes.loc[colonnes['Price (Lakhs)'].idxmin(), 'Model']
moinsp = colonnes['Price (Lakhs)'].min()
mc = colonnes['Company'].mode()[0]
mt = colonnes['Type'].mode()[0]
mf = colonnes['Fuel'].mode()[0]

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(" Total Véhicules", f"{total_voitures:,}")
with col2:
    st.metric(" Prix Moyen", f"{moy_prix:.2f} Lakhs")
with col3:
    st.metric(" Année Moyenne", f"{moy_year:.0f}")
with col4:
    st.metric(" Puissance Moyenne", f"{moy_horsepower:.1f} kW")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(" Plus chère", f"{plus_cher} ({plus_cherp:.1f} Lakhs)")
with col2:
    st.metric(" Moins chère", f"{moins} ({moinsp:.1f} Lakhs)")
with col3:
    st.metric(" Marque populaire", mc)
with col4:
    st.metric(" Carburant populaire", mf)

st.markdown(" ")


st.markdown('<div class="sub-header">  Graphiques</div>', unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs([" Distribution des prix", " Analyse par marque", " Évolution temporelle", " Corrélations"])

with tab1:
    col1, col2 = st.columns(2)
    
    with col1:
        
        fig_price = px.histogram(colonnes, x='Price (Lakhs)', nbins=50, 
                                  title='Distribution des prix des Voitures',
                                  color_discrete_sequence=['#1E88E5'])
        fig_price.update_layout(xaxis_title='Prix (Lakhs)', yaxis_title='Nombre de véhicules')
        st.plotly_chart(fig_price, use_container_width=True)
        
       
        fig_box_type = px.box(colonnes, x='Type', y='Price (Lakhs)', 
                              title='Distribution des prix par type de véhicule',
                              color='Type')
        st.plotly_chart(fig_box_type, use_container_width=True)
    
    with col2:
        
        fuel_prix = colonnes.groupby('Fuel')['Price (Lakhs)'].agg(['mean', 'median']).reset_index()
        fig_fuel = px.bar(fuel_prix, x='Fuel', y='mean', 
                          title='Prix moyen par type de carburant',
                          color='Fuel',
                          text_auto='.2f')
        fig_fuel.update_layout(yaxis_title='Prix moyen (Lakhs)')
        st.plotly_chart(fig_fuel, use_container_width=True)
        
        
        topcher = colonnes.nlargest(10, 'Price (Lakhs)')[['Model', 'Company', 'Price (Lakhs)']]
        fig_top = px.bar(topcher, x='Price (Lakhs)', y='Model', 
                         title='Top 10 des voitures les plus chères',
                         orientation='h', color='Company',
                         color_discrete_sequence=px.colors.qualitative.Set3)
        st.plotly_chart(fig_top, use_container_width=True)

with tab2:
    col1, col2 = st.columns(2)
    
    with col1:
        
        compagnie_c = colonnes['Company'].value_counts().head(10).reset_index()
        compagnie_c.columns = ['Company', 'Count']
        fig_c = px.bar(compagnie_c, x='Company', y='Count', 
                             title='Top 10 des arques par nombre de éhicules',
                             color='Count', color_continuous_scale='Blues')
        st.plotly_chart(fig_c, use_container_width=True)
        

        prix_compagnie = colonnes.groupby('Company')['Price (Lakhs)'].mean().sort_values(ascending=False).head(10).reset_index()
        fig_compagniep = px.bar(prix_compagnie, x='Company', y='Price (Lakhs)',
                                   title='Prix moyen par marque ',
                                   color='Price (Lakhs)', color_continuous_scale='Reds')
        st.plotly_chart(fig_compagniep , use_container_width=True)
    
    with col2:
       
        type_c = colonnes['Type'].value_counts().reset_index()
        type_c.columns = ['Type', 'Count']
        fig_type_pie = px.pie(type_c, values='Count', names='Type', 
                              title='répartition des types de véhicules',
                              hole=0.3)
        st.plotly_chart(fig_type_pie, use_container_width=True)
        
     
        type_moy_p = colonnes.groupby('Type')['Price (Lakhs)'].mean().sort_values().reset_index()
        fig_type_p = px.bar(type_moy_p, x='Type', y='Price (Lakhs)',
                                title='prix moyen par type de véhicule',
                                color='Price (Lakhs)', color_continuous_scale='Greens')
        st.plotly_chart(fig_type_p, use_container_width=True)

with tab3:
    col1, col2 = st.columns(2)
    
    with col1:
        # Évolution du prix moyen par année
        ap = colonnes.groupby('Year')['Price (Lakhs)'].mean().reset_index()
        fig_ap = px.line(ap, x='Year', y='Price (Lakhs)',
                             title='Évolution du prix moyen par an',
                             markers=True, line_shape='linear')
        fig_ap.update_layout(yaxis_title='Prix Moyen (Lakhs)')
        st.plotly_chart(fig_ap, use_container_width=True)
        
        # Évolution du nombre de véhicules par année
        ac = colonnes['Year'].value_counts().sort_index().reset_index()
        ac.columns = ['Year', 'Count']
        fig_c = px.area(ac, x='Year', y='Count',
                            title='Nombre de véhicules par an',
                            color_discrete_sequence=['#1E88E5'])
        st.plotly_chart(fig_c, use_container_width=True)
    
    with col2:
       
        annee_mileage = colonnes.groupby('Year')['Mileage'].mean().reset_index()
        fig_mileage = px.bar(annee_mileage, x='Year', y='Mileage',
                             title='Évolution du kilométrage moyen (km/l)',
                             color='Mileage', color_continuous_scale='Viridis')
        st.plotly_chart(fig_mileage, use_container_width=True)
        
        
        a_hp = colonnes.groupby('Year')['Horsepower_kw'].mean().reset_index()
        fig_hp = px.scatter(a_hp, x='Year', y='Horsepower_kw',
                            title='Évolution de la puissance moyenne (kW)',
                            size='Horsepower_kw', color='Horsepower_kw',
                            color_continuous_scale='Plasma')
        st.plotly_chart(fig_hp, use_container_width=True)

with tab4:
    
    numeric_cols = ['Price (Lakhs)', 'Mileage', 'Engine', 'Km_driven', 'Year', 'Horsepower_kw']
    corr_matrice = colonnes[numeric_cols].corr()
    
    fig_corr = px.imshow(corr_matrice, 
                         text_auto=True, 
                         aspect="auto",
                         title="Matrice de corrélation ",
                         color_continuous_scale='RdBu',
                         zmin=-1, zmax=1)
    st.plotly_chart(fig_corr, use_container_width=True)
    
   
    st.markdown('<div class="insight-text">', unsafe_allow_html=True)
    st.markdown(" Principales corrélations avec le prix (données nettoyées) :")
    correlations = corr_matrice['Price (Lakhs)'].sort_values(ascending=False)
    for var, corr in correlations.items():
        if var != 'Price (Lakhs)':
            st.write(f"- {var}: {corr:.2f} ({'positive' if corr > 0 else 'negative'})")
    st.markdown('</div>', unsafe_allow_html=True)
    
    
    fig_scatter = px.scatter(colonnes, x='Horsepower_kw', y='Price (Lakhs)',
                             color='Type', size='Engine', hover_data=['Model', 'Company'],
                             title='Prix vs Puissance (taille = Cylindrée)',
                             trendline="ols")
    st.plotly_chart(fig_scatter, use_container_width=True)


st.markdown(" ")
st.markdown('<div class="sub-header">données et affichage détaillé</div>', unsafe_allow_html=True)


lignes_par_page = st.selectbox("Lignes par page", [10, 25, 50, 100])
numero_page = st.number_input("Page", min_value=1, max_value=max(1, len(colonnes)//lignes_par_page + 1), value=1)

start_idx = (numero_page - 1) * lignes_par_page
end_idx = start_idx + lignes_par_page

st.dataframe(
    colonnes.iloc[start_idx:end_idx],
    use_container_width=True,
    height=400
)


st.markdown(" ")
st.markdown('<div class="sub-header">pip Statistiques </div>', unsafe_allow_html=True)

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



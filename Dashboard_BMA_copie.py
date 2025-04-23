import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import base64
from datetime import date
import calendar
from io import BytesIO
import plotly.express as px
import plotly.graph_objects as go
import os


# Configuration de la page
st.set_page_config(
    page_title="Suivi d'Activité Garage Automobile",
    page_icon="🔧",
    layout="wide"
)

# Titre de l'application
st.title('📊 Dashboard de Suivi d\'Activité - Garage Automobile')
st.markdown("""
Cette application permet de suivre l'activité d'un établissement de réparation automobile (mécanique et carrosserie).
* **Suivi des prestations facturées**
* **Montant des pièces fournisseur**
* **Décompte des charges mensuelles**
* **Gestion des absences du personnel**
* **Indicateurs de performance**
""")


# Fonction pour générer des données fictives
@st.cache_data
def generate_sample_data():
    # Données des prestations
    num_prestations = 1000
    dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')

    types_prestation = ['Revision intermediaire','Revision generale', 'Freinage',
                        'Carrosserie', 'Pneus', 'Suspension', 'Geometrie',
                        'Embrayage', 'Batterie', 'Climatisation', 'Diagnostic', 'Kit Distribution']

    types_vehicule = ['Citadine', 'Berline', 'SUV', 'Utilitaire', 'Break']

    mechaniciens = ['Saddem', 'Ismail']
    carrossiers = ['Sohaib']

    prestations = pd.DataFrame({
        'date': np.random.choice(dates, num_prestations),
        'type_prestation': np.random.choice(types_prestation, num_prestations),
        'type_vehicule': np.random.choice(types_vehicule, num_prestations),
        'technicien': np.random.choice(mechaniciens + carrossiers, num_prestations),
        'main_oeuvre_heures': np.random.uniform(0.5, 8, num_prestations).round(1),
        'montant_main_oeuvre': np.random.uniform(50, 800, num_prestations).round(2),
        'montant_pieces': np.random.uniform(20, 1500, num_prestations).round(2),
        'marge_pieces': np.random.uniform(0.1, 0.4, num_prestations).round(2),
        'tva_applicable': np.random.choice([0.2], num_prestations),
        'client': np.random.choice(['Particulier', 'Entreprise', 'Assurance'], num_prestations,
                                   p=[0.6, 0.3, 0.1])
    })

    prestations['montant_pieces_fournisseur'] = prestations['montant_pieces'] / (1 + prestations['marge_pieces'])
    prestations['montant_total_ht'] = prestations['montant_main_oeuvre'] + prestations['montant_pieces']
    prestations['montant_total_ttc'] = prestations['montant_total_ht'] * (1 + prestations['tva_applicable'])
    prestations['marge_totale'] = prestations['montant_main_oeuvre'] * 0.7 + (
                prestations['montant_pieces'] - prestations['montant_pieces_fournisseur'])

    # Données des charges
    charges_types = ['Loyer', 'Électricité', 'Eau', 'Internet', 'Assurance', 'Alarme',
                     'Salaires', 'Charges sociales', 'Fournitures', 'Dette OI',
                     'Publicité', 'Comptabilité', 'Forfait tel', 'Carburant', 'IRP',
                     'Dette Irp', 'SPSAO', 'Renault', 'Flauraud', 'La Cora', 'AD',
                     'Ouest Injection', 'P&P']

    charges_data = []
    for month in range(1, 13):  # Janvier à Decembre 2024
        for charge_type in charges_types:
            if charge_type == 'Salaires':
                montant = np.random.uniform(3800, 5300, 1)[0]
            elif charge_type == 'Charges sociales':
                montant = np.random.uniform(2000, 2500, 1)[0]
            elif charge_type == 'Loyer':
                montant = np.random.uniform(1830, 1950, 1)[0]
            elif charge_type == 'Électricité':
                montant = np.random.uniform(190, 350, 1)[0]
            elif charge_type == 'Eau':
                montant = np.random.uniform(50, 150, 1)[0]
            elif charge_type == 'Assurance':
                montant = np.random.uniform(380, 450, 1)[0]
            elif charge_type == 'Alarme':
                montant = np.random.uniform(134, 150, 1)[0]
            elif charge_type == 'Comptabilité':
                montant = np.random.uniform(200, 300, 1)[0]
            elif charge_type == 'Flauraud':
                montant = np.random.uniform(1700, 2900, 1)[0]
            elif charge_type == 'Carburant':
                montant = np.random.uniform(320, 400, 1)[0]
            elif charge_type == 'Ouest Injection':
                montant = np.random.uniform(1500, 2300, 1)[0]
            elif charge_type == 'P&P':
                montant = np.random.uniform(1000, 1900, 1)[0]
            else:
                montant = np.random.uniform(100, 2000, 1)[0]

            charges_data.append({
                'date': f'2024-{month:02d}-01',
                'type': charge_type,
                'montant': round(montant, 2),
                'payee': np.random.choice([True, False], p=[0.8, 0.2])
            })

    charges = pd.DataFrame(charges_data)
    charges['date'] = pd.to_datetime(charges['date'])

    # Données du personnel
    personnel_data = []
    for nom in mechaniciens + carrossiers:
        for month in range(1, 13):  # Janvier à Decembre 2024
            days_in_month = calendar.monthrange(2024, month)[1]
            absences = np.random.randint(0, 4)  # 0 à 3 jours d'absence par mois

            for _ in range(absences):
                day = np.random.randint(1, days_in_month + 1)
                personnel_data.append({
                    'nom': nom,
                    'date': f'2024-{month:02d}-{day:02d}',
                    'type_absence': np.random.choice(['Maladie', 'Congé payé', 'Formation', 'Sans solde']),
                    'duree': np.random.randint(1, 4),  # 1 à 3 jours
                    'status': 'Mécanicien' if nom in mechaniciens else 'Carrossier'
                })

    absences = pd.DataFrame(personnel_data)
    absences['date'] = pd.to_datetime(absences['date'])

    # Données des fournisseurs
    fournisseurs_data = []
    fournisseurs = ['Flauraud', 'P&P', 'Ouest Injection', 'La Cora AD', 'SPSAO', 'Renault', 'Audi VW']

    for month in range(1, 13):  # Janvier à Decembre 2024
        for fournisseur in fournisseurs:
            for _ in range(np.random.randint(1, 10)):  # 1 à 9 commandes par mois par fournisseur
                day = np.random.randint(1, calendar.monthrange(2024, month)[1] + 1)
                montant = np.random.uniform(500, 3000, 1)[0]
                fournisseurs_data.append({
                    'date': f'2024-{month:02d}-{day:02d}',
                    'fournisseur': fournisseur,
                    'montant': round(montant, 2),
                    'payee': np.random.choice([True, False], p=[0.7, 0.3]),
                    'delai_paiement': np.random.choice([30, 45, 60])
                })

    fournisseurs_df = pd.DataFrame(fournisseurs_data)
    fournisseurs_df['date'] = pd.to_datetime(fournisseurs_df['date'])

    return prestations, charges, absences, fournisseurs_df

    # Génération des données de bonus
    bonus_data = []
    for month in range(1, 13):  # Janvier à Décembre 2024
        for _ in range(np.random.randint(1, 6)):  # De 1 à 5 bonus par mois
            day = np.random.randint(1, calendar.monthrange(2024, month)[1] + 1)
            amount = np.random.uniform(50, 1000)  # Montant entre 50 et 1000 euros
            description = np.random.choice([
                "Bonus performance trimestrielle",
                "Bonus fidélité client",
                "Bonus innovation technique",
                "Bonus qualité service",
                "Bonus dépassement objectif"
            ])
            bonus_data.append({
                'date': f'2024-{month:02d}-{day:02d}',
                'amount': round(amount, 2),
                'description': description
            })

    bonus_df = pd.DataFrame(bonus_data)
    bonus_df['id_bonus'] = range(1, len(bonus_df) + 1)
    bonus_df['date'] = pd.to_datetime(bonus_df['date'])

    # Intégrer les données de bonus dans le dictionnaire des données
    if "bonus" not in data:
        data["bonus"] = pd.DataFrame()
    data["bonus"] = pd.concat([data["bonus"], bonus_df], ignore_index=True)
"""
    # Interface utilisateur pour ajouter des bonus
    with st.expander("Ajouter un Bonus"):
        col1, col2 = st.columns(2)
        with col1:
            new_date = st.date_input("Date du Bonus")
            new_amount = st.number_input("Montant du Bonus", min_value=0)
        with col2:
            new_description = st.text_input("Description du Bonus")

        if st.button("Ajouter le Bonus"):
            # Ajout des données dans le DataFrame
            data['bonus'] = pd.concat([
                data['bonus'],
                pd.DataFrame({
                    'id_bonus': [len(data['bonus']) + 1],
                    'date': [new_date],
                    'amount': [new_amount],
                    'description': [new_description]
                })
            ])
"""
    # Section pour visualiser les bonus
    with st.expander("Analyse des Bonus"):
        col1, col2 = st.columns(2)

        # Graphique de l'évolution des bonus au fil du temps
        with col1:
            st.subheader("Évolution des bonus")
            if not data['bonus'].empty:
                fig = px.line(data['bonus'], x='date', y='amount',
                              title="Montant des bonus au fil du temps",
                              labels={'x': 'Date', 'y': 'Montant'})
                st.plotly_chart(fig)
            else:
                st.info("Aucun bonus enregistré pour l'instant.")

        # Tableau des bonus
        with col2:
            st.subheader("Liste des bonus")
            if not data['bonus'].empty:
                st.dataframe(data['bonus'],
                             column_config={
                                 'id_bonus': {'visible': False},
                                 'date': {'label': 'Date'},
                                 'amount': {'label': 'Montant', 'format': '${{value:.2f}'},
                                 'description': {'label': 'Description'}
                             })
            else:
                st.info("Aucun bonus enregistré pour l'instant.")
"""
    # Sauvegarde dans le fichier CSV
    data['bonus'].to_csv(f"{data_dir}/bonus.csv", index=False)
    st.success("Bonus ajouté avec succès !")
"""
    # Visualisation des bonus existants
    st.subheader("Historique des Bonus")
    st.dataframe(data['bonus'], use_container_width=True)

    # Interface utilisateur pour filtrer les bonus par période
    st.subheader("Calcul du Total des Bonus selon la Période")
    start_date = st.date_input("Date de Début", date.today())
    end_date = st.date_input("Date de Fin", date.today())

    if start_date <= end_date:
        filtered_bonus = data['bonus'][
            (data['bonus']['date'] >= start_date) &
            (data['bonus']['date'] <= end_date)
            ]

        total_amount = filtered_bonus['amount'].sum()
        st.write(f"Montant Total du Bonus pour la période : **{total_amount}**")
    else:
        st.warning("La date de fin doit être supérieure ou égale à la date de début.")


# Charger les données
prestations, charges, absences, fournisseurs = generate_sample_data()

# Sidebar - Paramètres généraux
st.sidebar.header('Filtres')

# Filtres de date
min_date = prestations['date'].min().date()
max_date = prestations['date'].max().date()

date_range = st.sidebar.date_input(
    "Période d'analyse",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

if len(date_range) == 2:
    start_date, end_date = date_range
    mask_date = (prestations['date'].dt.date >= start_date) & (prestations['date'].dt.date <= end_date)
    filtered_prestations = prestations[mask_date]

    mask_date_charges = (charges['date'].dt.date >= start_date) & (charges['date'].dt.date <= end_date)
    filtered_charges = charges[mask_date_charges]

    mask_date_absences = (absences['date'].dt.date >= start_date) & (absences['date'].dt.date <= end_date)
    filtered_absences = absences[mask_date_absences]

    mask_date_fournisseurs = (fournisseurs['date'].dt.date >= start_date) & (fournisseurs['date'].dt.date <= end_date)
    filtered_fournisseurs = fournisseurs[mask_date_fournisseurs]
else:
    filtered_prestations = prestations
    filtered_charges = charges
    filtered_absences = absences
    filtered_fournisseurs = fournisseurs

# Filtre par type de prestation
types_prestation_unique = sorted(prestations['type_prestation'].unique())
selected_types = st.sidebar.multiselect('Type de prestation', types_prestation_unique, default=types_prestation_unique)

if selected_types:
    filtered_prestations = filtered_prestations[filtered_prestations['type_prestation'].isin(selected_types)]

# Filtre par technicien
techniciens_unique = sorted(prestations['technicien'].unique())
selected_techniciens = st.sidebar.multiselect('Technicien', techniciens_unique, default=techniciens_unique)

if selected_techniciens:
    filtered_prestations = filtered_prestations[filtered_prestations['technicien'].isin(selected_techniciens)]


# Fonction pour télécharger les données
def download_df(df, filename):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}.csv">Télécharger en CSV</a>'
    return href


# Organisation en onglets
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📈 Vue d'ensemble",
    "🔧 Prestations",
    "💰 Finances",
    "👥 Personnel",
    "📊 Analyses Avancées",
    "💵 Bonus"
])

with tab1:
    st.header("Vue d'ensemble de l'activité")

    # Indicateurs clés
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total_ca = filtered_prestations['montant_total_ttc'].sum()
        st.metric("CA Total TTC", f"{total_ca:.2f} €")

    with col2:
        total_marge = filtered_prestations['marge_totale'].sum()
        st.metric("Marge Totale", f"{total_marge:.2f} €")

    with col3:
        taux_marge = (total_marge / filtered_prestations[
            'montant_total_ht'].sum()) * 100 if not filtered_prestations.empty else 0
        st.metric("Taux de Marge", f"{taux_marge:.1f} %")

    with col4:
        total_prestations = len(filtered_prestations)
        st.metric("Nombre Prestations", total_prestations)

    # Graphique CA hebdomadaire
    st.subheader("Évolution du CA")

    # Préparer les données par semaine
    if not filtered_prestations.empty:
        prestations_by_week = filtered_prestations.copy()
        prestations_by_week['semaine'] = prestations_by_week['date'].dt.isocalendar().week
        prestations_by_week['mois'] = prestations_by_week['date'].dt.month
        weekly_revenue = prestations_by_week.groupby(['mois', 'semaine'])['montant_total_ttc'].sum().reset_index()
        weekly_revenue['période'] = weekly_revenue.apply(lambda x: f"M{x['mois']}-S{x['semaine']}", axis=1)

        fig = px.bar(
            weekly_revenue,
            x='période',
            y='montant_total_ttc',
            title="CA Hebdomadaire",
            labels={'montant_total_ttc': 'CA TTC (€)', 'période': 'Période'},
            text_auto='.2s'
        )
        st.plotly_chart(fig, use_container_width=True, key='évolution_ca')
    else:
        st.info("Aucune donnée disponible pour la période sélectionnée")

    # Répartition par type de prestation
    col1, col2 = st.columns(2)

    with col1:
        if not filtered_prestations.empty:
            prestation_type_revenue = filtered_prestations.groupby('type_prestation')[
                'montant_total_ttc'].sum().reset_index()
            fig = px.pie(
                prestation_type_revenue,
                values='montant_total_ttc',
                names='type_prestation',
                title="Répartition du CA par type de prestation"
            )
            st.plotly_chart(fig, use_container_width=True, key='type_prestation')
        else:
            st.info("Aucune donnée disponible pour la période sélectionnée")

    with col2:
        if not filtered_prestations.empty:
            tech_performance = filtered_prestations.groupby('technicien').agg({
                'montant_total_ttc': 'sum',
                'date': 'count'
            }).reset_index()
            tech_performance.rename(columns={'date': 'nb_prestations'}, inplace=True)
            tech_performance.sort_values('montant_total_ttc', ascending=False, inplace=True)

            fig = px.bar(
                tech_performance,
                x='technicien',
                y=['montant_total_ttc', 'nb_prestations'],
                barmode='group',
                title="Performance par technicien",
                labels={'value': '', 'technicien': 'Technicien', 'variable': 'Mesure'},
                text_auto='.2s'
            )
            st.plotly_chart(fig, use_container_width=True, key='performance_tech')
        else:
            st.info("Aucune donnée disponible pour la période sélectionnée")

with tab2:
    st.header("Suivi des prestations")

    # Filtres supplémentaires pour les prestations
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Données brutes")
        st.write(f"Nombre de prestations: {len(filtered_prestations)}")
        st.dataframe(filtered_prestations[['date', 'type_prestation', 'technicien', 'montant_main_oeuvre',
                                           'montant_pieces', 'montant_total_ttc', 'marge_totale']])
        st.markdown(download_df(filtered_prestations, "prestations"), unsafe_allow_html=True)

    with col2:
        if not filtered_prestations.empty:
            st.subheader("Top prestations par marge")
            top_prestations = filtered_prestations.sort_values('marge_totale', ascending=False).head(10)

            fig = px.bar(
                top_prestations,
                x='type_prestation',
                y='marge_totale',
                color='technicien',
                title="Top 10 des prestations par marge",
                labels={'marge_totale': 'Marge (€)', 'type_prestation': 'Type de prestation'},
                text_auto='.2s'
            )
            st.plotly_chart(fig, use_container_width=True, key='top_presta_marge')
        else:
            st.info("Aucune donnée disponible pour la période sélectionnée")

    # Analyses par type de véhicule
    st.subheader("Analyse par type de véhicule")

    if not filtered_prestations.empty:
        vehicle_analysis = filtered_prestations.groupby('type_vehicule').agg({
            'montant_total_ttc': 'sum',
            'main_oeuvre_heures': 'sum',
            'date': 'count'
        }).reset_index()

        vehicle_analysis.rename(columns={'date': 'nb_prestations'}, inplace=True)
        vehicle_analysis['montant_moyen'] = vehicle_analysis['montant_total_ttc'] / vehicle_analysis['nb_prestations']
        vehicle_analysis['heures_moyennes'] = vehicle_analysis['main_oeuvre_heures'] / vehicle_analysis[
            'nb_prestations']

        col1, col2 = st.columns(2)

        with col1:
            fig = px.bar(
                vehicle_analysis,
                x='type_vehicule',
                y='montant_moyen',
                title="Montant moyen par type de véhicule",
                labels={'montant_moyen': 'Montant moyen (€)', 'type_vehicule': 'Type de véhicule'},
                text_auto='.2s'
            )
            st.plotly_chart(fig, use_container_width=True, key='type_vehicule')

        with col2:
            fig = px.bar(
                vehicle_analysis,
                x='type_vehicule',
                y='heures_moyennes',
                title="Heures de main d'œuvre moyennes par type de véhicule",
                labels={'heures_moyennes': 'Heures moyennes', 'type_vehicule': 'Type de véhicule'},
                text_auto='.2f'
            )
            st.plotly_chart(fig, use_container_width=True, key='mo_par_vehicule')
    else:
        st.info("Aucune donnée disponible pour la période sélectionnée")

with tab3:
    st.header("Suivi financier")

    # Répartition CA vs Charges
    st.subheader("CA vs Charges")

    col1, col2 = st.columns(2)

    with col1:
        if not filtered_prestations.empty and not filtered_charges.empty:
            # Regrouper les données par mois
            ca_monthly = filtered_prestations.groupby(filtered_prestations['date'].dt.month)[
                'montant_total_ttc'].sum().reset_index()
            ca_monthly.rename(columns={'date': 'mois'}, inplace=True)

            charges_monthly = filtered_charges.groupby(filtered_charges['date'].dt.month)['montant'].sum().reset_index()
            charges_monthly.rename(columns={'date': 'mois'}, inplace=True)

            # Fusionner les données
            months_list = range(1, 13)
            month_names = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin', 'Juil', 'Août', 'Sep', 'Oct', 'Nov', 'Déc']
            months_df = pd.DataFrame({'mois': list(months_list), 'nom_mois': month_names[:len(months_list)]})

            # Joindre les données de CA
            months_df = pd.merge(months_df, ca_monthly, on='mois', how='left')
            months_df = pd.merge(months_df, charges_monthly, on='mois', how='left')
            months_df.rename(columns={'montant_total_ttc': 'CA', 'montant': 'Charges'}, inplace=True)
            months_df.fillna(0, inplace=True)

            # Calcul du résultat
            months_df['Résultat'] = months_df['CA'] - months_df['Charges']

            # Graphique
            fig = go.Figure()

            fig.add_trace(go.Bar(
                x=months_df['nom_mois'],
                y=months_df['CA'],
                name='CA TTC',
                marker_color='green'
            ))

            fig.add_trace(go.Bar(
                x=months_df['nom_mois'],
                y=months_df['Charges'],
                name='Charges',
                marker_color='red'
            ))

            fig.add_trace(go.Scatter(
                x=months_df['nom_mois'],
                y=months_df['Résultat'],
                name='Résultat',
                mode='lines+markers',
                line=dict(color='blue', width=2)
            ))

            fig.update_layout(
                title='CA vs Charges par mois',
                xaxis_title='Mois',
                yaxis_title='Montant (€)',
                barmode='group',
                hovermode='x unified'
            )

            st.plotly_chart(fig, use_container_width=True, key='ca_charge')
        else:
            st.info("Données insuffisantes pour la période sélectionnée")

    with col2:
        if not filtered_charges.empty:
            # Répartition des charges par type
            charges_by_type = filtered_charges.groupby('type')['montant'].sum().reset_index()
            charges_by_type.sort_values('montant', ascending=False, inplace=True)

            fig = px.pie(
                charges_by_type,
                values='montant',
                names='type',
                title="Répartition des charges par type"
            )

            st.plotly_chart(fig, use_container_width=True, key='charge_par_type')
        else:
            st.info("Aucune donnée de charges disponible pour la période sélectionnée")

    # Suivi des fournisseurs
    st.subheader("Suivi des pièces et fournisseurs")

    col1, col2 = st.columns(2)

    with col1:
        if not filtered_fournisseurs.empty:
            st.write("Factures fournisseurs")
            # Calcul des factures impayées
            unpaid = filtered_fournisseurs[~filtered_fournisseurs['payee']]
            st.write(f"Total factures impayées: {unpaid['montant'].sum():.2f} €")

            # Graphique des factures par fournisseur
            fournisseur_summary = filtered_fournisseurs.groupby('fournisseur').agg({
                'montant': 'sum',
                'payee': lambda x: (~x).sum()  # Compte les non-payées
            }).reset_index()

            fournisseur_summary.rename(columns={'payee': 'nb_impayees'}, inplace=True)

            fig = px.bar(
                fournisseur_summary,
                x='fournisseur',
                y='montant',
                color='nb_impayees',
                title="Montant des achats par fournisseur",
                labels={'montant': 'Montant total (€)', 'fournisseur': 'Fournisseur',
                        'nb_impayees': 'Nb factures impayées'},
                text_auto='.2s',
                color_continuous_scale='Reds'
            )

            st.plotly_chart(fig, use_container_width=True, key='facture_fournisseur')
        else:
            st.info("Aucune donnée fournisseur disponible pour la période sélectionnée")

    with col2:
        if not filtered_prestations.empty:
            # Ratio pièces vs main d'œuvre
            pieces_mo_data = pd.DataFrame({
                'Type': ['Pièces', 'Main d\'œuvre'],
                'Montant': [
                    filtered_prestations['montant_pieces'].sum(),
                    filtered_prestations['montant_main_oeuvre'].sum()
                ]
            })

            fig = px.pie(
                pieces_mo_data,
                values='Montant',
                names='Type',
                title="Répartition pièces vs main d'œuvre",
                hole=0.4
            )

            st.plotly_chart(fig, use_container_width=True, key='ratio_pieces_mo')

            # Marge sur pièces
            marge_pieces = filtered_prestations['montant_pieces'].sum() - filtered_prestations[
                'montant_pieces_fournisseur'].sum()
            taux_marge_pieces = (marge_pieces / filtered_prestations['montant_pieces_fournisseur'].sum()) * 100 if \
            filtered_prestations['montant_pieces_fournisseur'].sum() > 0 else 0

            st.metric("Marge sur pièces", f"{marge_pieces:.2f} €", f"{taux_marge_pieces:.1f}%")
        else:
            st.info("Aucune donnée de prestations disponible pour la période sélectionnée")

    # Charges à payer
    st.subheader("Charges restant à payer")

    if not filtered_charges.empty:
        charges_impayees = filtered_charges[~filtered_charges['payee']]

        if not charges_impayees.empty:
            st.dataframe(charges_impayees)
            st.markdown(download_df(charges_impayees, "charges_a_payer"), unsafe_allow_html=True)

            st.metric("Total à payer", f"{charges_impayees['montant'].sum():.2f} €")
        else:
            st.success("Toutes les charges de la période ont été payées")
    else:
        st.info("Aucune donnée de charges disponible pour la période sélectionnée")

with tab4:
    st.header("Gestion du personnel")

    # Analyse des absences
    st.subheader("Suivi des absences")

    if not filtered_absences.empty:
        absences_by_person = filtered_absences.groupby('nom').agg({
            'duree': 'sum',
            'date': 'count'
        }).reset_index()

        absences_by_person.rename(columns={'date': 'nb_absences', 'duree': 'jours_absence'}, inplace=True)
        absences_by_person.sort_values('jours_absence', ascending=False, inplace=True)

        col1, col2 = st.columns(2)

        with col1:
            fig = px.bar(
                absences_by_person,
                x='nom',
                y='jours_absence',
                title="Jours d'absence par employé",
                labels={'jours_absence': 'Jours d\'absence', 'nom': 'Employé'},
                text_auto='.0f'
            )
            st.plotly_chart(fig, use_container_width=True, key='absences')

        with col2:
            absences_by_type = filtered_absences.groupby('type_absence')['duree'].sum().reset_index()

            fig = px.pie(
                absences_by_type,
                values='duree',
                names='type_absence',
                title="Répartition des absences par type"
            )
            st.plotly_chart(fig, use_container_width=True, key='duree_type_absence')

        # Calendrier des absences
        st.subheader("Calendrier des absences")

        absences_by_date = filtered_absences.copy()
        absences_by_date['semaine'] = absences_by_date['date'].dt.isocalendar().week
        absences_by_date['mois'] = absences_by_date['date'].dt.month_name()

        # Créer un calendrier mensuel
        absences_grouped = absences_by_date.groupby(['mois', 'date']).agg({
            'nom': lambda x: ', '.join(set(x)),
            'duree': 'sum'
        }).reset_index()

        # Afficher les données d'absence par jour
        st.dataframe(absences_grouped[['date', 'nom', 'duree']])
        st.markdown(download_df(filtered_absences, "absences"), unsafe_allow_html=True)
    else:
        st.info("Aucune donnée d'absence disponible pour la période sélectionnée")

    # Productivité du personnel
    st.subheader("Productivité du personnel")

    if not filtered_prestations.empty:
        # Heures facturées par technicien
        heures_par_tech = filtered_prestations.groupby('technicien')['main_oeuvre_heures'].sum().reset_index()
        heures_par_tech.sort_values('main_oeuvre_heures', ascending=False, inplace=True)

        # Calculer la moyenne d'heures facturées par jour ouvré (estimé à 20 jours par mois)
        selected_months = len(set(filtered_prestations['date'].dt.month))
        jours_ouvres = selected_months * 20  # Estimation

        heures_par_tech['moy_heures_jour'] = heures_par_tech['main_oeuvre_heures'] / jours_ouvres

        fig = px.bar(
            heures_par_tech,
            x='technicien',
            y='moy_heures_jour',
            title="Heures facturées en moyenne par jour ouvré",
            labels={'moy_heures_jour': 'Heures facturées/jour', 'technicien': 'Technicien'},
            text_auto='.1f'
        )

        # Ajouter une ligne pour l'objectif (par exemple 7h par jour)
        fig.add_shape(
            type="line",
            x0=-0.5,
            y0=7,
            x1=len(heures_par_tech) - 0.5,
            y1=7,
            line=dict(color="red", width=2, dash="dash"),
        )

        fig.add_annotation(
            x=len(heures_par_tech) / 2,
            y=7.2,
            text="Objectif",
            showarrow=False,
            font=dict(color="red")
        )

        st.plotly_chart(fig, use_container_width=True, key='productivite_personnel')
    else:
        st.info("Aucune donnée de prestations disponible pour la période sélectionnée")

with tab5:
    st.header("Analyses avancées")

    # Performance par type de véhicule et type de prestation
    st.subheader("Performance par type de véhicule et type de prestation")

    if not filtered_prestations.empty:
        # Création d'une heatmap pour voir les prestations les plus rentables par type de véhicule
        perf_matrix = filtered_prestations.pivot_table(
            index='type_vehicule',
            columns='type_prestation',
            values='marge_totale',
            aggfunc='mean'
        ).fillna(0)

        fig = px.imshow(
            perf_matrix,
            labels=dict(x="Type de prestation", y="Type de véhicule", color="Marge moyenne (€)"),
            text_auto='.0f',
            aspect="auto",
            title="Marge moyenne par type de véhicule et prestation"
        )

        st.plotly_chart(fig, use_container_width=True, key='heatmap_rentabilite')

        # Temps moyen par type de prestation
        temps_moyen = filtered_prestations.groupby('type_prestation')['main_oeuvre_heures'].mean().reset_index()
        temps_moyen.sort_values('main_oeuvre_heures', ascending=False, inplace=True)

        fig = px.bar(
            temps_moyen,
            x='type_prestation',
            y='main_oeuvre_heures',
            title="Temps moyen par type de prestation",
            labels={'main_oeuvre_heures': 'Heures de main d\'œuvre', 'type_prestation': 'Type de prestation'},
            text_auto='.1f'
        )

        st.plotly_chart(fig, use_container_width=True, key='tps_moyen_prestation')
    else:
        st.info("Aucune donnée disponible pour la période sélectionnée")

    # Analyse de rentabilité
    st.subheader("Analyse de rentabilité")

    col1, col2 = st.columns(2)

    with col1:
        if not filtered_prestations.empty:
            # Calcul du ratio de rentabilité (marge / heures)
            filtered_prestations['rentabilite_horaire'] = filtered_prestations['marge_totale'] / filtered_prestations[
                'main_oeuvre_heures']

            rentabilite_prestation = filtered_prestations.groupby('type_prestation')[
                'rentabilite_horaire'].mean().reset_index()
            rentabilite_prestation.sort_values('rentabilite_horaire', ascending=False, inplace=True)

            fig = px.bar(
                rentabilite_prestation,
                x='type_prestation',
                y='rentabilite_horaire',
                title="Rentabilité horaire par type de prestation",
                labels={'rentabilite_horaire': 'Marge par heure (€/h)', 'type_prestation': 'Type de prestation'},
                text_auto='.0f'
            )

            st.plotly_chart(fig, use_container_width=True, key='rentabilite_marge_heure')
        else:
            st.info("Aucune donnée de prestations disponible pour la période sélectionnée")

    with col2:
        if not filtered_prestations.empty and not filtered_charges.empty:
            # Calcul du point mort
            ca_total = filtered_prestations['montant_total_ttc'].sum()
            charges_totales = filtered_charges['montant'].sum()

            # Calculer le CA journalier moyen
            jours_periode = (filtered_prestations['date'].max() - filtered_prestations['date'].min()).days + 1
            ca_journalier = ca_total / jours_periode if jours_periode > 0 else 0

            # Calculer les charges journalières
            charges_journalieres = charges_totales / jours_periode if jours_periode > 0 else 0

            # Point mort en jours (combien de jours pour couvrir les charges)
            point_mort_jours = charges_totales / ca_journalier if ca_journalier > 0 else float('inf')

            # Afficher le résultat
            st.metric("CA journalier moyen", f"{ca_journalier:.2f} €")
            st.metric("Charges journalières moyennes", f"{charges_journalieres:.2f} €")

            if point_mort_jours != float('inf'):
                st.metric("Point mort", f"{point_mort_jours:.1f} jours de travail")
            else:
                st.error("Point mort non calculable (CA journalier nul)")
        else:
            st.info("Données insuffisantes pour la période sélectionnée")

    # Prévisions et tendances
    st.subheader("Prévisions et tendances")

    if not filtered_prestations.empty:
        # Évolution du CA au fil du temps
        ca_daily = filtered_prestations.groupby(filtered_prestations['date'])['montant_total_ttc'].sum().reset_index()
        ca_daily.sort_values('date', inplace=True)

        # Calculer la moyenne mobile sur 7 jours
        ca_daily['moyenne_mobile_7j'] = ca_daily['montant_total_ttc'].rolling(window=7, min_periods=1).mean()

        fig = px.line(
            ca_daily,
            x='date',
            y=['montant_total_ttc', 'moyenne_mobile_7j'],
            title="Évolution du CA quotidien et tendance",
            labels={'value': 'Montant (€)', 'date': 'Date', 'variable': ''},
            color_discrete_map={
                'montant_total_ttc': 'lightblue',
                'moyenne_mobile_7j': 'darkblue'
            }
        )

        fig.update_layout(hovermode="x unified")
        st.plotly_chart(fig, use_container_width=True, key='évolution_ca_temps')

        # Analyse de saisonnalité par jour de la semaine
        ca_daily['jour_semaine'] = ca_daily['date'].dt.day_name()

        # Ordre des jours de la semaine
        jours_ordre = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        jours_fr = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']

        mapping_jours = dict(zip(jours_ordre, jours_fr))
        ca_daily['jour_semaine_fr'] = ca_daily['jour_semaine'].map(mapping_jours)

        ca_jour_semaine = ca_daily.groupby('jour_semaine_fr')['montant_total_ttc'].mean().reset_index()

        # Réordonner les jours de la semaine
        ca_jour_semaine['ordre'] = ca_jour_semaine['jour_semaine_fr'].map(dict(zip(jours_fr, range(7))))
        ca_jour_semaine.sort_values('ordre', inplace=True)

        fig = px.bar(
            ca_jour_semaine,
            x='jour_semaine_fr',
            y='montant_total_ttc',
            title="CA moyen par jour de la semaine",
            labels={'montant_total_ttc': 'CA moyen (€)', 'jour_semaine_fr': 'Jour de la semaine'},
            text_auto='.0f'
        )

        st.plotly_chart(fig, use_container_width=True, key='rentabilite_jour_semaine')
    else:
        st.info("Aucune donnée de prestations disponible pour la période sélectionnée")

    # KPIs avancés
    st.subheader("KPIs et indicateurs clés")

    col1, col2, col3 = st.columns(3)

    if not filtered_prestations.empty:
        with col1:
            # Taux de conversion horaire (combien rapporte une heure facturée en moyenne)
            taux_conversion = filtered_prestations['montant_total_ttc'].sum() / filtered_prestations[
                'main_oeuvre_heures'].sum() if filtered_prestations['main_oeuvre_heures'].sum() > 0 else 0
            st.metric("Taux horaire moyen facturé", f"{taux_conversion:.2f} €/h")

            # Montant moyen par prestation
            montant_moyen = filtered_prestations['montant_total_ttc'].mean()
            st.metric("Montant moyen par prestation", f"{montant_moyen:.2f} €")

        with col2:
            # Ratio pièces/main d'œuvre
            ratio_pieces_mo = filtered_prestations['montant_pieces'].sum() / filtered_prestations[
                'montant_main_oeuvre'].sum() if filtered_prestations['montant_main_oeuvre'].sum() > 0 else 0
            st.metric("Ratio pièces/main d'œuvre", f"{ratio_pieces_mo:.2f}")

            # Marge moyenne par prestation
            marge_moyenne = filtered_prestations['marge_totale'].mean()
            st.metric("Marge moyenne par prestation", f"{marge_moyenne:.2f} €")

        with col3:
            # Nombre de prestations par jour
            nb_jours = len(filtered_prestations['date'].dt.date.unique())
            prestations_par_jour = len(filtered_prestations) / nb_jours if nb_jours > 0 else 0
            st.metric("Prestations par jour", f"{prestations_par_jour:.1f}")

            # Délai moyen entre prestations (pour les clients réguliers)
            if len(filtered_prestations) > 10:  # Seulement si assez de données
                # Simuler un ID client pour l'exemple (en réalité il faudrait avoir cette donnée)
                filtered_prestations['client_id'] = np.random.randint(1, 100, size=len(filtered_prestations))

                # Compter les clients avec plus d'une prestation
                clients_count = filtered_prestations.groupby('client_id').size()
                clients_reguliers = clients_count[clients_count > 1].count()

                st.metric("Clients réguliers", f"{clients_reguliers}")
            else:
                st.info("Données insuffisantes pour certains KPIs")
    else:
        st.info("Aucune donnée disponible pour calculer les KPIs")

    # Recommandations automatiques
    st.subheader("Recommandations")

    if not filtered_prestations.empty and not filtered_charges.empty:
        recommandations = []

        # Analyse des prestations les plus rentables
        prestations_rentables = filtered_prestations.groupby('type_prestation')[
            'rentabilite_horaire'].mean().sort_values(ascending=False)
        prestations_populaires = filtered_prestations.groupby('type_prestation').size().sort_values(ascending=False)

        # Identifier les prestations rentables mais peu populaires
        top_rentables = set(prestations_rentables.head(3).index)
        top_populaires = set(prestations_populaires.head(3).index)

        opportunites = top_rentables - top_populaires
        if opportunites:
            recommandations.append(
                f"Opportunité: Les prestations {', '.join(opportunites)} sont très rentables mais peu fréquentes. Considérez des actions marketing pour ces services.")

        # Analyse des techniciens
        tech_perf = filtered_prestations.groupby('technicien')['marge_totale'].sum().sort_values()
        if len(tech_perf) >= 3:
            least_performing = tech_perf.index[0]
            recommandations.append(
                f"Formation: {least_performing} génère moins de marge que les autres techniciens. Envisagez une formation ou un accompagnement.")

        # Analyse des charges
        charges_elevees = filtered_charges.groupby('type')['montant'].sum().sort_values(ascending=False).head(1)
        if not charges_elevees.empty:
            top_charge = charges_elevees.index[0]
            recommandations.append(
                f"Optimisation des coûts: {top_charge} représente une part importante des charges. Examinez les possibilités de réduction.")

        # Analyse saisonnière
        if 'ca_jour_semaine' in locals():
            jours_faibles = ca_jour_semaine.sort_values('montant_total_ttc').iloc[0]['jour_semaine_fr']
            recommandations.append(
                f"Activité: Le {jours_faibles} est généralement le jour le moins actif. Envisagez des promotions spéciales pour ce jour.")

        # Afficher les recommandations
        if recommandations:
            for i, rec in enumerate(recommandations, 1):
                st.info(f"{i}. {rec}")
        else:
            st.success("Pas de recommandations spécifiques pour la période sélectionnée.")
    else:
        st.info("Données insuffisantes pour générer des recommandations")
        
with tab6:

    # Initialisation des données si elles ne sont pas déjà chargées
    def generate_sample_data():
        # Données par défaut pour les bonus
        if 'bonus' not in st.session_state:
            st.session_state.bonus = pd.DataFrame({
                'id_bonus': [],
                'date': [],
                'amount': [],
                'description': []
            })

        return {
            'bonus': st.session_state.bonus
        }

    # Charger les données si elles existent, sinon générer des données par défaut
    data = generate_sample_data()

    # Interface utilisateur principale
    st.title("Gestion des Bonus")

    # Section pour ajouter de nouveaux bonus
    with st.expander("Ajouter un Bonus"):
        col1, col2 = st.columns(2)

        with col1:
            new_date = st.date_input("Date du Bonus", date.today())
            new_amount = st.number_input("Montant du Bonus", min_value=0)

        with col2:
            new_description = st.text_input("Description du Bonus")

        if st.button("Ajouter le Bonus"):
            # Ajout des données dans le DataFrame
            data['bonus'] = pd.concat([
                data['bonus'],
                pd.DataFrame({
                    'id_bonus': [len(data['bonus']) + 1],
                    'date': [new_date],
                    'amount': [new_amount],
                    'description': [new_description]
                })
            ])

            # Sauvegarde dans le fichier CSV
            st.session_state.bonus = data['bonus']
            st.success("Bonus ajouté avec succès !")

    # Section pour visualiser les bonus existants
    with st.expander("Analyse des Bonus"):
        col1, col2 = st.columns(2)

        # Graphique de l'évolution des bonus au fil du temps
        with col1:
            st.subheader("Évolution des bonus")
            if not data['bonus'].empty:
                fig = px.line(data['bonus'], x='date', y='amount',
                              title="Montant des bonus au fil du temps",
                              labels={'x': 'Date', 'y': 'Montant'})
                st.plotly_chart(fig)
            else:
                st.info("Aucun bonus enregistré pour l'instant.")

        # Tableau des bonus
        with col2:
            st.subheader("Liste des bonus")
            if not data['bonus'].empty:
                st.dataframe(data['bonus'],
                             column_config={
                                 'id_bonus': {'visible': False},
                                 'date': {'label': 'Date'},
                                 'amount': {'label': 'Montant', 'format': '${{value:.2f}'},
                                 'description': {'label': 'Description'}
                             })
            else:
                st.info("Aucun bonus enregistré pour l'instant.")

    # Interface utilisateur pour filtrer les bonus par période
    st.subheader("Calcul du Total des Bonus selon la Période")
    start_date = st.date_input("Date de Début", date.today())
    end_date = st.date_input("Date de Fin", date.today())

    if start_date <= end_date:
        filtered_bonus = data['bonus'][
            (data['bonus']['date'] >= start_date) &
            (data['bonus']['date'] <= end_date)
            ]

        if not filtered_bonus.empty:
            total_amount = filtered_bonus['amount'].sum()
            st.write(f"Montant Total du Bonus pour la période : **{total_amount}**")
        else:
            st.warning("Aucun bonus trouvé pour cette période.")
    else:
        st.warning("La date de fin doit être supérieure ou égale à la date de début.")

    # Interface utilisateur pour générer un rapport au format PDF
    with st.expander("Générer un Rapport"):
        if not data['bonus'].empty:
            # Code pour générer le rapport (à implémenter selon vos besoins)
            st.info("Cliquez ici pour générer un rapport au format PDF.")
        else:
            st.warning("Aucun bonus enregistré pour générer un rapport.")

    # Informations complémentaires
    with st.expander("Informations sur les Bonus"):
        st.markdown("""
        ### Guide rapide :
        - Vous pouvez ajouter de nouveaux bonus en utilisant l'onglet 'Ajouter un Bonus'.
        - Visualiser l'évolution des bonus dans le graphique interactif.
        - Filtrer les bonus par période pour obtenir le total correspondant.
        """)


# Ajouter un pied de page
st.markdown("---")
st.markdown("© 2024 Dashboard de Suivi d'Activité - Garage Automobile")

# Performance par type de véhicule et type de prestation
st.subheader("Performance par type de véhicule et type de prestation")

if not filtered_prestations.empty:
    # Création d'une heatmap pour voir les prestations les plus rentables par type de véhicule
    perf_matrix = filtered_prestations.pivot_table(
        index='type_vehicule',
        columns='type_prestation',
        values='marge_totale',
        aggfunc='mean'
    ).fillna(0)

    fig = px.imshow(
        perf_matrix,
        labels=dict(x="Type de prestation", y="Type de véhicule", color="Marge moyenne (€)"),
        text_auto='.0f',
        aspect="auto",
        title="Marge moyenne par type de véhicule et prestation"
    )

    st.plotly_chart(fig, use_container_width=True, key='heatmap_rentabilité_vehicule')

    # Temps moyen par type de prestation
    temps_moyen = filtered_prestations.groupby('type_prestation')['main_oeuvre_heures'].mean().reset_index()
    temps_moyen.sort_values('main_oeuvre_heures', ascending=False, inplace=True)

    fig = px.bar(
        temps_moyen,
        x='type_prestation',
        y='main_oeuvre_heures',
        title="Temps moyen par type de prestation",
        labels={'main_oeuvre_heures': 'Heures de main d\'œuvre', 'type_prestation': 'Type de prestation'},
        text_auto='.1f'
    )

    st.plotly_chart(fig, use_container_width=True, key='tps_moyen_type_prestation')
else:
    st.info("Aucune donnée disponible pour la période sélectionnée")

# Analyse de rentabilité
st.subheader("Analyse de rentabilité")

col1, col2 = st.columns(2)

with col1:
    if not filtered_prestations.empty:
        # Calcul du ratio de rentabilité (marge / heures)
        filtered_prestations['rentabilite_horaire'] = filtered_prestations['marge_totale'] / filtered_prestations[
            'main_oeuvre_heures']

        rentabilite_prestation = filtered_prestations.groupby('type_prestation')[
            'rentabilite_horaire'].mean().reset_index()
        rentabilite_prestation.sort_values('rentabilite_horaire', ascending=False, inplace=True)

        fig = px.bar(
            rentabilite_prestation,
            x='type_prestation',
            y='rentabilite_horaire',
            title="Rentabilité horaire par type de prestation",
            labels={'rentabilite_horaire': 'Marge par heure (€/h)', 'type_prestation': 'Type de prestation'},
            text_auto='.0f'
        )

        st.plotly_chart(fig, use_container_width=True, key='rentabilité_heure')
    else:
        st.info("Aucune donnée de prestations disponible pour la période sélectionnée")

with col2:
    if not filtered_prestations.empty and not filtered_charges.empty:
        # Calcul du point mort
        ca_total = filtered_prestations['montant_total_ttc'].sum()
        charges_totales = filtered_charges['montant'].sum()

        # Calculer le CA journalier moyen
        jours_periode = (filtered_prestations['date'].max() - filtered_prestations['date'].min()).days + 1
        ca_journalier = ca_total / jours_periode if jours_periode > 0 else 0

        # Calculer les charges journalières
        charges_journalieres = charges_totales / jours_periode if jours_periode > 0 else 0

        # Point mort en jours (combien de jours pour couvrir les charges)
        point_mort_jours = charges_totales / ca_journalier if ca_journalier > 0 else float('inf')

        # Afficher le résultat
        st.metric("CA journalier moyen", f"{ca_journalier:.2f} €")
        st.metric("Charges journalières moyennes", f"{charges_journalieres:.2f} €")

        if point_mort_jours != float('inf'):
            st.metric("Point mort", f"{point_mort_jours:.1f} jours de travail")
        else:
            st.error("Point mort non calculable (CA journalier nul)")
    else:
        st.info("Données insuffisantes pour la période sélectionnée")

# Prévisions et tendances
st.subheader("Prévisions et tendances")

if not filtered_prestations.empty:
    # Évolution du CA au fil du temps
    ca_daily = filtered_prestations.groupby(filtered_prestations['date'])['montant_total_ttc'].sum().reset_index()
    ca_daily.sort_values('date', inplace=True)

    # Calculer la moyenne mobile sur 7 jours
    ca_daily['moyenne_mobile_7j'] = ca_daily['montant_total_ttc'].rolling(window=7, min_periods=1).mean()

    fig = px.line(
        ca_daily,
        x='date',
        y=['montant_total_ttc', 'moyenne_mobile_7j'],
        title="Évolution du CA quotidien et tendance",
        labels={'value': 'Montant (€)', 'date': 'Date', 'variable': ''},
        color_discrete_map={
            'montant_total_ttc': 'lightblue',
            'moyenne_mobile_7j': 'darkblue'
        }
    )

    fig.update_layout(hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True, key='prevision_tendance')

    # Analyse de saisonnalité par jour de la semaine
    ca_daily['jour_semaine'] = ca_daily['date'].dt.day_name()

    # Ordre des jours de la semaine
    jours_ordre = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    jours_fr = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']

    mapping_jours = dict(zip(jours_ordre, jours_fr))
    ca_daily['jour_semaine_fr'] = ca_daily['jour_semaine'].map(mapping_jours)

    ca_jour_semaine = ca_daily.groupby('jour_semaine_fr')['montant_total_ttc'].mean().reset_index()

    # Réordonner les jours de la semaine
    ca_jour_semaine['ordre'] = ca_jour_semaine['jour_semaine_fr'].map(dict(zip(jours_fr, range(7))))
    ca_jour_semaine.sort_values('ordre', inplace=True)

    fig = px.bar(
        ca_jour_semaine,
        x='jour_semaine_fr',
        y='montant_total_ttc',
        title="CA moyen par jour de la semaine",
        labels={'montant_total_ttc': 'CA moyen (€)', 'jour_semaine_fr': 'Jour de la semaine'},
        text_auto='.0f'
    )

    st.plotly_chart(fig, use_container_width=True, key='saisonnalite_jour_semaine')
else:
    st.info("Aucune donnée de prestations disponible pour la période sélectionnée")

# KPIs avancés
st.subheader("KPIs et indicateurs clés")

col1, col2, col3 = st.columns(3)

if not filtered_prestations.empty:
    with col1:
        # Taux de conversion horaire (combien rapporte une heure facturée en moyenne)
        taux_conversion = filtered_prestations['montant_total_ttc'].sum() / filtered_prestations[
            'main_oeuvre_heures'].sum() if filtered_prestations['main_oeuvre_heures'].sum() > 0 else 0
        st.metric("Taux horaire moyen facturé", f"{taux_conversion:.2f} €/h")

        # Montant moyen par prestation
        montant_moyen = filtered_prestations['montant_total_ttc'].mean()
        st.metric("Montant moyen par prestation", f"{montant_moyen:.2f} €")

    with col2:
        # Ratio pièces/main d'œuvre
        ratio_pieces_mo = filtered_prestations['montant_pieces'].sum() / filtered_prestations[
            'montant_main_oeuvre'].sum() if filtered_prestations['montant_main_oeuvre'].sum() > 0 else 0
        st.metric("Ratio pièces/main d'œuvre", f"{ratio_pieces_mo:.2f}")

        # Marge moyenne par prestation
        marge_moyenne = filtered_prestations['marge_totale'].mean()
        st.metric("Marge moyenne par prestation", f"{marge_moyenne:.2f} €")

    with col3:
        # Nombre de prestations par jour
        nb_jours = len(filtered_prestations['date'].dt.date.unique())
        prestations_par_jour = len(filtered_prestations) / nb_jours if nb_jours > 0 else 0
        st.metric("Prestations par jour", f"{prestations_par_jour:.1f}")

        # Délai moyen entre prestations (pour les clients réguliers)
        if len(filtered_prestations) > 10:  # Seulement si assez de données
            # Simuler un ID client pour l'exemple (en réalité il faudrait avoir cette donnée)
            filtered_prestations['client_id'] = np.random.randint(1, 100, size=len(filtered_prestations))

            # Compter les clients avec plus d'une prestation
            clients_count = filtered_prestations.groupby('client_id').size()
            clients_reguliers = clients_count[clients_count > 1].count()

            st.metric("Clients réguliers", f"{clients_reguliers}")
        else:
            st.info("Données insuffisantes pour certains KPIs")
else:
    st.info("Aucune donnée disponible pour calculer les KPIs")

# Recommandations automatiques
st.subheader("Recommandations")

if not filtered_prestations.empty and not filtered_charges.empty:
    recommandations = []

    # Analyse des prestations les plus rentables
    prestations_rentables = filtered_prestations.groupby('type_prestation')['rentabilite_horaire'].mean().sort_values(
        ascending=False)
    prestations_populaires = filtered_prestations.groupby('type_prestation').size().sort_values(ascending=False)

    # Identifier les prestations rentables mais peu populaires
    top_rentables = set(prestations_rentables.head(3).index)
    top_populaires = set(prestations_populaires.head(3).index)

    opportunites = top_rentables - top_populaires
    if opportunites:
        recommandations.append(
            f"Opportunité: Les prestations {', '.join(opportunites)} sont très rentables mais peu fréquentes. Considérez des actions marketing pour ces services.")

    # Analyse des techniciens
    tech_perf = filtered_prestations.groupby('technicien')['marge_totale'].sum().sort_values()
    if len(tech_perf) >= 3:
        least_performing = tech_perf.index[0]
        recommandations.append(
            f"Formation: {least_performing} génère moins de marge que les autres techniciens. Envisagez une formation ou un accompagnement.")

    # Analyse des charges
    charges_elevees = filtered_charges.groupby('type')['montant'].sum().sort_values(ascending=False).head(1)
    if not charges_elevees.empty:
        top_charge = charges_elevees.index[0]
        recommandations.append(
            f"Optimisation des coûts: {top_charge} représente une part importante des charges. Examinez les possibilités de réduction.")

    # Analyse saisonnière
    if 'ca_jour_semaine' in locals():
        jours_faibles = ca_jour_semaine.sort_values('montant_total_ttc').iloc[0]['jour_semaine_fr']
        recommandations.append(
            f"Activité: Le {jours_faibles} est généralement le jour le moins actif. Envisagez des promotions spéciales pour ce jour.")

    # Afficher les recommandations
    if recommandations:
        for i, rec in enumerate(recommandations, 1):
            st.info(f"{i}. {rec}")
    else:
        st.success("Pas de recommandations spécifiques pour la période sélectionnée.")
else:
    st.info("Données insuffisantes pour générer des recommandations")

# Ajouter un pied de page
st.markdown("---")
st.markdown("© 2024 Dashboard de Suivi d'Activité - Garage Automobile")

"""


1. **Analyse croisée véhicule/prestation** : Une heatmap qui montre la rentabilité moyenne par type de véhicule et type de prestation pour identifier les combinaisons les plus lucratives.

2. **Analyse de rentabilité** :
   - Calcul de la rentabilité horaire par type de prestation
   - Analyse du point mort (nombre de jours nécessaires pour couvrir les charges)

3. **Prévisions et tendances** :
   - Évolution du CA quotidien avec moyenne mobile sur 7 jours
   - Analyse des performances par jour de la semaine pour identifier les patterns récurrents

4. **KPIs avancés** :
   - Taux horaire moyen facturé
   - Montant moyen par prestation
   - Ratio pièces/main d'œuvre
   - Marge moyenne par prestation
   - Nombre de prestations par jour
   - Suivi des clients réguliers

5. **Recommandations automatiques** qui analysent les données pour suggérer des actions concrètes :
   - Identification des prestations rentables mais peu fréquentes
   - Détection des techniciens moins performants qui pourraient bénéficier de formation
   - Analyse des charges les plus importantes pour optimisation
   - Suggestion d'actions pour les jours de la semaine moins rentables

Cette application  permet une vision complète l'activité du garage avec :
- Le suivi financier (CA, marges, charges)
- L'analyse des prestations (types, rentabilité)
- La gestion des fournisseurs et des pièces
- Le suivi des absences du personnel
- Des analyses avancées pour prendre des décisions stratégiques

Pour utiliser cette application, il  suffira de remplacer les données fictives par les données réelles en modifiant la fonction `generate_sample_data()` ou en important vos données depuis des fichiers.

"""

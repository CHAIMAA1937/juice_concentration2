
import streamlit as st
import pandas as pd
from io import BytesIO

from backend.streamlit_server import start_api_server

start_api_server()
from frontend.api_client import (
    register_user,
    login_user,
    get_current_user,
    logout_user,
    save_calculation,
    get_calculations
)

from calculations import calculate_concentration

from graphs import (
    create_concentration_graph,
    create_mass_flow_graph,
    create_thermal_power_graph
)

from process_diagram import create_process_diagram
from excel_export import export_results_to_excel


# =====================================================
# CONFIGURATION
# =====================================================

st.set_page_config(
    page_title="Juice Concentration",
    page_icon="🍹",
    layout="wide"
)


# =====================================================
# INITIALISATION
# =====================================================

if "token" not in st.session_state:
    st.session_state.token = None

if "user" not in st.session_state:
    st.session_state.user = None

if "results" not in st.session_state:
    st.session_state.results = None


# =====================================================
# VERIFICATION DE SESSION
# =====================================================

if st.session_state.token:

    response = get_current_user(st.session_state.token)

    if response is not None and response.status_code == 200:
        st.session_state.user = response.json()

    else:
        st.session_state.token = None
        st.session_state.user = None
        st.session_state.results = None


# =====================================================
# STYLE
# =====================================================

st.markdown("""
<style>
.main {
    background-color: #f7faf7;
}

.title {
    color: #16834a;
    text-align: center;
    font-size: 38px;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)


# =====================================================
# TITRE
# =====================================================

st.markdown(
    '<p class="title">🍹 Juice Concentration</p>',
    unsafe_allow_html=True
)

st.markdown(
    "<p style='text-align:center'>"
    "Simulation et calcul du procédé de concentration du jus"
    "</p>",
    unsafe_allow_html=True
)

st.divider()


# =====================================================
# AUTHENTIFICATION
# =====================================================

if not st.session_state.user:

    tab1, tab2 = st.tabs([
        "Connexion",
        "Inscription"
    ])

    # CONNEXION

    with tab1:

        with st.form("login_form"):

            username = st.text_input(
                "Nom d'utilisateur ou Email"
            )

            password = st.text_input(
                "Mot de passe",
                type="password"
            )

            submit = st.form_submit_button(
                "Se connecter"
            )

        if submit:

            response = login_user(username, password)

            if response is not None and response.status_code == 200:

                data = response.json()

                st.session_state.token = data["access_token"]
                st.session_state.user = data["user"]

                st.success("Connexion réussie.")

                st.rerun()

            elif response is None:

                st.error(
                    "Impossible de contacter FastAPI."
                )

            else:

                st.error(
                    response.json().get(
                        "detail",
                        "Erreur de connexion."
                    )
                )

    # INSCRIPTION

    with tab2:

        with st.form("register_form"):

            new_username = st.text_input(
                "Nom d'utilisateur"
            )

            email = st.text_input(
                "Email"
            )

            new_password = st.text_input(
                "Mot de passe",
                type="password"
            )

            confirm_password = st.text_input(
                "Confirmer le mot de passe",
                type="password"
            )

            register = st.form_submit_button(
                "Créer un compte"
            )

        if register:

            if not all([
                new_username,
                email,
                new_password,
                confirm_password
            ]):

                st.warning(
                    "Veuillez remplir tous les champs."
                )

            elif new_password != confirm_password:

                st.error(
                    "Les mots de passe ne correspondent pas."
                )

            else:

                response = register_user(
                    new_username,
                    email,
                    new_password,
                    confirm_password
                )

                if response is not None and response.status_code == 200:

                    st.success(
                        "Compte créé avec succès. Vous pouvez vous connecter."
                    )

                elif response is None:

                    st.error(
                        "Impossible de contacter FastAPI."
                    )

                else:

                    st.error(
                        response.json().get(
                            "detail",
                            "Erreur d'inscription."
                        )
                    )


# =====================================================
# APPLICATION APRES CONNEXION
# =====================================================

else:

    st.sidebar.success(
        f"Bienvenue {st.session_state.user['username']}"
    )

    # DECONNEXION

    if st.sidebar.button("Se déconnecter"):

        response = logout_user(st.session_state.token)

        if response is not None and response.status_code == 200:

            st.session_state.token = None
            st.session_state.user = None
            st.session_state.results = None

            st.rerun()

        else:

            st.sidebar.error(
                "Erreur de déconnexion."
            )

    # NAVIGATION

    page = st.sidebar.radio(
        "Navigation",
        [
            "Paramètres et calculs",
            "Résultats",
            "Graphiques",
            "Schéma du procédé",
            "Historique"
        ]
    )


    # =================================================
    # PAGE 1 : PARAMETRES ET CALCULS
    # =================================================

    if page == "Paramètres et calculs":

        st.header("Paramètres du procédé")

        with st.form("calculation_form"):

            # DONNEES DU JUS BRUT

            st.subheader("1. Données du jus brut")

            col1, col2, col3 = st.columns(3)

            with col1:

                m0 = st.number_input(
                    "Débit massique du jus brut (kg/h)",
                    min_value=0.01,
                    value=1000.0
                )

            with col2:

                x0 = st.number_input(
                    "Fraction insoluble x0",
                    min_value=0.0,
                    max_value=1.0,
                    value=0.02
                )

            with col3:

                y0 = st.number_input(
                    "Fraction soluble y0",
                    min_value=0.0,
                    max_value=1.0,
                    value=0.10
                )

            meau = st.number_input(
                "Fraction d'eau meau",
                min_value=0.0,
                max_value=1.0,
                value=0.88
            )

            # FILTRATION ET MELANGE

            st.subheader("2. Filtration et mélange")

            col1, col2, col3 = st.columns(3)

            with col1:

                mResidus = st.number_input(
                    "Débit des résidus (kg/h)",
                    min_value=0.0,
                    value=20.0
                )

            with col2:

                mR = st.number_input(
                    "Débit du jus concentré ajouté (kg/h)",
                    min_value=0.0,
                    value=100.0
                )

            with col3:

                xr = st.number_input(
                    "Fraction soluble du jus ajouté xr",
                    min_value=0.0,
                    max_value=1.0,
                    value=0.40
                )

            # CHAUFFAGE

            st.subheader("3. Chauffage")

            col1, col2, col3 = st.columns(3)

            with col1:

                Cp = st.number_input(
                    "Capacité calorifique Cp (kJ/kg.K)",
                    min_value=0.01,
                    value=3.8
                )

            with col2:

                T2 = st.number_input(
                    "Température initiale T2 (°C)",
                    value=20.0
                )

            with col3:

                T3 = st.number_input(
                    "Température après chauffage T3 (°C)",
                    value=80.0
                )

            # EVAPORATION

            st.subheader("4. Évaporation")

            col1, col2 = st.columns(2)

            with col1:

                x4 = st.number_input(
                    "Fraction massique finale x4",
                    min_value=0.01,
                    max_value=1.0,
                    value=0.40
                )

            with col2:

                lambda_v = st.number_input(
                    "Chaleur latente (kJ/kg)",
                    min_value=0.01,
                    value=2300.0
                )

            # REFROIDISSEMENT

            st.subheader("5. Refroidissement")

            col1, col2 = st.columns(2)

            with col1:

                T4 = st.number_input(
                    "Température avant refroidissement T4 (°C)",
                    value=80.0
                )

            with col2:

                T5 = st.number_input(
                    "Température finale T5 (°C)",
                    value=25.0
                )

            calculate = st.form_submit_button(
                "Calculer tous les paramètres",
                type="primary",
                use_container_width=True
            )

        # EXECUTION DU CALCUL

        if calculate:

            try:

                st.session_state.results = calculate_concentration(
                    m0,
                    x0,
                    y0,
                    meau,
                    mResidus,
                    mR,
                    xr,
                    Cp,
                    T2,
                    T3,
                    x4,
                    T4,
                    T5,
                    lambda_v
                )

                # SAUVEGARDE SQLITE

                response = save_calculation(
                    st.session_state.token,
                    st.session_state.results
                )

                if response is not None and response.status_code == 200:

                    st.success(
                        "Calcul effectué et enregistré dans l'historique avec succès."
                    )

                elif response is None:

                    st.warning(
                        "Calcul effectué, mais impossible de contacter le serveur pour enregistrer l'historique."
                    )

                else:

                    st.warning(
                        "Calcul effectué, mais erreur lors de l'enregistrement dans l'historique."
                    )

            except ValueError as error:

                st.session_state.results = None

                st.error(str(error))


    # =================================================
    # PAGE 2 : RESULTATS
    # =================================================

    elif page == "Résultats":

        st.header("Résultats des opérations unitaires")

        r = st.session_state.results

        if r is None:

            st.info(
                "Veuillez d'abord saisir les paramètres et effectuer les calculs."
            )

        else:

            # FILTRATION

            st.subheader("Filtration")

            st.write(
                f"Débit après filtration : **{r['m1']:.2f} kg/h**"
            )

            st.write(
                f"Fraction soluble y1 : **{r['y1']:.4f}**"
            )

            # MELANGE

            st.subheader("Mélange")

            st.write(
                f"Débit après mélange : **{r['m2']:.2f} kg/h**"
            )

            st.write(
                f"Fraction soluble y2 : **{r['y2']:.4f}**"
            )

            # CHAUFFAGE

            st.subheader("Chauffage")

            st.metric(
                "Puissance de chauffage",
                f"{r['Q3']:.2f} kW"
            )

            # EVAPORATION

            st.subheader("Évaporation")

            c1, c2, c3 = st.columns(3)

            c1.metric(
                "Débit final",
                f"{r['m4']:.2f} kg/h"
            )

            c2.metric(
                "Eau évaporée",
                f"{r['mv']:.2f} kg/h"
            )

            c3.metric(
                "Puissance évaporation",
                f"{r['Q4']:.2f} kW"
            )

            # REFROIDISSEMENT

            st.subheader("Refroidissement")

            st.metric(
                "Puissance de refroidissement",
                f"{r['Q5']:.2f} kW"
            )

            st.divider()

            # BILANS MATIERE

            st.subheader(
                "Vérification des bilans de matière"
            )

            bilan_data = {

                "Paramètre": [
                    "Débit total entrant",
                    "Débit total sortant",
                    "Écart global",
                    "Matières solubles entrantes",
                    "Matières solubles sortantes",
                    "Écart des matières solubles",
                    "Résidus théoriques",
                    "Écart des résidus"
                ],

                "Valeur": [
                    r["entrees"],
                    r["sorties"],
                    r["ecart_global"],
                    r["solubles_entrantes"],
                    r["solubles_sortantes"],
                    r["ecart_solubles"],
                    r["residus_theoriques"],
                    r["ecart_residus"]
                ]
            }

            st.dataframe(
                pd.DataFrame(bilan_data).round(4),
                use_container_width=True,
                hide_index=True
            )

            if (
                abs(r["ecart_global"]) < 0.000001
                and abs(r["ecart_solubles"]) < 0.000001
            ):

                st.success(
                    "Bilans global et des matières solubles vérifiés."
                )

            else:

                st.warning(
                    "Attention : vérifier les bilans de matière."
                )

            st.divider()

            # EXPORT RESULTATS EXCEL

            st.subheader("Exportation des résultats")

            excel_file = export_results_to_excel(r)

            st.download_button(
                label="📥 Télécharger les résultats en Excel",
                data=excel_file,
                file_name="resultats_concentration_jus.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )


    # =================================================
    # PAGE 3 : GRAPHIQUES
    # =================================================

    elif page == "Graphiques":

        st.title(
            "Graphiques du procédé de concentration"
        )

        if st.session_state.results is None:

            st.warning(
                "Veuillez effectuer un calcul avant d'afficher les graphiques."
            )

        else:

            r = st.session_state.results

            st.subheader("1. Évolution de la concentration")

            fig1 = create_concentration_graph(
                r["y2"] * 100,
                r["x4"] * 100,
                120
            )

            st.plotly_chart(
                fig1,
                use_container_width=True
            )

            st.subheader("2. Débits massiques")

            fig2 = create_mass_flow_graph(r)

            st.plotly_chart(
                fig2,
                use_container_width=True
            )

            st.subheader("3. Puissances thermiques")

            fig3 = create_thermal_power_graph(r)

            st.plotly_chart(
                fig3,
                use_container_width=True
            )


    # =================================================
    # PAGE 4 : SCHEMA DU PROCEDE
    # =================================================

    elif page == "Schéma du procédé":

        st.header(
            "Schéma du procédé de concentration"
        )

        fig = create_process_diagram()

        st.plotly_chart(
            fig,
            use_container_width=True
        )


    # =================================================
    # PAGE 5 : HISTORIQUE
    # =================================================

    elif page == "Historique":

        st.header("Historique de mes calculs")

        st.write(
            "Retrouvez ici les calculs enregistrés dans votre compte."
        )

        if st.button("Actualiser l'historique"):

            st.rerun()

        response = get_calculations(
            st.session_state.token
        )

        if response is None:

            st.error(
                "Impossible de contacter le serveur."
            )

        elif response.status_code == 200:

            history = response.json()

            if not history:

                st.info(
                    "Aucun calcul enregistré pour le moment."
                )

            else:

                st.success(
                    f"{len(history)} calcul(s) enregistré(s)."
                )

                # AFFICHAGE DES CALCULS

                for calculation in history:

                    with st.expander(
                        f"Calcul #{calculation['id']} - {calculation['created_at']}"
                    ):

                        results = calculation["results"]

                        st.subheader("Résultats du calcul")

                        st.json(results)

                # EXPORT COMPLET DE L'HISTORIQUE

                st.divider()

                st.subheader(
                    "Télécharger tout l'historique"
                )

                history_rows = []

                for calculation in history:

                    row = {
                        "ID": calculation["id"],
                        "Date": calculation["created_at"]
                    }

                    row.update(calculation["results"])

                    history_rows.append(row)

                history_df = pd.DataFrame(history_rows)

                excel_buffer = BytesIO()

                with pd.ExcelWriter(
                    excel_buffer,
                    engine="openpyxl"
                ) as writer:

                    history_df.to_excel(
                        writer,
                        index=False,
                        sheet_name="Historique"
                    )

                st.download_button(
                    label="📥 Télécharger tout l'historique en Excel",
                    data=excel_buffer.getvalue(),
                    file_name="historique_calculs.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

        else:

            st.error(
                "Erreur lors de la récupération de l'historique."
            )


# =====================================================
# PIED DE PAGE
# =====================================================

st.divider()

st.caption(
    "Juice Concentration | FastAPI + Streamlit + SQLite"
)

import pandas as pd
import streamlit as st
import json

from pathlib import Path
from modules.cover_letter import generate_cover_message
from modules.job_scraper import extract_job_from_url
from modules.auth import get_authenticator, load_config, register_user
from streamlit_option_menu import option_menu
from modules.database import (
    init_db,
    add_job,
    get_jobs,
    get_job_by_id,
    update_job_status,
    add_cover_message_column,
    update_cover_message,
    delete_job,
)
from modules.profile import (
    load_profile,
    save_profile,
    extract_text_from_pdf,
    create_profile_from_cv_text,
    format_profile,
)

# =========================
# CONFIG
# =========================

st.set_page_config(page_title="JobHunter AI", page_icon="🎯")

config = load_config()
authenticator = get_authenticator(config)

if not st.session_state.get("authentication_status"):
    auth_mode = st.radio(
        "Choisis une action",
        ["Connexion", "Inscription"],
        horizontal=True,
    )

    if auth_mode == "Connexion":
        authenticator.login(
            location="main",
            fields={
                "Form name": "Connexion",
                "Username": "Nom d'utilisateur",
                "Password": "Mot de passe",
                "Login": "Se connecter",
            },
        )

    elif auth_mode == "Inscription":
        register_user(authenticator, config)
        st.stop()

if st.session_state.get("authentication_status") is False:
    st.error("Identifiant ou mot de passe incorrect")
    st.stop()

if st.session_state.get("authentication_status") is None:
    st.warning("Connecte-toi pour accéder à JobHunter AI")
    st.stop()

authenticator.logout("Déconnexion", "sidebar")
st.sidebar.success(f"Connecté : {st.session_state.get('name')}")

username = st.session_state["username"]

init_db()
add_cover_message_column()


# =========================
# SIDEBAR
# =========================

with st.sidebar:
    selection = option_menu(
        menu_title="🎯 JobHunter AI",
        options=[
            "Dashboard",
            "Profil candidat",
            "Importer par URL",
            "Ajouter une offre",
            "Mes offres",
        ],
        icons=[
            "house",
            "person",
            "globe",
            "plus-circle",
            "folder",
        ],
        default_index=0,
        orientation="vertical",
    )

    st.divider()
    st.caption("Assistant IA pour candidatures data")


# =========================
# HEADER
# =========================

st.title("🎯 JobHunter AI")
st.write("Mon assistant IA pour chercher un emploi")
st.divider()


# =========================
# DASHBOARD
# =========================

if selection == "Dashboard":
    st.header("Dashboard")

    jobs = get_jobs(username)

    if jobs:
        df = pd.DataFrame(
            jobs,
            columns=[
                "ID",
                "Titre",
                "Entreprise",
                "Localisation",
                "Contrat",
                "Statut",
                "Date d'ajout",
            ],
        )

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Offres enregistrées", len(df))

        with col2:
            st.metric(
                "Candidatures envoyées",
                len(df[df["Statut"] == "Candidature envoyée"]),
            )

        with col3:
            st.metric(
                "Entretiens",
                len(df[df["Statut"] == "Entretien"]),
            )

        st.subheader("Répartition par statut")
        st.bar_chart(df["Statut"].value_counts())

    else:
        st.info("Aucune offre enregistrée pour le moment.")

# =========================
# PROFIL CANDIDAT
# =========================
elif selection == "Profil candidat":
    st.header("Profil candidat")

    profile = load_profile(username)

    st.subheader("Importer un CV")

    uploaded_file = st.file_uploader("Importer un CV PDF", type=["pdf"])

    if uploaded_file and st.button("Importer le CV dans le profil"):
        with st.spinner("Lecture du CV..."):
            cv_text = extract_text_from_pdf(uploaded_file)

            if len(cv_text.strip()) < 50:
                st.error("Impossible de lire correctement le CV.")
                st.stop()

            auto_profile = create_profile_from_cv_text(cv_text)
            save_profile(username, auto_profile)

        st.success("CV importé dans le profil")
        st.rerun()

    st.divider()

    with st.form("profile_form"):
        st.subheader("Informations personnelles")

        full_name = st.text_input("Nom complet", profile.get("full_name", ""))
        target_job = st.text_input("Poste recherché", profile.get("target_job", ""))
        location = st.text_input("Localisation", profile.get("location", ""))
        availability = st.text_input("Disponibilité", profile.get("availability", ""))

        education = st.text_area("Formation", profile.get("education", ""))
        skills = st.text_area("Compétences", profile.get("skills", ""))
        experiences = st.text_area("Expériences", profile.get("experiences", ""))
        projects = st.text_area("Projets", profile.get("projects", ""))
        summary = st.text_area(
            "Profil / CV importé",
            profile.get("summary", ""),
            height=300
        )

        submitted = st.form_submit_button("Enregistrer")

    if submitted:
        data = {
            "full_name": full_name,
            "target_job": target_job,
            "location": location,
            "availability": availability,
            "education": education,
            "skills": skills,
            "experiences": experiences,
            "projects": projects,
            "summary": summary,
        }

        save_profile(username, data)

        st.success("Profil enregistré")
        st.rerun()
# =========================
# IMPORT PAR URL
# =========================

elif selection == "Importer par URL":
    st.header("Importer une offre par URL")

    with st.form("url_import_form"):
        job_url = st.text_input("URL de l'offre")
        import_submit = st.form_submit_button("Pré-remplir l'offre")

    if import_submit:
        if job_url:
            try:
                with st.spinner("Import de l'offre..."):
                    job = extract_job_from_url(job_url)
                    st.session_state["imported_job"] = job

                st.success("Offre pré-remplie. Vérifie les infos avant d'enregistrer.")

            except Exception as e:
                st.error(f"Erreur pendant l'import : {e}")
        else:
            st.warning("Ajoute une URL.")

    if "imported_job" in st.session_state:
        job = st.session_state["imported_job"]

        st.subheader("Vérifier l'offre importée")

        with st.form("confirm_import_form"):
            imported_title = st.text_input(
                "Titre du poste",
                value=job.get("title", ""),
            )

            imported_company = st.text_input(
                "Entreprise",
                value=job.get("company", ""),
            )

            imported_location = st.text_input(
                "Localisation",
                value=job.get("location", ""),
            )

            imported_contract_type = st.selectbox(
                "Type de contrat",
                ["Alternance", "Stage", "CDI", "CDD", "Freelance", "Autre"],
                index=0,
            )

            imported_url = st.text_input(
                "URL",
                value=job.get("url", ""),
            )

            imported_description = st.text_area(
                "Description",
                value=job.get("description", ""),
                height=300,
            )

            confirm_submit = st.form_submit_button("Enregistrer l'offre")

        if confirm_submit:
            add_job(
                imported_title,
                imported_company,
                imported_location,
                imported_contract_type,
                imported_url,
                imported_description,
                username
            )

            del st.session_state["imported_job"]

            st.success("Offre enregistrée.")
            st.rerun()

# =========================
# AJOUT MANUEL
# =========================

elif selection == "Ajouter une offre":
    st.header("Ajouter une offre manuellement")

    with st.form("job_form"):
        title = st.text_input("Titre du poste")
        company = st.text_input("Entreprise")
        location = st.text_input("Localisation")

        contract_type = st.selectbox(
            "Type de contrat",
            ["Alternance", "Stage", "CDI", "CDD", "Freelance", "Autre"],
        )

        url = st.text_input("Lien de l'offre")
        description = st.text_area("Description de l'offre", height=200)

        submitted = st.form_submit_button("Ajouter l'offre")

    if submitted:
        add_job(
            title,
            company,
            location,
            contract_type,
            url,
            description,
            username
        )

        st.success("Offre ajoutée.")
        st.rerun()

# =========================
# MES OFFRES
# =========================

elif selection == "Mes offres":
    st.header("Mes offres")

    jobs = get_jobs(username)

    if jobs:
        df = pd.DataFrame(
            jobs,
            columns=[
                "ID",
                "Titre",
                "Entreprise",
                "Localisation",
                "Contrat",
                "Statut",
                "Date d'ajout",
            ],
        )

        st.dataframe(df, width="stretch")

        st.subheader("Voir le détail d'une offre")

        selected_id = st.selectbox(
            "Sélectionne l'ID de l'offre",
            df["ID"].tolist(),
        )

        selected_job = get_job_by_id(selected_id, username)

        if selected_job:
            (
                job_id,
                title,
                company,
                location,
                contract_type,
                url,
                description,
                status,
                created_at,
                cover_message,
            ) = selected_job

            st.markdown(f"## {title}")
            st.write(f"**Entreprise :** {company}")
            st.write(f"**Localisation :** {location}")
            st.write(f"**Contrat :** {contract_type}")
            st.write(f"**Statut actuel :** {status}")
            st.write(f"**Date d'ajout :** {created_at}")

            if url:
                st.link_button("Voir l'offre", url)

            st.markdown("### Description")
            st.write(description)

            st.markdown("### Message de candidature")

            if cover_message:
                st.text_area(
                    "Message généré",
                    value=cover_message,
                    height=250,
                )
            else:
                st.info("Aucun message généré pour cette offre.")

            if st.button("Générer un message de candidature"):
                with st.spinner("Génération du message..."):
                    raw_profile = load_profile(username)  # 👈 récupère le JSON
                    profile = format_profile(raw_profile) 

                    message = generate_cover_message(
                        profile,  # 👈 AJOUT
                        title,
                        company,
                        description
                    )

                update_cover_message(job_id, message, username)
                print(message)
                st.success("Message enregistré.")
                st.rerun()

            st.markdown("### Modifier le statut")

            status_options = [
                "Intéressante",
                "Candidature envoyée",
                "Relance à faire",
                "Entretien",
                "Refus",
                "Archivée",
            ]

            new_status = st.selectbox(
                "Nouveau statut",
                status_options,
                index=status_options.index(status) if status in status_options else 0,
            )

            if st.button("Mettre à jour le statut"):
                update_job_status(job_id, new_status, username)
                st.success("Statut mis à jour.")
                st.rerun()

            st.markdown("### Supprimer l'offre")

            if st.button("🗑️ Supprimer cette offre"):
                delete_job(job_id, username)
                st.success("Offre supprimée.")
                st.rerun()

    else:
        st.info("Aucune offre enregistrée pour le moment.")
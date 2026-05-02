import streamlit as st
import pandas as pd

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

from modules.cover_letter import generate_cover_message
from modules.job_scraper import extract_job_from_url


st.set_page_config(page_title="JobHunter AI", page_icon="🎯", layout="wide")

init_db()
add_cover_message_column()

st.title("🎯 JobHunter AI")
st.write("Mon assistant IA pour chercher une alternance ou un emploi data.")

st.divider()


# =========================
# AJOUT MANUEL
# =========================

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
    )

    st.success("Offre ajoutée.")
    st.rerun()


st.divider()


# =========================
# IMPORT PAR URL
# =========================

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

        imported_contract_type = st.text_input(
            "Type de contrat",
            value=job.get("contract_type", ""),
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
        )

        del st.session_state["imported_job"]

        st.success("Offre enregistrée.")
        st.rerun()


st.divider()


# =========================
# LISTE DES OFFRES
# =========================

st.header("Mes offres")

jobs = get_jobs()

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

    st.dataframe(df, use_container_width=True)

    st.subheader("Voir le détail d'une offre")

    selected_id = st.selectbox(
        "Sélectionne l'ID de l'offre",
        df["ID"].tolist(),
    )

    selected_job = get_job_by_id(selected_id)

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
                message = generate_cover_message(title, company, description)
                update_cover_message(job_id, message)

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
            update_job_status(job_id, new_status)
            st.success("Statut mis à jour.")
            st.rerun()
        
        st.markdown("### Supprimer l'offre")

        if st.button("🗑️ Supprimer cette offre"):
            delete_job(job_id)
            st.success("Offre supprimée.")
            st.rerun()

else:
    st.info("Aucune offre enregistrée pour le moment.")
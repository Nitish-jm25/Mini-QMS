
# app.py
# Mini QMS - Student Software Project Risk Management

import sqlite3
from datetime import date, timedelta

import pandas as pd
import plotly.express as px
import streamlit as st

from database import (
    init_db,
    get_connection,
    create_project,
    get_projects,
    delete_project,
    create_risk,
    get_risks,
    update_risk,
    delete_risk,
    get_history,
)
from risk_engine import assess_risk


# ==================== PAGE CONFIGURATION ====================

st.set_page_config(
    page_title="Mini QMS | Risk Management",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_db()


# ==================== CUSTOM CSS ====================

st.markdown(
    """
    <style>
    /* Main page spacing */
    .block-container {
        padding-top: 2.5rem !important;
        padding-bottom: 2rem !important;
        padding-left: 2rem;
        padding-right: 2rem;
    }

    /* Fix clipped title */
    .main-title {
        font-size: 2.4rem;
        font-weight: 800;
        line-height: 1.5;
        padding-top: 8px;
        padding-bottom: 8px;
        margin: 0;
        overflow: visible;
        display: block;
    }

    /* Subtitle */
    .sub-title {
        color: #808080;
        font-size: 1.05rem;
        line-height: 1.7;
        margin-top: 4px;
        margin-bottom: 24px;
    }

    /* Metric cards */
    div[data-testid="stMetric"] {
        border: 1px solid rgba(128, 128, 128, 0.25);
        padding: 16px;
        border-radius: 12px;
    }

    /* Form spacing */
    div[data-testid="stForm"] {
        border-radius: 12px;
    }

    /* Buttons */
    div.stButton > button {
        border-radius: 8px;
    }

    /* Tabs */
    button[data-baseweb="tab"] {
        font-weight: 600;
    }

    /* Footer */
    .qms-footer {
        color: #808080;
        font-size: 0.85rem;
        padding-top: 12px;
        padding-bottom: 8px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ==================== CONSTANTS ====================

CATEGORIES = [
    "Requirements",
    "Technical",
    "Schedule",
    "Resources",
    "Security",
    "Database",
    "Testing",
    "Deployment",
    "Other",
]

STATUSES = [
    "Open",
    "In Progress",
    "Mitigated",
    "Closed",
]

LEVEL_COLORS = {
    "Low": "#16A34A",
    "Medium": "#D97706",
    "High": "#EA580C",
    "Critical": "#DC2626",
}


# ==================== HELPER FUNCTIONS ====================

def risk_form(project_id, existing=None, form_key="risk_form"):
    """Create or edit a project risk."""

    existing = existing or {}

    with st.form(form_key):
        title = st.text_input(
            "Risk title *",
            value=existing.get("title", ""),
        )

        description = st.text_area(
            "Risk description",
            value=existing.get("description", ""),
        )

        category = st.selectbox(
            "Risk category",
            CATEGORIES,
            index=(
                CATEGORIES.index(existing["category"])
                if existing.get("category") in CATEGORIES
                else 0
            ),
        )

        col1, col2 = st.columns(2)

        with col1:
            probability = st.slider(
                "Probability (1–5)",
                min_value=1,
                max_value=5,
                value=int(existing.get("probability", 3)),
                help="1 = Very unlikely; 5 = Very likely",
            )

        with col2:
            impact = st.slider(
                "Impact (1–5)",
                min_value=1,
                max_value=5,
                value=int(existing.get("impact", 3)),
                help="1 = Negligible; 5 = Severe",
            )

        owner = st.text_input(
            "Risk owner *",
            value=existing.get("owner", ""),
        )

        mitigation = st.text_area(
            "Mitigation / preventive action",
            value=existing.get("mitigation", ""),
        )

        default_due = existing.get("due_date") or str(
            date.today() + timedelta(days=7)
        )

        try:
            due_value = date.fromisoformat(default_due)
        except (ValueError, TypeError):
            due_value = date.today() + timedelta(days=7)

        due_date = st.date_input(
            "Mitigation due date",
            value=due_value,
        )

        status = st.selectbox(
            "Status",
            STATUSES,
            index=(
                STATUSES.index(existing["status"])
                if existing.get("status") in STATUSES
                else 0
            ),
        )

        assessment = assess_risk(probability, impact)

        st.info(
            f"Calculated score: {assessment['score']}/25\n\n"
            f"Risk level: {assessment['level']}\n\n"
            f"{assessment['recommended_action']}"
        )

        submitted = st.form_submit_button(
            "Save changes" if existing else "Register risk",
            type="primary",
            use_container_width=True,
        )

    if submitted:
        if not title.strip() or not owner.strip():
            st.error("Risk title and risk owner are required.")
            return

        data = {
            "project_id": project_id,
            "title": title.strip(),
            "description": description.strip(),
            "category": category,
            "probability": probability,
            "impact": impact,
            "score": assessment["score"],
            "level": assessment["level"],
            "owner": owner.strip(),
            "mitigation": mitigation.strip(),
            "status": status,
            "due_date": str(due_date),
        }

        try:
            if existing:
                update_risk(existing["id"], data)
                st.success("Risk updated successfully.")
            else:
                create_risk(data)
                st.success("Risk registered successfully.")

            st.rerun()

        except (sqlite3.Error, ValueError) as exc:
            st.error(f"Could not save risk: {exc}")


# ==================== HEADER ====================

st.markdown(
    """
    <div class="main-title">
        🛡️ MINI QMS
    </div>
    <div class="sub-title">
        Student Software Project Quality and Risk Management System
    </div>
    """,
    unsafe_allow_html=True,
)


# ==================== SIDEBAR ====================

projects = get_projects()

with st.sidebar:
    st.header("⚙️ Workspace")
    st.caption("Project risk management")

    if projects:
        project_options = {
            f"{p['name']} (ID: {p['id']})": p["id"]
            for p in projects
        }

        selected_label = st.selectbox(
            "Select project",
            list(project_options.keys()),
        )

        selected_project_id = project_options[selected_label]

        selected_project = next(
            p for p in projects
            if p["id"] == selected_project_id
        )

        st.divider()
        st.caption(f"Team: {selected_project['team_name']}")
        st.caption("Risk scoring: Probability × Impact")

    else:
        selected_project_id = None
        st.info("Create your first project to get started.")

    st.divider()
    st.caption("Mini QMS")


# ==================== NAVIGATION ====================

tabs = st.tabs([
    "Dashboard",
    "Projects",
    "Risk Register",
    "Mitigation",
    "Reports",
])


# ==================== 1. DASHBOARD ====================

with tabs[0]:
    st.subheader("Project Dashboard")

    if not projects:
        st.info(
            "No projects found. Open the Projects tab to create one."
        )

    else:
        project = next(
            p for p in projects
            if p["id"] == selected_project_id
        )

        risks = get_risks(selected_project_id)
        df = pd.DataFrame(risks)

        total = len(risks)
        critical = sum(
            r["level"] == "Critical" for r in risks
        )
        open_count = sum(
            r["status"] in ["Open", "In Progress"]
            for r in risks
        )
        closed = sum(
            r["status"] == "Closed" for r in risks
        )

        c1, c2, c3, c4 = st.columns(4)

        c1.metric("Total Risks", total)
        c2.metric("Critical Risks", critical)
        c3.metric("Open / In Progress", open_count)
        c4.metric("Closed Risks", closed)

        st.markdown("### Project Information")

        a, b, c = st.columns(3)

        a.write(f"**Project:** {project['name']}")
        b.write(f"**Team:** {project['team_name']}")
        c.write(f"**Deadline:** {project['deadline']}")

        st.divider()

        left, right = st.columns(2)

        with left:
            st.markdown("### Risks by Priority")

            if not df.empty:
                order = ["Low", "Medium", "High", "Critical"]

                level_counts = (
                    df["level"]
                    .value_counts()
                    .reindex(order, fill_value=0)
                    .rename_axis("Risk Level")
                    .reset_index(name="Count")
                )

                fig = px.bar(
                    level_counts,
                    x="Risk Level",
                    y="Count",
                    color="Risk Level",
                    category_orders={"Risk Level": order},
                    color_discrete_map=LEVEL_COLORS,
                    text="Count",
                )

                fig.update_layout(showlegend=False)

                st.plotly_chart(
                    fig,
                    use_container_width=True,
                )

            else:
                st.info("Register risks to see the chart.")

        with right:
            st.markdown("### Risks by Status")

            if not df.empty:
                status_counts = (
                    df["status"]
                    .value_counts()
                    .rename_axis("Status")
                    .reset_index(name="Count")
                )

                fig = px.pie(
                    status_counts,
                    names="Status",
                    values="Count",
                    hole=0.5,
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True,
                )

            else:
                st.info("No risk data available.")

        st.markdown("### Highest-Priority Risks")

        if not df.empty:
            columns = [
                "id",
                "title",
                "level",
                "score",
                "owner",
                "status",
                "due_date",
            ]

            st.dataframe(
                df[columns].head(5),
                use_container_width=True,
                hide_index=True,
            )

        else:
            st.success("No risks registered for this project.")


# ==================== 2. PROJECTS ====================

with tabs[1]:
    st.subheader("Project Management")

    with st.expander(
        "➕ Create a New Project",
        expanded=not projects,
    ):
        with st.form("project_form"):
            project_name = st.text_input("Project name *")
            team_name = st.text_input("Team name *")

            start_date = st.date_input(
                "Start date",
                value=date.today(),
            )

            deadline = st.date_input(
                "Project deadline",
                value=date.today() + timedelta(days=30),
            )

            description = st.text_area("Project description")

            submitted = st.form_submit_button(
                "Create Project",
                type="primary",
            )

        if submitted:
            if not project_name.strip() or not team_name.strip():
                st.error(
                    "Project name and team name are required."
                )

            elif deadline < start_date:
                st.error(
                    "Deadline cannot be earlier than the start date."
                )

            else:
                try:
                    create_project(
                        project_name,
                        team_name,
                        start_date,
                        deadline,
                        description,
                    )

                    st.success("Project created successfully.")
                    st.rerun()

                except sqlite3.IntegrityError:
                    st.error(
                        "A project with this name already exists."
                    )

    st.markdown("### Existing Projects")

    if projects:
        project_df = pd.DataFrame(projects)

        st.dataframe(
            project_df[
                [
                    "id",
                    "name",
                    "team_name",
                    "start_date",
                    "deadline",
                    "total_risks",
                ]
            ],
            use_container_width=True,
            hide_index=True,
        )

        st.warning(
            "Deleting a project also deletes its risks and history."
        )

        with st.form("delete_project_form"):
            project_to_delete = st.selectbox(
                "Select project to delete",
                projects,
                format_func=lambda p: (
                    f"{p['name']} (ID: {p['id']})"
                ),
            )

            confirm_delete = st.checkbox(
                "I understand this permanently deletes project data."
            )

            delete_project_btn = st.form_submit_button(
                "Delete Project"
            )

        if delete_project_btn:
            if confirm_delete:
                delete_project(project_to_delete["id"])
                st.success("Project deleted.")
                st.rerun()
            else:
                st.error("Confirm deletion before proceeding.")

    else:
        st.info("Create a project to begin.")


# ==================== 3. RISK REGISTER ====================

with tabs[2]:
    st.subheader("Risk Register")

    if not projects:
        st.info("Create a project before registering risks.")

    else:
        project = next(
            p for p in projects
            if p["id"] == selected_project_id
        )

        st.caption(f"Project: {project['name']}")

        mode = st.radio(
            "Action",
            ["Add Risk", "Edit or Delete Risk"],
            horizontal=True,
        )

        if mode == "Add Risk":
            risk_form(
                selected_project_id,
                form_key="add_risk_form",
            )

        else:
            risks = get_risks(selected_project_id)

            if not risks:
                st.info("There are no risks to edit.")

            else:
                risk_options = {
                    f"#{r['id']} — {r['title']} ({r['level']})": r
                    for r in risks
                }

                selected_label = st.selectbox(
                    "Select a risk",
                    list(risk_options.keys()),
                    key="edit_risk_selector",
                )

                selected_risk = risk_options[selected_label]

                risk_form(
                    selected_project_id,
                    existing=selected_risk,
                    form_key=f"edit_risk_{selected_risk['id']}",
                )

                st.divider()
                st.markdown("#### Delete Selected Risk")

                risk_id = selected_risk["id"]

                if st.button(
                    "Delete This Risk",
                    key=f"delete_risk_{risk_id}",
                ):
                    st.session_state["confirm_risk_delete"] = risk_id

                if (
                    st.session_state.get("confirm_risk_delete")
                    == risk_id
                ):
                    st.warning(
                        "This permanently deletes the risk and its history."
                    )

                    col1, col2 = st.columns(2)

                    with col1:
                        if st.button(
                            "Confirm Delete",
                            key=f"confirm_delete_{risk_id}",
                        ):
                            delete_risk(risk_id)
                            del st.session_state["confirm_risk_delete"]
                            st.success("Risk deleted.")
                            st.rerun()

                    with col2:
                        if st.button(
                            "Cancel",
                            key=f"cancel_delete_{risk_id}",
                        ):
                            del st.session_state["confirm_risk_delete"]
                            st.rerun()

        st.divider()
        st.markdown("### Registered Risks")

        risks = get_risks(selected_project_id)

        if risks:
            df = pd.DataFrame(risks)

            st.dataframe(
                df[
                    [
                        "id",
                        "title",
                        "category",
                        "probability",
                        "impact",
                        "score",
                        "level",
                        "owner",
                        "status",
                        "due_date",
                    ]
                ],
                use_container_width=True,
                hide_index=True,
            )

        else:
            st.info("No risks registered yet.")


# ==================== 4. MITIGATION ====================

with tabs[3]:
    st.subheader("Mitigation and Monitoring")

    if not projects:
        st.info("Create a project to track mitigation actions.")

    else:
        risks = get_risks(selected_project_id)

        if not risks:
            st.info("Register a risk to manage its mitigation.")

        else:
            risk_options = {
                f"#{r['id']} — {r['title']}": r
                for r in risks
            }

            chosen_label = st.selectbox(
                "Choose a risk to review",
                list(risk_options.keys()),
                key="mitigation_selector",
            )

            chosen = risk_options[chosen_label]

            c1, c2, c3 = st.columns(3)

            c1.metric("Risk Score", f"{chosen['score']}/25")
            c2.metric("Priority", chosen["level"])
            c3.metric("Status", chosen["status"])

            st.markdown("#### Risk Details")

            st.write(
                f"**Description:** "
                f"{chosen['description'] or 'Not provided'}"
            )
            st.write(f"**Owner:** {chosen['owner']}")
            st.write(f"**Category:** {chosen['category']}")
            st.write(
                f"**Due date:** {chosen['due_date'] or 'Not set'}"
            )
            st.write(
                f"**Mitigation plan:** "
                f"{chosen['mitigation'] or 'No plan recorded'}"
            )

            due = chosen.get("due_date")

            if (
                due
                and due < str(date.today())
                and chosen["status"] not in ["Mitigated", "Closed"]
            ):
                st.error("Overdue: this risk requires attention.")

            elif chosen["status"] == "Closed":
                st.success("This risk has been closed.")

            st.markdown("#### Update Mitigation")

            with st.form(f"mitigation_form_{chosen['id']}"):
                new_status = st.selectbox(
                    "Current status",
                    STATUSES,
                    index=STATUSES.index(chosen["status"]),
                )

                new_owner = st.text_input(
                    "Responsible owner",
                    value=chosen["owner"],
                )

                new_mitigation = st.text_area(
                    "Mitigation / corrective action",
                    value=chosen["mitigation"],
                )

                try:
                    default_due = date.fromisoformat(due) if due else (
                        date.today() + timedelta(days=7)
                    )
                except (ValueError, TypeError):
                    default_due = date.today() + timedelta(days=7)

                new_due = st.date_input(
                    "Action due date",
                    value=default_due,
                )

                update_btn = st.form_submit_button(
                    "Update Mitigation",
                    type="primary",
                )

            if update_btn:
                data = {
                    "title": chosen["title"],
                    "description": chosen["description"],
                    "category": chosen["category"],
                    "probability": chosen["probability"],
                    "impact": chosen["impact"],
                    "score": chosen["score"],
                    "level": chosen["level"],
                    "owner": new_owner,
                    "mitigation": new_mitigation,
                    "status": new_status,
                    "due_date": str(new_due),
                }

                if not new_owner.strip():
                    st.error("Owner cannot be empty.")

                else:
                    update_risk(chosen["id"], data)
                    st.success("Mitigation details updated.")
                    st.rerun()

            st.divider()
            st.markdown("### Risk History")

            history = get_history(selected_project_id)

            filtered_history = [
                h for h in history
                if h["risk_id"] == chosen["id"]
            ]

            if filtered_history:
                history_df = pd.DataFrame(filtered_history)

                st.dataframe(
                    history_df[
                        [
                            "changed_at",
                            "old_status",
                            "new_status",
                            "remarks",
                        ]
                    ],
                    use_container_width=True,
                    hide_index=True,
                )

            else:
                st.info("No history available.")


# ==================== 5. REPORTS ====================

with tabs[4]:
    st.subheader("Quality Reports")

    if not projects:
        st.info("Create a project to generate reports.")

    else:
        risks = get_risks(selected_project_id)
        df = pd.DataFrame(risks)

        st.markdown("### Risk Summary")

        if df.empty:
            st.info("There is no risk data to report.")

        else:
            total = len(df)
            closed = int((df["status"] == "Closed").sum())
            closure_rate = closed / total * 100

            overdue_mask = (
                (df["due_date"] < str(date.today()))
                & (~df["status"].isin(["Mitigated", "Closed"]))
            )

            overdue_count = int(overdue_mask.sum())

            c1, c2, c3 = st.columns(3)

            c1.metric("Total Risks", total)
            c2.metric("Closure Rate", f"{closure_rate:.1f}%")
            c3.metric("Overdue Open Risks", overdue_count)

            st.markdown("### Risk Score Distribution")

            score_fig = px.histogram(
                df,
                x="score",
                nbins=25,
                labels={
                    "score": "Risk Score",
                    "count": "Number of Risks",
                },
                title="Distribution of Risk Scores",
            )

            st.plotly_chart(
                score_fig,
                use_container_width=True,
            )

            st.markdown("### Export Reports")

            report_columns = [
                "id",
                "project_name",
                "title",
                "description",
                "category",
                "probability",
                "impact",
                "score",
                "level",
                "owner",
                "mitigation",
                "status",
                "due_date",
                "created_at",
                "updated_at",
            ]

            st.download_button(
                "⬇️ Download Risk Register (CSV)",
                data=df[report_columns].to_csv(
                    index=False
                ).encode("utf-8"),
                file_name="qms_risk_register.csv",
                mime="text/csv",
            )

            history = get_history(selected_project_id)

            if history:
                history_df = pd.DataFrame(history)

                st.download_button(
                    "⬇️ Download Risk History (CSV)",
                    data=history_df.to_csv(
                        index=False
                    ).encode("utf-8"),
                    file_name="qms_risk_history.csv",
                    mime="text/csv",
                )

            st.caption(
                "Closure rate = Closed risks / Total registered risks × 100. "
                "This measures closure, not necessarily risk elimination."
            )


# ==================== FOOTER ====================

st.divider()

st.markdown(
    """
    <div class="qms-footer">
        Mini QMS | Student Software Project Risk Management |
        Risk Score = Probability × Impact
    </div>
    """,
    unsafe_allow_html=True,
)

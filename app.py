import streamlit as st
import sqlite3
import pandas as pd
from pathlib import Path
from datetime import datetime

DB_PATH = Path("groups.db")
ADMIN_PASSWORD = st.secrets.get("ADMIN_PASSWORD", "admin123")

APPLICATIONS = [
    "Smart Waste Sorting Assistant",
    "Mood-Based Music / Activity Recommender",
    "Personalized Study Assistant",
    "Food Image & Healthy Choice Assistant",
    "Accessible Product Selector",
    "Campus Accessibility Assistant",
    "Gesture-Controlled Interactive Application",
    "Fashion / Outfit Recommendation Tool",
    "AI Learning Game",
    "Product Preference Predictor",
]

st.set_page_config(page_title="AI Project Group Formation", page_icon="👥", layout="wide")

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS groups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_name TEXT UNIQUE NOT NULL,
            application TEXT,
            created_at TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_id INTEGER NOT NULL,
            member_no INTEGER NOT NULL,
            name TEXT NOT NULL,
            reg_no TEXT NOT NULL,
            programme TEXT NOT NULL,
            UNIQUE(group_id, member_no),
            FOREIGN KEY(group_id) REFERENCES groups(id) ON DELETE CASCADE
        )
    """)
    conn.commit()
    return conn

def get_data():
    conn = get_conn()
    q = """
    SELECT g.id, g.group_name, g.application, g.created_at,
           m.member_no, m.name, m.reg_no, m.programme
    FROM groups g JOIN members m ON g.id = m.group_id
    ORDER BY g.id, m.member_no
    """
    df = pd.read_sql_query(q, conn)
    conn.close()
    return df

def registered_students():
    df = get_data()
    if df.empty:
        return set(), set()
    return set(df["reg_no"].str.strip().str.lower()), set(df["name"].str.strip().str.lower())

def delete_group(group_id):
    conn = get_conn()
    conn.execute("DELETE FROM members WHERE group_id=?", (group_id,))
    conn.execute("DELETE FROM groups WHERE id=?", (group_id,))
    conn.commit()
    conn.close()

def save_group(group_name, application, members):
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO groups(group_name, application, created_at) VALUES(?,?,?)",
            (group_name.strip(), application, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )
        gid = cur.lastrowid
        for i, member in enumerate(members, 1):
            cur.execute(
                "INSERT INTO members(group_id, member_no, name, reg_no, programme) VALUES(?,?,?,?,?)",
                (gid, i, member["name"].strip(), member["reg_no"].strip(), member["programme"])
            )
        conn.commit()
        return True, ""
    except sqlite3.IntegrityError as e:
        conn.rollback()
        if "groups.group_name" in str(e):
            return False, "That group name is already registered."
        return False, "A student or group entry already exists."
    finally:
        conn.close()

st.title("👥 AI Project Group Formation")
st.caption("Digital Fluency • 1st Year ID + PD • 4 students per group")

with st.sidebar:
    st.header("Project Settings")
    st.info("Each group must contain exactly 4 students.")
    st.write("**Programmes:** ID / PD")
    st.write("**Target groups:** 10")
    st.divider()
    st.write("Faculty/Admin access is available from the **Admin Dashboard** tab.")

tab1, tab2 = st.tabs(["📝 Register Group", "📊 Admin Dashboard"])

with tab1:
    st.subheader("Register your project group")
    st.write("Enter the group name and details of all four members. Each registration number can be used only once.")

    with st.form("group_form", clear_on_submit=False):
        group_name = st.text_input("Group Name *", placeholder="e.g., AI Innovators")
        application = st.selectbox("Project Application *", ["— Select an application —"] + APPLICATIONS)

        st.markdown("### Member Details")
        members = []
        cols = st.columns(2)
        for i in range(4):
            with cols[i % 2]:
                st.markdown(f"**Member {i+1}**")
                name = st.text_input("Name *", key=f"name_{i}", placeholder="Full name")
                reg = st.text_input("Registration No. *", key=f"reg_{i}", placeholder="Registration number")
                programme = st.selectbox("Programme *", ["ID", "PD"], key=f"prog_{i}")
                members.append({"name": name, "reg_no": reg, "programme": programme})

        submitted = st.form_submit_button("✅ Submit Group", use_container_width=True)

    if submitted:
        errors = []
        if not group_name.strip():
            errors.append("Enter a group name.")
        if application == "— Select an application —":
            errors.append("Select a project application.")

        seen_regs, seen_names = set(), set()
        existing_regs, existing_names = registered_students()

        for i, m in enumerate(members, 1):
            if not m["name"].strip():
                errors.append(f"Enter the name for Member {i}.")
            if not m["reg_no"].strip():
                errors.append(f"Enter the registration number for Member {i}.")
            reg_key = m["reg_no"].strip().lower()
            name_key = m["name"].strip().lower()
            if reg_key:
                if reg_key in seen_regs:
                    errors.append(f"Duplicate registration number inside the group: {m['reg_no']}.")
                seen_regs.add(reg_key)
                if reg_key in existing_regs:
                    errors.append(f"Registration number already registered: {m['reg_no']}.")
            if name_key:
                if name_key in seen_names:
                    errors.append(f"Duplicate student name inside the group: {m['name']}.")
                seen_names.add(name_key)
                if name_key in existing_names:
                    errors.append(f"Student name already registered: {m['name']}.")

        if group_name.strip().lower() in set(
            get_data()["group_name"].str.strip().str.lower()
        ) if not get_data().empty else False:
            errors.append("That group name is already registered.")

        if errors:
            for e in errors:
                st.error(e)
        else:
            ok, msg = save_group(group_name, application, members)
            if ok:
                st.success("🎉 Group registered successfully!")
                st.balloons()
                st.info(f"**{group_name}** has been registered for **{application}**.")
            else:
                st.error(msg)

with tab2:
    st.subheader("Faculty / Admin Dashboard")
    password = st.text_input("Admin password", type="password", key="admin_password")
    if password == ADMIN_PASSWORD:
        df = get_data()
        group_count = 0 if df.empty else df["id"].nunique()
        student_count = 0 if df.empty else len(df)

        c1, c2, c3 = st.columns(3)
        c1.metric("Groups Registered", group_count, f"{max(0, 10-group_count)} remaining")
        c2.metric("Students Registered", student_count, f"{max(0, 40-student_count)} remaining")
        c3.metric("Project Applications", len(APPLICATIONS))

        if not df.empty:
            st.markdown("### Registered Groups")
            summary = (
                df.groupby(["id", "group_name", "application"], as_index=False)
                .agg(Members=("name", lambda x: ", ".join(x)))
                .rename(columns={"group_name": "Group", "application": "Application", "Members": "Members"})
            )
            st.dataframe(summary[["Group", "Application", "Members"]], use_container_width=True, hide_index=True)

            st.markdown("### Detailed Student List")
            detail = df[["group_name", "application", "member_no", "name", "reg_no", "programme"]].copy()
            detail.columns = ["Group", "Application", "Member", "Name", "Registration No.", "Programme"]
            st.dataframe(detail, use_container_width=True, hide_index=True)

            csv = detail.to_csv(index=False).encode("utf-8")
            st.download_button("⬇️ Download CSV", csv, "project_groups.csv", "text/csv")

            st.markdown("### Delete a Group")
            group_options = dict(zip(df["group_name"].unique(), df.drop_duplicates("group_name")["id"]))
            selected = st.selectbox("Select group to delete", ["— Select —"] + list(group_options.keys()))
            confirm = st.checkbox("I confirm that I want to delete this group.")
            if selected != "— Select —" and confirm:
                if st.button("🗑️ Delete Selected Group", type="secondary"):
                    delete_group(group_options[selected])
                    st.success(f"{selected} deleted.")
                    st.rerun()
        else:
            st.info("No groups have been registered yet.")
    elif password:
        st.error("Incorrect password.")

st.divider()
st.caption("Faculty can change the admin password in Streamlit secrets before deployment.")

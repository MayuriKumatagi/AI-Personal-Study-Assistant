import streamlit as st
import sqlite3
import hashlib
import pandas as pd

from export_pdf import export_to_pdf
from ai_helper import ask_ai, generate_quiz, study_recommendation


# ---------------- PAGE CONFIG ----------------

st.set_page_config(
    page_title="AI Personal Study Assistant",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ---------------- DATABASE CONNECTION ----------------

conn = sqlite3.connect(
    "study.db",
    check_same_thread=False
)

cursor = conn.cursor()


# ---------------- CREATE USERS TABLE ----------------

cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT
)
""")


# ---------------- CREATE TOPICS TABLE ----------------

cursor.execute("""
CREATE TABLE IF NOT EXISTS topics(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    subject TEXT,
    topic TEXT,
    status TEXT
)
""")


# ---------------- CREATE TASKS TABLE ----------------

cursor.execute("""
CREATE TABLE IF NOT EXISTS tasks(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    task TEXT,
    hours INTEGER
)
""")


conn.commit()


# ---------------- SESSION ----------------

if "user_id" not in st.session_state:
    st.session_state["user_id"] = None

if "username" not in st.session_state:
    st.session_state["username"] = None


# ---------------- TITLE ----------------

st.title("📚 AI Personal Study Assistant")

st.markdown("""
### Welcome 👋

Manage your study, track progress, and learn smarter with AI.

---
""")


col1, col2, col3 = st.columns(3)

with col1:
    st.info("📚 Study Management")

with col2:
    st.success("🤖 AI Learning")

with col3:
    st.warning("📈 Progress Tracking")


# ---------------- SIDEBAR ----------------

st.sidebar.title("📚 Study Assistant")


if st.session_state["username"]:

    st.sidebar.success(
        f"Welcome {st.session_state['username']} 👋"
    )

    if st.sidebar.button("Logout"):

        st.session_state["user_id"] = None
        st.session_state["username"] = None

        st.success("Logged out successfully ✅")
        st.rerun()

else:

    st.sidebar.info(
        "Please Login"
    )


st.sidebar.divider()


menu = st.sidebar.radio(
    "Menu",
    [
        "Register",
        "Login",
        "Forgot Password",
        "Add Topic",
        "My Topics",
        "Progress",
        "Update Topic",
        "Delete Topic",
        "Daily Planner",
        "AI Explanation",
        "Export Data",
        "AI Chat Assistant",
        "AI Quiz Generator"
    ]
)
# ---------------- REGISTER ----------------

if menu == "Register":

    st.subheader("📝 Register")


    username = st.text_input(
        "Enter Username",
        key="register_username"
    )


    password = st.text_input(
        "Enter Password",
        type="password",
        key="register_password"
    )


    if st.button("Register"):

        if username and password:

            try:

                hashed_password = hashlib.sha256(
                    password.encode()
                ).hexdigest()


                cursor.execute(
                    """
                    INSERT INTO users(username,password)
                    VALUES(?,?)
                    """,
                    (
                        username,
                        hashed_password
                    )
                )


                conn.commit()


                st.success(
                    "Registration Successful ✅"
                )


            except sqlite3.IntegrityError:

                st.error(
                    "Username already exists ❌"
                )


        else:

            st.warning(
                "Please enter username and password"
            )



# ---------------- LOGIN ----------------

# ---------------- LOGIN ----------------

elif menu == "Login":

    st.subheader("🔐 Login")


    username = st.text_input(
        "Enter Username",
        key="login_username"
    )


    password = st.text_input(
        "Enter Password",
        type="password",
        key="login_password"
    )


    if st.button("Login"):


        if username and password:


            hashed_password = hashlib.sha256(
                password.encode()
            ).hexdigest()


            cursor.execute(
                """
                SELECT id, username
                FROM users
                WHERE username=? 
                AND password=?
                """,
                (
                    username,
                    hashed_password
                )
            )


            user = cursor.fetchone()


            if user:


                st.session_state["user_id"] = user[0]

                st.session_state["username"] = user[1]


                st.success(
                    f"Login Successful Welcome {user[1]} ✅"
                )


            else:


                st.error(
                    "Invalid Username or Password ❌"
                )


        else:


            st.warning(
                "Please enter username and password"
            )



# ---------------- FORGOT PASSWORD ----------------

elif menu == "Forgot Password":

    st.subheader("🔑 Forgot Password")


    username = st.text_input(
        "Enter Username",
        key="forgot_username"
    )


    new_password = st.text_input(
        "Enter New Password",
        type="password",
        key="reset_password"
    )


    if st.button("Reset Password"):


        if username and new_password:


            cursor.execute(
                """
                SELECT * FROM users
                WHERE username=?
                """,
                (username,)
            )


            user = cursor.fetchone()


            if user:


                hashed_password = hashlib.sha256(
                    new_password.encode()
                ).hexdigest()


                cursor.execute(
                    """
                    UPDATE users
                    SET password=?
                    WHERE username=?
                    """,
                    (
                        hashed_password,
                        username
                    )
                )


                conn.commit()


                st.success(
                    "Password updated successfully ✅"
                )


            else:

                st.error(
                    "Username not found ❌"
                )


        else:

            st.warning(
                "Enter username and new password"
            )
# ---------------- ADD TOPIC ----------------

elif menu == "Add Topic":

    st.subheader("➕ Add Topic")


    if st.session_state["user_id"] is None:

        st.warning("Please login first 🔐")
        st.stop()


    subject = st.text_input(
        "Enter Subject"
    )


    topic = st.text_input(
        "Enter Topic"
    )


    status = st.selectbox(
        "Select Status",
        [
            "Pending",
            "Completed"
        ]
    )


    if st.button("Add Topic"):


        if subject and topic:


            cursor.execute(
                """
                INSERT INTO topics(
                    user_id,
                    subject,
                    topic,
                    status
                )
                VALUES(?,?,?,?)
                """,
                (
                    st.session_state["user_id"],
                    subject,
                    topic,
                    status
                )
            )


            conn.commit()


            st.success(
                "Topic added successfully ✅"
            )


        else:

            st.warning(
                "Enter subject and topic"
            )



# ---------------- MY TOPICS ----------------

elif menu == "My Topics":

    st.subheader("📖 My Topics")


    if st.session_state["user_id"] is None:

        st.warning("Please login first 🔐")
        st.stop()



    search = st.text_input(
        "Search Topic"
    )


    if search:


        cursor.execute(
            """
            SELECT * FROM topics
            WHERE user_id=?
            AND topic LIKE ?
            """,
            (
                st.session_state["user_id"],
                "%" + search + "%"
            )
        )


    else:


        cursor.execute(
            """
            SELECT * FROM topics
            WHERE user_id=?
            """,
            (
                st.session_state["user_id"],
            )
        )


    topics = cursor.fetchall()



    if topics:


        for row in topics:


            st.write(
                "🆔 ID:",
                row[0]
            )

            st.write(
                "📚 Subject:",
                row[2]
            )

            st.write(
                "📌 Topic:",
                row[3]
            )

            st.write(
                "📊 Status:",
                row[4]
            )



            if st.button(
                "Delete",
                key=f"delete_{row[0]}"
            ):


                cursor.execute(
                    """
                    DELETE FROM topics
                    WHERE id=?
                    AND user_id=?
                    """,
                    (
                        row[0],
                        st.session_state["user_id"]
                    )
                )


                conn.commit()


                st.success(
                    "Topic deleted successfully ✅"
                )


                st.rerun()



            st.divider()



    else:

        st.info(
            "No topics found 📚"
        )
# ---------------- UPDATE TOPIC ----------------

elif menu == "Update Topic":

    st.subheader("✏️ Update Topic")


    if st.session_state["user_id"] is None:

        st.warning("Please login first 🔐")
        st.stop()



    topic_id = st.number_input(
        "Enter Topic ID",
        min_value=1,
        step=1
    )


    new_topic = st.text_input(
        "Enter New Topic"
    )


    new_status = st.selectbox(
        "Update Status",
        [
            "Pending",
            "Completed"
        ]
    )


    if st.button("Update Topic"):


        cursor.execute(
            """
            UPDATE topics
            SET topic=?,
                status=?
            WHERE id=?
            AND user_id=?
            """,
            (
                new_topic,
                new_status,
                topic_id,
                st.session_state["user_id"]
            )
        )


        conn.commit()


        if cursor.rowcount > 0:

            st.success(
                "Topic updated successfully ✅"
            )

        else:

            st.error(
                "Topic not found or not yours ❌"
            )

# ---------------- DELETE TOPIC ----------------

elif menu == "Delete Topic":

    st.subheader("🗑️ Delete Topic")


    if st.session_state["user_id"] is None:

        st.warning("Please login first 🔐")
        st.stop()


    topic_id = st.number_input(
        "Enter Topic ID to Delete",
        min_value=1,
        step=1
    )


    if st.button("Delete Topic"):


        cursor.execute(
            """
            DELETE FROM topics
            WHERE id=?
            AND user_id=?
            """,
            (
                topic_id,
                st.session_state["user_id"]
            )
        )


        conn.commit()


        if cursor.rowcount > 0:

            st.success(
                "Topic deleted successfully ✅"
            )

        else:

            st.error(
                "Topic not found ❌"
            )



# ---------------- PROGRESS ----------------

elif menu == "Progress":

    st.subheader("📊 Study Progress")


    if st.session_state["user_id"] is None:

        st.warning("Please login first 🔐")
        st.stop()



    # Total Topics

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM topics
        WHERE user_id=?
        """,
        (
            st.session_state["user_id"],
        )
    )


    total_topics = cursor.fetchone()[0]



    # Completed Topics

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM topics
        WHERE user_id=?
        AND status='Completed'
        """,
        (
            st.session_state["user_id"],
        )
    )


    completed_topics = cursor.fetchone()[0]


    pending_topics = (
        total_topics - completed_topics
    )



    if total_topics > 0:

        progress = (
            completed_topics /
            total_topics
        )

    else:

        progress = 0



    col1, col2, col3 = st.columns(3)



    with col1:

        st.metric(
            "📚 Total Topics",
            total_topics
        )


    with col2:

        st.metric(
            "✅ Completed",
            completed_topics
        )


    with col3:

        st.metric(
            "⏳ Pending",
            pending_topics
        )



    st.progress(progress)



    st.success(
        f"Progress: {progress*100:.2f}%"
    )



    # Chart Data

    chart_data = pd.DataFrame(
        {
            "Status":
            [
                "Completed",
                "Pending"
            ],

            "Count":
            [
                completed_topics,
                pending_topics
            ]
        }
    )



    st.subheader(
        "📈 Topic Status Chart"
    )


    st.bar_chart(
        chart_data.set_index("Status")
    )

# ---------------- DAILY PLANNER ----------------

elif menu == "Daily Planner":

    st.subheader("📅 Daily Study Planner")


    if st.session_state["user_id"] is None:

        st.warning("Please login first 🔐")
        st.stop()



    task = st.text_input(
        "Enter Task"
    )


    hours = st.number_input(
        "Study Hours",
        min_value=1,
        step=1
    )


    if st.button("Add Task"):


        if task:


            cursor.execute(
                """
                INSERT INTO tasks(
                    user_id,
                    task,
                    hours
                )
                VALUES(?,?,?)
                """,
                (
                    st.session_state["user_id"],
                    task,
                    hours
                )
            )


            conn.commit()


            st.success(
                "Task added successfully ✅"
            )


        else:

            st.warning(
                "Enter task name"
            )



    st.subheader(
        "📌 My Tasks"
    )


    cursor.execute(
        """
        SELECT * FROM tasks
        WHERE user_id=?
        """,
        (
            st.session_state["user_id"],
        )
    )


    tasks = cursor.fetchall()



    for t in tasks:

        st.write(
            "✅",
            t[2],
            "-",
            t[3],
            "hours"
        )



# ---------------- AI EXPLANATION ----------------

elif menu == "AI Explanation":

    st.subheader(
        "🤖 AI Topic Explanation"
    )


    if st.session_state["user_id"] is None:

        st.warning("Please login first 🔐")
        st.stop()



    ai_topic = st.text_input(
        "Enter Topic"
    )


    if st.button("Explain"):


        if ai_topic:


            answer = ask_ai(
                f"""
                Explain {ai_topic}
                for a BCA student.

                Include:
                1. Definition
                2. Features
                3. Advantages
                4. Example
                """
            )


            st.success(answer)


        else:

            st.warning(
                "Enter a topic"
            )



# ---------------- AI CHAT ASSISTANT ----------------

elif menu == "AI Chat Assistant":

    st.subheader(
        "🤖 AI Chat Assistant"
    )


    if st.session_state["user_id"] is None:

        st.warning("Please login first 🔐")
        st.stop()



    question = st.text_area(
        "Ask your question"
    )


    if st.button("Ask AI"):


        if question:


            answer = ask_ai(
                question
            )


            st.success(answer)


        else:

            st.warning(
                "Enter your question"
            )



# ---------------- AI QUIZ GENERATOR ----------------

elif menu == "AI Quiz Generator":

    st.subheader(
        "📝 AI Quiz Generator"
    )


    if st.session_state["user_id"] is None:

        st.warning("Please login first 🔐")
        st.stop()



    topic = st.text_input(
        "Enter Topic Name",
        key="quiz_topic"
    )


    if st.button(
        "Generate Quiz"
    ):


        if topic:


            quiz = generate_quiz(
                topic
            )


            st.success(
                "Quiz Generated Successfully 🎉"
            )


            st.write(
                quiz
            )


        else:

            st.warning(
                "Enter a topic"
            )

# ---------------- EXPORT DATA ----------------

elif menu == "Export Data":

    st.subheader("📤 Export Study Data")


    if st.session_state["user_id"] is None:

        st.warning("Please login first 🔐")
        st.stop()



    # Get only user's topics

    cursor.execute(
        """
        SELECT subject, topic, status
        FROM topics
        WHERE user_id=?
        """,
        (
            st.session_state["user_id"],
        )
    )


    data = cursor.fetchall()



    if data:


        df = pd.DataFrame(
            data,
            columns=[
                "Subject",
                "Topic",
                "Status"
            ]
        )



        # CSV Export

        csv = df.to_csv(
            index=False
        )


        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name="my_study_topics.csv",
            mime="text/csv"
        )



        # PDF Export

        if st.button(
            "Generate PDF"
        ):


            pdf_data = [
                [
                    "Subject",
                    "Topic",
                    "Status"
                ]
            ]


            for row in data:

                pdf_data.append(
                    list(row)
                )


            export_to_pdf(
                pdf_data
            )


            with open(
                "Study_Report.pdf",
                "rb"
            ) as file:


                st.download_button(
                    label="📄 Download PDF",
                    data=file,
                    file_name="Study_Report.pdf",
                    mime="application/pdf"
                )


    else:

        st.info(
            "No study data available"
        )
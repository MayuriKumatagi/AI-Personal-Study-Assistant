import streamlit as st
import sqlite3
import pandas as pd

from export_pdf import export_to_pdf
from ai_helper import ask_ai, generate_quiz, study_recommendation
st.set_page_config(
    page_title="AI Personal Study Assistant",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)


# Database Connection
conn = sqlite3.connect("study.db")
cursor = conn.cursor()


# Create Users Table
cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    password TEXT
)
""")


# Create Topics Table
cursor.execute("""
CREATE TABLE IF NOT EXISTS topics(
    id INTEGER PRIMARY KEY,
    subject TEXT,
    topic TEXT,
    status TEXT
)
""")


# Create Tasks Table
cursor.execute("""
CREATE TABLE IF NOT EXISTS tasks(
    id INTEGER PRIMARY KEY,
    task TEXT,
    hours INTEGER
)
""")


conn.commit()


# Page Configuration
st.set_page_config(
    page_title="AI Personal Study Assistant",
    page_icon="📚"
)


# Title
st.title("📚 AI Personal Study Assistant")

st.markdown("""
### Welcome 👋

Manage your study, track your progress, generate AI quizzes, and learn smarter with AI.

---
""")
col1, col2, col3 = st.columns(3)

with col1:
    st.info("📚 Study Management")

with col2:
    st.success("🤖 AI Learning")

with col3:
    st.warning("📈 Progress Tracking")


# Sidebar
st.sidebar.title("📚 Study Assistant")
st.sidebar.success("Welcome to AI Study Assistant")
st.sidebar.info("Manage your study with AI")
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

                cursor.execute(
                    "INSERT INTO users(username,password) VALUES(?,?)",
                    (username, password)
                )

                conn.commit()

                st.success(
                    "Registration Successful ✅"
                )

            except:

                st.error(
                    "Username already exists ❌"
                )

        else:

            st.warning(
                "Please enter username and password"
            )



# ---------------- LOGIN ----------------

elif menu == "Login":

    st.subheader("🔐 Login")


    username = st.text_input(
        "Username",
        key="login_username"
    )


    password = st.text_input(
        "Password",
        type="password",
        key="login_password"
    )


    if st.button("Login"):


        cursor.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        )


        user = cursor.fetchone()


        if user:

            st.success(
                "Login Successful ✅"
            )

        else:

            st.error(
                "Invalid Username or Password ❌"
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
        key="new_password"
    )


    if st.button("Reset Password"):


        cursor.execute(
            "SELECT * FROM users WHERE username=?",
            (username,)
        )


        user = cursor.fetchone()


        if user:

            cursor.execute(
                "UPDATE users SET password=? WHERE username=?",
                (new_password, username)
            )


            conn.commit()


            st.success(
                "Password updated successfully ✅"
            )

        else:

            st.error(
                "Username not found ❌"
            )
# ---------------- ADD TOPIC ----------------

elif menu == "Add Topic":

    st.subheader("➕ Add Topic")


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
                "INSERT INTO topics(subject,topic,status) VALUES(?,?,?)",
                (subject, topic, status)
            )

            conn.commit()


            st.success(
                "Topic added successfully ✅"
            )

        else:

            st.warning(
                "Please enter subject and topic"
            )



# ---------------- MY TOPICS ----------------

elif menu == "My Topics":

    st.subheader("📖 My Topics")


    search = st.text_input(
        "Search Topic"
    )


    if search:

        cursor.execute(
            "SELECT * FROM topics WHERE topic LIKE ?",
            ('%' + search + '%',)
        )

    else:

        cursor.execute(
            "SELECT * FROM topics"
        )


    data = cursor.fetchall()


    for row in data:

        st.write("🆔 ID:", row[0])
        st.write("📚 Subject:", row[1])
        st.write("📌 Topic:", row[2])
        st.write("📊 Status:", row[3])


        if st.button(
            "Delete",
            key=f"delete_{row[0]}"
        ):

            cursor.execute(
                "DELETE FROM topics WHERE id=?",
                (row[0],)
            )

            conn.commit()

            st.success(
                "Topic deleted successfully ✅"
            )

            st.rerun()


        st.divider()



# ---------------- UPDATE TOPIC ----------------

elif menu == "Update Topic":

    st.subheader("✏️ Update Topic")


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
            SET topic=?, status=?
            WHERE id=?
            """,
            (new_topic, new_status, topic_id)
        )


        conn.commit()


        st.success(
            "Topic updated successfully ✅"
        )
# ---------------- PROGRESS ----------------

elif menu == "Progress":

    st.subheader("📊 Study Progress")


    cursor.execute(
        "SELECT COUNT(*) FROM topics"
    )

    total_topics = cursor.fetchone()[0]


    cursor.execute(
        "SELECT COUNT(*) FROM topics WHERE status='Completed'"
    )

    completed_topics = cursor.fetchone()[0]


    pending_topics = total_topics - completed_topics


    if total_topics > 0:

        progress = completed_topics / total_topics

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



    chart_data = pd.DataFrame(
        {
            "Status": [
                "Completed",
                "Pending"
            ],

            "Count": [
                completed_topics,
                pending_topics
            ]
        }
    )


    st.subheader("📈 Topic Status Chart")


    st.bar_chart(
        chart_data.set_index("Status")
    )



# ---------------- DAILY PLANNER ----------------

elif menu == "Daily Planner":

    st.subheader("📅 Daily Study Planner")


    task = st.text_input(
        "Enter Task"
    )


    hours = st.number_input(
        "Study Hours",
        min_value=1
    )


    if st.button("Add Task"):


        cursor.execute(
            "INSERT INTO tasks(task,hours) VALUES(?,?)",
            (task, hours)
        )


        conn.commit()


        st.success(
            "Task added successfully ✅"
        )



    st.subheader("📌 My Tasks")


    cursor.execute(
        "SELECT * FROM tasks"
    )


    tasks = cursor.fetchall()


    for t in tasks:

        st.write(
            "✅",
            t[1],
            "-",
            t[2],
            "hours"
        )
# ---------------- AI EXPLANATION ----------------

elif menu == "AI Explanation":

    st.subheader("🤖 AI Topic Explanation")

    ai_topic = st.text_input("Enter Topic")

    if st.button("Explain"):

        if ai_topic:

            answer = ask_ai(
                f"Explain {ai_topic} in simple words for a BCA student with definition, features, advantages and one example."
            )

            st.success(answer)

        else:

            st.warning("Please enter a topic.")

elif menu == "Export Data":

    st.subheader("📤 Export Study Data")

    import pandas as pd

    cursor.execute("SELECT * FROM topics")
    data = cursor.fetchall()

    df = pd.DataFrame(
        data,
        columns=["ID", "Subject", "Topic", "Status"]
    )

    csv = df.to_csv(index=False)

    st.download_button(
        "Download Topics CSV",
        csv,
        "study_topics.csv",
        "text/csv"
    )

    if st.button("Export PDF"):

        pdf_data = [["Subject", "Topic", "Status"]]

        cursor.execute("SELECT subject, topic, status FROM topics")
        rows = cursor.fetchall()

        for row in rows:
            pdf_data.append(list(row))

        export_to_pdf(pdf_data)

        with open("Study_Report.pdf", "rb") as pdf_file:
            st.download_button(
                label="Download PDF",
                data=pdf_file,
                file_name="Study_Report.pdf",
                mime="application/pdf"
            )



# ---------------- AI CHAT ASSISTANT ----------------

elif menu == "AI Chat Assistant":

    st.subheader("🤖 AI Chat Assistant")


    question = st.text_area(
        "Ask your question"
    )


    if st.button("Ask AI"):


        if question:


            answer = ask_ai(question)


            st.success(answer)


        else:

            st.warning(
                "Please enter a question"
            )



# ---------------- AI QUIZ GENERATOR ----------------

elif menu == "AI Quiz Generator":

    st.subheader("📝 AI Quiz Generator")


    topic = st.text_input(
        "Enter Topic Name",
        key="quiz_topic"
    )


    if st.button(
        "Generate Quiz",
        key="generate_quiz"
    ):


        if topic.strip():


            quiz = generate_quiz(topic)


            st.success(
                "Quiz Generated Successfully 🎉"
            )


            st.subheader(
                "Your AI Generated Quiz"
            )


            st.write(quiz)


        else:

            st.warning(
                "Please enter a topic"
            )
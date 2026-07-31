
import streamlit as st
import sqlite3

conn = sqlite3.connect("study.db")

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS topics(
    id INTEGER PRIMARY KEY,
    subject TEXT,
    topic TEXT
)
""")

conn.commit()
conn.close()

print("Database Created Successfully")
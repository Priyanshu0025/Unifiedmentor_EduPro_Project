import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(page_title="EduPro app", layout="wide")
st.title("EduPro data")

file = Path(__file__).parent / "data" / "EduPro_Online_Platform.xlsx"

users = pd.read_excel(file, sheet_name="Users")
courses = pd.read_excel(file, sheet_name="Courses")
teachers = pd.read_excel(file, sheet_name="Teachers")
transactions = pd.read_excel(file, sheet_name="Transactions")


for data in [users, courses, teachers, transactions]:
    data.columns = data.columns.str.strip()

users = users.drop_duplicates()
courses = courses.drop_duplicates()
teachers = teachers.drop_duplicates()
transactions = transactions.drop_duplicates()

users["Age"] = pd.to_numeric(users["Age"], errors="coerce")

df = transactions.merge(
    users[["UserID", "UserName", "Age", "Gender", "Email"]],
    on="UserID",
    how="left"
)

df = df.merge(
    courses.drop(columns=["Age", "Gender"], errors="ignore"),
    on="CourseID",
    how="left"
)

df = df.merge(
    teachers.drop(columns=["Age", "Gender"], errors="ignore"),
    on="TeacherID",
    how="left"
)

df["TransactionDate"] = pd.to_datetime(
    df["TransactionDate"], errors="coerce"
)

df["AgeGroup"] = pd.cut(
    df["Age"],
    bins=[0, 17, 25, 35, 45, 120],
    labels=["Under 18", "18-25", "26-35", "36-45", "46+"]
)

#filters
st.sidebar.header("Filters")

age = st.sidebar.multiselect(
    "Age Group", df["AgeGroup"].dropna().unique()
)
gender = st.sidebar.multiselect(
    "Gender", df["Gender"].dropna().unique()
)
category = st.sidebar.multiselect(
    "Course Category", df["CourseCategory"].dropna().unique()
)
level = st.sidebar.multiselect(
    "Course Level", df["CourseLevel"].dropna().unique()
)

filtered = df.copy()

if age:
    filtered = filtered[filtered["AgeGroup"].isin(age)]
if gender:
    filtered = filtered[filtered["Gender"].isin(gender)]
if category:
    filtered = filtered[filtered["CourseCategory"].isin(category)]
if level:
    filtered = filtered[filtered["CourseLevel"].isin(level)]


a, b, c, d = st.columns(4)
a.metric("Enrolment Records", len(filtered))
b.metric("Unique Learners", filtered["UserID"].nunique())
c.metric("Paid Records", (filtered["Amount"] > 0).sum())
d.metric("Course Categories", filtered["CourseCategory"].nunique())

left, right = st.columns(2)

with left:
    st.subheader("Enrolments by Category")
    st.bar_chart(filtered["CourseCategory"].value_counts())
with right:
    st.subheader("Enrolments by Age Group")
    st.bar_chart(filtered["AgeGroup"].value_counts().sort_index())
st.subheader("Monthly Enrolment Trend")
monthly = filtered.dropna(subset=["TransactionDate"]).copy()
monthly["Month"] = monthly["TransactionDate"].dt.to_period("M").astype(str)
st.line_chart(monthly.groupby("Month").size())
st.subheader("Filtered Data")
st.dataframe(
    filtered.drop(columns=["Email", "UserName"], errors="ignore").head(100),
    use_container_width=True
)
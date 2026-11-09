import os
import sqlite3
import pandas as pd


# --------------------------------
# Paths
# --------------------------------

TIMETABLE_FOLDER = "data/timetable"
FACULTY_FILE = "data/faculty/faculty_contacts_dummy.csv"

DATABASE_FOLDER = "database"
DATABASE_FILE = os.path.join(
    DATABASE_FOLDER,
    "academic.db"
)


# --------------------------------
# Create database folder
# --------------------------------

os.makedirs(
    DATABASE_FOLDER,
    exist_ok=True
)


# --------------------------------
# Create SQLite database
# --------------------------------

connection = sqlite3.connect(
    DATABASE_FILE
)


# --------------------------------
# Load course data
# --------------------------------

course_dataframes = []


for filename in os.listdir(TIMETABLE_FOLDER):

    if not filename.lower().endswith(".csv"):
        continue

    # Only load CSVs related to courses
    if "course" not in filename.lower():
        continue

    file_path = os.path.join(
        TIMETABLE_FOLDER,
        filename
    )

    dataframe = pd.read_csv(
        file_path
    )

    course_dataframes.append(
        dataframe
    )


if course_dataframes:

    courses = pd.concat(
        course_dataframes,
        ignore_index=True
    )

    courses.to_sql(
        "courses",
        connection,
        if_exists="replace",
        index=False
    )

    print(
        "Courses table created:",
        len(courses),
        "rows"
    )

else:

    print(
        "No course CSV files found."
    )


# --------------------------------
# Load faculty data
# --------------------------------

faculty = pd.read_csv(
    FACULTY_FILE
)


faculty.to_sql(
    "faculty",
    connection,
    if_exists="replace",
    index=False
)


print(
    "Faculty table created:",
    len(faculty),
    "rows"
)


# --------------------------------
# Show database tables
# --------------------------------

cursor = connection.cursor()

cursor.execute(
    """
    SELECT name
    FROM sqlite_master
    WHERE type='table';
    """
)

tables = cursor.fetchall()


print("\nDATABASE TABLES:")

for table in tables:

    print(
        "-",
        table[0]
    )


# --------------------------------
# Close database
# --------------------------------

connection.close()


print(
    "\nDatabase created successfully:"
)

print(
    DATABASE_FILE
)
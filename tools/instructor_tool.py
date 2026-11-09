import pandas as pd

from tools.course_data import courses


FACULTY_CSV_PATH = (
    "data/faculty/faculty_contacts_dummy.csv"
)

faculty = pd.read_csv(
    FACULTY_CSV_PATH
)


def lookup_instructor(query):
    """
    Find instructor information using:

    - course code
    - course name
    - instructor name
    """
    if isinstance(query, dict):

        if "query" in query:
            query = query["query"]

        elif "course" in query:
            query = query["course"]

        elif "course_code" in query:
            query = query["course_code"]

        elif "instructor" in query:
            query = query["instructor"]

        else:
            return []

    query = query.strip().lower()

    # ---------------------------------------
    # Search by course code
    # ---------------------------------------

    course_matches = courses[
        courses["Course Code"]
        .astype(str)
        .str.lower()
        .str.strip()
        == query
    ]

    # ---------------------------------------
    # Search by course name
    # ---------------------------------------

    if course_matches.empty:

        course_matches = courses[
            courses["Course Name"]
            .astype(str)
            .str.lower()
            .str.contains(
                query,
                na=False
            )
        ]

    # ---------------------------------------
    # Search directly by instructor name
    # ---------------------------------------

    if course_matches.empty:

        faculty_matches = faculty[
            faculty["instructor"]
            .astype(str)
            .str.lower()
            .str.contains(
                query,
                na=False
            )
        ]

        if faculty_matches.empty:
            return []

        result = []

        for _, row in faculty_matches.iterrows():

            instructor_name = row["instructor"]
            email = row["email"]

            # Protect against NaN
            if pd.isna(instructor_name):
                instructor_name = ""

            if pd.isna(email):
                email = ""

            result.append({
                "Instructor": str(instructor_name),
                "Email": str(email)
            })

        return result

    # ---------------------------------------
    # Course matched
    # ---------------------------------------

    result = []

    for _, course_row in course_matches.iterrows():

        course_code = course_row["Course Code"]
        instructor_name = course_row["Instructor(s)"]

        if pd.isna(instructor_name):
            instructor_name = ""

        instructor_name = str(
            instructor_name
        ).strip()

        # -----------------------------------
        # Find instructor in faculty table
        # -----------------------------------

        faculty_matches = faculty[
            faculty["instructor"]
            .astype(str)
            .str.lower()
            .str.strip()
            ==
            instructor_name.lower()
        ]

        # -----------------------------------
        # Faculty email not found
        # -----------------------------------

        if faculty_matches.empty:

            result.append({
                "Course Code": str(course_code),
                "Instructor": instructor_name,
                "Email": ""
            })

            continue

        # -----------------------------------
        # Faculty found
        # -----------------------------------

        for _, faculty_row in faculty_matches.iterrows():

            email = faculty_row["email"]

            if pd.isna(email):
                email = ""

            result.append({
                "Course Code": str(course_code),
                "Instructor": instructor_name,
                "Email": str(email)
            })

    return result

# --------------------------------
# Test the tool
# --------------------------------

if __name__ == "__main__":

    course_code = "CSL7350"

    results = lookup_instructor(course_code)

    print("\nCOURSE CODE:")
    print(course_code)

    print("\nRESULTS:")

    if not results:

        print("No instructor found.")

    else:

        for instructor in results:

            print("-----------------------------")

            print(
                "Instructor:",
                instructor["Instructor"]
            )

            print(
                "Email:",
                instructor["Email"]
            )
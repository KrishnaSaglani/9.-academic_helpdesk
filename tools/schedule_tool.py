import pandas as pd


# --------------------------------
# Load the course CSV
# --------------------------------

from tools.course_data import courses


# --------------------------------
# Course lookup function
# --------------------------------

def lookup_course(course_query):
    """
    Find a course using its course code or course name.
    """

    course_query = course_query.strip().lower()

    # Search by course code
    code_matches = courses[
        courses["Course Code"]
        .astype(str)
        .str.lower()
        .str.strip()
        == course_query
    ]

    if not code_matches.empty:
        return code_matches.to_dict("records")


    # Search by course name
    name_matches = courses[
        courses["Course Name"]
        .astype(str)
        .str.lower()
        .str.contains(course_query, na=False)
    ]

    if not name_matches.empty:
        return name_matches.to_dict("records")


    # Nothing found
    return []


# --------------------------------
# Test the tool
# --------------------------------

if __name__ == "__main__":

    question = "Autonomous Systems"

    results = lookup_course(question)

    print("\nSEARCH:")
    print(question)

    print("\nRESULTS:")

    if not results:

        print("No course found.")

    else:

        for course in results:

            print("-----------------------------")

            print(
                "Course Code:",
                course["Course Code"]
            )

            print(
                "Course Name:",
                course["Course Name"]
            )

            print(
                "Credits:",
                course["Credits"]
            )

            print(
                "Instructor:",
                course["Instructor(s)"]
            )

            print(
                "Slot:",
                course["Slot"]
            )
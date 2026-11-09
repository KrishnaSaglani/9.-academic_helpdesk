import os
import pandas as pd


# --------------------------------
# Folder containing course CSVs
# --------------------------------

COURSE_DATA_FOLDER = "data/timetable"


# --------------------------------
# Load all course CSV files
# --------------------------------

def load_all_courses():
    """
    Load all course CSV files from the timetable folder.

    Every CSV should contain the standard course columns.
    """

    all_courses = []

    for filename in os.listdir(COURSE_DATA_FOLDER):

        if not filename.lower().endswith(".csv"):
            continue

        # Do not load timetable committee files
        # as course data.
        if "course" not in filename.lower():
            continue

        file_path = os.path.join(
            COURSE_DATA_FOLDER,
            filename
        )

        dataframe = pd.read_csv(file_path)

        # Remember which file the course came from
        dataframe["Source File"] = filename

        all_courses.append(dataframe)


    if not all_courses:

        return pd.DataFrame()


    combined_courses = pd.concat(
        all_courses,
        ignore_index=True
    )

    return combined_courses


# --------------------------------
# Load courses when module starts
# --------------------------------

courses = load_all_courses()


# --------------------------------
# Display information
# --------------------------------

if __name__ == "__main__":

    print(
        f"Total courses loaded: "
        f"{len(courses)}"
    )

    print("\nFiles contributing course data:")

    if not courses.empty:

        source_files = (
            courses["Source File"]
            .unique()
            .tolist()
        )

        for filename in source_files:

            print(f" - {filename}")
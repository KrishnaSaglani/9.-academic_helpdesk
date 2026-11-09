import sqlite3


# --------------------------------
# Database path
# --------------------------------

DATABASE_FILE = (
    "database/academic.db"
)


# --------------------------------
# Execute SQL query
# --------------------------------

def execute_sql(query):
    """
    Execute a read-only SQL query.

    Only SELECT queries are allowed.
    """

    query = query.strip()

    # --------------------------------
    # Safety check
    # --------------------------------

    if not query.lower().startswith("select"):

        return {
            "success": False,
            "error": "Only SELECT queries are allowed."
        }


    # --------------------------------
    # Connect to database
    # --------------------------------

    connection = sqlite3.connect(
        DATABASE_FILE
    )

    connection.row_factory = (
        sqlite3.Row
    )


    try:

        cursor = connection.cursor()

        cursor.execute(
            query
        )

        rows = cursor.fetchall()


        # Convert SQLite rows
        # into normal dictionaries

        results = []

        for row in rows:

            results.append(
                dict(row)
            )


        return {
            "success": True,
            "results": results
        }


    except sqlite3.Error as error:

        return {
            "success": False,
            "error": str(error)
        }


    finally:

        connection.close()


# --------------------------------
# Test
# --------------------------------

if __name__ == "__main__":

    query = """
    SELECT
        "Course Code",
        "Course Name",
        "Slot"
    FROM courses
    WHERE "Course Name"
    LIKE '%Autonomous Systems%';
    """


    result = execute_sql(
        query
    )


    print("\nSQL RESULT:")

    print(result)
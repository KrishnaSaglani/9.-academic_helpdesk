import ollama

from tools.check_policy import check_policy
from tools.schedule_tool import lookup_course
from tools.instructor_tool import lookup_instructor
from tools.sql_tool import execute_sql


MODEL_NAME = "qwen3:8b"


def format_sql_results(results, route):
    """
    Convert raw SQL results into a readable answer.
    """

    if not results:
        return "I could not find matching information."

    # ---------------------------------------
    # INSTRUCTOR results
    # ---------------------------------------

    if route == "INSTRUCTOR":

        instructor_names = []

        for row in results:

            # Course instructor column
            if "Instructor(s)" in row:
                name = row["Instructor(s)"]

                if name not in instructor_names:
                    instructor_names.append(name)

            # Faculty table instructor column
            elif "instructor" in row:
                name = row["instructor"]

                if name not in instructor_names:
                    instructor_names.append(name)

        if len(instructor_names) == 1:

            return (
                f"The instructor is "
                f"{instructor_names[0]}."
            )

        answer = "The instructors are:\n\n"

        for index, name in enumerate(
            instructor_names,
            start=1
        ):
            answer += f"{index}. {name}\n"

        return answer.strip()

    # ---------------------------------------
    # SCHEDULE results
    # ---------------------------------------

    if route == "SCHEDULE":

        answer_lines = []

        for row in results:

            parts = []

            for column, value in row.items():

                parts.append(
                    f"{column}: {value}"
                )

            answer_lines.append(
                " | ".join(parts)
            )

        return "\n".join(answer_lines)

    # ---------------------------------------
    # Generic fallback
    # ---------------------------------------

    answer_lines = []

    for row in results:

        answer_lines.append(
            str(row)
        )

    return "\n".join(answer_lines)


def call_qwen(question):
    """
    Make the ONE and ONLY Qwen call.
    """

    prompt = f"""
You are the routing and planning component of an Academic Helpdesk Agent for IIT Jodhpur.

You must classify the user's question into exactly ONE of these routes:

1. POLICY
2. SCHEDULE
3. INSTRUCTOR
4. EMAIL
5. UNKNOWN

Your job is ONLY to classify the request and, where required,
generate SQL or an email draft.

Do NOT answer the user's question yourself.

--------------------------------------------------
DATABASE SCHEMAS
--------------------------------------------------

Table: courses

Columns:
- "Batch"
- "Course Code"
- "Course Name"
- "L-T-P"
- "Credits"
- "Slot"
- "Instructor(s)"

Table: faculty

Columns:
- "instructor"
- "email"

The database is SQLite.

--------------------------------------------------
ROUTE RULES
--------------------------------------------------

POLICY:
Use POLICY for questions about:

- academic rules
- attendance
- examinations
- credits
- curriculum requirements
- academic regulations
- degree requirements
- academic calendar
- academic policies

Return exactly:

POLICY
<full user question>

--------------------------------------------------

SCHEDULE:
Use SCHEDULE for questions asking about:

- course slot
- course timing
- when a course is offered
- which courses are offered
- timetable-related course information

You MUST generate a valid SQLite SELECT query.

Return exactly:

SCHEDULE
SQL:
<SQL query>

Rules:

- Only SELECT queries are allowed.
- Use only the tables and columns given above.
- Do not invent columns.
- Do not use INSERT, UPDATE, DELETE, DROP, ALTER, CREATE, PRAGMA, ATTACH, or other commands.

Example:

User:
What is the slot for Autonomous Systems?

Return:

SCHEDULE
SQL:
SELECT "Course Code", "Course Name", "Slot"
FROM courses
WHERE LOWER("Course Name") LIKE '%autonomous systems%';

--------------------------------------------------

INSTRUCTOR:
Use INSTRUCTOR when the user wants:

- instructor of a course
- instructor name
- instructor email
- faculty information associated with a course

You MUST generate a valid SQLite SELECT query.

Return exactly:

INSTRUCTOR
SQL:
<SQL query>

Rules:

- Only SELECT queries are allowed.
- Use only the tables and columns given above.
- Do not invent columns.
- Do not use INSERT, UPDATE, DELETE, DROP, ALTER, CREATE, PRAGMA, ATTACH, or other commands.

Examples:

User:
Who teaches CSL7350?

Return:

INSTRUCTOR
SQL:
SELECT "Course Code", "Course Name", "Instructor(s)"
FROM courses
WHERE LOWER("Course Code") = 'csl7350';

User:
What is Navchetan Awasthi's email?

Return:

INSTRUCTOR
SQL:
SELECT instructor, email
FROM faculty
WHERE LOWER(instructor) LIKE '%navchetan awasthi%';

--------------------------------------------------

EMAIL:
Use EMAIL when the user wants an email drafted.

Examples:

- Draft an email to my CSL7350 instructor.
- Write an email to the instructor of Autonomous Systems.
- Draft a leave email to Navchetan Awasthi.

For EMAIL, you MUST identify the instructor using ONE of:

- course code
- course name
- instructor name

The identifier is MANDATORY.

You MUST return exactly this structure:

EMAIL
IDENTIFIER: <course code OR course name OR instructor name>
DRAFT:
<complete email>

IMPORTANT:

If the user says:

"Draft an email to my CSL7350 instructor..."

you MUST return:

EMAIL
IDENTIFIER: CSL7350
DRAFT:
...

Do NOT leave IDENTIFIER empty.

Do NOT invent information that the user did not provide.

For example, if the user says:

"Draft an email to my CSL7350 instructor asking for leave because I was sick for two days."

You may write a draft such as:

EMAIL
IDENTIFIER: CSL7350
DRAFT:
Subject: Request for Leave

Dear [INSTRUCTOR_NAME],

I was sick for two days and would like to request leave for the same period. I would be grateful if you could kindly consider my request.

Thank you.

Regards,
[YOUR_NAME]

Do NOT invent:
- dates
- medical conditions
- hospital visits
- documents
- approvals
- permissions
- assignments
- exam details
- any other facts not provided by the user

Keep placeholders such as [INSTRUCTOR_NAME] and [INSTRUCTOR_EMAIL] where appropriate.

--------------------------------------------------

UNKNOWN:
Use UNKNOWN for questions outside the academic helpdesk scope.

Examples:

- Who won yesterday's cricket match?
- What is the weather?
- Where is the dining hall?
- Tell me a joke.

Return exactly:

UNKNOWN
<full user question>

--------------------------------------------------

IMPORTANT OUTPUT RULES
--------------------------------------------------

Return ONLY one of the five formats.

Do not add explanations before the route.

Do not add explanations after the route.

The route must be exactly one of:

POLICY
SCHEDULE
INSTRUCTOR
EMAIL
UNKNOWN

--------------------------------------------------

USER QUESTION
--------------------------------------------------

{question}
"""

    response = ollama.chat(
        model=MODEL_NAME,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    response_text = response["message"]["content"].strip()

    print("\nRAW QWEN RESPONSE:")
    print(response_text)

    return response_text


def parse_qwen_response(response_text):
    """
    Parse Qwen's structured response.
    """

    lines = response_text.splitlines()

    route = ""
    sql_lines = []

    identifier = ""
    draft_lines = []

    inside_sql = False
    inside_draft = False

    for line in lines:

        stripped_line = line.strip()

        # -----------------------------
        # ROUTE
        # -----------------------------

        if not route and stripped_line.upper() in [
            "POLICY",
            "SCHEDULE",
            "INSTRUCTOR",
            "EMAIL",
            "UNKNOWN"
        ]:
            route = stripped_line.upper()
            continue

        # -----------------------------
        # IDENTIFIER
        # -----------------------------

        if stripped_line.upper().startswith("IDENTIFIER:"):

            identifier = stripped_line[
                len("IDENTIFIER:"):
            ].strip()

            continue

        # -----------------------------
        # SQL
        # -----------------------------

        if stripped_line.upper() == "SQL:":
            inside_sql = True
            inside_draft = False
            continue

        # -----------------------------
        # DRAFT
        # -----------------------------

        if stripped_line.upper() == "DRAFT:":
            inside_draft = True
            inside_sql = False
            continue

        # -----------------------------
        # SQL CONTENT
        # -----------------------------

        if inside_sql:
            sql_lines.append(line)

        # -----------------------------
        # EMAIL DRAFT CONTENT
        # -----------------------------

        elif inside_draft:
            draft_lines.append(line)

    sql_query = "\n".join(sql_lines).strip()
    draft = "\n".join(draft_lines).strip()

    return {
        "route": route,
        "sql": sql_query,
        "identifier": identifier,
        "draft": draft
    }


def handle_question(question):

    print("\nQUESTION:")
    print(question)

    # ---------------------------------------
    # ONE AND ONLY QWEN CALL
    # ---------------------------------------

    response_text = call_qwen(question)

    parsed = parse_qwen_response(response_text)

    route = parsed["route"]
    sql_query = parsed["sql"]
    identifier = parsed["identifier"]
    draft = parsed["draft"]

    print("\nROUTE SELECTED:")
    print(route)

    # =======================================
    # POLICY
    # =======================================

    if route == "POLICY":

        return check_policy(question)

    # =======================================
    # SCHEDULE
    # =======================================

    elif route == "SCHEDULE":

        print("\nGENERATED SQL:")
        print(sql_query)

        if not sql_query:
            return "I could not generate a valid database query for this question."

        result = execute_sql(sql_query)

        print("\nSQL RESULT:")
        print(result)

        if not result["success"]:
            return (
                "I could not retrieve the requested schedule information "
                "because the database query failed."
            )

        if not result["results"]:
            return "I could not find matching course information."

        return format_sql_results(
            result["results"],
            "SCHEDULE"
        )

    # =======================================
    # INSTRUCTOR
    # =======================================

    elif route == "INSTRUCTOR":

        print("\nGENERATED SQL:")
        print(sql_query)

        if not sql_query:
            return "I could not generate a valid database query for this question."

        result = execute_sql(sql_query)

        print("\nSQL RESULT:")
        print(result)

        if not result["success"]:
            return (
                "I could not retrieve the requested instructor information "
                "because the database query failed."
            )

        if not result["results"]:
            return "I could not find matching instructor information."

        return format_sql_results(
            result["results"],
            "INSTRUCTOR"
        )

    # =======================================
    # EMAIL
    # =======================================

    elif route == "EMAIL":

        print("\nINSTRUCTOR LOOKUP IDENTIFIER:")
        print(identifier)

        # -----------------------------------
        # Identifier validation
        # -----------------------------------

        if not identifier:
            return (
                "I could not determine which instructor the email "
                "should be addressed to."
            )

        # -----------------------------------
        # Deterministic Python lookup
        # -----------------------------------

        instructor_results = lookup_instructor(identifier)

        if not instructor_results:

            return (
                "I could not find the instructor associated with "
                f"'{identifier}'."
            )

        instructor = instructor_results[0]

        # -----------------------------------
        # Safely retrieve values
        # -----------------------------------

        instructor_name = instructor.get(
            "Instructor",
            ""
        )

        instructor_email = instructor.get(
            "Email",
            ""
        )

        # -----------------------------------
        # Protect against pandas NaN / float
        # -----------------------------------

        if not isinstance(instructor_name, str):
            instructor_name = ""

        if not isinstance(instructor_email, str):
            instructor_email = ""

        # -----------------------------------
        # Replace placeholders
        # -----------------------------------

        final_email = draft

        final_email = final_email.replace(
            "[INSTRUCTOR_NAME]",
            instructor_name
        )

        final_email = final_email.replace(
            "[INSTRUCTOR_EMAIL]",
            instructor_email
        )

        # -----------------------------------
        # If draft itself is missing
        # -----------------------------------

        if not final_email.strip():

            return (
                "I could not generate the email draft."
            )

        return final_email

    # =======================================
    # UNKNOWN
    # =======================================

    elif route == "UNKNOWN":

        return (
            "Sorry, I can only help with academic questions "
            "related to IIT Jodhpur."
        )

    # =======================================
    # INVALID ROUTE
    # =======================================

    else:

        return (
            "I could not determine how to handle this question."
        )


if __name__ == "__main__":

    question = input("\nEnter your question: ")

    answer = handle_question(question)

    print("\nFINAL ANSWER:")
    print(answer)
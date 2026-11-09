import ollama


def draft_email(
    course_code,
    instructor_name,
    requirement
):
    """
    Draft a professional academic email based on
    the student's requirement.

    The requirement can describe any academic request.
    """

    prompt = f"""
You are an academic email drafting assistant.

Draft a concise and professional email to a course instructor.

Course code: {course_code}
Instructor: {instructor_name}

Student's requirement:
{requirement}

Requirements:

1. Create a suitable subject line.
2. Address the instructor professionally.
3. Clearly explain the student's requirement.
4. Include only information provided by the student.
5. Do not invent medical details, dates, reasons,
   permissions, or other facts.
6. If the student is requesting something, clearly
   phrase it as a request.
7. Do not claim that the request has already been approved.
8. Keep the email polite and reasonably concise.
9. End with an appropriate closing.
10. This is only a draft. Do not send the email.

Return only the email draft.
"""

    response = ollama.chat(
        model="qwen3:8b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response["message"]["content"]


if __name__ == "__main__":

    email = draft_email(
        course_code="CSL7350",
        instructor_name="Navchetan Awasthi",
        requirement="""
I was unwell and could not attend the course for
two days. I want to request leave for those days.
"""
    )

    print("\nEMAIL DRAFT:")
    print("-----------------------------")
    print(email)
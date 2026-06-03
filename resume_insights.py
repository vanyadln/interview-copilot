def get_resume_insights(text):

    skills = []

    keywords = [
        "Python",
        "C++",
        "Java",
        "SQL",
        "Machine Learning",
        "Deep Learning",
        "Pandas",
        "NumPy",
        "TensorFlow",
        "PyTorch",
        "LeetCode"
    ]

    lower_text = text.lower()

    for skill in keywords:
        if skill.lower() in lower_text:
            skills.append(skill)

    return skills

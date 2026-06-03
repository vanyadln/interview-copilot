import streamlit as st
import json

st.set_page_config(page_title="Interview Summary")

st.title("Interview Summary")

try:

    with open("results.json", "r") as f:
        results = json.load(f)

    answered = 0

    for item in results:

        if item["answer"].strip():
            answered += 1

    total = len(results)

    score = int((answered / total) * 100)

    st.metric(
        "Completion Score",
        f"{score}%"
    )

    st.metric(
        "Questions Answered",
        f"{answered}/{total}"
    )

    st.subheader("Interview Review")

    for item in results:

        st.write("Question:")
        st.write(item["question"])

        st.write("Answer:")
        st.write(item["answer"])

        st.divider()

except:

    st.error(
        "No interview results found."
    )
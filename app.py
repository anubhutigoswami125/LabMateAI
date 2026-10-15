import os
from datetime import date

import streamlit as st

try:
    from groq import Groq
except ImportError:
    Groq = None


st.set_page_config(
    page_title="LabMateAI",
    page_icon="🧪",
    layout="wide",
)

st.title("🧪 LabMateAI")
st.caption("Your AI lab companion for biotechnology learning, calculations, and report drafting.")
st.warning(
    "Educational support only. Verify all protocols, calculations, and interpretations with "
    "your instructor and validated laboratory procedures. Do not use generated content as a "
    "substitute for institutional safety guidance."
)


def get_api_key():
    """Read the Groq key from Streamlit secrets or the environment."""
    try:
        secret_key = st.secrets.get("GROQ_API_KEY", "")
    except Exception:
        secret_key = ""
    return secret_key or os.getenv("GROQ_API_KEY", "")


def ask_groq(messages, temperature=0.3, max_tokens=1800):
    if Groq is None:
        raise RuntimeError("The Groq package is not installed. Run: pip install -r requirements.txt")
    api_key = get_api_key()
    if not api_key:
        raise RuntimeError(
            "Groq API key not found. Add GROQ_API_KEY to your environment or Streamlit secrets."
        )
    client = Groq(api_key=api_key)
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content or "No response was returned."


chat_tab, pcr_tab, report_tab, about_tab = st.tabs(
    ["Lab Assistant", "PCR Calculator", "Report Builder", "About"]
)

with chat_tab:
    st.subheader("Ask a biotechnology question")
    if "labmate_messages" not in st.session_state:
        st.session_state.labmate_messages = [
            {
                "role": "assistant",
                "content": "Hi! Ask me about microbiology, genetics, biochemistry, lab concepts, or data interpretation.",
            }
        ]

    for message in st.session_state.labmate_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    prompt = st.chat_input("Ask a lab or biotechnology question…")
    if prompt:
        st.session_state.labmate_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            with st.spinner("Thinking…"):
                try:
                    system_message = {
                        "role": "system",
                        "content": (
                            "You are LabMateAI, a careful biotechnology learning assistant. "
                            "Explain concepts clearly, show assumptions in calculations, distinguish "
                            "established evidence from uncertainty, and encourage users to follow "
                            "approved institutional protocols. Never invent experimental results. "
                            "Do not present yourself as a substitute for a qualified supervisor."
                        ),
                    }
                    answer = ask_groq(
                        [system_message] + st.session_state.labmate_messages[-12:]
                    )
                    st.markdown(answer)
                    st.session_state.labmate_messages.append(
                        {"role": "assistant", "content": answer}
                    )
                except Exception as exc:
                    error_text = f"Could not get an AI response: {exc}"
                    st.error(error_text)
                    st.session_state.labmate_messages.pop()
    if st.button("Clear chat", key="clear_chat"):
        st.session_state.labmate_messages = [
            {
                "role": "assistant",
                "content": "Chat cleared. What biotechnology topic can I help you with?",
            }
        ]
        st.rerun()

with pcr_tab:
    st.subheader("PCR reaction-volume calculator")
    st.write("Calculate master-mix volumes for a reaction setup. Enter volumes from your approved protocol.")
    col1, col2 = st.columns(2)
    with col1:
        reaction_count = st.number_input("Number of reactions", min_value=1, max_value=384, value=10, step=1)
        excess_percent = st.number_input("Extra volume (%)", min_value=0.0, max_value=50.0, value=10.0, step=1.0)
        reaction_volume = st.number_input("Final volume per reaction (µL)", min_value=1.0, max_value=200.0, value=25.0, step=0.5)
    with col2:
        water = st.number_input("Water per reaction (µL)", min_value=0.0, value=15.0, step=0.5)
        buffer = st.number_input("Buffer per reaction (µL)", min_value=0.0, value=2.5, step=0.5)
        primers = st.number_input("Primer mix per reaction (µL)", min_value=0.0, value=2.0, step=0.5)
        polymerase = st.number_input("Polymerase per reaction (µL)", min_value=0.0, value=0.5, step=0.1)
        dntps = st.number_input("dNTP mix per reaction (µL)", min_value=0.0, value=0.5, step=0.1)

    template = reaction_volume - (water + buffer + primers + polymerase + dntps)
    if template < -1e-9:
        st.error("The entered reagent volumes exceed the final reaction volume. Adjust the inputs.")
    else:
        st.metric("Calculated template volume per reaction (µL)", f"{template:.2f}")
        factor = reaction_count * (1 + excess_percent / 100)
        ingredients = [
            ("Water", water),
            ("Buffer", buffer),
            ("Primer mix", primers),
            ("Polymerase", polymerase),
            ("dNTP mix", dntps),
            ("Template", template),
        ]
        rows = [
            {"Component": name, "Per reaction (µL)": round(vol, 3), f"Total for {reaction_count} + {excess_percent:g}% excess (µL)": round(vol * factor, 3)}
            for name, vol in ingredients
        ]
        st.dataframe(rows, use_container_width=True, hide_index=True)
        st.caption("This calculator performs volume arithmetic only; it does not validate whether the recipe is appropriate for a specific assay.")
        csv_text = "Component,Per reaction (uL),Total including excess (uL)\n"
        csv_text += "\n".join(
            f"{name},{vol:.3f},{vol * factor:.3f}" for name, vol in ingredients
        )
        st.download_button(
            "Download PCR mix as CSV",
            data=csv_text,
            file_name="labmateai_pcr_mastermix.csv",
            mime="text/csv",
        )

with report_tab:
    st.subheader("Laboratory report draft builder")
    st.write("Create a structured first draft from your own notes. Check every claim and replace placeholders before submission.")
    report_title = st.text_input("Experiment / report title", placeholder="e.g., Effect of temperature on enzyme activity")
    objective = st.text_area("Aim / objective", height=80)
    background = st.text_area("Principle / background notes", height=120)
    methods = st.text_area("Method summary (your notes only)", height=120)
    observations = st.text_area("Observations / data", height=120, placeholder="Paste your actual observations; do not invent data.")
    conclusion_notes = st.text_area("Your interpretation / conclusion notes", height=80)
    if st.button("Generate report draft", type="primary"):
        if not report_title.strip() or not objective.strip():
            st.error("Enter at least a title and an objective.")
        else:
            with st.spinner("Drafting your report…"):
                prompt = f"""Create an editable educational laboratory-report draft using only the notes below.
Do not invent observations, numerical results, citations, or experimental steps.
If information is missing, use a clearly labelled [ADD INFORMATION] placeholder.
Keep interpretations proportional to the evidence and include a short limitations section.
Use headings: Title, Aim, Principle, Materials and Methods, Results/Observations, Discussion,
Limitations, Conclusion, and References to Verify. For references, suggest search terms rather
than fabricating bibliographic citations.

Title: {report_title}
Aim: {objective}
Principle/background notes: {background or '[Not provided]'}
Method summary: {methods or '[Not provided]'}
Actual observations/data: {observations or '[Not provided]'}
User's interpretation notes: {conclusion_notes or '[Not provided]'}
"""
                try:
                    draft = ask_groq(
                        [
                            {
                                "role": "system",
                                "content": "You are a careful scientific writing assistant. Never fabricate data or references.",
                            },
                            {"role": "user", "content": prompt},
                        ],
                        temperature=0.2,
                        max_tokens=2400,
                    )
                    st.session_state.report_draft = draft
                except Exception as exc:
                    st.error(f"Could not generate the draft: {exc}")
    if st.session_state.get("report_draft"):
        edited_draft = st.text_area(
            "Review and edit the generated draft",
            value=st.session_state.report_draft,
            height=420,
            key="editable_report_draft",
        )
        st.download_button(
            "Download report draft (.md)",
            data=edited_draft,
            file_name="labmateai_lab_report.md",
            mime="text/markdown",
        )

with about_tab:
    st.subheader("About this project")
    st.markdown(
        """
        **LabMateAI** is a student-built prototype exploring how generative AI can support
        biotechnology learning and common lab-preparation tasks.

        **Current modules**
        - Biotechnology Q&A powered by Groq and Llama 3.3
        - A configurable PCR reaction-volume calculator with CSV export
        - A laboratory-report draft builder that uses user-provided notes

        **Technology:** Python · Streamlit · Groq API

        **Important:** This is an educational prototype, not a validated laboratory instrument.
        Never submit confidential, personal, patient, or unpublished sensitive data to an AI service.
        """
    )
    st.caption(f"Prototype · {date.today().year}")

import os

import requests
import streamlit as st


API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")


def init_state() -> None:
    st.session_state.setdefault("thread_id", None)
    st.session_state.setdefault("step", 1)
    st.session_state.setdefault("analysis", None)
    st.session_state.setdefault("modern_code", None)
    st.session_state.setdefault("changes_made", [])
    st.session_state.setdefault("migration_report", None)


def post_api(path: str, payload: dict) -> dict:
    response = requests.post(f"{API_BASE_URL}{path}", json=payload, timeout=120)
    response.raise_for_status()
    return response.json()


def risk_delta_color(risk_level: str) -> str:
    colors = {
        "CRITICAL": "red",
        "HIGH": "orange",
        "MEDIUM": "yellow",
        "LOW": "green",
    }
    return colors.get(risk_level, "gray")


st.set_page_config(page_title="Code Modernisation Assistant", layout="centered")
st.markdown(
    """
    <style>
    .block-container {
        max-width: 920px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }
    div[data-testid="stTextArea"] textarea,
    div[data-testid="stTextInput"] input {
        background: rgba(255, 255, 255, 0.96);
        border: 1px solid #d7dce2;
        border-radius: 8px;
        color: #111827;
        caret-color: #111827;
    }
    div[data-testid="stTextArea"] textarea::placeholder,
    div[data-testid="stTextInput"] input::placeholder {
        color: #6b7280;
        opacity: 1;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

init_state()

st.title("Code Modernisation Assistant")

code = st.text_area("Paste your legacy code", height=300, key="code_input")
language = st.selectbox("Language", ["VB6", "ClassicASP", "JavaEE", "COBOL"])
target_framework = st.selectbox(
    "Target framework",
    ["Python/FastAPI", "C#/.NET 8", "Node.js/Express", "Java/Spring Boot"],
)

if st.button("Analyse Code"):
    try:
        with st.spinner("Analysing..."):
            result = post_api(
                "/analyse",
                {
                    "code": code,
                    "language": language,
                    "target_framework": target_framework,
                },
            )
        st.session_state.analysis = result
        st.session_state.thread_id = result["thread_id"]
        st.session_state.step = 2
    except requests.RequestException as e:
        st.error(f"Analysis failed: {e}")
    except KeyError as e:
        st.error(f"Unexpected analysis response: missing {e}")

if st.session_state.step >= 2 and st.session_state.analysis:
    analysis = st.session_state.analysis
    risk_report = analysis.get("risk_report") or {}
    risk_level = risk_report.get("risk_level", "UNKNOWN")

    with st.expander("Code Analysis", expanded=True):
        st.write(analysis.get("summary", ""))
        st.code(analysis.get("identified_patterns", []))
        st.metric("Complexity Score", analysis.get("complexity_score", 0.0))

    with st.expander("Risk Assessment", expanded=True):
        st.metric(
            "Risk Level",
            risk_level,
            delta=risk_delta_color(risk_level),
            delta_color="off",
        )
        for factor in risk_report.get("risk_factors", []):
            st.write(f"- {factor}")

    with st.expander("Raw JSON"):
        st.json(analysis)

    approve_col, reject_col = st.columns(2)
    with approve_col:
        if st.button("Approve & Generate Modern Code", use_container_width=True):
            try:
                with st.spinner("Generating..."):
                    result = post_api(
                        "/generate",
                        {
                            "thread_id": st.session_state.thread_id,
                            "approved": True,
                        },
                    )
                st.session_state.modern_code = result.get("modern_code")
                st.session_state.changes_made = result.get("changes_made") or []
                st.session_state.step = 3
            except requests.RequestException as e:
                st.error(f"Generation failed: {e}")

    with reject_col:
        if st.button("Reject", use_container_width=True):
            try:
                with st.spinner("Generating..."):
                    post_api(
                        "/generate",
                        {
                            "thread_id": st.session_state.thread_id,
                            "approved": False,
                        },
                    )
                st.session_state.thread_id = None
                st.session_state.step = 1
                st.session_state.analysis = None
                st.session_state.modern_code = None
                st.session_state.changes_made = []
                st.session_state.migration_report = None
                st.rerun()
            except requests.RequestException as e:
                st.error(f"Reject failed: {e}")

if st.session_state.step >= 3 and st.session_state.modern_code:
    st.caption("Switch language tab if not Python")
    st.code(st.session_state.modern_code, language="python")

    if st.session_state.changes_made:
        st.write("Changes made:")
        for change in st.session_state.changes_made:
            st.write(f"- {change}")

    include_checklist = st.checkbox("Include migration checklist in report")
    if st.button("Build Migration Report"):
        try:
            with st.spinner("Building report..."):
                result = post_api(
                    "/checklist",
                    {
                        "thread_id": st.session_state.thread_id,
                        "request_checklist": include_checklist,
                    },
                )
            report = result.get("migration_report", "")
            st.session_state.migration_report = report
            st.markdown(report)
            st.download_button(
                "Download migration_report.md",
                data=report,
                file_name="migration_report.md",
                mime="text/markdown",
            )
        except requests.RequestException as e:
            st.error(f"Report build failed: {e}")

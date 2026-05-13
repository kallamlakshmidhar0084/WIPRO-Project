import os
import time
from typing import Any

import requests
import streamlit as st


API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")


st.set_page_config(page_title="Code Modernisation Agent", page_icon="</>", layout="centered")

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
    .small-muted {
        color: #667085;
        font-size: 0.85rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def init_state() -> None:
    st.session_state.setdefault("messages", [])
    st.session_state.setdefault("snippet_id", None)
    st.session_state.setdefault("last_code", "")
    st.session_state.setdefault("last_query", "")


def request_api(method: str, path: str, **kwargs: Any) -> Any:
    url = f"{API_BASE_URL}{path}"
    response = requests.request(method, url, timeout=90, **kwargs)
    response.raise_for_status()
    return response.json()


def stream_status(lines: list[str]) -> None:
    placeholder = st.empty()
    rendered = ""
    for line in lines:
        rendered += f"- {line}\n"
        placeholder.markdown(rendered)
        time.sleep(0.15)


def add_message(role: str, content: str) -> None:
    st.session_state.messages.append({"role": role, "content": content})


def render_migration(data: dict[str, Any]) -> None:
    st.markdown(data["summary"])
    st.code(data["modernized_code"], language=data.get("language") or None)
    st.markdown("### Checklist")
    for item in data["checklist"]:
        st.markdown(f"- **{item['status']}**: {item['item']} - {item['notes']}")
    st.markdown("### Risks")
    for risk in data["risks"]:
        st.markdown(f"- **{risk['severity']}**: {risk['risk']} Mitigation: {risk['mitigation']}")


def render_patterns(data: dict[str, Any]) -> None:
    for pattern in data["patterns"]:
        st.markdown(f"### {pattern['name']}")
        st.markdown(pattern["description"])
        if pattern.get("example"):
            st.code(pattern["example"])
        if pattern.get("modern_alternative"):
            st.markdown(f"**Modern alternative:** {pattern['modern_alternative']}")


init_state()

st.title("AI Code Modernisation Agent")
st.caption("Analyse legacy code, detect migration risks, and generate a structured modernisation draft.")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

with st.container():
    code = st.text_area(
        "Code snippet",
        value=st.session_state.last_code,
        height=150,
        placeholder="Paste legacy code here...",
        label_visibility="collapsed",
    )
    query = st.text_input(
        "Optional query",
        value=st.session_state.last_query,
        placeholder="Optional: focus the analysis on security, Java 17 migration, performance...",
        label_visibility="collapsed",
    )

    col1, col2, col3 = st.columns([1, 1, 1])
    analyse_clicked = col1.button("Analyse", type="primary", use_container_width=True)
    migrate_clicked = col2.button(
        "Generate",
        disabled=st.session_state.snippet_id is None,
        use_container_width=True,
    )
    patterns_clicked = col3.button(
        "Get Patterns",
        disabled=st.session_state.snippet_id is None,
        use_container_width=True,
    )
    st.markdown(
        f'<p class="small-muted">Backend: {API_BASE_URL}</p>',
        unsafe_allow_html=True,
    )

if analyse_clicked:
    if not code.strip():
        st.error("Code snippet is required.")
    else:
        st.session_state.last_code = code
        st.session_state.last_query = query
        add_message("user", f"Please analyse this snippet.\n\n```text\n{code}\n```")
        with st.chat_message("assistant"):
            stream_status(["Validating input", "Sending to backend", "Agent analysing"])
            try:
                data = request_api("POST", "/analyse", json={"code": code, "query": query or None})
                st.session_state.snippet_id = data["snippet_id"]
                st.markdown(data["analysis"])
                add_message("assistant", data["analysis"])
            except requests.HTTPError as exc:
                st.error(f"Backend error: {exc.response.text}")
            except requests.RequestException as exc:
                st.error(f"Could not reach backend: {exc}")
        st.rerun()

if migrate_clicked and st.session_state.snippet_id:
    with st.chat_message("assistant"):
        stream_status(["Validating snippet", "Sending to backend", "Agent generating"])
        try:
            data = request_api("POST", "/generate")
            render_migration(data)
            add_message("assistant", f"Generated modernised code for snippet `{data['snippet_id']}`.")
        except requests.HTTPError as exc:
            st.error(f"Backend error: {exc.response.text}")
        except requests.RequestException as exc:
            st.error(f"Could not reach backend: {exc}")

if patterns_clicked:
    with st.chat_message("assistant"):
        stream_status(["Requesting anti-pattern catalogue", "Agent preparing patterns"])
        try:
            data = request_api("GET", "/patterns")
            render_patterns(data)
            add_message("assistant", "Loaded anti-pattern catalogue.")
        except requests.HTTPError as exc:
            st.error(f"Backend error: {exc.response.text}")
        except requests.RequestException as exc:
            st.error(f"Could not reach backend: {exc}")

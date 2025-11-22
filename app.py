import streamlit as st
import ollama
import json
import pandas as pd
import re
import logging
from datetime import datetime

# --- CONFIGURATION ---
MODEL_NAME = "qwen3-coder:30b"
MAX_INPUT_LENGTH = 10000  # Prevent abuse

# --- LOGGING SETUP ---
logging.basicConfig(
    filename='audit_trail.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

st.set_page_config(
    page_title="Sovereign GRC Auditor",
    page_icon="🛡️",
    layout="wide"
)

# --- HELPER FUNCTIONS ---
def extract_json(text):
    """
    Robust JSON extraction that handles nested objects.
    Finds the largest {...} block in the text.
    """
    try:
        # Try simple parsing first
        return json.loads(text)
    except json.JSONDecodeError:
        # Improved regex that handles nested braces
        # Matches outer {...} including nested structures
        json_pattern = r'\{(?:[^{}]|(?:\{(?:[^{}]|(?:\{[^{}]*\}))*\}))*\}'
        match = re.search(json_pattern, text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass
    return None

def sanitize_input(text):
    """
    Basic input sanitization to prevent injection attacks.
    Removes potentially dangerous characters while preserving audit text.
    """
    if not text or len(text) > MAX_INPUT_LENGTH:
        return None

    # Remove null bytes and control characters (except newlines/tabs)
    sanitized = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f]', '', text)

    return sanitized.strip()

def check_ollama_status():
    """
    Checks if Ollama service is running AND if the specific model is available.
    """
    try:
        models = ollama.list()
        # Check if our model exists in the list
        model_names = [model['model'] for model in models.get('models', [])]

        # Handle both exact match and tag variations
        model_available = any(
            MODEL_NAME in name or name.startswith(MODEL_NAME.split(':')[0])
            for name in model_names
        )

        return model_available
    except Exception as e:
        logging.error(f"Ollama status check failed: {e}")
        return False

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/security-checked.png", width=60)
    st.title("Private Auditor")

    # SERVICE HEALTH CHECK
    if check_ollama_status():
        st.success(f"🟢 System Online ({MODEL_NAME})")
    else:
        st.error("🔴 Ollama Offline or Model Missing")
        st.info(f"Please run:\n```\nollama serve\nollama pull {MODEL_NAME}\n```")
        st.stop()  # Stop execution if backend is down

    st.markdown("---")
    st.caption("🔒 Privacy Mode: Active (No Cloud)")
    st.caption(f"📊 Max Input: {MAX_INPUT_LENGTH} chars")

# --- MAIN UI ---
st.title("🛡️ Automated Risk & Compliance Mapper")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📝 Audit Findings Input")
    audit_input = st.text_area(
        "Raw Audit Notes:",
        height=300,
        placeholder="Paste interview notes, slack logs, or observation data here...",
        max_chars=MAX_INPUT_LENGTH
    )

    analyze_btn = st.button("🔍 Analyze Risks", type="primary")

# --- STATE MANAGEMENT (Persistence) ---
if "results" not in st.session_state:
    st.session_state.results = None

# --- LOGIC ---
if analyze_btn and audit_input:
    # Sanitize input first
    clean_input = sanitize_input(audit_input)

    if not clean_input:
        st.error("❌ Input validation failed. Please check your text and try again.")
        logging.warning("Input sanitization failed - empty or too long")
        st.stop()

    with col2:
        st.subheader("📊 Compliance Analysis")

        with st.spinner(f"🤖 Analyzing with {MODEL_NAME}..."):
            try:
                # Log the audit request (without full content for privacy)
                logging.info(f"Audit analysis started - Input length: {len(clean_input)} chars")

                system_prompt = """
                You are an expert GRC Automation Engine.
                Map the user's audit findings to ISO 27001:2022 controls.
                Output STRICT JSON only. No markdown. No chatter.
                Structure: {"risks": [{"description": "...", "iso_control": "...", "recommendation": "..."}]}
                """

                response = ollama.chat(model=MODEL_NAME, messages=[
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user', 'content': clean_input},
                ])

                raw_output = response['message']['content']

                # Robust Extraction
                data = extract_json(raw_output)

                if data:
                    # Normalize list/dict
                    risks = data.get("risks", data) if isinstance(data, dict) else data

                    # Validate risk structure
                    if isinstance(risks, list) and all(isinstance(r, dict) for r in risks):
                        # Save to session state (Persistence)
                        st.session_state.results = risks
                        logging.info(f"Analysis successful - {len(risks)} risks identified")
                    else:
                        st.error("❌ Invalid risk data structure")
                        logging.error("Risk validation failed - not a list of dicts")
                else:
                    st.error("❌ AI Output Error: Could not parse JSON.")
                    logging.error("JSON parsing failed")
                    with st.expander("Debug Raw Output"):
                        st.code(raw_output)

            except Exception as e:
                st.error(f"System Error: {str(e)}")
                logging.error(f"System error during analysis: {e}")

# --- RESULTS DISPLAY & EXPORT ---
if st.session_state.results:
    with col2:
        # Display Cards
        for idx, risk in enumerate(st.session_state.results, 1):
            # Safety check for keys
            desc = risk.get('description', 'Unknown')
            iso = risk.get('iso_control', 'General')
            rec = risk.get('recommendation', 'None')

            with st.expander(f"⚠️ {iso} - {desc[:40]}...", expanded=True):
                st.markdown(f"**Risk #{idx}:** {desc}")
                st.markdown(f"**Control:** `{iso}`")
                st.info(f"**Fix:** {rec}")

        # EXPORT TO CSV
        df = pd.DataFrame(st.session_state.results)
        csv = df.to_csv(index=False).encode('utf-8')

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        st.download_button(
            label="📥 Download Audit Report (CSV)",
            data=csv,
            file_name=f'audit_report_{timestamp}.csv',
            mime='text/csv',
        )

        logging.info(f"Report exported - {len(st.session_state.results)} risks")

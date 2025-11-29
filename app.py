import streamlit as st
import ollama
import json
import pandas as pd
import re
import logging
from datetime import datetime
import time
import rag_engine  # Import our new RAG module

# --- CONFIGURATION ---
MODEL_NAME = "llama3.2"
MAX_INPUT_LENGTH = 10000  # Prevent abuse
OLLAMA_MAX_RETRIES = 3  # Number of retry attempts

# --- CACHED INITIALIZATION ---
@st.cache_resource
def initialize_rag_engine():
    """
    Initialize and cache the RAG engine (ChromaDB collections).
    This runs once and is cached across all sessions for better performance.
    """
    rag_engine.load_crosswalk_db()
    return {
        'crosswalk': rag_engine.crosswalk_collection,
        'policy': rag_engine.policy_collection
    }

# Load RAG engine (cached)
rag_collections = initialize_rag_engine()

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

def ollama_chat_with_retry(model, messages, options=None, max_retries=OLLAMA_MAX_RETRIES):
    """
    Call Ollama chat with exponential backoff retry logic.

    Args:
        model (str): Model name
        messages (list): Chat messages
        options (dict): Ollama options (timeout, etc.)
        max_retries (int): Maximum retry attempts

    Returns:
        dict: Ollama response

    Raises:
        Exception: If all retries fail
    """
    for attempt in range(max_retries):
        try:
            response = ollama.chat(model=model, messages=messages, options=options)
            return response
        except Exception as e:
            if attempt == max_retries - 1:
                # Last attempt failed, re-raise
                logging.error(f"Ollama call failed after {max_retries} attempts: {e}")
                raise

            # Exponential backoff: 1s, 2s, 4s
            wait_time = 2 ** attempt
            logging.warning(f"Ollama call failed (attempt {attempt + 1}/{max_retries}), retrying in {wait_time}s: {e}")
            time.sleep(wait_time)

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

    # --- RAG: POLICY UPLOAD ---
    st.markdown("---")
    st.subheader("📚 Knowledge Base")
    uploaded_file = st.file_uploader("Upload Policy (PDF)", type="pdf")
    
    if uploaded_file:
        # Save temp file
        temp_path = f"temp_{uploaded_file.name}"
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        with st.spinner("🧠 Ingesting Policy..."):
            success, msg = rag_engine.ingest_policy(temp_path)
            if success:
                st.success("Policy Learned!")
            else:
                st.error(f"Error: {msg}")
        
        # Cleanup
        import os
        if os.path.exists(temp_path):
            os.remove(temp_path)

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

                # --- STEP 1: GET DATABASE MAPPINGS (ELIMINATES HALLUCINATIONS) ---
                db_mappings = rag_engine.get_framework_mappings(clean_input)
                
                # --- STEP 2: RETRIEVE POLICY CONTEXT ---
                context = rag_engine.query_policy(clean_input)
                context_text = f"\n\nRELEVANT COMPANY POLICY:\n{context}" if context else ""

                # --- STEP 3: BUILD PROMPT BASED ON DATABASE RESULTS ---
                if db_mappings:
                    # Database found a match - use verified control IDs
                    st.info(f"✅ Matched to risk pattern: {db_mappings.get('pattern_name', 'Unknown')}")
                    
                    system_prompt = f"""
                    You are a GRC compliance analyst.
                    
                    The finding has been mapped to these verified controls from our database:
                    - ISO 27001: {db_mappings.get('iso_27001', 'N/A')}
                    - SOC 2: {db_mappings.get('soc_2', 'N/A')}
                    - HIPAA: {db_mappings.get('hipaa', 'N/A')}
                    - NIST CSF: {db_mappings.get('nist_csf', 'N/A')}
                    
                    {context_text}
                    
                    YOUR TASK:
                    1. Write a clear, professional risk description (2-3 sentences)
                    2. Write an actionable remediation recommendation (specific steps)
                    3. If company policy is provided above, reference it in your recommendation
                    
                    Output STRICT JSON only. No markdown. No explanation.
                    Structure: 
                    {{
                        "risks": [
                            {{
                                "description": "Clear description of the security risk",
                                "recommendation": "Specific remediation steps",
                                "mappings": {{
                                    "iso_27001": "{db_mappings.get('iso_27001', 'N/A')}",
                                    "soc_2": "{db_mappings.get('soc_2', 'N/A')}",
                                    "hipaa": "{db_mappings.get('hipaa', 'N/A')}",
                                    "nist_csf": "{db_mappings.get('nist_csf', 'N/A')}"
                                }}
                            }}
                        ]
                    }}
                    """
                else:
                    # No database match - fallback to LLM (but warn user)
                    st.warning("⚠️ No exact database match found. Using AI analysis (may be less accurate).")
                    
                    system_prompt = f"""
                    You are an expert GRC Automation Engine.
                    Map the user's audit findings to the following frameworks:
                    1. ISO 27001:2022
                    2. SOC 2 Type II
                    3. HIPAA Security Rule
                    4. NIST CSF 2.0
                    
                    {context_text}
                    
                    If the company policy is provided above, YOU MUST PRIORITIZE IT over general standards.
                    Output STRICT JSON only. No markdown. No chatter.
                    Structure: 
                    {{
                        "risks": [
                            {{
                                "description": "...", 
                                "recommendation": "...",
                                "mappings": {{
                                    "iso_27001": "Control ID (e.g. A.9.4.1)",
                                    "soc_2": "Criteria ID (e.g. CC6.1)",
                                    "hipaa": "Rule ID (e.g. 164.312(a)(1))",
                                    "nist_csf": "Function ID (e.g. PR.AC-7)"
                                }}
                            }}
                        ]
                    }}
                    """

                # --- STEP 4: CALL LLM (with retry logic) ---
                response = ollama_chat_with_retry(
                    model=MODEL_NAME,
                    messages=[
                        {'role': 'system', 'content': system_prompt},
                        {'role': 'user', 'content': clean_input},
                    ],
                    options={'timeout': 120.0}  # 2 minute timeout
                )

                raw_output = response['message']['content']

                # --- STEP 5: EXTRACT AND VALIDATE JSON ---
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

            except TimeoutError:
                st.error("⏱️ Request timed out. The model may be overloaded. Please try again.")
                logging.error("Ollama API request timed out")
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
            rec = risk.get('recommendation', 'None')
            mappings = risk.get('mappings', {})

            with st.expander(f"⚠️ Risk #{idx} - {desc[:40]}...", expanded=True):
                st.markdown(f"**Description:** {desc}")
                
                # Multi-Framework Tabs
                tab1, tab2, tab3, tab4 = st.tabs(["ISO 27001", "SOC 2", "HIPAA", "NIST CSF"])
                
                with tab1:
                    st.info(f"**ISO Control:** `{mappings.get('iso_27001', 'N/A')}`")
                with tab2:
                    st.info(f"**SOC 2 Criteria:** `{mappings.get('soc_2', 'N/A')}`")
                with tab3:
                    st.info(f"**HIPAA Rule:** `{mappings.get('hipaa', 'N/A')}`")
                with tab4:
                    st.info(f"**NIST Function:** `{mappings.get('nist_csf', 'N/A')}`")

                st.success(f"**Recommendation:** {rec}")

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
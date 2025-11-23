# 📖 Line-by-Line Explanation: app.py

## **Lines 1-7: Import Libraries**

```python
import streamlit as st      # Line 1
import ollama               # Line 2
import json                 # Line 3
import pandas as pd         # Line 4
import re                   # Line 5
import logging              # Line 6
from datetime import datetime  # Line 7
```

### **What Each Does:**

| Line | Library | Purpose | Output Example |
|------|---------|---------|----------------|
| 1 | `streamlit` | Creates web UI (buttons, text boxes) | 🖥️ Browser interface at localhost:8501 |
| 2 | `ollama` | Talks to local LLM server | 🤖 Sends "Map risks..." → Gets JSON back |
| 3 | `json` | Parses text into Python objects | `'{"key":"val"}'` → `{"key":"val"}` |
| 4 | `pandas` | Creates spreadsheet-like data | 📊 Converts list → CSV file |
| 5 | `re` | Pattern matching (regex) | Finds `{...}` in messy AI text |
| 6 | `logging` | Writes to audit_trail.log | `2025-11-22 14:30 - Analysis started` |
| 7 | `datetime` | Gets current time | `20251122_143015` for filename |

---

## **Lines 9-11: Configuration Constants**

```python
MODEL_NAME = "qwen3-coder:30b"  # Line 10
MAX_INPUT_LENGTH = 10000        # Line 11
```

### **What This Does:**

**Line 10:** Tells the code which AI model to use.
- **Output:** When app loads, sidebar shows "🟢 System Online (qwen3-coder:30b)"

**Line 11:** Maximum characters allowed in input box.
- **Output:** If user pastes 15,000 chars, they get error: "❌ Input validation failed"

---

## **Lines 14-18: Logging Configuration**

```python
logging.basicConfig(
    filename='audit_trail.log',     # Line 15
    level=logging.INFO,              # Line 16
    format='%(asctime)s - %(levelname)s - %(message)s'  # Line 17
)
```

### **What This Does:**

Creates a file called `audit_trail.log` in your project folder.

**Output in audit_trail.log:**
```
2025-11-22 09:49:15 - INFO - Audit analysis started - Input length: 234 chars
2025-11-22 09:49:18 - INFO - Analysis successful - 3 risks identified
2025-11-22 09:49:20 - INFO - Report exported - 3 risks
```

**Line 16:** `level=logging.INFO` means "log everything except debug messages"
- Logs: INFO, WARNING, ERROR
- Doesn't log: DEBUG

**Line 17:** Format template
- `%(asctime)s` → Current timestamp
- `%(levelname)s` → INFO/ERROR/WARNING
- `%(message)s` → The actual message

---

## **Lines 20-24: Page Configuration**

```python
st.set_page_config(
    page_title="Sovereign GRC Auditor",  # Line 21
    page_icon="🛡️",                      # Line 22
    layout="wide"                        # Line 23
)
```

### **What This Does:**

**Visual Output in Browser:**

**Line 21:** Sets browser tab title
```
Browser Tab: 🛡️ Sovereign GRC Auditor
```

**Line 22:** Sets browser tab icon (emoji)
```
Tab Icon: 🛡️
```

**Line 23:** Makes content use full screen width
```
WITHOUT layout="wide":
┌──────────────────────────────────────┐
│    [narrow content in center]        │
└──────────────────────────────────────┘

WITH layout="wide":
┌──────────────────────────────────────┐
│[full width content edge-to-edge]    │
└──────────────────────────────────────┘
```

---

## **Lines 27-45: Helper Function #1 - extract_json()**

```python
def extract_json(text):                    # Line 27
    """Robust JSON extraction..."""       # Lines 28-31
    try:                                   # Line 32
        return json.loads(text)            # Line 34
    except json.JSONDecodeError:           # Line 35
        json_pattern = r'\{(?:[^{}]|(?:\{(?:[^{}]|(?:\{[^{}]*\}))*\}))*\}'  # Line 38
        match = re.search(json_pattern, text, re.DOTALL)  # Line 39
        if match:                          # Line 40
            try:                           # Line 41
                return json.loads(match.group(0))  # Line 42
            except json.JSONDecodeError:   # Line 43
                pass                       # Line 44
    return None                            # Line 45
```

### **What Each Line Does:**

**Line 27:** Define function that takes AI text as input

**Line 34:** Try to parse text as JSON directly
- **Input:** `'{"risks": []}'`
- **Output:** `{"risks": []}`
- If successful, return immediately

**Line 35:** If parsing failed (AI added extra text)...

**Line 38:** Create pattern to find JSON block
- Regex that matches `{...}` including nested braces

**Line 39:** Search for JSON pattern in the text
- **Input:** `'Sure! Here is your JSON:\n{"risks":[]}\nHope this helps!'`
- **Output:** `match` object pointing to `{"risks":[]}`

**Line 42:** Extract just the JSON part and parse it
- `match.group(0)` → `{"risks":[]}`
- `json.loads(...)` → Python dictionary

**Line 45:** If nothing worked, return None
- Signals "AI didn't return valid JSON"

### **Visual Example:**

```
AI Response: "Here is the output:\n{\"risks\": [{\"desc\": \"Bad\"}]}\nDone!"
              ↓
         extract_json()
              ↓
         Line 34 fails (extra text)
              ↓
         Line 39 finds: {"risks": [{"desc": "Bad"}]}
              ↓
         Line 42 parses it
              ↓
         Returns: {"risks": [{"desc": "Bad"}]}
```

---

## **Lines 47-58: Helper Function #2 - sanitize_input()**

```python
def sanitize_input(text):                  # Line 47
    """Basic input sanitization..."""      # Lines 48-51
    if not text or len(text) > MAX_INPUT_LENGTH:  # Line 52
        return None                        # Line 53

    sanitized = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f]', '', text)  # Line 56
    return sanitized.strip()               # Line 58
```

### **What Each Line Does:**

**Line 52:** Check if text is empty or too long
- `not text` → Empty string check
- `len(text) > 10000` → Too long check
- **Output if true:** Function returns `None`

**Line 56:** Remove dangerous characters
- **Input:** `"Audit notes\x00\x1bHACKED"`
- `\x00` = Null byte (crashes parsers)
- `\x1b` = Escape code (terminal injection)
- **Output:** `"Audit notesHACKED"` (dangerous chars removed)

**Line 58:** Remove leading/trailing whitespace and return
- **Input:** `"  text  "`
- **Output:** `"text"`

### **Character Removal Details:**

```
REMOVES:
\x00 = Null byte
\x01-\x08 = Control chars
\x0b = Vertical tab
\x0c = Form feed
\x0e-\x1f = More control chars
\x7f = Delete

KEEPS:
\x09 = Tab (\t)
\x0a = Newline (\n)
\x0d = Carriage return (\r)
a-z, A-Z, 0-9, punctuation
```

---

## **Lines 60-78: Helper Function #3 - check_ollama_status()**

```python
def check_ollama_status():                 # Line 60
    """Checks if Ollama service is running..."""  # Lines 61-63
    try:                                   # Line 64
        models = ollama.list()             # Line 65
        model_names = [model['model'] for model in models.get('models', [])]  # Line 67

        model_available = any(             # Line 70
            MODEL_NAME in name or name.startswith(MODEL_NAME.split(':')[0])  # Line 71
            for name in model_names        # Line 72
        )

        return model_available             # Line 75
    except Exception as e:                 # Line 76
        logging.error(f"Ollama status check failed: {e}")  # Line 77
        return False                       # Line 78
```

### **What Each Line Does:**

**Line 65:** Ask Ollama "what models do you have?"
- **Output:**
```python
{
  'models': [
    {'model': 'qwen3-coder:30b', 'size': '18GB', ...},
    {'model': 'llama3.1:latest', 'size': '4GB', ...}
  ]
}
```

**Line 67:** Extract just the model names
- **Input:** Response from Line 65
- **Output:** `['qwen3-coder:30b', 'llama3.1:latest']`

**Line 70-72:** Check if our model exists
- **Logic:**
  - Check exact match: `"qwen3-coder:30b" in name`
  - OR check prefix: `name.startswith("qwen3-coder")`
- **Why?** Handles these variations:
  - `qwen3-coder:30b` ✅
  - `qwen3-coder:latest` ✅
  - `qwen3-coder:v2` ✅

**Line 75:** Return True if found, False if not

**Line 76-78:** If Ollama is offline (connection error)
- **Line 77:** Write to log: `"Ollama status check failed: [Errno 111] Connection refused"`
- **Line 78:** Return False

### **Visual Output in UI:**

```
If Line 75 returns True:
  Sidebar shows: 🟢 System Online (qwen3-coder:30b)

If Line 78 returns False:
  Sidebar shows: 🔴 Ollama Offline or Model Missing
                 Please run:
                 ollama serve
                 ollama pull qwen3-coder:30b
```

---

## **Lines 81-96: Sidebar UI**

```python
with st.sidebar:                           # Line 81
    st.image("https://...", width=60)      # Line 82
    st.title("Private Auditor")            # Line 83

    if check_ollama_status():              # Line 86
        st.success(f"🟢 System Online ({MODEL_NAME})")  # Line 87
    else:
        st.error("🔴 Ollama Offline or Model Missing")  # Line 89
        st.info(f"Please run:\n```\nollama serve\n...")  # Line 90
        st.stop()                          # Line 91

    st.markdown("---")                     # Line 93
    st.caption("🔒 Privacy Mode: Active")  # Line 94
    st.caption(f"📊 Max Input: {MAX_INPUT_LENGTH} chars")  # Line 95
```

### **What Each Line Does:**

**Line 81:** Everything indented here appears in left sidebar

**Line 82:** Show shield icon at top
- **Output:**
```
Sidebar:
  🛡️ [shield icon image]
```

**Line 83:** Big title text
- **Output:**
```
  Private Auditor
```

**Line 86-91:** Health check with conditional display
- **If Ollama running:**
```
  ✅ 🟢 System Online (qwen3-coder:30b)
```
- **If Ollama offline:**
```
  ❌ 🔴 Ollama Offline or Model Missing
  ℹ️  Please run:
      ollama serve
      ollama pull qwen3-coder:30b

  [App stops here, rest of page doesn't load]
```

**Line 91:** `st.stop()` halts execution
- Nothing below this line runs
- User can't click buttons or interact

**Line 93:** Horizontal divider line
- **Output:**
```
  ─────────────────────
```

**Line 94-95:** Small gray text at bottom
- **Output:**
```
  🔒 Privacy Mode: Active (No Cloud)
  📊 Max Input: 10000 chars
```

---

## **Lines 98-111: Main Input UI**

```python
st.title("🛡️ Automated Risk & Compliance Mapper")  # Line 98

col1, col2 = st.columns([1, 1])            # Line 100

with col1:                                 # Line 102
    st.subheader("📝 Audit Findings Input")  # Line 103
    audit_input = st.text_area(            # Line 104
        "Raw Audit Notes:",                # Line 105
        height=300,                        # Line 106
        placeholder="Paste interview notes...",  # Line 107
        max_chars=MAX_INPUT_LENGTH         # Line 108
    )

    analyze_btn = st.button("🔍 Analyze Risks", type="primary")  # Line 111
```

### **What Each Line Does:**

**Line 98:** Big header at top of page
- **Output:**
```
🛡️ Automated Risk & Compliance Mapper
──────────────────────────────────────
```

**Line 100:** Split page into two equal columns
- **Output:**
```
┌─────────────────┬─────────────────┐
│   Column 1      │   Column 2      │
│   (col1)        │   (col2)        │
└─────────────────┴─────────────────┘
```

**Line 103:** Smaller heading in left column
- **Output:**
```
Column 1:
  📝 Audit Findings Input
  ─────────────────
```

**Line 104-109:** Multi-line text input box
- **Line 105:** Label above box: "Raw Audit Notes:"
- **Line 106:** Box is 300 pixels tall
- **Line 107:** Gray placeholder text (disappears when typing)
- **Line 108:** Prevents typing more than 10,000 chars
- **Output:**
```
  Raw Audit Notes:
  ┌───────────────────────────────┐
  │ Paste interview notes, slack  │
  │ logs, or observation data...  │
  │                               │
  │                               │
  │                               │
  │                               │
  └───────────────────────────────┘
```

**Line 111:** Blue button
- **Output:**
```
  ┌──────────────────┐
  │ 🔍 Analyze Risks │  ← Clickable
  └──────────────────┘
```
- `type="primary"` makes it blue (otherwise gray)

---

## **Lines 113-115: Session State Initialization**

```python
if "results" not in st.session_state:      # Line 114
    st.session_state.results = None        # Line 115
```

### **What This Does:**

**The Problem Streamlit Has:**
Every time you click a button, Streamlit **re-runs the entire script from line 1**.

**Without this code:**
```
User clicks "Analyze" → Results show
User clicks anything else → Script reruns → Results disappear ❌
```

**With this code:**
```
First run:
  - Line 114 is True (no 'results' key exists)
  - Line 115 creates st.session_state.results = None

When analysis completes:
  - Code sets st.session_state.results = [risk1, risk2, risk3]

Next rerun (user scrolls, clicks, etc.):
  - Line 114 is False ('results' already exists)
  - Line 115 doesn't run
  - Results stay in memory ✅
```

**Visual Effect:**
```
Without session state:
  [Analyze] → Results show → [Scroll] → Results gone

With session state:
  [Analyze] → Results show → [Scroll] → Results still there
```

---

## **Lines 118-125: Input Validation**

```python
if analyze_btn and audit_input:            # Line 118
    clean_input = sanitize_input(audit_input)  # Line 120

    if not clean_input:                    # Line 122
        st.error("❌ Input validation failed...")  # Line 123
        logging.warning("Input sanitization failed")  # Line 124
        st.stop()                          # Line 125
```

### **What Each Line Does:**

**Line 118:** Only run if BOTH are true:
- Button was clicked (`analyze_btn == True`)
- Text box has content (`audit_input != ""`)

**Line 120:** Clean the input
- **Input:** User's raw text
- **Output:** Sanitized text (or `None` if invalid)

**Line 122-125:** If sanitization failed...
- **Line 123 Output:**
```
  ❌ Input validation failed. Please check your text and try again.
```
- **Line 124:** Writes to log file
- **Line 125:** Stops execution (like hitting a wall)

**Scenarios that trigger this:**
1. User pastes 50,000 characters (too long)
2. User pastes empty text then clicks
3. Text is all whitespace: "     "

---

## **Lines 127-145: AI Inference**

```python
with col2:                                 # Line 127
    st.subheader("📊 Compliance Analysis")  # Line 128

    with st.spinner(f"🤖 Analyzing with {MODEL_NAME}..."):  # Line 130
        try:                               # Line 131
            logging.info(f"Audit analysis started - Input length: {len(clean_input)} chars")  # Line 133

            system_prompt = """            # Line 135
            You are an expert GRC Automation Engine.
            Map the user's audit findings to ISO 27001:2022 controls.
            Output STRICT JSON only. No markdown. No chatter.
            Structure: {"risks": [{"description": "...", "iso_control": "...", "recommendation": "..."}]}
            """                            # Line 140

            response = ollama.chat(model=MODEL_NAME, messages=[  # Line 142
                {'role': 'system', 'content': system_prompt},    # Line 143
                {'role': 'user', 'content': clean_input},        # Line 144
            ])                             # Line 145
```

### **What Each Line Does:**

**Line 127:** Switch to right column (col2)

**Line 128:** Heading in right column
- **Output:**
```
Column 2:
  📊 Compliance Analysis
  ─────────────────
```

**Line 130:** Show loading spinner
- **Output while AI is thinking:**
```
  🤖 Analyzing with qwen3-coder:30b...
  [Spinning animation]
```

**Line 133:** Log to file (not visible to user)
- **Output in audit_trail.log:**
```
2025-11-22 09:49:15 - INFO - Audit analysis started - Input length: 234 chars
```

**Lines 135-140:** Instructions for the AI
- This is the "personality" of the AI
- **What it does:**
  - Tells AI to act like a GRC expert
  - Demands JSON output (not prose)
  - Shows expected format

**Lines 142-145:** Send request to Ollama
- **What goes to AI:**
```
System: "You are a GRC expert. Output JSON only..."
User: "HR emails passwords in plaintext. No MFA on admin accounts."
```
- **What comes back:**
```python
response = {
  'message': {
    'content': '{"risks": [{"description": "Passwords in email", "iso_control": "A.5.2.2", ...}]}'
  }
}
```

---

## **Lines 147-168: Parse AI Response**

```python
raw_output = response['message']['content']  # Line 147

data = extract_json(raw_output)            # Line 150

if data:                                   # Line 152
    risks = data.get("risks", data) if isinstance(data, dict) else data  # Line 154

    if isinstance(risks, list) and all(isinstance(r, dict) for r in risks):  # Line 157
        st.session_state.results = risks   # Line 159
        logging.info(f"Analysis successful - {len(risks)} risks identified")  # Line 160
    else:
        st.error("❌ Invalid risk data structure")  # Line 162
        logging.error("Risk validation failed")  # Line 163
else:
    st.error("❌ AI Output Error: Could not parse JSON.")  # Line 165
    logging.error("JSON parsing failed")   # Line 166
    with st.expander("Debug Raw Output"):  # Line 167
        st.code(raw_output)                # Line 168
```

### **What Each Line Does:**

**Line 147:** Extract text from response
- **Input:** Ollama response object
- **Output:** Just the AI's text (string)

**Line 150:** Try to find JSON in the text
- Calls `extract_json()` function we defined earlier
- **Returns:** Dictionary if successful, `None` if failed

**Line 152-160:** If JSON was found...

**Line 154:** Handle two possible formats
- **Format 1:** `{"risks": [...]}`  → Extract the `[...]` part
- **Format 2:** `[...]` → Use as-is
- **Output:** Python list of dictionaries

**Line 157:** Validate structure
- **Check 1:** `isinstance(risks, list)` → Is it a list?
- **Check 2:** `all(isinstance(r, dict) ...)` → Is each item a dictionary?
- **Why?** Prevent this: `risks = ["string", 123, None]` ❌

**Line 159:** Save results to session state (persistent storage)

**Line 160:** Log success
- **Output in log:**
```
2025-11-22 09:49:18 - INFO - Analysis successful - 3 risks identified
```

**Line 162-163:** If validation failed
- **User sees:**
```
  ❌ Invalid risk data structure
```
- **Log file:**
```
2025-11-22 09:49:18 - ERROR - Risk validation failed - not a list of dicts
```

**Line 165-168:** If JSON parsing failed entirely
- **User sees:**
```
  ❌ AI Output Error: Could not parse JSON.

  ▼ Debug Raw Output
    Sure! Here is what I found:
    The risks are very serious...
    (Shows the messy AI response)
```

---

## **Lines 175-187: Display Results**

```python
if st.session_state.results:               # Line 175
    with col2:                             # Line 176
        for idx, risk in enumerate(st.session_state.results, 1):  # Line 178
            desc = risk.get('description', 'Unknown')  # Line 180
            iso = risk.get('iso_control', 'General')   # Line 181
            rec = risk.get('recommendation', 'None')   # Line 182

            with st.expander(f"⚠️ {iso} - {desc[:40]}...", expanded=True):  # Line 184
                st.markdown(f"**Risk #{idx}:** {desc}")     # Line 185
                st.markdown(f"**Control:** `{iso}`")        # Line 186
                st.info(f"**Fix:** {rec}")                  # Line 187
```

### **What Each Line Does:**

**Line 175:** Only run if we have results

**Line 178:** Loop through each risk with index
- `enumerate(..., 1)` starts counting at 1 (not 0)
- **Example:**
```python
risks = [risk1, risk2, risk3]
enumerate(risks, 1) → (1, risk1), (2, risk2), (3, risk3)
```

**Line 180-182:** Extract fields with fallbacks
- `risk.get('description', 'Unknown')` means:
  - Try to get `risk['description']`
  - If key doesn't exist, use `'Unknown'`
- **Why?** AI might forget a field. Don't crash.

**Line 184:** Create expandable card
- `desc[:40]` = First 40 characters (truncate long descriptions)
- `expanded=True` = Show open by default
- **Output:**
```
  ▼ ⚠️ A.5.2.2 - HR emails passwords in plaint...
    Risk #1: HR emails passwords in plaintext to contractors
    Control: A.5.2.2
    ℹ️ Fix: Implement encrypted file transfer system
```

**Line 185-187:** Content inside the card
- **Line 185:** `**text**` = Bold in markdown
- **Line 186:** Backticks = Code formatting
- **Line 187:** `st.info()` = Blue info box

**Visual Example:**
```
Column 2:
  ┌─────────────────────────────────────────┐
  │ ▼ ⚠️ A.5.2.2 - HR emails passwords...   │
  ├─────────────────────────────────────────┤
  │ Risk #1: HR emails passwords in plain-  │
  │ text to external contractors            │
  │                                         │
  │ Control: A.5.2.2                        │
  │                                         │
  │ ℹ️ Fix: Implement encrypted file transfer│
  └─────────────────────────────────────────┘

  ┌─────────────────────────────────────────┐
  │ ▼ ⚠️ A.8.3 - No MFA on admin accounts   │
  ├─────────────────────────────────────────┤
  │ Risk #2: Administrative accounts lack   │
  │ multi-factor authentication             │
  │ ...                                     │
  └─────────────────────────────────────────┘
```

---

## **Lines 189-202: CSV Export**

```python
df = pd.DataFrame(st.session_state.results)  # Line 190
csv = df.to_csv(index=False).encode('utf-8')  # Line 191

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")  # Line 193

st.download_button(                        # Line 195
    label="📥 Download Audit Report (CSV)",  # Line 196
    data=csv,                              # Line 197
    file_name=f'audit_report_{timestamp}.csv',  # Line 198
    mime='text/csv',                       # Line 199
)                                          # Line 200

logging.info(f"Report exported - {len(st.session_state.results)} risks")  # Line 202
```

### **What Each Line Does:**

**Line 190:** Convert list of dicts → spreadsheet
- **Input:**
```python
[
  {"description": "Risk 1", "iso_control": "A.5.2", "recommendation": "Fix it"},
  {"description": "Risk 2", "iso_control": "A.8.3", "recommendation": "Do this"}
]
```
- **Output (DataFrame):**
```
  description | iso_control | recommendation
  Risk 1      | A.5.2       | Fix it
  Risk 2      | A.8.3       | Do this
```

**Line 191:** Convert DataFrame → CSV text
- `index=False` = Don't add row numbers
- `.encode('utf-8')` = Convert to bytes (required for download)
- **Output:**
```
description,iso_control,recommendation
Risk 1,A.5.2,Fix it
Risk 2,A.8.3,Do this
```

**Line 193:** Create timestamp for filename
- **Input:** Current time = Nov 22, 2025, 2:30:15 PM
- **Output:** `"20251122_143015"`

**Line 195-200:** Create download button
- **Output in UI:**
```
  ┌─────────────────────────────┐
  │ 📥 Download Audit Report    │  ← Click downloads file
  │    (CSV)                    │
  └─────────────────────────────┘
```

**Line 198:** Filename includes timestamp
- **Output:** `audit_report_20251122_143015.csv`
- **Why timestamp?** Multiple downloads don't overwrite each other

**Line 199:** Tell browser it's a CSV file
- Browser knows to open in Excel/Google Sheets

**Line 202:** Log the export
- **Output in audit_trail.log:**
```
2025-11-22 14:30:20 - INFO - Report exported - 3 risks
```

---

## **Complete Data Flow Example**

Let me show you what happens when a user analyzes this input:

### **User Input:**
```
HR emails employee contracts with SSNs to payroll@external.com without encryption.
Admin accounts don't have MFA enabled.
```

### **Step-by-Step Execution:**

1. **Line 118:** Button clicked + text present → Continue
2. **Line 120:** Sanitize → `clean_input = "HR emails..."` ✅
3. **Line 130:** Show spinner in UI
4. **Line 133:** Log: `"Audit analysis started - Input length: 124 chars"`
5. **Lines 142-145:** Send to AI:
```
System: "You are a GRC expert. Output JSON..."
User: "HR emails employee contracts..."
```
6. **Line 147:** AI returns:
```json
{
  "risks": [
    {
      "description": "Sensitive data transmitted unencrypted via email",
      "iso_control": "A.5.2.2, A.8.2.3",
      "recommendation": "Implement secure file transfer solution"
    },
    {
      "description": "Admin accounts lack multi-factor authentication",
      "iso_control": "A.8.3.1, A.8.5.2",
      "recommendation": "Enable MFA for all privileged accounts"
    }
  ]
}
```
7. **Line 150:** Parse JSON ✅
8. **Line 154:** Extract risks list
9. **Line 157:** Validate structure ✅
10. **Line 159:** Save to session state
11. **Line 160:** Log: `"Analysis successful - 2 risks identified"`
12. **Line 178-187:** Display 2 cards in right column
13. **Line 190-191:** Create CSV:
```csv
description,iso_control,recommendation
Sensitive data transmitted unencrypted,A.5.2.2; A.8.2.3,Implement secure file transfer
Admin accounts lack MFA,A.8.3.1; A.8.5.2,Enable MFA for privileged accounts
```
14. **Line 195:** Show download button
15. **User clicks download:**
    - File saved: `audit_report_20251122_143015.csv`
16. **Line 202:** Log: `"Report exported - 2 risks"`

---

## **Key Takeaways**

### **Three Main Sections:**
1. **Setup (Lines 1-78):** Import libraries, define helper functions
2. **UI (Lines 80-115):** Create sidebar, input box, button
3. **Logic (Lines 117-202):** Process input, call AI, display results

### **Important Patterns You Learned:**

**Pattern 1: Defensive Programming**
```python
desc = risk.get('description', 'Unknown')  # Don't crash if key missing
```

**Pattern 2: Try/Except Chains**
```python
try:
    return json.loads(text)  # Try simple way
except:
    # Try complex way with regex
```

**Pattern 3: State Persistence**
```python
st.session_state.results = risks  # Survives page reruns
```

**Pattern 4: Logging Without Leaking**
```python
logging.info(f"Input length: {len(text)}")  # Log metadata
# NOT: logging.info(f"Input: {text}")      # Don't log sensitive data
```

---

Want me to explain any specific section in more detail?

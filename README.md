# Sovereign GRC Auditor 🛡️

A privacy-first, local AI agent that automates ISO 27001 compliance mapping.

## 🚀 The Problem
Enterprise GRC teams spend thousands of hours manually mapping audit findings to control frameworks. Using public LLMs (ChatGPT) for this is a security risk due to data leakage of sensitive audit notes.

## 🛠️ The Solution
This tool runs entirely **offline** (Local Inference). It uses a specialized logic model (`Qwen2.5-Coder`) to parse unstructured audit notes and map them to **ISO 27001:2022** controls with 0% data egress.

## ⚙️ Tech Stack
* **Engine:** Ollama (Local Inference)
* **Model:** Qwen2.5-Coder (32B Parameter) - Chosen for strict logic compliance.
* **Frontend:** Streamlit
* **Security:** Input sanitization (Regex) + Local Audit Logging (ISO A.12.4 compliant).

## 📸 Features
* **Strict JSON Parsing:** Enforces structured data output for integration with GRC platforms.
* **Automated Reporting:** Exports findings to CSV for immediate client delivery.
* **Audit Trail:** Logs system performance without logging PII.

## 🔧 Installation

### Prerequisites
- Python 3.11+
- Ollama ([Download here](https://ollama.com/download))
- 20GB free disk space (for model)

### Step 1: Install Ollama
```bash
# Windows/Mac/Linux
# Download from https://ollama.com/download
```

### Step 2: Pull the Model
```bash
ollama pull qwen3-coder:30b
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Run the Application
```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

## 🎯 Usage

1. **Paste Raw Audit Notes:** Copy-paste unstructured findings from interviews, reports, or observations
2. **Click Analyze:** The AI processes locally (no cloud calls)
3. **Review Mappings:** See risks mapped to specific ISO 27001:2022 controls
4. **Export Report:** Download CSV for immediate client delivery

## 🔒 Security Features

- **Zero Data Egress:** All processing happens locally via Ollama
- **Input Sanitization:** Removes control characters and validates input length
- **Audit Logging:** Tracks analysis metadata (not sensitive content) to `audit_trail.log`
- **Model Verification:** Validates Ollama service and model availability before processing

## 📊 Example Output

**Input:**
```
HR team emails employee contracts containing passport numbers to external
payroll provider without encryption. The provider's contract has no 'Right
to Audit' clause. Three ex-employees still have active accounts.
```

**Output:**
| Risk | ISO Control | Recommendation |
|------|-------------|----------------|
| HR team emails sensitive data unencrypted | A.5.2.2, A.8.2.3, A.13.2.3 | Implement encryption for all sensitive data transfers |
| No 'Right to Audit' clause | A.5.2.3, A.12.3.2, A.13.2.4 | Negotiate audit rights in supplier contracts |
| Ex-employees have active access | A.5.3.1, A.8.2.4, A.13.2.1 | Implement immediate account deactivation procedures |

## 🏗️ Architecture

```
User Input → Sanitization → Ollama (Local) → JSON Parser → Risk Validator → Streamlit UI
                                                                    ↓
                                                              Audit Logger
```

## 🚧 Roadmap

- [ ] Multi-framework support (NIST CSF, SOC 2)
- [ ] PDF report generation
- [ ] Historical analysis dashboard
- [ ] API endpoint for GRC platform integration

## ⚖️ License

MIT License - Built for defensive security purposes only.

## 🤝 Contributing

This is a demonstration project. For enterprise deployments or custom frameworks, open an issue to discuss.

---

**Built with privacy-first AI. No cloud. No compromise.**

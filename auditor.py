import ollama
import json

system_prompt = """
You are an expert GRC Automation Engine.
Your job is to map informal risks to ISO 27001:2022 Annex A controls.
You MUST output raw JSON only. 
The JSON must be a list of objects under a root key called "risks".
Example:
{
  "risks": [
    {"description": "Risk 1", "iso_control": "A.5.1", "recommendation": "Do X"},
    {"description": "Risk 2", "iso_control": "A.8.2", "recommendation": "Do Y"}
  ]
}
"""

audit_input = """
We have a problem where developers are leaving API keys hardcoded in GitHub repositories.
Also, we don't have any way to track who enters the server room.
"""

print("⏳ Qwen is analyzing risks locally...")

response = ollama.chat(model='qwen3-coder:30b', messages=[
    {'role': 'system', 'content': system_prompt},
    {'role': 'user', 'content': f"Map these risks to ISO controls: {audit_input}"},
])

raw_output = response['message']['content']

print("\n--- RAW MODEL OUTPUT (For Debugging) ---")
print(raw_output)
print("----------------------------------------\n")

try:
    # Clean up markdown if present
    clean_json = raw_output.replace("```json", "").replace("```", "").strip()
    data = json.loads(clean_json)
    
    print("✅ SUCCESS! Parsed JSON.\n")
    
    # Handle the structure dynamically
    # If the root is a dictionary with a 'risks' key
    if isinstance(data, dict) and "risks" in data:
        items_to_process = data["risks"]
    elif isinstance(data, list):
        items_to_process = data
    else:
        # Fallback: try to look at values
        items_to_process = data.values()

    # Print the Audit Report
    for item in items_to_process:
        # Check if item is a dictionary (it should be)
        if isinstance(item, dict):
            print(f"⚠️  Risk: {item.get('description', 'Unknown Risk')}")
            print(f"    -> ISO Control: {item.get('iso_control', 'N/A')}")
            print(f"    -> Recommendation: {item.get('recommendation', 'N/A')}\n")
        
except json.JSONDecodeError:
    print("❌ JSON Error. The model output text instead of data.")
except Exception as e:
    print(f"❌ Python Logic Error: {e}")
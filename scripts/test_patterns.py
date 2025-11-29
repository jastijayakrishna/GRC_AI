"""
Test script to validate pattern matching across different audit scenarios
"""
import rag_engine

# Test scenarios
test_cases = [
    {
        "name": "Physical Security",
        "input": "Office server room door uses a 4-digit code (1234) that has been unchanged for 2 years. The code is written on a sticky note on the door frame. No entry/exit logs are maintained. Cleaning staff have 24/7 access to the room."
    },
    {
        "name": "Vendor Risk",
        "input": "Marketing team uses a third-party email platform (MailChimpPro) to send customer newsletters containing email addresses and purchase history. No vendor security assessment was performed. The contract has no data breach notification clause or right-to-audit provision."
    },
    {
        "name": "Backup Failure",
        "input": "Database backups run nightly but haven't been tested in 14 months. Last restoration test failed due to corrupted backup files. Backups are stored on the same network as production systems. No offsite backup copies exist."
    },
    {
        "name": "Weak Password",
        "input": "User accounts allow passwords like 'password123' and 'admin'. No complexity requirements enforced."
    },
    {
        "name": "No MFA",
        "input": "VPN access requires only username and password. Multi-factor authentication is not enabled."
    },
    {
        "name": "Excessive Admin Privileges",
        "input": "12 employees have domain admin rights but only perform standard office tasks."
    },
    {
        "name": "Unencrypted Data",
        "input": "Customer credit card data is stored in a MySQL database without encryption. Files containing SSNs are saved to shared network drives in Excel format."
    },
    {
        "name": "Missing Patches",
        "input": "Windows Server 2012 hosts are 8 months behind on security patches. Critical vulnerabilities CVE-2023-1234 remain unpatched."
    }
]

print("=" * 80)
print("PATTERN MATCHING TEST RESULTS")
print("=" * 80)

for test in test_cases:
    print(f"\nScenario: {test['name']}")
    print(f"Input: {test['input'][:80]}...")

    # Query the database
    results = rag_engine.crosswalk_collection.query(
        query_texts=[test['input']],
        n_results=3
    )

    # Show top 3 matches
    print("\nTop 3 Matches:")
    for i in range(3):
        pattern = results['metadatas'][0][i]['pattern_name']
        distance = results['distances'][0][i]
        iso = results['metadatas'][0][i]['iso_27001']

        # Check if it would match (threshold = 1.4)
        match_status = "[MATCH]" if distance < 1.4 else "[NO MATCH]"

        print(f"  {i+1}. {pattern}: {distance:.4f} {match_status}")
        if i == 0:  # Show controls for best match
            print(f"     ISO 27001: {iso}")

    print("-" * 80)

print("\nTest complete!")

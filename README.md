The Offer Processing Automation Script is designed to streamline the offer generation process within a popular ATS system.
This automation reduces manual data entry, minimizes user error, and speeds up the offer preparation workflow by automatically filling multiple contract fields based on an Excel data source.
________________________________________
🎯 Purpose
Traditionally, the offer process requires the user to:
•	Manually change up to 17+ currency fields from USD to the local region’s currency.
•	Manually input key prospect details from external data sources.
•	Verify that each field is accurately entered before submission.
This script automates these repetitive tasks — ensuring speed, accuracy, and consistency across all offers.
________________________________________
⚙️ How It Works
Once initiated, the script:
1.	Collects the required input data from a designated folder on the user’s local machine.
2.	Reads the provided Excel document containing critical offer data.
3.	Uses a debug-enabled Chrome session to interact with the ATS prospect page.
4.	Automatically:
o	Changes currency fields (USD → target region currency).
o	Inputs key offer details from the Excel file.
5.	Waits for user review before submission.
________________________________________
📂 Prerequisites
System Requirements
•	Operating System: Linux
•	Browser: Google Chrome (stable release)
•	Python Version: 3.9+
•	Libraries: As specified in requirements.txt
•	Excel File: Must be prepared with required data columns and saved in the designated folder.
Folder Structure
offer-automation/
│
├── venv/                  # Python virtual environment
├── mr-offer.py            # Main automation script
├── requirements.txt        # Dependencies
└── data/
    └── offer_data.xlsx     # Designated Excel file
________________________________________
🚀 How to Run
1. Prepare the Excel Data
•	Ensure the correct Excel file (offer_data.xlsx) is saved in the data/ folder.
•	Verify that all required fields are complete and formatted correctly.
2. Launch Debugging Browser
Open two Linux terminals, then in the first one, run:
google-chrome-stable --remote-debugging-port=9222 --user-data-dir=/tmp/sr-prospect
This launches a Chrome session that allows the script to control the browser.
3. Log in and Navigate
In the Chrome window:
•	Log in to your ATS account.
•	Navigate to the prospect’s page.
•	Select the correct offer template.
4. Run the Script
In the second terminal:
source venv/bin/activate
python3 mr-offer.py
⚠️ Important:
Once the script starts running, do not click or interact with the browser until completion.
Manual interference can cause field mismatches or execution errors.
________________________________________
✅ After Script Completion
Once the script finishes:
1.	Review the populated fields for accuracy.
2.	Add any personal or custom prospect details (if required).
3.	Finalize and close the hire process.
________________________________________
🧠 Tips & Troubleshooting
Issue	Possible Cause	Solution
Script doesn’t launch browser	Debug port not active	Check Chrome command and re-run with --remote-debugging-port=9222
Fields not updating	Wrong Excel file or structure	Verify correct file and folder
Script crashes mid-run	Browser interference	Avoid touching mouse/keyboard during execution
Excel data not read	File not found	Ensure Excel file is saved in the designated folder
________________________________________
🔒 Notes
•	Only run the script after selecting the correct offer template.
•	Ensure the Excel data follows the naming and format conventions.
•	This automation is intended for internal administrative use only.

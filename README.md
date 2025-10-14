The Offer Processing Automation Script streamlines the business offer admin process within a popular ATS system.
My professional workflow is optimised reducing manual data entry, user error and speed of business process.
________________________________________
🎯 The user journey today 

•	Manually change up to 17+ currency fields from USD to the local region’s currency.

•	Manually input key prospect details from external data sources.

•	Verify that each field is accurately entered before submission.

This script automates these repetitive tasks — ensuring speed, accuracy, and consistency across all offers.
________________________________________
🚀 How to Run
1. Prepare the Excel Data
•	Ensure the correct Excel file (offer_data.xlsx) is saved in the data/ folder.
•	Verify that all required fields are complete and formatted correctly.
2. Launch Debugging Browser
Open two Linux terminals, then in the first one, run:
google-chrome-stable --remote-debugging-port=9222 --user-data-dir=/tmp/sr-prospect

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
Manual interference will cause errors
________________________________________
✅ After Script Completion
Once the script finishes:
1.	Review the populated fields for accuracy.
2.	Add any personal or custom prospect details (if required).
3.	Finalize and close the hire process.
________________________________________

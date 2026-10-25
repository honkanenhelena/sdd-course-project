The same verification plan will be used for both the vibe coded build and the sdd-build.

The verifications will be run on both branches final versions before fixing any more of the found errors. Fresh environments will be made for both branches for the tests with the same python version and tools. The outputs of the verification will be in verificationEvidence.md in /docs with a subfolder for the vibe and the sdd. Github issues will be raised for the found problems. 

Automated tests to run:

pytest and pytest-cov, bandit and pip-audit. These will be logged accordingly:

pytest and pytest-cov will show the amount of tests they ran, how many passed or failed and what the coverage % was. 
bandit will be recorded accoridng to the findings by severity
pip-audit will show the number of vulnerable packages found in the application implementations.

Manual tests to run:

Every feature in the features.md will be tested by hand
Checks for the features:
Add an expense with a disallowed number/character
Add expense with 0 as amount
Add expense with a non-existent date
Submit an expense with a requirement field empty
Note that has a large amount of characters
Note containing a script injection
Note containing special characters such as . , : ;
Add expenses with varying amounts of cents in one category
Add expenses in different months
Restart server
Edit a non-existent id in the /docs
Delete a non-existent id in the /docs
POST a negative amount via /docs
Filtering with start date after end date

Prompt 0.1

Prompt: Use Python 3.15 with FastAPI and SQLite with the frontend being HTML and JavaScript. Keep it simple, no frameworks. All user input needs to be validated and every feature must have automated tests with pytest.

Expected outcome/result: Nothing except a setup for the context of the agent to have to use in future prompts.

Outcome of prompt: As expected the LLM made no changes but it also said it could not update the constitution. This was due to the spec kit not being initialized correctly, so performed the initialization again since the .venv was also remade when changing to main. 



Prompt 1

Prompt: Use Python 3.15 with FastAPI and SQLite with the frontend being HTML and JavaScript. Keep it simple, no frameworks. All user input needs to be validated and every feature must have automated tests with pytest.

Expected outcome/result: Nothing except a setup for the context of the agent to have to use in future prompts.

Outcome of prompt: An edited constitution which can be used in future prompts.


Prompt 2:

Prompt: /speckit-specify An expense tracker that helps the user see what their money goes to and helps them cut costs. Feature list: The application needs to have the possibility to add expenses with the data being: Amount spent, date, category of purchase, option to select it as a necessity, option for a note. The application then must present these expenses in a way where the user can edit and delete expenses. The expenses should be presented in a way where they can be filtered by date, category and necessity, and the application needs to have a monthly summary available with a breakdown of the expenses. To help the user cut costs the application needs to have a possibility to set a monthly budget for categories which also shows how close the user is to said budget. The application needs to validate the input that the user gives it, so that no false dates or negative numbers can be inserted, and it also needs to enforce the necessary field for the data. The data that exists in the application must also be saved and be consistent so that the application can be used on a monthly basis. The application also needs to have a separate spending chart where the different categories can be visualized. 

Expected outcome/result: A new branch with the specifications of the application in a file. I also expect a checklist of clarifications that are needed after the prompt. 

Outcome of prompt: It did not create a branch so did that by hand and named it the same as the created folder. There were no clarifications marked but still performed a check on the outcome (spec.md file) and found that all requirements seem to have been logged successfully.
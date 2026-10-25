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



Prompt 3.1

Prompt: /speckit-clarify

Expected outcome/result: The chat will ask for clarifications regarding the spec one by one and give options. 

Outcome of prompt: Question about the user scope being about if the tracker will be a private single-user app or will it have multiple users. It also gave options A B C and short own answer, with A being single user no login, B single user network login, C being multiple users and short being one of my own. 

Prompt 3.2 

Prompt: A

Expected outcome/result: For it to log my choice and to ask another question.

Outcome of prompt: It logged this and asked about a possible export of the expenses for making a backup, with the choices being A for no export, B for user-triggered CSV exports and C for automatic periodic backups.

Prompt 3.3

Prompt: A

Expected outcome/result: It logs this answer and asks another clarifying question.

Outcome of prompt: The answer was logged and the previous one was also confirmed as logged and then it asked about the currency to use, with suggested being for its recommended EURO choice, and short answer otherwise.

Prompt 3.4

Prompt: suggested

Expected outcome/result: For it to log this aswell and to ask another question about clarifications.

Outcome of prompt: It finished the clarifications and showed that the requirements still all passed with no checkbox states changed. It also recommended /speckit-plan as the next command.


Prompt 4

Prompt: /speckit-plan Use the defined stack in the constitution. Keep the implementation simple with one FastAPI app, a SQLite database and a frontend made with HTML and JS.

Expected outcome/result: An updated plan file for the model to work from. Also expect it to list the stack it will use and that it will match the listed one.

Outcome of prompt: The prompt researched the web for simple designs with a subagent and it then udpated the plan with the information it received along with some other .md files such as quickstart and research. It also recommended the next step which is speckit-tasks


Prompt 5

Prompt: /speckit-tasks

Expected outcome/result: A task file with the tasks it sees as needed to be done with tests for them. This tasks file will be important for after the prompt so that it can be reviewed so that I can confirm that the AI has understood the task at hand correctly.

Outcome of prompt: Exactly as expected it created tasks.md with 25 tasks with user stories and tests. Checked the tasks.md file and it seemed to have tests for each task and the user stories were also involved in the tasks. The tests were also linked with the user stories well. It recommended speckit-implement next.

Prompt 6

Prompt: /speckit-analyze

Expected outcome/result: A checklist for inconsistencies between the created documents so that these can be solved before the development starts.

Outcome of prompt: A list with both a specification analysis report and a coverage summary. There are some now obvious problems and hallucinations in the implementation, so these will be fixed before starting development as planned. One example is C2 which is a performance requirement which it has implemented itself and is not required nor in scope. 


Prompt 7

Prompt: Apply the following fixes to the files: I1, a reversed date range needs to return 422 with an error message. A1, replace SC-001 with the requirement "a first-time user can add an expense to the app without further instructions". C1, add the implementation and test tasks for GET/api/categories. U1, List the category slugs in the spec and T006. C2, This was not apart of scope so remove the performance target from the plan. U2, use pip_audit -r requirements.txt

Expected outcome/result: A fix to ONLY the requested parts and a confirmation on what was changed.

Outcome of prompt: As expected it applied the requested fixes and checked these according to the tasks.

Prompt 8

Prompt: /sepckit-analyze

Expected outcome/result: A clean run with no items in the specification analysis report and no ambiguities.

Outcome of prompt: As expected the fixes have solved the issues and there were no new issues found, so the repo is ready for development.




Prompt 8

Prompt: /speckit-implement Implement the first phase from the tasks.md and stop after phase 1. 


Expected outcome/result: The initial setup of the stack and the empty frontend files that are mentioned in phase 1 in tasks.md. I also expect it to stop after this so that I can perform this with one phase at a time.


Outcome of prompt: The output confirmed that it completed only phase 1 and that it created the files that were mentioned in the tasks file. Checked tasks.md and noticed that it had placed a check for the phase one tasks.

Prompt 9

Prompt: /speckit-implement Implement the second phase from the tasks.md file and stop after it is complete.

Expected oucome/result: A complete phase 2 with the tasks for it checked of with no excessive work done.

Outcome of prompt: It completed this but only after having some trouble with a command about Starlette (FastAPI), but it did fix this and the tasks were checked off in the tasks file.


Prompt 10

Prompt: /speckit-implement Implement phase three of the tasks.md and stop after phase 3 is complete.

Expected oucome/result: A complete phase 3 with the first user story complete and the appropriate tests for it made and completed.

Outcome of prompt: A complete expense CRUD MVP with the appropriate tests done and passed. It did fail the tests 3 times but after the last fix it completed with 4 passed and with 1 warning, but this was about the phase 2 Starlette depreceation. The tasks.md file tasks, tests and implementations for user story 1 were all checked.


Prompt 11

Prompt: /speckit-implement Implement the fourth phase of the tasks.md file and stop after phase 4 is complete.

Expected outcome/result: A complete phase 4 which includes the second user story and its tasks and tests. Expect it to create tests and probably also fail these again during the development.

Outcome of prompt: As expected the AI completed the phase with the tasks marked as completed in the tasks file. After a few tries it passed the tests, so checked the application and took some screenshots. As seen in Phase4SaveBudget the application also has placeholder for the next phase parts.



Prompt 12

Prompt: /speckit-implement Implement the fifth phase of the tasks.md file and stop when the phase is complete.

Expected outcome/result: An implementation of the budgets per category as mentioned in the tasks.md together with the appropriate tests for the tasks and user stories.  

Outcome of prompt: The AI completed the phase with all tasks completed and all tests passed, and tested it with a smoke test which passed. There was however an old expenses.db which it saw as legacy so left unchanged, and this is probably from the vibe build since the git ignores the .db ending files. The AI created a temporary db but moved this one so that it could create one with the next prompt. The AI edited the .gitignore so checked it to make sure there were no vulnerabilities.


Prompt 13

Prompt: /speckit-implement Implement the sixth phase of the tasks.md. The expenses.md was not part of this project so it has been moved. No migration is needed, but the app should have a fresh database.

Expected outcome/result: The final version of the application with the new database that was requested. The Starlette depreceation is fine to not be fixed for this small scope project but expect the final polish to make sure it fills all requirements.

Outcome of prompt: The AI completed the sixth phase and found some serious bugs in its testing and the application aswell. The add/edit/delete form had not been working in the frontend because the tests for phase 3 were only for the API. This was promptly fixed in this phase but this should have been caught in phase 3. It also found a security problem where the app accepted requests from other local addresses and ports than the origin, so this was fixed. pip_audit also found a vulnerable dependency being pytest, so the version limit in requirements was raised and this was fixed. There was however not any certain version ever requested so not sure on where the limit came from. Errors were also fixed to be shown on the webpage. It also mentioned save expense not working via the browser, but this was checked by hand and confirmed to be working. After this I tested the website and found out that the inputs for the dates accepted years with 6 digits while the check was for 4 digit years, and the check worked so that you could not create an expense with a date of 6 digits, but the budget search which also dictates the recent expenses instead threw the error for how the date should be input in the recent expenses section.

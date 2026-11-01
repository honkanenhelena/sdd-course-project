## An Experience Report on a Specification-Driven, AI-Assisted Software Construction Project 

Team Details (Team [Insert Team Number/Name]) 

[Helena Honkanen] 

[2403510] 

[Solo] 

[100%]



 

Executive Summary (Must be included in the report)
Th project was to build a small web application with both vibe coding and specification-driven development (sdd) to compare the outcome and development of the application. The application of choice was a small expense tracker meant for personal use. The app needs to let a user add, edit, and delete expenses with the data for an expense being amount, date, category, necessity and an optional note. The app then needs to filter these expenses, let the user view a monthly summary and then chart the expenses by category. The application also needs to have a feature for the user to set a monthly budget for a category. The applications used the same stack for the application, using Python 3.15, FastAPI, SQLite and a HTML and JavaScript frontend. Both builds were also made with the same AI, being the Github Copilot inside of VS Code switched to Agent mode with the automatic model selection on, this selecting GPT 6 Luna for both the vibe and sdd version.

The vibe coded version was made by talking in plain words with conversational prompts with no written specification for the model to follow. The vibe coded version reached a version which fulfilled all of the features in just 3 prompts after 5 hours of work. The SDD build used Githubs Spec Kit and followed its workflow, being constitution, specify, clarify, plan, tasks, analyze and implement. The analyze step found six issues with the plan before the development started in the next phase, which let it fix these before it started. The application was completed in 13 prompts which took around 9 hours of work. 

Both builds were verified after development with the same verification plan. The verification was automated tests ran with their own pytest suites with coverage measurements, bandit security linting and then pip-audit checks for the dependencies used. After this there was a manual verification where a human tested edge-cases using the web-application and the API. After the edge-cases there was also an acceptance check for the features. Using the human-in-the-loop review a Github issue was raised for each problem encountered during the verification.
 

1. Introduction & Paradigm Shift (3 Points)

1.1 Project Overview & Objectives 
The project idea is to create a finance tracker where one can input their spendings and make it easier to possibly cut costs or to just keep track of what they are spending and where. A user can record expenses with an amount, date, category, necessity and optional note, letting them then edit and delete these expenses as need be. The application then needs to let the user filter the expenses according to date, category and necessity and it needs to show a monthly summary with a chart of the spending for each month. The application also needs to include a feature for setting budgets per category with a limit per month. The expenses need to be saved between sessions as well.

The objective of the project was to build the same application twice so that vibe coding and sdd based coding could be compared. They were both built with the same features required, using the same technology stack and with the same AI tool.

1.2 The Vibe Coding 
Vibe coding is the act of talking with an AI model with human language to produce some application or other form of software. The developer that is vibe coding is describing the thing they want to build in natural language to the model, and then the model produces this as a response to this. If there are possible changes or fixes the developer needs or wants then they respond with this in the next prompt. 

I used this approach in the vibe coded build by writing a short first prompt which included all of the features I wanted but in my own words instead of with criteria. I then sent it to the Github Copilot chat which directed it to GPT Luna 6. After the model model had built the application and responded with it I checked it out by running the app, compared it to what I expected and the wrote the next prompt according to what was missing. The build using this method was completed in just 3 prompts. 

1.3 The SDD Methodology 
Specification-driven development is the development method where the developer makes a specification and has it as the focus of the project. The specification has the requirements, constraints and design decisions figured out before any code is written so that these can be checked before development. 

For the SDD build I used the Github Spec kit which is an open-sourced SDD toolkit with instructions for an AI model. I chose it since it is the toolkit that was included in the course materials and since it also integrated well with the Github Copilot model which I used. The scope of both builds was the same 7 feature list with the appropriate criteria for when it can be considered done. Both builds were kept to purely these features and any out-of-scope features that the AI may have tried implementing were excluded.

The timeline of the project was:

Setup phase, October 16-17, Created the repository, feature list, decided on tech stack
Vibe build, October 17-21, First prompt, Prompt 1, 2 and 3
SDD build, October 22-24, Constitution, specify, clarify, plan, tasks, analyze, implement
Verification, October 25-31, Automated and manual verification steps

2. Requirements & System Specification: (6 points)

This is the most critical section of the report. It details the "source of truth" you constructed to feed into the AI. 

2.1 Stakeholders:
End users
Private individuals who want to track their spending and stay within their own budgets. They are included since they are the primary user of the application and all features are derived from what is their expected needs.

Developer
The developer who wants have clear code which meets the requirements, is maintainable and testable. The developer is included since it is them who writes the specification, prompts the AI and verifies the outcomes. 

2.2 Functional Requirements: 

Describe briefly what the functional requirements are. Later, explain the functional requirements of this project.
2.3 Non-Functional Requirements: 

Describe briefly what the non-functional requirements are. Later, explain the non-functional requirements of this project (Performance, security, usability, and reliability constraints e.g., "The system must load in under 2 seconds"). 
2.4 Technology Stack 

This section should describe the technology stack used for the project. There are several technology stacks available. Therefore, the reason behind choosing a specific technology stack needs to be explained in this section.

AI Generation & Orchestration Tools: [e.g., Spec-Kit, Cursor IDE, GitHub Copilot, Claude 3.5 Sonnet, Custom GPTs] 

2.5 Interface & API Specifications 
 
2.6 How these requirements and specifications were created (using SDD AI tools)
 

3. Vibe coding and your project (5 pts)

Your approach towards the project using vibe-coding. Briefly describe your approach and how you decided among your team members. For example, if any specific promptbook has been used, the project is divided into several modules, and how they were combined at a later stage. All of them need to be explained here.
3.1 Prompting Framework 

Describe the system prompting techniques used. Chain-of-Thought, or automated agentic workflows?
3.2 Master Prompts / System Prompts 

Describe and include the prompts that you have used for vibe coding your project, add your reasoning for the prompt, what you expected the prompt would do, what did not go according to plan, and how you modified the prompt later.
Document the prompts you used during AI-assisted development (Vibe-coding) and explain how they evolved throughout the project. For each significant prompt, include the original prompt text, the purpose of the prompt, and your reasoning for using it. Describe what you expected the AI to generate, evaluate whether the output met your expectations, and discuss any issues encountered (e.g., incorrect, incomplete, or inefficient code). If the initial prompt did not produce the desired result, explain how you refined or modified the prompt, why those changes were made, and how the revised prompt improved the outcome. Include representative prompt-response examples where appropriate, and reflect on the importance of prompt engineering in achieving accurate and reliable AI-generated software artifacts.
Example System Prompt: 

"You are an expert software engineer specializing in secure Node.js APIs. Your task is to implement the routing logic for the attached OpenAPI specification…." 

3.3 Prompt Iteration Log 

Show an example of where a prompt failed or hallucinated, and how you iteratively refined the specification or prompt to resolve it. 

Initial Prompt/Specification 

AI Failure Mode / Bug Produced 

Refined Prompt/Specification 

Resulting Code Quality 

What did not happen according to your plan

Modified Prompt

"Write a database model for user registration." 

Left passwords in plain text; skipped validation. 

"Implement the User model following schema schema.json, ensuring password hashing using bcrypt via a mongoose pre-save hook." 

Successfully hashed passwords and validated inputs. 

Which task was not done

How did you modify the prompt and what is the modified prompt

 

4. Specification Driven Development and Your Project (7 pts)

4.1 SDD Tool-kit

Deciding on the tool-kit that you have used. For example, Spec Kit is an open-source toolkit created by GitHub for Spec-Driven Development (SDD). Explain the reason behind choosing this tool.
4.2 Development Environment

Which system environment and IDE/coding agents have been used, and why did you choose to use them? 
4.3 Deriving the requirements using the IDE/coding agents

How did you create and derive the Functional and non-functional requirements from the toolkit and IDE? This section can contain the prompts used to derive the requirements. Possible activities can be as follows:
Develop Software Requirements Specification (SRS)
Specify system constraints
Define interfaces
Establish acceptance criteria
Establish Compliance requirements
4.4 SDD Workflow and Implementation

Briefly describe which workflow you have used. Though there are several workflows that have been used across different projects, you can adopt any workflows or propose your own workflow that you have used across your projects.
4.5 Prompts 

Describe and include the prompts that you have used, add your reasoning for the prompt, what you expected the prompt would do, what did not go according to plan, and how you modified the prompt later. Document the prompts you used during AI-assisted development (SDD) and explain how they evolved throughout the project. For each significant prompt, include the original prompt text, the purpose of the prompt, and your reasoning for using it. Describe what you expected the AI to generate, evaluate whether the output met your expectations, and discuss any issues encountered (e.g., incorrect, incomplete, or inefficient code). If the initial prompt did not produce the desired result, explain how you refined or modified the prompt, why those changes were made, and how the revised prompt improved the outcome. Include representative prompt-response examples where appropriate, and reflect on the importance of prompt engineering in achieving accurate and reliable AI-generated software artifacts.
5. Verification and Validation (6 pts)

Since AI code can contain subtle bugs and security vulnerabilities, document how you verified the output. 

5.1 V&V Strategy 

Describe how you verified the code. Did you use AI to write tests based on the specifications before generating the code (Test-Driven Development with AI)?. OR Have you used the human-in-the-loop method to verify code? Your chosen technique may include a description of threats to validity. Describe how the implementation was verified. Possible activities:
Unit testing
Integration testing
Functional testing
Requirement verification
User acceptance testing
Compliance Testing
5.2 Code Audit Log 

What security flaws, compliance flaws, and logical flaws did your team catch during your code review of the AI's output? Therefore, describe whether you have used AI or AI+human to examine and fix the flaws in the project. Later, identify the technique that you have used to resolve those flaws. So this portion can include the following:

Issue Found: [e.g., AI used an outdated library method with known vulnerabilities.] 

Resolution: [e.g., Manually updated dependencies and prompted AI to rewrite using safe methods.] 

5.3 Test Execution Results 

Summarize the execution of your test cases by indicating the expected and actual results, along with the pass/fail status for each test. Include evidence such as screenshots, console outputs, logs, or other relevant artifacts where appropriate. Discuss any defects or unexpected behaviors identified during testing, explain how they were resolved (or why they remain unresolved), and evaluate the overall quality and reliability of the software. If applicable, report testing metrics (e.g., number of test cases executed, passed, failed, and code coverage) and briefly reflect on how the test results validate the correctness and robustness of your implementation.

6. Project Management & AI Toolchain Workflows (3 points)

Since the project will be monitored in Git, the repository needs to be configured well. The whole project needs to be built there. It should contain a README file that can include either the full project report along with the submission file, or a brief description of the project. Additionally, the modifications, issues raised, and discussions should be included in git. Each member needs to contribute to the git repository so that their contributions are clearly visible, along with the work distribution, in the project report.

6.1 Version Control & Prompt Integration 

Git Commit Conventions: Did your commit messages link code modifications to specific prompt iterations or specification changes?

Workspace Configuration: Describe your project rules setup and configuration. How did you set up the workspace, and how did you handle different issues?

6.2 Team Contribution Breakdown 

Explain how human roles shifted from "coding" to "specifying, prompting, auditing, and orchestrating." / as per your workflow. For example:

Member 1 (Specifier): Responsible for architectural design, and schema writing, etc

Member 2 (Prompt Engineer): Interacted with LLMs, optimized generation context, and managed the toolchain, etc

Member 3 (Verifier): Set up automated testing pipelines, ran code coverage analysis, and ran security linting on generated code,etc

7. Reflections on Specification-Driven Development (5 points)

7.1 Benefits of AI-Assisted SDD 

What worked incredibly well? How much did this speed up your construction phase compared to manual typing?
7.2 Core Bottlenecks and Challenges 

Where did the paradigm struggle? Discuss issues like context window limitations, AI drifting from the spec, hallucinated package dependencies, or maintaining consistency across large codebases, etc. Complement this with an account of how you have overcome these challenges.
7.3 Lessons Learned & Best Practices 

Go beyond describing activities and critically evaluate the development process.
Support observations with concrete examples from the project (e.g., bugs found, prompt revisions, testing outcomes, or integration issues).
Compare Vibe Coding and SDD using evidence rather than personal preference.
Discuss both successes and limitations of AI-assisted development.
Present actionable best practices that future students could realistically apply.
Conclude with a balanced reflection on how the experience influenced your understanding of software construction and professional software engineering practices.
7.4 . Proposed Specification-Driven Development Workflow  

Propose a Specification-Driven Development (SDD) workflow that could be used by future developers to build similar software systems. Your workflow should be based on your project experience, lessons learned, and the strengths and limitations you observed when using both Specification-Driven Development and Vibe Coding.

A high-quality "Proposed Specification-Driven Development Workflow" section should:

Present a clear, logical, and reusable development workflow rather than simply describing the project's implementation process.
Briefly explain the workflow phase, including its objectives, activities, inputs, outputs, and expected deliverables.
Clearly identify where AI-assisted development or Vibe Coding can be integrated and where human oversight remains essential.
Briefly justify the proposed workflow using evidence and insights gained from the project.
Include a well-structured process diagram that effectively communicates the proposed development lifecycle.

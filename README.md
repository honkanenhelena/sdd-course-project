## An Experience Report on a Specification-Driven, AI-Assisted Software Construction Project 

Team Details (Team [Insert Team Number/Name]) 

[Helena Honkanen] 

[2403510] 

[e.g., Lead Spec Writer, Prompt Engineer] 

[100%]



 

Executive Summary (Must be included in the report)

Provide a concise summary (200–300 words) of the project. Clearly state:

The system is built, 
The specific formal/semi-formal specification techniques used,
The AI models/tools leveraged (e.g., Cursor, GitHub Copilot, custom LLM pipelines), 
The SDD workflow that you have used in your project
The SDD tool (i.e., Spec-kit) that you have used
The verification and validation method used to ensure that the AI-generated code implements your specifications. 
 

1. Introduction & Paradigm Shift (3 Points)

1.1 Project Overview & Objectives 
The project idea is to create a finance tracker where one can input their spendings and make it easier to possibly cut costs or to just keep track of what they are spending and where.

1.2 The Vibe Coding 

Explain what vibe coding is and how your team approached development using Vibe coding
1.3 The SDD Methodology 

Briefly introduce SDD and how your team approached the project development using Specification-Driven Software Development. Which specific tool has been used and briefly explain the reason behind choosing that tool 
Lastly, briefly explain the project's specifications and scope, and provide a summary of the development timeline. This portion can also be complemented with the workflow of the project (both for Vibe Coding and SDD)
2. Requirements & System Specification: (6 points)

This is the most critical section of the report. It details the "source of truth" you constructed to feed into the AI. 

2.1 Stakeholders:

Brief description of the different stakeholders for your system, and also explain why you have chosen them as system stakeholders.
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

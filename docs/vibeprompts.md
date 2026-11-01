Prompt 1

Prompt: You are an expert software engineer tasked with making an application for managing and tracking expenses with python, FastAPI and SQLite. The frontend should be a web page. The application must allow for adding, editing and removing expenses, and the expenses should have an amount, date, category, information if it was a necessity and an optional note about the expense. It must also include a feature for filtering the expenses and it must have a monthly summary for the expenses by category. The application must have a feature for setting a monthly budget for the categories and it also needs a separate spending chart where the categories can be shown.

Expected answer/result: A working base version which would fill the basic requests and be built with the correct tech stack.

Outcome of prompt: A base version which does look professional and seems to deliver on most basics, but it is missing some features and has some flaws. Main features that were directly asked for that are missing or broken are: Filtering by the date, for this to work there ofcourse also needs to be a monthly or global list somewhere for the expenses, the budgets cant be edited in any intuitive way and instead need the user to resubmit the budget for the category, the budgets are also missing a delete button and feature completely since they cant be re-submitted with the value at 0, this is also one thing the AI has invented since a user may want a total 0 budget on something a certain month. 
A feature that was not explicitly asked for but that the AI decided for was to show all of the categories in the budget section, even though they did not have budgets set. So once a category got a budget all of the other categories were also listed on the budgets list even if they had no budget set.

Type of prompt: Initial vibe code core idea prompt


Prompt 2

Prompt: There are some parts missing, I wanted filtering by date, I need the budgets to have a button to edit and remove them, and the budget list shows categories which dont have budgets, the user also cant add a budget of 0 for a category.

Expected answer/result: Fixes to all requested issues with a possibility of an additional feature by the AI

Outcome of prompt: A very clean fix to all of the issues listed, date filtering was added with an additional clear dates button that was not asked for but nice to have. The budgets were also fixed to only show categories with budgets and now budgets with a value of 0 could be added. One thing however which was noticed when testing this version was that the selection of category when adding an expense did not suggest existing categories, but the user instead had to remember them and make sure the letters were capitalized the same. One obvious missing part was also the visual spending chart which should show the different categories and their respective parts of the total. 

Prompt 3

Prompt: The category selection when creating a new expense should recommend existing ones. There is also still no visual spending chart with a visual representation of the different categories and their parts of the total. 

Expected answer/result: It fixes what was asked of it and the final result is an application which fills all of the criteria. 

Outcome of the prompt: Both requested fixes were completed and nothing else unnecessary was added. The application now fulfills the requirements set for it so it was deemed to be the correct time to stop the vibe coded part. 


Summary of vibe coded version:

The total active time working with the vibe coded version and testing the produced versions ~1.5 hours. The copilot Chatgpt luna 6 model received 3 prompts and with these it completed 7/7 requested items. 
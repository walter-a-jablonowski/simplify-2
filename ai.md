Any Clarifying questions for this prompt?

Create a Python application to identify and manage duplicate/similar information across a large file system using AI-powered content understanding. We want to identify duplicate "ideas" in multiple files, which means parts of the file contents needs to be compared.

ChatGPT made a sample using python FAISS which you can see in sample.py. Use that as a starting point for an application.

UI

- Simple web interface with Bootstrap, keep UI implementation simple
- text box for entering text to look for
- below result list of files that have semantically similar information
  - I want to be able to edit found text files in the app itself
  - best would be: load the file in an editable element with limied height and scroll to the relevant portion of the file
  - per list entry also include a save button and a buttonthat can be used to open the folder where a file is in window explorer

Misc

- file formats in tree: most are markdown, but also txt, all kind of plain text formats
- Performant storage of indexed information
- Performant enough for use with a large file system tree

Also add demo files an folders in folder /debug

 --

Clarification:

Sound good overall, here are some comments on that to consider

- The root dir currently is /debug, make the default root editable in content and add an url arg
- I am unsure if we need the watchdog here, updating the index when I press a button is enough
- Of source we need to compare parts of files as given on the requirements
- No auth
- We edit typical text file types only
- Keep the web ui as simple as possible, Flask sounds too complicated

I think we can implement now

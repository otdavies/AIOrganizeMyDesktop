# AIOrganizeMyDesktop
Too lazy to organize my desktop, make gpt + BLIP-2 do it

# Running it
- You need python installed, 3.7+
- An [OpenAI API key](https://platform.openai.com/account/api-keys) (for gpt-3.5, file naming, and file grouping suggestions)
- You will need to pip install these libraries:
`pip install pillow transformers torch openai`
  
- You'll need to add an .env file in the same directory as the main.py. Put your OpenAI key in there, nothing else.
- Update the `path` variable in main.py.
- Run `python main.py "Path/to/your/folder"`

# Adding `Organize Files` to your windows right click options:
- run `python install.py`, this will need admin access to add it to the right click option menu.
- run `python uninstall.py` to remove it from the right click menu
  

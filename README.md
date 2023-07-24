# AIOrganizeMyDesktop
*Too lazy to organize my desktop, make gpt + BLIP-2 do it*

![sRmr39vcIm](https://github.com/otdavies/AIOrganizeMyDesktop/assets/3145170/b1f1d44a-fa69-42b7-93a6-ef241f23de86)
![NVIDIA_Share_ilWV3RypOw](https://github.com/otdavies/AIOrganizeMyDesktop/assets/3145170/0abd3bc2-9e3f-4558-af04-66dbc2cac17f)
![cmd_wqTJmnsPIL](https://github.com/otdavies/AIOrganizeMyDesktop/assets/3145170/2929698f-665b-440e-806b-ffa68a0fc1e0)

Renames image files based on content (BLIPv2):

![explorer_yNHkNprOD9](https://github.com/otdavies/AIOrganizeMyDesktop/assets/3145170/6cbbe3c5-9876-4ca3-9d96-da26d4cc9375)


# Running it
- You need python installed, 3.7+
- An [OpenAI API key](https://platform.openai.com/account/api-keys) (for gpt-3.5, file naming, and file grouping suggestions)
- You will need to pip install these libraries:
`pip install pillow transformers torch openai`
  
- You'll need to add an .env file in the same directory as the main.py. Put your OpenAI key in there, nothing else.
- Run `python main.py "Path/to/your/folder"`

# Adding `Organize Files` to your windows right click options:
- run `python install.py`, this will need admin access to add it to the right click option menu.
- run `python uninstall.py` to remove it from the right click menu

# Disclaimer
- This is a toy example and might damage your file organization. Use at your own risk.
  

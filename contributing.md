# Contribution Guide

Please follow the instructions on this guide when making contributions to the JCT Discord Bot.

## Contributing

### 1 - Creating an Issue

When making a contribution, whether to fix a bug, or to add a new feature, first **create an issue** if it doesn't already exist, outlining briefly what needs to be accomplished. (Note each issue has an issue number by which we will reference it later on.)

Once the issue exists, **add any appropriate labels**, then add it to the project **JCT Discord Bot**. (This can be accomplished on the issue's page on GitHub, on the right hand side on desktop, or at the bottom on mobile.) Then you can **assign yourself** to the issue.

### 2 - Creating a Branch

Create a branch for the contribution you are making. If it is a new command you want to add, simply name the branch the same as the command (without the command prefix). If it is a bug you want to fix or something else, come up with some descriptive yet concise name for the branch.

This name will be referred to as _my_feature_ throughout this guide.

### 3 - Writing the Code

Now you can write your code to implement your feature. You can commit and push to the dedicated branch as often and whenever you like.

Please check out the [style guide](style_guide.md).

#### 3.1 - Creating the Cog

Create a file `/modules/my_feature/cog.py` (where _my_feature_ is the name of your command or feature) for whatever you feature you want to add. Create a class which inherits from `commands.Cog`, and define its constructor as follows.

```py
from discord.ext import commands

class MyFeatureCog(commands.Cog):
	"""A cog which has no features and does nothing"""
	def __init__(self, bot: commands.Bot):
		self.bot = bot
```

Then as methods to that class, add any functions you need for the bot. For example:

````py
	@commands.command(name='my_feature')
	async def my_feature(self, ctx: commands.Context, n: int, word: str):
		"""A command which takes two arguments and does nothing

		Usage:
		```
		++my_feature num, word
		```
		Arguments:

			> **num**: A number with no meaning
			> **word**: Any word you like

		"""

		# log in console that a ping was received
		print('Executing command "my_feature".')

		# reply with a message
		await ctx.send(f"Command received with num {n} and word {word}.")
````

Finally, (this part is important,) add a function (outside the class) to add an instance of the class you've created (which is a "cog") to the bot.

```py
def setup(bot: commands.Bot):
	bot.add_cog(MyFeatureCog(bot))
```

#### 3.2 - Additional files

If you need additional files, be it python modules (`.py` files with functions and/or classes) or other files such as `.txt`, `.json`, etc, you can put them in `/modules/my_feature/`

##### 3.2.1 - Using Additional Python Files

Suppose your additional file is `/modules/my_feature/foo.py` and it contains a class or function `bar`.

You can import the file from anywhere with any one of the following.

```py
import modules.my_feature.foo           # access bar with: modules.my_feature.foo.bar
import modules.my_feature.foo as foo    # access bar with: foo.bar
from modules.my_feature.foo import bar  # access bar with: bar
```

##### 3.2.2 - Using Additional Data Files

You can add any data files you want to read from your python code in the `/modules/my_feature/` folder. (Let's call one such file `biz.txt`.) To read them from your code, you can access them with the path relative to the repository root. For example:

```py
with open('modules/my_feature/biz.txt') as biz:
	pass
```

#### 3.3 - Error Handling

If when trying to have the bot perform some action based on something a user said, you have to inform the user of an error, you can use the `FriendlyError` class to do so as follows:

```py
from modules.error.friendly_error import FriendlyError
#...
raise FriendlyError("user friendly error message", channel, member)
```

where `channel` is of type `discord.TextChannel` and `member` is of type `discord.Member`. Optionally, you can also pass as internal Exception, if applicable, and the error will be logged to `err.log`.

When raising a `FriendlyError`, the message passed to it will be sent to the channel provided, tagging `member` if a member was passed.

### 4 - Testing your Code

You may want to add the bot to your own server to test stuff yourself first. To do so, [invite the bot to your server](https://discord.com/api/oauth2/authorize?client_id=796039233789100053&permissions=8&scope=bot).

To run the bot locally, you may want to first disable the hosted version of the bot, otherwise the bot will react to everything twice. Ask [Jonah Lawrence](https://github.com/DenverCoder1) for permission to manage the hosting service if necessary.

You will also need the `.env` file in the project's root directory. Again, ask [Jonah Lawrence](https://github.com/DenverCoder1) for this file, or check the pinned messages in the `#jct-bot-development` Discord channel.

You will need to make sure you have the all the necessary libraries installed. The best way to do this is to install everything you need into a virtual environment. You can do this by typing the following commands in your terminal.

```
python -m venv .venv  # creates a virtual environment in a folder called .venv

# activate the virtual environment (use only one of these two commands)
source .venv/bin/activate # for bash/zsh (you'll need this one if you're on linux or mac, or if you're using bash on windows)
.venv\Scripts\activate # for cmd.exe (you'll probably need this one if you're on windows and don't know what bash is)

# install everything you need
pip install -r requirements.txt
pip install -r requirements.dev.txt
```

Now you should be able to run the bot locally. Well done!
```sh
python bot.py
```

### 5 - Creating a Pull Request

Once you have tested your feature and you think it is ready to be deployed, you can go ahead and **create a pull request** on GitHub to merge your branch to the Main branch.

Start the description of the pull request with the line `Close #N` (where `N` is the number of the issue) in order to link the pull request with the corresponding issue. (This can also be done manually after the PR is created, but it's preferable if you do it this way.)

Once the pull request is made, or while creating it, **add a reviewer** to your pull request. They will review your changes and additions, and if they approve, you can merge your pull request.

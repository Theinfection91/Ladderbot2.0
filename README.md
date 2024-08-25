**NEW 3.0 VERSION OUT**:
- https://github.com/Theinfection91/Ladderbot3.0

# Discord Ladderbot

The predecessor to **Ladderbot3.0**, Ladderbot2.0 is a Discord bot designed to manage and facilitate challenges between teams in a ladder-style competition. Teams can challenge others, track their rankings, and receive notifications when they are challenged.

## Features

- **Team Management**: Create and manage teams, including adding members and tracking wins and losses.
- **Challenge System**: Teams can challenge others up to two ranks above them. Challenges are exclusive and prevent other teams from challenging or being challenged until resolved.
- **Notifications**: Team members receive notifications when their team is challenged.

# Discord Bot Token Usage

To properly use the Discord bot token with your program, you have two options: manually entering the token directly in the code or using a separate Python file to import the token.

## Option 1: Manual Token Entry

1. **Delete the import statement:**

   If you prefer to manually enter your token, remove the following line from the top of your code:
   
   ```python
   from my_token import MY_DISCORD_TOKEN

2. **Add your token in the main() function:**

   In the main() function located at the very bottom of the code, replace the MY_DISCORD_TOKEN variable with your actual Discord bot token. Make sure to enclose the token string in single quotes:

   ```python
   await bot.start('your_discord_token_here')
   ```
   This method is straightforward but requires you to manually edit your code whenever you want to change the token.

## Option 2: Import Token from a Separate File

1. **Create a my_token.py file:**

   If you prefer to keep your token separate, create a new file called my_token.py in the same directory as ladderbot2.py

2. **Add your token to my_token.py:**

   Inside my_token.py, include the following line of code, replacing 'your_long_discord_token_here' with your actual token. Again, make sure to enclose the token string in single quotes:

   ```python
   MY_DISCORD_TOKEN = 'your_discord_token_here'
   ```

3. **Keep the import statement:**

   Ensure that the following line remains at the top of your main script:

   ```python
   from my_token import MY_DISCORD_TOKEN
   ```
   
   This method allows you to easily manage your token without modifying the main bot script each time.

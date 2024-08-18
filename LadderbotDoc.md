# Ladder Bot Documentation v2.0

## Overview
The Ladder Bot manages a competitive ladder where teams can challenge each other and move up or down the ranks based on match results. This bot handles team registration, match reporting, challenge management, and more.

## Commands

### Registering a Team
- **Command:** `!register_team <team_name> <@member1> <@member2> ...`
- **Description:** Registers a new team with the specified members.
- **Parameters:**
  - `<team_name>`: The name of the team to be registered.
  - `<@member1>, <@member2>, etc.`: Mentions of Discord users who are members of the team. If no members are mentioned, the command creator will be added as the sole member.
- **Example:** `!register_team Alpha @User1 @User2`
- **Response:** Confirms registration and lists the team members.
- **Permissions:** Any user can register a team.

### Removing a Team
- **Command:** `!remove_team <team_name>`
- **Description:** Removes a team from the ladder.
- **Parameters:**
  - `<team_name>`: The name of the team to be removed.
- **Example:** `!remove_team Alpha`
- **Response:** Confirms removal of the given team.
- **Permissions:** Admin only.

### Starting the Ladder
- **Command:** `!start_ladder`
- **Description:** Initializes the ladder, sorting teams alphabetically and assigning initial ranks.
- **Parameters:** None.
- **Example:** `!start_ladder`
- **Response:** Confirms that the ladder has been started and posts the initial standings.
- **Permissions:** Admin only.

### Challenging a Team
- **Command:** `!challenge <challenger_team> <team_name>`
- **Description:** The `challenger_team` challenges `team_name`. The challenger can only challenge a team up to two ranks higher.
- **Parameters:**
  - `<challenger_team>`: The name of the team initiating the challenge.
  - `<team_name>`: The name of the team being challenged.
- **Example:** `!challenge Bravo Alpha`
- **Response:** Confirms the challenge and lists the teams involved.
- **Permissions:** Any user can challenge if the ladder is running.

### ADMIN - Challenging a Team
- **Command:** `!admin_challenge <challenger_team> <team_name>`
- **Description:** An Admin forces a challenge between `challenger_team` and `team_name`.
- **Parameters:**
  - `<challenger_team>`: The name of the team initiating the challenge.
  - `<team_name>`: The name of the team being challenged.
- **Example:** `!admin_challenge Bravo Alpha`
- **Response:** Confirms the challenge and lists the teams involved, states an Admin has issued this command.
- **Permissions:** Admin only.

### Cancelling a Challenge
- **Command:** `!cancel_challenge <team_name>`
- **Description:** Cancel the challenge sent out by `team_name`.
- **Parameters:**
  - `<team_name>`: The name of the team that sent out a challenge that you want to delete.
- **Example:** `!cancel_challenge Bravo`
- **Response:** Confirms the challenge was canceled
- **Permissions:** Everyone

### ADMIN - Cancelling a Challenge
- **Command:** `!admin_cancel_challenge <team_name>`
- **Description:** Cancel the challenge sent out by `team_name`.
- **Parameters:**
  - `<team_name>`: The name of the team that sent out a challenge that you want to delete.
- **Example:** `!admin_cancel_challenge Echo`
- **Response:** Confirms the challenge was canceled by an Admin
- **Permissions:** Admins Only

### Post Challenges
- **Command:** `!post_challenges`
- **Description:** Shows all challenges currently on the board.
- **Parameters:** None.
- **Example:** `!post_challenges`
- **Response:** Posts all the challenges currently going on.
- **Permissions:** Everyone

### Setting the Challenges Channel
- **Command:** `!set_challenges_channel <#channel>`
- **Description:** Sets the channel where challenges will be posted.
- **Parameters:**
  - `<#channel>`: The channel where challenges will be posted.
- **Example:** `!set_challenges_channel #standings`
- **Response:** Confirms the new challenges channel.
- **Permissions:** Admin only.

### Clearing the Challenges Channel
- **Command:** `!clear_challenges_channel`
- **Description:** Clears the channel that was set with !set_challenges_channel
- **Parameters:** None.
- **Example:** `!clear_challenges_channel`
- **Response:** Confirms the challenges channel id was cleared, if no ID was found a message is displayed saying so.
- **Permissions:** Admin only.

### Reporting a Win
- **Command:** `!report_win <winning_team>`
- **Description:** Reports the result of a match, adjusting ranks accordingly.
- **Parameters:**
  - `<winning_team>`: The name of the team that won the match.
- **Example:** `!report_win Alpha`
- **Response:** Updates the ranks and confirms the match result.
- **Permissions:** Any member of the involved teams can report a win.

### ADMIN - Reporting a Win
- **Command:** `!admin_report_win <winning_team>`
- **Description:** Reports the result of a match, adjusting ranks accordingly. Admin Only
- **Parameters:**
  - `<winning_team>`: The name of the team that won the match.
- **Example:** `!admin_report_win Delta`
- **Response:** Updates the ranks and confirms the match result and says it was performed by an Admin/
- **Permissions:** Admins Only

### Posting Standings
- **Command:** `!post_standings`
- **Description:** Displays the current standings.
- **Parameters:** None.
- **Example:** `!post_standings`
- **Response:** Lists the current rankings of all teams.
- **Permissions:** Any user can post standings if the ladder is running.

### Setting the Standings Channel
- **Command:** `!set_standings_channel <#channel>`
- **Description:** Sets the channel where standings will be posted.
- **Parameters:**
  - `<#channel>`: The channel where standings will be posted.
- **Example:** `!set_standings_channel #standings`
- **Response:** Confirms the new standings channel.
- **Permissions:** Admin only.

### Clearing the Standings Channel
- **Command:** `!clear_standings_channel`
- **Description:** Clears the channel that was set with !set_standings_channel
- **Parameters:** None.
- **Example:** `!clear_standings_channel`
- **Response:** Confirms the standings channel id was cleared, if no ID was found a message is displayed saying so.
- **Permissions:** Admin only.

### Adjusting Team Rank
- **Command:** `!set_rank <team_name> <rank>`
- **Description:** Manually sets a team's rank.
- **Parameters:**
  - `<team_name>`: The name of the team whose rank is being adjusted.
  - `<rank>`: The new rank for the team.
- **Example:** `!set_rank Alpha 1`
- **Response:** Updates the team's rank and adjusts other teams' ranks as needed.
- **Permissions:** Admin only.

### Adding a Win
- **Command:** `!add_win <team_name>`
- **Description:** Manually adds a win to a team.
- **Parameters:**
  - `<team_name>`: The name of the team to which the win is being added.
- **Example:** `!add_win Alpha`
- **Response:** Informs that a win has been added and updates the team's win count.
- **Permissions:** Admin only.

### Subtracting a Win
- **Command:** `!subtract_win <team_name>`
- **Description:** Manually subtracts a win from a team.
- **Parameters:**
  - `<team_name>`: The name of the team from which the win is being subtracted.
- **Example:** `!subtract_win Alpha`
- **Response:** Informs that a win has been subtracted and updates the team's win count.
- **Permissions:** Admin only.

### Adding a Loss
- **Command:** `!add_loss <team_name>`
- **Description:** Manually adds a loss to a team.
- **Parameters:**
  - `<team_name>`: The name of the team to which the loss is being added.
- **Example:** `!add_loss Alpha`
- **Response:** Informs that a loss has been added and updates the team's loss count.
- **Permissions:** Admin only.

### Subtracting a Loss
- **Command:** `!subtract_loss <team_name>`
- **Description:** Manually subtracts a loss from a team.
- **Parameters:**
  - `<team_name>`: The name of the team from which the loss is being subtracted.
- **Example:** `!subtract_loss Alpha`
- **Response:** Informs that a loss has been subtracted and updates the team's loss count.
- **Permissions:** Admin only.

### Ending the Ladder
- **Command:** `!end_ladder`
- **Description:** Ends the ladder and clears all data.
- **Parameters:** None.
- **Example:** `!end_ladder`
- **Response:** Posts final standings, announces winners, and clears all teams and matches.
- **Permissions:** Admin only.

### Show Documentation Link
- **Command:** `!show_help`
- **Description:** Provides a link to the Ladder Bot's documentation.
- **Parameters:** None.
- **Example:** `!show_help`
- **Response:** Provides a GitHub link to the documentation.
- **Permissions:** Anyone.

# v2.0
import discord
from discord.ext import commands, tasks
import json
import os
import time

class Ladderbot(commands.Cog):
    """
    --LADDERBOT 2.0--
    Created by Ixnay (Chase Carter)
    

    This is a refactored class from all the functions
    that made up Ladderbot 1.x
    """
    def __init__(self, bot):
        """
        Initializes a new instance of the Ladderbot class.

        Initializes the bot, teams, matches, channels, and file paths.
        Loads data from teams.json, matches.json, and state.json files.
        """
        self.bot = bot

        # Variables to hold the data from teams.json and matches.json
        self.teams = {}
        self.matches = {}

        # Variables for the designated channels for seperate Standings and Challenges data
        self.standings_channel_id = None
        self.challenges_channel_id = None

        # Variable for updating seperate Standings and Challenges channel message
        self.standings_message = None
        self.challenges_message = None

        # Flag for whether or not the ladder is currently running, pulled from state.json
        self.ladder_running = False

        # File paths
        self.TEAMS_FILE = 'teams.json'
        self.MATCHES_FILE = 'matches.json'
        self.STATE_FILE = 'state.json'

        # Load data from .json files
        self.load_teams()
        self.load_matches()
        self.load_state()
    
    def load_teams(self):
        """
        LOAD data from teams.json
        """
        if os.path.exists(self.TEAMS_FILE):
            with open(self.TEAMS_FILE, 'r') as f:
                self.teams = json.load(f)
    
    def load_matches(self):
        """
        LOAD data from matches.json
        """
        if os.path.exists(self.MATCHES_FILE):
            with open(self.MATCHES_FILE, 'r') as f:
                self.matches = json.load(f)
    
    def load_state(self):
        """
        LOAD data from state.json
        """
        if os.path.exists(self.STATE_FILE):
            with open(self.STATE_FILE, 'r') as f:
                state = json.load(f)
                self.standings_channel_id = state.get('standings_channel_id', None)
                self.challenges_channel_id = state.get('challenges_channel_id', None)
                self.ladder_running = state.get('ladder_running', False)

    def save_teams(self):
        """
        SAVE data to teams.json
        """
        with open(self.TEAMS_FILE, 'w') as f:
            json.dump(self.teams, f)

    def save_matches(self):
        """
        SAVE data to matches.json
        """
        with open(self.MATCHES_FILE, 'w') as f:
            json.dump(self.matches, f)

    def save_state(self):
        """
        SAVE to state.json
        """
        state = {
            'standings_channel_id': self.standings_channel_id,
            'challenges_channel_id': self.challenges_channel_id,
            'ladder_running': self.ladder_running
        }
        with open(self.STATE_FILE, 'w') as f:
            json.dump(state, f)
    
    @commands.Cog.listener()
    async def on_ready(self):
        """
        A listener method used to keep track of
        if the ladder is running and also the locations
        of the seperate standings and
        challenges channels.
        """
        print(f"Logged in as {self.bot.user}")
        if self.ladder_running:
            print("The ladder is currently running.")
            if self.standings_channel_id:
                channel = self.bot.get_channel(self.standings_channel_id)
                if channel:
                    await self.update_standings_message(channel)
                    self.periodic_update_standings.start()

    def normalize_ranks(self):
        """
        Helper method used to normalize ranks when
        removing teams, setting ranks, etc.
        """
        sorted_teams = sorted(self.teams.items(), key=lambda x: x[1]['rank'])
        new_rank = 1
        for team_name, team_data in sorted_teams:
            if team_data['rank'] is not None:
                team_data['rank'] = new_rank
                new_rank += 1
    
    @commands.command()
    async def register_team(self, ctx, team_name, *members: discord.Member):
        """
        Method that all level of users can call on
        to create a new team with specific members.

        If no members are given, a team is created with
        only the user who called on it as the sole
        person on the team.
        """
        if team_name in self.teams:
            await ctx.send(f"Team {team_name} already exists, please choose a different team name.")
            return
        
        # Grabs the ID of every member used as a parameter for this method and stores it
        team_members = [member.id for member in (members or [ctx.author])]

        # Each newly created team will start in the last most place in standings
        add_team_rank = len(self.teams) + 1

        self.teams[team_name] = {
            'members': team_members,
            'rank': add_team_rank,
            'wins': 0,
            'losses': 0
        }

        self.save_teams()
        member_names = [ctx.guild.get_member(member_id).display_name for member_id in team_members]
        await ctx.send(f"Team {team_name} has been registered with members {', '.join(member_names)}.")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def remove_team(self, ctx, team_name):
        """
        An Admin only method for removing a
        specified team name.
        """
        if team_name not in self.teams:
            await ctx.send(f"Team {team_name} does not exist.")
            return
        
        if team_name in self.teams:
            del self.teams[team_name]
            self.normalize_ranks()
            self.save_teams()
            await ctx.send(f"An Admin has removed Team {team_name} from the ladder.")
    
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def start_ladder(self, ctx):
        """
        Admin only method to start the ladder.
        """
        if self.ladder_running:
            await ctx.send("The ladder is already running.")
            return
        
        self.ladder_running = True
        self.normalize_ranks()
        self.save_teams()
        self.save_state()
        await self.post_standings(ctx)
        await ctx.send("The ladder has been started!")
    
    @commands.command()
    async def challenge(self, ctx, challenger_team, team_name):
        """
        Normal challenge command that EVERYONE can use.

        Takes the challenger team and the team they want
        to challenge as the arguments. 

        Only members of the challenging team can send
        out challenges on their teams behalf.
        """
        # Checks if the ladder is running
        if not self.ladder_running:
            await ctx.send("The ladder has not been started yet.")
            return
        
        # Ensure the challenger is part of the challenging team
        if ctx.author.id not in self.teams[challenger_team]['members']:
            await ctx.send("You are not part of the challenging team.")
            return
        
        # Checks if both teams exist in teams.json
        if challenger_team not in self.teams or team_name not in self.teams:
            await ctx.send("One or both teams do not exist.")
            return
        
        # Holds the rank of each team
        challenger_rank = self.teams[challenger_team]['rank']
        challenged_rank = self.teams[team_name]['rank']
        
        # Calculates to see if challenge is within the rank range of 2 above at most
        if challenged_rank > challenger_rank or challenged_rank <= challenger_rank - 3:
            await ctx.send(f"You can only challenge teams up to two ranks above your current rank.")
            return
        
        # Check if either team is currently involved in another challenge, if so then cancel
        for match in self.matches.values():
            if (match['challenged'] == team_name or match['challenger'] == team_name or
            match['challenged'] == challenger_team or match['challenger'] == challenger_team):
                await ctx.send(f"One or both of these teams are currently involved in a match.")
                return
            
        # If all checks are passed, create and add the new challenge to matches.json
        match_id = f"{challenger_team}"
        self.matches[match_id] = {
            'challenger': challenger_team,
            'challenged': team_name,
            'status': 'pending'
        }
        self.save_matches()
        await ctx.send(f"{challenger_team} has challenged {team_name}!")

    @commands.command()
    async def cancel_challenge(self, ctx, team_name):
        """
        A team that has sent out a challenge in mistake
        can use this method to cancel it.
        """
        # Check if given team name actually exists in teams.json
        if team_name not in self.teams:
            await ctx.send(f"Team {team_name} does not exist.")
            return

        # Check if the given team name has an active challenge sent out
        match_id = next((key for key, value in self.matches.items() if value['challenger'] == team_name), None)

        # If no sent challenge is found from team_name, stop method and print message
        if not match_id:
            await ctx.send(f"Team {team_name} does not have an active challenge.")
            return
        
        # Ensure the author who called command is part of team that is trying to cancel the challenge
        if ctx.author.id not in self.teams[team_name]['members']:
            await ctx.send(f"You are not part of Team {team_name} and may not cancel their challenge!")
            return
        
        # Cancel the challenge and print confirmation message
        del self.matches[match_id]
        self.save_matches()
        await ctx.send(f"The challenge issued by {team_name} has been successfully canceled.")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def admin_challenge(self, ctx, challenger_team, team_name):
        """
        Admin only method so that an admin can
        manually set up challenges if need be.
        """
        # Checks if the ladder is running
        if not self.ladder_running:
            await ctx.send("The ladder has not been started yet.")
            return
        
        # Checks if both teams exist in teams.json
        if challenger_team not in self.teams or team_name not in self.teams:
            await ctx.send("One or both teams do not exist.")
            return
        
        # Holds the rank of each team
        challenger_rank = self.teams[challenger_team]['rank']
        challenged_rank = self.teams[team_name]['rank']
        
        # Calculates to see if challenge is within the rank range of 2 above at most
        if challenged_rank > challenger_rank or challenged_rank <= challenger_rank - 3:
            await ctx.send(f"Teams can only challenge other teams up to two ranks above their current rank.")
            return
        
        # Check if either team is currently involved in another challenge, if so then cancel
        for match in self.matches.values():
            if (match['challenged'] == team_name or match['challenger'] == team_name or
            match['challenged'] == challenger_team or match['challenger'] == challenger_team):
                await ctx.send(f"One or both of these teams are currently involved in a match. Admin challenge canceled.")
                return
            
        # If all checks are passed, create and add the new challenge to matches.json
        match_id = f"{challenger_team}"
        self.matches[match_id] = {
            'challenger': challenger_team,
            'challenged': team_name,
            'status': 'pending'
        }
        self.save_matches()
        await ctx.send(f"An Admin has manually created this challenge: {challenger_team} has challenged {team_name}!")
    
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def admin_cancel_challenge(self, ctx, team_name):
        """
        Admin only method for handling canceling challenges
        sent out by a given team.
        """
        # Check if given team name actually exists in teams.json
        if team_name not in self.teams:
            await ctx.send(f"Team {team_name} does not exist.")
            return

        # Check if the given team name has an active challenge sent out
        match_id = next((key for key, value in self.matches.items() if value['challenger'] == team_name), None)

        # If no sent challenge is found from team_name, stop method and print message
        if not match_id:
            await ctx.send(f"Team {team_name} does not have an active challenge.")
            return
        
        # Cancel the challenge and print confirmation message
        del self.matches[match_id]
        self.save_matches()
        await ctx.send(f"The challenge issued by {team_name} has been successfully canceled by an Admin.")
    
    @commands.command()
    async def report_win(self, ctx, winning_team):
        """
        This is the report_win method that everyone
        will have access to.

        If the winning team is a challenger team then
        they will either move up one rank or two ranks,
        depending on how far up they challenged in
        the ladder.

        If the winning team is a challenged team then
        no rank changes will occur as they defended
        their rank.
        """
        # Check if the winning team is in matches.json
        match = next((m for m in self.matches.values() if m['challenger'] == winning_team or m['challenged'] == winning_team), None)
        if match is None:
            await ctx.send(f"There is no match involving {winning_team}.")
            return

        # Ensure the author is part of either the winning or losing team
        if ctx.author.id not in self.teams[match['challenger']['members']] and ctx.author.id not in self.teams[match['challenged']['memers']]:
            await ctx.send("You are not part of this match.")
            return
        
        # Determine the loser team
        loser_team = match['challenged'] if match['challenger'] == winning_team else match['challenger']
        winner_team = winning_team

        # If the winning team was a challenger then rank changes need to occur
        if winner_team == match['challenger']:
            # Challenger wins - update ranks
            losing_rank = self.teams[loser_team]['rank']

            # Winner team takes the loser's rank on the ladder
            self.teams[winner_team]['rank'] = losing_rank

            # The loser team moves down on rank
            self.teams[loser_team]['rank'] += 1

            # Shift teams ranked below the losing team down by one
            for team_name, team_data in self.teams.items():
                if team_name != winner_team and team_name != loser_team and team_data['rank'] >= self.teams[loser_team]['rank']:
                    team_data['rank'] += 1
            
            # Normalize ranks for safe measure
            self.normalize_ranks()

            # Send message confirmation about win and rank changes
            await ctx.send(f"Team {winning_team} has won the match and taken the rank of Team {loser_team}! Team {loser_team} moves down one in the ranks...")
        
        # If winning team is a challenged team
        else:
            # Challenger loses - no rank change occurs.
            await ctx.send(f"Team {loser_team} has lost their match against Team {winning_team}... No rank changes occur.")

        # Update wins and losses for both teams
        self.teams[winning_team]['wins'] += 1
        self.teams[loser_team]['losses'] += 1

        # Remove the match from matches.json, then save it and teams.json
        del self.matches[match['challenger']]
        self.save_teams()
        self.save_matches()

        #Post the newly updated standings
        await self.post_standings(ctx)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def admin_report_win(self, ctx, winning_team):
        """
        This is the report_win method that only
        Admins will have access to.

        This method works the exact same as the
        report_win method, but is only accessible
        by an Admin and does not require the author
        to be part of the match.
        """
        # Check if the winning team is in matches.json
        match = next((m for m in self.matches.values() if m['challenger'] == winning_team or m['challenged'] == winning_team), None)
        if match is None:
            await ctx.send(f"There is no match involving {winning_team}.")
            return
        
        # Determine the loser team
        loser_team = match['challenged'] if match['challenger'] == winning_team else match['challenger']
        winner_team = winning_team

        # If the winning team was a challenger then rank changes need to occur
        if winner_team == match['challenger']:
            # Challenger wins - update ranks
            losing_rank = self.teams[loser_team]['rank']

            # Winner team takes the loser's rank on the ladder
            self.teams[winner_team]['rank'] = losing_rank

            # The loser team moves down on rank
            self.teams[loser_team]['rank'] += 1

            # Shift teams ranked below the losing team down by one
            for team_name, team_data in self.teams.items():
                if team_name != winner_team and team_name != loser_team and team_data['rank'] >= self.teams[loser_team]['rank']:
                    team_data['rank'] += 1
            
            # Normalize ranks for safe measure
            self.normalize_ranks()

            # Send message confirmation about win and rank changes
            await ctx.send(f"Team {winning_team} has won the match and taken the rank of Team {loser_team}! Team {loser_team} moves down one in the ranks... -This report was made by an Admin.")
        
        # If winning team is a challenged team
        else:
            # Challenger loses - no rank change occurs.
            await ctx.send(f"Team {loser_team} has lost their match against Team {winning_team}... No rank changes occur. -This report was made by an Admin.")

        # Update wins and losses for both teams
        self.teams[winning_team]['wins'] += 1
        self.teams[loser_team]['losses'] += 1

        # Remove the match from matches.json, then save it and teams.json
        del self.matches[match['challenger']]
        self.save_teams()
        self.save_matches()

        # Post the newly updated standings
        await self.post_standings(ctx)
    
    @commands.command()
    async def post_challenges(self, ctx):
        """
        This method posts the current challenges
        in the matches.json file.
        """
        # Check if matches.json has any data inside of it
        if not self.matches:
            await ctx.send("There are currently no active challenges on the board.")
            return
        
        # Format the list of current challenges
        challenge_list = []
        for match_id, match_info in self.matches.items():
            challenger = match_info['challenger']
            challenged = match_info['challenged']
            challenge_list.append(f"**Match ID**: {match_id}\n**Challenger**: {challenger}\n**Challenged**: {challenged}\n")
        
        # Join all challenges from challenge_list into a single string
        challenges_text = "\n".join(challenge_list)

        # Send the list of challenges
        await ctx.send(f"**Current Challenges**:\n{challenges_text}")
    
    @commands.command()
    async def post_standings(self, ctx):
        """
        Callable method by everyone to post the
        standings in the channel this is called from
        """

        # Sort the teams by rank
        sorted_teams = sorted(self.teams.items(), key=lambda x: (x[1]['rank'] is None, x[1]['rank']))

        # Variable to hold data before we join it into a string
        standings_list = []

        # Iterate through every team in our sorted teams
        for team in sorted_teams:
            if team[1]['rank'] is not None:
                
                # Collect names of members on each team
                member_names = []
                for member_id in team[1]['members']:
                    try:
                        user = await self.bot.fetch_user(member_id)
                        member_names.append(user.display_name)
                    except discord.NotFound:
                        member_names.append("Unknown User")
                    except discord.HTTPException:
                        member_names.append("Fetch Error")
                
                # Format the team information into something kind of pretty
                standings_list.append(f"{team[1]['rank']}. {team[0]} ({' - '.join(member_names)}) - W: {team[1]['wins']} L: {team[1]['losses']}")
        
        # Join everything from standings_list into one string
        standings = "\n".join(standings_list)

        # Send standings to the channel where the command was called
        await ctx.send(f"**Current Standings**:\n{standings}")
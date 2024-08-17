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
        Method for loading data from teams.json
        """
        if os.path.exists(self.TEAMS_FILE):
            with open(self.TEAMS_FILE, 'r') as f:
                self.teams = json.load(f)
    
    def load_matches(self):
        """
        Method for loading data from matches.json
        """
        if os.path.exists(self.MATCHES_FILE):
            with open(self.MATCHES_FILE, 'r') as f:
                self.matches = json.load(f)
    
    def load_state(self):
        """
        Method for loading data from state.json
        """
        if os.path.exists(self.STATE_FILE):
            with open(self.STATE_FILE, 'r') as f:
                state = json.load(f)
                self.standings_channel_id = state.get('standings_channel_id', None)
                self.challenges_channel_id = state.get('challenges_channel_id', None)
                self.ladder_running = state.get('ladder_running', False)

    def save_teams(self):
        """
        Method for saving data to teams.json
        """
        with open(self.TEAMS_FILE, 'w') as f:
            json.dump(self.teams, f)

    def save_matches(self):
        """
        Method for saving data to matches.json
        """
        with open(self.MATCHES_FILE, 'w') as f:
            json.dump(self.matches, f)

    def save_state(self):
        """
        Method to save data to state.json
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
        to create a new team with specific members

        If no members are given, a team is created with
        only the user who called on it as the sole
        person on the team
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
        specified team name
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
        Admin only method to start the ladder
        """
        if self.ladder_running:
            await ctx.send("The ladder is already running.")
            return
        
        self.ladder_running = True
        self.normalize_ranks()
        self.save_teams()
        self.save_state()
        await ctx.send("The ladder has been started!")
    

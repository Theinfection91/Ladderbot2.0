# v2.0
import discord
from discord.ext import commands, tasks
import json
import os
import time

class Ladderbot(commands.Cog):
    """
    LADDERBOT 2.0

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
        print(f"Logged in as {self.bot.user}")
        if self.ladder_running:
            print("The ladder is currently running.")
            if self.standings_channel_id:
                channel = self.bot.get_channel(self.standings_channel_id)
                if channel:
                    await self.update_standings_message(channel)
                    self.periodic_update_standings.start()
    
    @commands.command()
    async def register_team(self, ctx, team_name, *members: discord.Member):
        if team_name in self.teams:
            await ctx.send(f"Team {team_name} already exists, please choose a different team name.")
            return
        
        team_members = [member.id for member in (members or [ctx.author])]
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
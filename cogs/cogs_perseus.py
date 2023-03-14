import discord 
from discord.ext import commands
import string
import sys
import os
sys.path.append(os.path.abspath('./'))
from my_package.perseus1 import Perseus_game

empty_board = []
num_of_rows = 10 + 1#10 + 1
num_of_cols = 18#18
win_num = 5
embed_colour = 0x077ff7 #colour of line on embeds
empty_square = ':black_large_square:'
alp_emoji_text = '🇦 🇧 🇨 🇩 🇪 🇫 🇬 🇭 🇮 🇯 🇰 🇱 🇲 🇳 🇴 🇵 🇶 🇷 🇸 🇹 🇺 🇻 🇼 🇽 🇾 🇿' # discord reaction does not support :emoji_name: 
alp_emoji_text = list(alp_emoji_text.replace(" ", ""))         # so a text-based emoji is needed here
alphabet = list(string.ascii_lowercase)
for char in range(len(alphabet)): alphabet[char] = f':regional_indicator_{alphabet[char]}:'

def make_empty_board(board_use, row, col):
    board = board_use
    for row in range(num_of_rows):
        #board.append([])
        for col in range(num_of_cols):
            if row == num_of_rows - 1: # Last row is an alphabet row
                board[row][col] = alphabet[col]
            else:
                board[row][col] = empty_square

def fill_board(board_use, row, col):
    board = board_use
    emoji = empty_square
    for row in range(num_of_rows - 1):
        for col in range(num_of_cols):
            if board[row][col] != emoji:
                board[row][col] = emoji

def format_board_as_str(board_use, row, col):
    board = board_use
    num_of_rows = row
    num_of_cols = col
    board_as_str = ''
    for row in range(num_of_rows):
        for col in range(num_of_cols):
            board_as_str += (board[row][col])
            if col == num_of_cols - 1:
                board_as_str += "\n"
    return board_as_str


class Perseus(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.play_msg_id = None
        self.game = Perseus_game(num_of_rows - 1, num_of_cols, win_num)
        # offset row by 1 to make space for alphabet row
        self.embed_board = [[' ' for col in range(num_of_cols)] for row in range(num_of_rows)]
        self.player1 = None
        self.player2 = None
        self.p1_emoji = ':o:'
        self.p2_emoji = ':x:'

    @commands.Cog.listener()
    async def on_ready(self):
        print("perseus.py is Online!")

    @commands.command(aliases=['ps', 'game'])
    async def perseus(self, ctx):
        if(self.play_msg_id != None): 
            await ctx.send("**There is Already a Game being Played!**")
            return

        #initiate an empty embedded board
        self.game.ini_board()
        make_empty_board(self.embed_board, num_of_rows, num_of_cols)
        string_board = format_board_as_str(self.embed_board, num_of_rows, num_of_cols)
        embed = discord.Embed(title=f"**Perseus Turn - {self.game.turn}   {self.p1_emoji}**", description=string_board, color=embed_colour)
        
        #print embedded board and record the message_id of the board
        msg = await ctx.send(embed=embed)
        self.play_msg_id = msg.id

        #Add Row Buttons
        for col in range(num_of_cols):
            await msg.add_reaction(alp_emoji_text[col])
        
        
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):

        message_id = payload.message_id
        channel_id = payload.channel_id
        guild_id = payload.guild_id
        reaction = payload.emoji
        member = payload.member

        guild = self.bot.get_guild(guild_id)

        channel = guild.get_channel(channel_id)
        user = guild.get_member(payload.user_id)

        message = await channel.fetch_message(payload.message_id)

        #Ignore Bot Message
        if(message_id != self.play_msg_id or payload.user_id == self.bot.user.id): return
        #First Interaction is for P1
        if self.player1 == None and message_id == self.play_msg_id:
            self.player1 = user
            await channel.send(f"**{member.mention} is Player 1 {self.p1_emoji}**")
            await message.remove_reaction(payload.emoji, user)
            return
        #Remove Reaction if P1 attempt to react a second time before P2 registers
        elif user == self.player1 and self.player2 == None:
            await channel.send(f"**{member.mention} you already registered!**")
            await message.remove_reaction(payload.emoji, user)
            return
        #Second Interaction is for P2
        elif self.player2 == None and user != self.player1 and message_id == self.play_msg_id:
            self.player2 = user
            await channel.send(f"**{member.mention} is Player 2 {self.p2_emoji}**")
            await message.remove_reaction(payload.emoji, user)
            return
        #Ignore Members that is not playing
        elif user != self.player1 and user != self.player2:
            await channel.send(f"**{member.mention} you are not part of this!**")
            await message.remove_reaction(payload.emoji, user)
            return


    #Game Logic
        reaction_str = str(reaction)
        #Check if p1 or p2 is player out of their turns
        if((self.game.turn % 4 == 1 or self.game.turn % 4 == 2) and user != self.player1):
            await message.remove_reaction(payload.emoji, user)
            await channel.send(f"**{member.mention} this is not your turn!**")
            return
        if((self.game.turn % 4 == 3 or self.game.turn % 4 == 0) and user != self.player2):
            await message.remove_reaction(payload.emoji, user)
            await channel.send(f"**{member.mention} this is not your turn!**")
            return

        if(reaction_str in alp_emoji_text[0:num_of_cols]):
            # convert reacted alphabet into a number
            col_picked = alp_emoji_text.index(f'{reaction}') + 1
            placed_row, placed_col = self.game.taketurn(col_picked)
            symbol = self.game.curr_turn_symbol(self.p1_emoji, self.p2_emoji) 
            self.embed_board[placed_row][placed_col] = symbol
 

            if(self.game.check_win() == 1):
                    await self.game_won(payload, message, user)
                    await channel.send(f'**{user} is the Winner!**')
                    return
            elif(self.game.check_win() == 2): 
                    await self.game_draw(payload, message)
                    await channel.send('**The Game resulted in a Draw!**')
                    return
            # Update turn after checking for winner to correctly 
            # match the turn's current player and player to check for win
            self.game.turn += 1
            symbol = self.game.curr_turn_symbol(self.p1_emoji, self.p2_emoji) 
            string_board = format_board_as_str(self.embed_board, num_of_rows, num_of_cols)
            embed = discord.Embed(title=f"**Perseus Turn - {self.game.turn}   {symbol}**", description=string_board, color=embed_colour)
            await message.edit(embed=embed)
            await message.remove_reaction(payload.emoji, user)

        else:
            await message.remove_reaction(payload.emoji, user)
            await channel.send(f"**That is not a valid Column!**")
            return
        
    async def end_game_class(self, payload):
        channel_id = payload.channel_id
        guild_id = payload.guild_id
        guild = self.bot.get_guild(guild_id)
        channel = guild.get_channel(channel_id)
  
        await channel.send('**Game Ended**')
        self.play_msg_id = None
        self.game = Perseus_game(num_of_rows - 1, num_of_cols, win_num)
        # offset row by 1 to make space for alphabet row
        self.embed_board = [[' ' for col in range(num_of_cols)] for row in range(num_of_rows)]
        self.player1 = None
        self.player2 = None

    async def game_won(self, payload, message, winner_name):
        if winner_name == self.player1: symbol = self.p1_emoji
        else: symbol = self.p2_emoji
        string_board = format_board_as_str(self.embed_board, num_of_rows, num_of_cols)
        embed = discord.Embed(title=f"**THE WINNER IS  {symbol}**", description=string_board, color=embed_colour)
        await message.edit(embed=embed)
        await self.end_game_class(payload)

    async def game_draw(self, payload, message):
        string_board = format_board_as_str(self.embed_board, num_of_rows, num_of_cols)
        embed = discord.Embed(title=f"**THE GAME RESULTED IN A DRAW**", description=string_board, color=embed_colour)
        await message.edit(embed=embed)
        await self.end_game_class(payload)


    # for user use
    @commands.command(aliases = ['eg', 'end'])
    async def end_game(self, ctx):
        #Check if there is player in the game or not first 
        #(if there is not sufficient number of players this command can be called)
        #then check if the command sender is one of the player
        if(self.player1 != None and self.player2 != None):
            if(ctx.message.author != self.player1 and ctx.message.author.id != self.player2): return
        await ctx.send('**Game Ended**')
        self.play_msg_id = None
        self.game = Perseus_game(num_of_rows - 1, num_of_cols, win_num)
        # offset row by 1 to make space for alphabet row
        self.embed_board = [[' ' for col in range(num_of_cols)] for row in range(num_of_rows)]
        self.player1 = None
        self.player2 = None


async def setup(bot):
    await bot.add_cog(Perseus(bot))


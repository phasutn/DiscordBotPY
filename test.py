import requests
import json
import isodate
import wavelink


# url = "https://www.youtube.com/watch?v=-YMcymgGjOU"

# api_key = "AIzaSyBi-i3LYnpskYs_PzDUex0i7aWlq7oqD9M"
# video_id = url.split("v=")[-1].split("&")[0]
# api_url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet&id={video_id}&part=contentDetails&key={api_key}"
# response = requests.get(api_url)
# video_data = response.json()
# title = video_data['items'][0]['snippet']['title']
# duration_ISO = video_data['items'][0]['contentDetails']['duration']
# duration = isodate.parse_duration(duration_ISO)
# if(duration.total_seconds() < 3600): duration = str(duration)[2:]
# print(title)
# print(duration)

# FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
# YDL_OPTIONS = {
#     'format': 'bestaudio/best',
#     'noplaylist':'True',
#     'outtmpl': 'song.%(ext)s',
#     'postprocessors': [{
#         'key': 'FFmpegExtractAudio',
#         'preferredcodec': 'mp3',
#         'preferredquality': '192',
#     }],
# }

# with YoutubeDL(YDL_OPTIONS) as ydl:
#     info = ydl.extract_info(url, download = False)
#     url2 = info['formats'][0]['url']
#     source = await discord.FFmpegOpusAudio.from_probe(url2, **FFMPEG_OPTIONS)
#     vc.play(source)
#     await ctx.send(f"Now Playing")

# tracks = await self.bot.wavelink.get_tracks(f'ytsearch:{url}')

# if not tracks:
#     return await ctx.send('Could not find any songs with that link.')

# player = self.bot.wavelink.get_player(ctx.guild.id)
# if not player.is_connected:
#     await ctx.invoke(self.connect_)

# await ctx.send(f'Added {str(tracks[0])} to the queue.')
# await player.play(tracks[0])

# import string

# board = []
# alphabets = list(string.ascii_lowercase)
# num_of_rows = 11
# num_of_cols = 18
# embed_colour = 0x077ff7 #colour of line on embeds
# empty_square = ':black_large_square:'


# def alphabet_emojis():
#     alp_emojis = []
#     for i in alphabets:
#         alp_emojis.append(':' + i + ':')
#     return alp_emojis

# for i in range(len(alphabet_emojis())):
#     print(alphabet_emojis()[i])


# def make_empty_board():
#     for row in range(num_of_rows):
#         board.append([])
#         for col in range(num_of_cols):
#             if row == num_of_rows - 1:
#                 board[row].append(alphabet_emojis[col])
#             else:
#                 board[row].append(empty_square)  

# win_num = 3
# horz_win_way = 0
# num_rows = 5

# for i in range(0,8,1):
#     print(num_rows - (i - 1))

num_of_rows = 3
num_of_cols = 3
alphabet = '🇦 🇧 🇨 🇩 🇪 🇫 🇬 🇭 🇮 🇯 🇰 🇱 🇲 🇳 🇴 🇵 🇶 🇷 🇸 🇹 🇺 🇻 🇼 🇽 🇾 🇿'
alphabet = list(alphabet.replace(" ", "")) 
empty_square = 'sqr'

board = []

def make_empty_board(board_use, row, col):
    board = board_use
    for row in range(num_of_rows):
        board.append([])
        for col in range(num_of_cols):
            if row == num_of_rows - 1: # Last row is an alphabet row
                board[row].append(alphabet[col])
            else:
                board[row].append(empty_square)  

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
                board_as_str += "a\n"
    print(f'string - {board_as_str}')
    print(f'normal - {board}')
    return board_as_str

make_empty_board(board, num_of_rows, num_of_cols)
format_board_as_str(board, num_of_rows, num_of_cols)
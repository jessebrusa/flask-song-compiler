import os

# song_folders = sorted(os.listdir('./static/music'))[1:]

# song_info = []
# for song_folder in song_folders:
#     with open(f"./static/music/{song_folder}/info.txt", "r") as file:
#         song_info.append(file.read().splitlines())

# for num in range(len(song_info)):
#     song_info[num].append(song_folders[num])


# print(song_info[1])

song = 'Smoke Gets In Your Eyes'

song_info = []
with open(f"./static/music/{song}/info.txt", "r") as file:
    song_info.append(file.read().splitlines())

title = song_info[0][0]
artist = song_info[0][1]
img_url = song_info[0][2]

path = f'./static/music/{song}/'
folder_items = os.listdir(path)

# lyric_path = f"{path}{folder_items[1]}"

# print(title.title())

# if f'{title.title()} - {artist}.txt' in folder_items:
#     lyric_item = f'{title} - {artist}.txt'
#     print(lyric_item)

#     with open(f'./static/music/{song}/{lyric_item}') as file:
#         lyrics = file.read()

#         print(lyrics)

# if '.pdf' in folder_items[-1]:
#     pdf_path = f"{path}{folder_items[-1]}"

# if f'{title}.mp3' in folder_items:
#     mp3_path = f'{path}{title}.mp3'

# with open(lyric_path, 'r') as file:
#     lyrics = file.read()

# print(lyrics)

for filename in folder_items:
     if filename.lower().endswith('.pdf'):
        pdf_path = filename

print(pdf_path)

import os

song_folders = sorted(os.listdir('./static/music'))[1:]

song_info = []
for song_folder in song_folders:
    with open(f"./static/music/{song_folder}/info.txt", "r") as file:
        song_info.append(file.read().splitlines())

print(song_info)

import glob
import os
import shutil

def move_from_downloads(destination_folder):
    downloads_folder = '/Users/jessebrusa/Downloads'
    files = glob.glob(os.path.join(downloads_folder, '*'))
    sorted_files = sorted(files, key=os.path.getmtime, reverse=True)
    most_recent_file = sorted_files[0]

    destination_path = os.path.join(destination_folder, os.path.basename(most_recent_file))
    shutil.move(most_recent_file, destination_path)

path = f'./static/music/hotel key/'

move_from_downloads(path)
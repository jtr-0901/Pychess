import urllib.request
import os

icons = {
    'bot': 'https://img.icons8.com/ios-filled/50/ffffff/bot.png',
    'pass': 'https://img.icons8.com/ios-filled/50/ffffff/user-group-man-man.png',
    'history': 'https://img.icons8.com/ios-filled/50/ffffff/time-machine.png',
    'bullet': 'https://img.icons8.com/ios-filled/50/ffffff/bullet.png',
    'blitz': 'https://img.icons8.com/ios-filled/50/ffffff/flash-on.png',
    'rapid': 'https://img.icons8.com/ios-filled/50/ffffff/running.png',
    'classical': 'https://img.icons8.com/ios-filled/50/ffffff/hourglass.png',
    'back': 'https://img.icons8.com/ios-filled/50/ffffff/back.png'
}

target_dir = os.path.dirname(os.path.abspath(__file__))
icons_dir = os.path.join(target_dir, 'icons')

if not os.path.exists(icons_dir):
    os.makedirs(icons_dir)

print(f"Downloading icons to {icons_dir}...")

for name, url in icons.items():
    filepath = os.path.join(icons_dir, f"{name}.png")
    try:
        urllib.request.urlretrieve(url, filepath)
        print(f"Downloaded {name}.png")
    except Exception as e:
        print(f"Failed to download {name}.png: {e}")

print("Download complete.")

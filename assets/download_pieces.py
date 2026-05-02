import urllib.request
import os

pieces = ['wp', 'wn', 'wb', 'wr', 'wq', 'wk', 'bp', 'bn', 'bb', 'br', 'bq', 'bk']
# Using chess.com's neo-wood or glass or 3d piece set. Let's use 'glass' or 'wood' or 'neo'
# Another 3D theme is 'bases' or '3d_staunton' (let's try to use a known one, 'neo' is good and looks slightly 3D, 'glass' is pseudo-3D)
theme = 'neo'
base_url = f"https://images.chesscomfiles.com/chess-themes/pieces/{theme}/150/"

target_dir = os.path.dirname(os.path.abspath(__file__))
pieces_dir = os.path.join(target_dir, 'pieces')

if not os.path.exists(pieces_dir):
    os.makedirs(pieces_dir)

print(f"Downloading {theme} pieces to {pieces_dir}...")

for piece in pieces:
    url = f"{base_url}{piece}.png"
    filepath = os.path.join(pieces_dir, f"{piece}.png")
    try:
        urllib.request.urlretrieve(url, filepath)
        print(f"Downloaded {piece}.png")
    except Exception as e:
        print(f"Failed to download {piece}.png: {e}")

print("Download complete.")

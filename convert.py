import glob
from PIL import Image, ImageSequence, ImageOps
path = "./gachalib/images"

files = glob.glob(f"{path}/CARD-*")

for file in files:
    filename = file.split("/")[-1].split(".")[0]
    print(f"working on {filename}")
    img = Image.open(file)
    small = []
    inv_frames = []
    inv_small = []
    durations = []
    for frame in ImageSequence.Iterator(img):
        small.append(ImageOps.contain(frame, (350, 500)))
        inv_frames.append(ImageOps.invert(frame.convert("RGB")))
        inv_small.append(ImageOps.contain(inv_frames[-1], (350, 500)))
        durations.append(frame.info.get("duration", 40))
    ext = "png"
    if len(small) > 1:
        ext = "gif"
        small[0].save(
            f"{path}/small/{filename}.{ext}",format="GIF",save_all=True,append_images=small[1:],loop=0,durations=durations,disposal=2
        )
        inv_frames[0].save(
            f"{path}/E{filename}.{ext}",format="GIF",save_all=True,append_images=inv_frames[1:],loop=0,durations=durations
        )
        inv_small[0].save(
            f"{path}/small/E{filename}.{ext}",format="GIF",save_all=True,append_images=inv_small[1:],loop=0,durations=durations
        )
    else:
        small[0].save(f"{path}/small/{filename}.{ext}", format="png")
        inv_frames[0].save(f"{path}/E{filename}.{ext}", format="png")
        inv_small[0].save(f"{path}/small/E{filename}.{ext}", format="png")
    filename += f".{ext}"
print("Done!")
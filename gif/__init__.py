# Code i stole from stackoverflow because mine didn't work
from PIL import Image, ImageDraw, ImageSequence, ImageFont, GifImagePlugin
import io, textwrap, sys

im = Image.open('./gif/base.gif')
font = ImageFont.truetype('./gif/Futura Extra Bold Condensed.otf', 25)

def gen(text):
    text = textwrap.fill(text, 20)

    frames = []
    # Loop over each frame in the animated image
    for frame in ImageSequence.Iterator(im):
        # Get size
        d = ImageDraw.Draw(frame)
        textHeight = d.multiline_textbbox((0, 0), font=font, text=text, spacing=15)[3] + 24

        # Weird bs I don't understand
        b = io.BytesIO()
        frame.save(b, format="GIF")
        old_frame = Image.open(b)
        frame = Image.new("RGBA", (300, 169 + textHeight), (255, 255, 255, 0))
        frame.paste( (255,255,255), (0, 0, 300, textHeight))

        # Draw the text on the frame
        d = ImageDraw.Draw(frame)
        d.multiline_text((300 / 2, 12), text, (0,0,0), font, "ma", align="center", spacing=15)
        del d
        frame.paste(old_frame, (0, textHeight + 1))

        frames.append(frame)

    buffer = io.BytesIO()
    frames[0].save(buffer, format="GIF", save_all=True, append_images=frames[1:], loop=0, duration=40)
    buffer.seek(0)
    return buffer

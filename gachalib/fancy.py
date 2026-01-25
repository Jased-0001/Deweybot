import Bot
from PIL import Image, ImageDraw, ImageFont, ImageOps
import io, textwrap

font_name = ImageFont.truetype('./gachalib/templates/fonts/BBHHegarty-Regular.ttf', 60)
font_rarity = ImageFont.truetype('./gachalib/templates/fonts/BBHHegarty-Regular.ttf', 35)
font_description = ImageFont.truetype('./gachalib/templates/fonts/PTSerif-Bold.ttf', 45)

def generate_card_img(card:gachalib.types.Card):
    bg = Image.open('./gachalib/templates/card.png')
    img = ImageDraw.Draw(bg)
    img.text((100, 100), card.name, (255, 255, 255), font_name, stroke_width=6, stroke_fill=(0, 0, 0))
    img.text((261, 818), str.upper(card.rarity), (255, 255, 255), font_rarity, "mm", stroke_width=4, stroke_fill=(0, 0, 0))
    description = textwrap.fill(card.description, 25)
    img.multiline_text((134, 924), description, (255, 255, 255), font_description, stroke_width=4, stroke_fill=(0, 0, 0))

    fg = Image.open(f"gachalib/images/{card.filename}")
    fg = ImageOps.contain(fg, (768, 576))
    bg.paste(fg, (96+(768-fg.width)//2, 192), fg)

    buffer = io.BytesIO()
    bg.save(buffer, format="png")
    buffer.seek(0)
    return buffer
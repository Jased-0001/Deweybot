import gachalib.types, gachalib
import discord
import textwrap

class GachaView(discord.ui.LayoutView):
    def __init__(self, card: gachalib.types.Card, image: discord.File):
        super().__init__(timeout=None)
        container = discord.ui.Container(
            discord.ui.TextDisplay(f"# {card.name}"),
            discord.ui.MediaGallery(
                discord.MediaGalleryItem(image),
            ),
            discord.ui.TextDisplay(f"### {card.rarity}"),
            discord.ui.TextDisplay(textwrap.fill(card.description, 50)),
            discord.ui.Separator(),
            discord.ui.TextDisplay(f"-#{' !DRAFT!' if not card.accepted else ''} ID {card.card_id}, by <@{card.maker_id}>"),
            accent_color=gachalib.rarityColors[card.rarity]
        )

        self.add_item(container)
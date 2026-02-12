from urllib import response
from commands import Gacha
import db_lib,Bot
import gachalib.cards, gachalib.cards_inventory, gachalib.gacha_user, gachalib.types, gachalib.trade
import discord
from random import randint
from typing import Literal
import math
import textwrap
from PIL import Image, ImageDraw, ImageFont, ImageOps
import io

Rarities = Literal["Common", "Uncommon", "Rare", "Epic", "Legendary"
    "Common evil", "Uncommon evil", "Rare evil", "Epic evil", "Legendary evil"]
SortOptions = Literal["ID", "Rarity"]

rarityColors = {
    "None":      0xffffff, "None evil":      0xffffff,
    "Common":    0x04f9f9, "Common evil":    0xfb0606,
    "Uncommon":  0x04f94e, "Uncommon evil":  0xfb06b1,
    "Rare":      0xf9d104, "Rare evil":      0x062efb,
    "Epic":      0xf97f04, "Epic evil":      0x0680fb,
    "Legendary": 0xf93504, "Legendary evil": 0x06cafb,
}

rarity_order = {
    "None":      0, "None evil":      6,
    "Common":    1, "Common evil":    7,
    "Uncommon":  2, "Uncommon evil":  8,
    "Rare":      3, "Rare evil":      9,
    "Epic":      4, "Epic evil":      10,
    "Legendary": 5, "Legendary evil": 11,
}

def gacha_crop_image(card: gachalib.types.Card):
    img = Image.open(f"{Bot.DeweyConfig["image-save-path"]}/{card.filename}")
    img = ImageOps.contain(img, (350, 350))
    img = ImageOps.invert(img.convert("RGB")) if card.card_id < 0 else img
    buffer = io.BytesIO()
    img.save(buffer, format="png")
    buffer.seek(0)
    return discord.File(fp=buffer, filename="image.png")

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
            accent_color=rarityColors[card.rarity]
        )

        self.add_item(container)

#name, card_description, rarity, filename, title: str = "None", description: str = "None"
def gacha_embed(title:str, description:str, card:gachalib.types.Card, show_rarity:bool=True, show_desc:bool=True, show_name:bool=True,color:int=-1) -> discord.Embed:
    embed = discord.Embed(title=title, description=description,color=rarityColors[card.rarity] if color == -1 else color)
    if show_name:   embed.add_field(name="Name!", value=card.name)
    if show_desc:   embed.add_field(name="Description!", value=card.description)
    if show_rarity: embed.add_field(name="Rarity!", value=card.rarity)
    embed.set_image(url=Bot.DeweyConfig["imageurl"] + card.filename)
    return embed


def cardBrowserEmbed(uid:int, cards:list[gachalib.types.Card], page:int = 1, inventory:bool = False) -> discord.Embed | str:
    if inventory: card_grouped = gachalib.cards.group_like_cards(cards)

    startpage = (5*(page-1))+1

    if inventory:
        if page == 1:
            cards_a = card_grouped[0:5] # pyright: ignore[reportPossiblyUnboundVariable]
        elif page > 1:
            cards_a = card_grouped[startpage:startpage+5] # pyright: ignore[reportPossiblyUnboundVariable]
    else:
        if page == 1:
            cards_a = cards[0:5]
        elif page > 1:
            cards_a = cards[startpage-1:startpage+5]

    embed = discord.Embed(title="Card (inventory) bowser!" if inventory else "Card bowser!",
                          description=f"page {page}/{math.ceil(len(card_grouped)/5)}" if inventory else f"page {page}/{math.ceil(len(cards)/5)}") # pyright: ignore[reportPossiblyUnboundVariable]
    
    for i in cards_a: # pyright: ignore[reportPossiblyUnboundVariable]
        if inventory: embed.add_field(name=f'{i[0].name} (ID: {i[0].card_id}) | {i[0].rarity}  x{i[1]}', value=f'', inline=False) # pyright: ignore[reportIndexIssue]
        else: embed.add_field(name=f'{i.name} (ID: {i.card_id}) | {i.rarity}', value=f'{i.description}', inline=False) # pyright: ignore[reportAttributeAccessIssue]

    if len(embed.fields) > 0:
        return embed
    
    return f"(There are no cards on page {page}!)"


async def get_card_maker_channel(id:int) -> discord.User:
    return await Bot.client.fetch_user(id)

def rarest_card(cards:list[gachalib.types.Card]) -> gachalib.types.Card:
    return max(cards, key=lambda c: rarity_order[c.rarity])


def random_rarity(restraint:bool=False) -> str:
    number = randint(1,100)
    if restraint:
        if number < 60:
            return 'Common'
        else:
            return 'Uncommon'
    else:
        if number > 0 and number <= 35:
            return 'Common'
        elif number > 35 and number <= 60:
            return 'Uncommon'
        elif number > 60 and number <= 80:
            return 'Rare'
        elif number > 80 and number <= 95:
            return 'Epic'
        elif number > 95 and number <= 100:
            return 'Legendary'
        else:
            return 'Legendary'


class BrowserView(discord.ui.View):
    def __init__(self,inventory:bool=False,uid:int=0,cards:list[gachalib.types.Card]=[],page:int=1,sort:SortOptions="ID"):
        super().__init__(timeout=None)
        self.message = None
        self.page = page

        self.isInventory = inventory
        self.uid = uid
        
        if len(cards) == 0:
            if self.isInventory:
                _, self.cards = gachalib.cards_inventory.get_users_cards(self.uid)
                if sort == "ID":
                    self.cards = gachalib.cards_inventory.sort_cards_by_id(self.cards) # pyright: ignore[reportArgumentType]
                elif sort == "Rarity":
                    self.cards = gachalib.cards_inventory.sort_cards_by_rarity(self.cards)  # pyright: ignore[reportArgumentType]
            else:
                _, self.cards = gachalib.cards.get_cards()
        else:
            self.cards = cards
    
    def getPage(self):
        return cardBrowserEmbed(uid=self.uid,cards=self.cards,page=self.page,inventory=self.isInventory) # pyright: ignore[reportArgumentType]


    async def updatePage(self,interaction:discord.Interaction):
        embed = self.getPage()

        if type(embed) == discord.Embed:
            await interaction.response.edit_message(content="", embed=embed, view=self)
        else:
            await interaction.response.edit_message(content=embed, embed=None, view=self)

    @discord.ui.button(emoji="⬅️", style=discord.ButtonStyle.secondary, row=0, custom_id="backbtn")
    async def back_call(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:

        if self.page <= 0 or self.page - 1 <= 0:
            button.disabled = True
        else:
            button.disabled = False
            self.page -= 1

        await self.updatePage(interaction)


    @discord.ui.button(emoji="➡️", style=discord.ButtonStyle.secondary, row=0, custom_id="fwdbtn")
    async def forward_call(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        self.page += 1
        await self.updatePage(interaction)


class RequestView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.message = None

    @discord.ui.button(label="Approve", style=discord.ButtonStyle.success, row=0, custom_id="approve_btn")
    async def approve_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        a = db_lib.read_data(f"SELECT id FROM gacha WHERE (request_message_id) = (?)", (interaction.message.id,))[0] # pyright: ignore[reportOptionalMemberAccess]
        #print("I believe this is id ", a[0])

        _, card = gachalib.cards.get_card_by_id(a[0])
        _, status = await gachalib.cards.approve_card(True, card)

        await interaction.response.send_message(status)

        self.disable()


    @discord.ui.button(label="Deny", style=discord.ButtonStyle.secondary, row=0, custom_id="deny_btn")
    async def deny_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        a = db_lib.read_data(f"SELECT id FROM gacha WHERE (request_message_id) = (?)", (interaction.message.id,))[0] # pyright: ignore[reportOptionalMemberAccess]

        _, card = gachalib.cards.get_card_by_id(a[0])
        _, status = await gachalib.cards.approve_card(False, card)
        
        await interaction.response.send_message(status)

        self.disable()

    @discord.ui.button(label="BAN FROM DEWEY", style=discord.ButtonStyle.danger, row=1, custom_id="ban_btn")
    async def ban_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.send_message(f"not implemented", ephemeral=True)
        self.disable()

    def disable(self):
        for child in self.children:
            child.disabled=True # pyright: ignore[reportAttributeAccessIssue]


class PackView(discord.ui.View):
    def __init__(self,cards:list[gachalib.types.Card]):
        super().__init__(timeout=None)
        self.message = None
        self.cards = cards

        for i in range(len(cards)):
            button = discord.ui.Button(label=f"Card #{i+1}", style=discord.ButtonStyle.blurple, custom_id=f"{i}")

            button.callback = self.btn_callback
            self.add_item(button)
    
    async def btn_callback(self, interaction: discord.Interaction) -> None:
        card = self.cards[int(interaction.data["custom_id"])]  # pyright: ignore[reportOptionalSubscript, reportGeneralTypeIssues]
        image=gacha_crop_image(card)
        await interaction.response.send_message(
            view=GachaView(card,image), file=image, ephemeral=True
        )

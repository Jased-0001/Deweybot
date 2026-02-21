import db_lib,Bot
import gachalib.cards, gachalib.types
import discord
from random import randint
from typing import Literal
import math
import os

gacha_database = db_lib.setup_db(name="gacha", tables=
                                 ["CREATE TABLE gacha \
(maker_id int(19), request_message_id int(20), id int(5), accepted bool(1), name varchar(256), description varchar(256), rarity varchar(256), filename varchar(256));",
              "CREATE TABLE gacha_user \
(user_id int(19), last_use int(20));",
              "CREATE TABLE gacha_cards \
(id int(20), card_id int(5), user_id int(19));",], file=Bot.DeweyConfig["gacha-sqlite-path"])

if not gacha_database:
    raise Exception("Fuck!")

Rarities = Literal["None", "Common", "Uncommon", "Rare", "Epic", "Legendary",
    "None evil", "Common evil", "Uncommon evil", "Rare evil", "Epic evil", "Legendary evil"]
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

if Bot.DeweyConfig["deweycoins-enabled"]:
    rarity_costs = {
        "None":      999999, "None evil":      999999,
        "Common":    1,    "Common evil":    2,
        "Uncommon":  3,    "Uncommon evil":  6,
        "Rare":      10,   "Rare evil":      20,
        "Epic":      30,   "Epic evil":      60,
        "Legendary": 100,  "Legendary evil": 200,
}

    def getCardCost(card: gachalib.types.Card) -> int:
        return rarity_costs[card.rarity]


def get_small_filename(card: gachalib.types.Card):
    filename = card.filename.split(".")[0]
    filename += ".gif" if os.path.isfile(f"{Bot.DeweyConfig["image-save-path"]}/small/{filename}.gif") else ".png"
    return filename


def get_small_thumbnail(card: gachalib.types.Card):
    filename = get_small_filename(card)
    return discord.File(f"{Bot.DeweyConfig["image-save-path"]}/small/{filename}")


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







def cardBrowserEmbed(uid:int, cards:list[gachalib.types.CardsInventory] | list[gachalib.types.Card] | list[gachalib.types.CardsInventory | gachalib.types.Card], page:int = 1, inventory:bool = False) -> discord.Embed | str:
    startpage = (5*(page-1))+1
    cards_a = []

    if inventory:
        card_grouped = gachalib.cards.group_like_cards(cards)

        if page == 1:
            cards_a = card_grouped[0:5]
        elif page > 1:
            cards_a = card_grouped[startpage:startpage+5]
        
        embed = discord.Embed(title="Card (inventory) bowser!" if inventory else "Card bowser!",
                            description=f"page {page}/{math.ceil(len(card_grouped)/5)}")
        for i in cards_a: embed.add_field(name=f'{i[0].name} (ID: {i[0].card_id}) | {i[0].rarity}  x{i[1]}', value=f'', inline=False)
    else:
        if page == 1:
            cards_a = cards[0:5]
        elif page > 1:
            cards_a = cards[startpage-1:startpage+5]

        embed = discord.Embed(title="Card (inventory) bowser!" if inventory else "Card bowser!",
                          description=f"page {page}/{math.ceil(len(cards)/5)}")
        
        for i in cards_a:
            _,i = gachalib.cards.get_card_by_id(i.card_id)
            embed.add_field(name=f'{i.name} (ID: {i.card_id}) | {i.rarity}', value=f'{i.description}', inline=False)

    if len(embed.fields) > 0:
        return embed
    
    return f"(There are no cards on page {page}!)"


#name, card_description, rarity, filename, title: str = "None", description: str = "None"
def gacha_embed(title:str, description:str, card:gachalib.types.Card, show_rarity:bool=True, show_desc:bool=True, show_name:bool=True,color:int=-1) -> discord.Embed:
    embed = discord.Embed(title=title, description=description,color=rarityColors[card.rarity] if color == -1 else color)
    if show_name:   embed.add_field(name="Name!", value=card.name)
    if show_desc:   embed.add_field(name="Description!", value=card.description)
    if show_rarity: embed.add_field(name="Rarity!", value=card.rarity)
    embed.set_image(url=Bot.DeweyConfig["imageurl"] + card.filename)
    return embed
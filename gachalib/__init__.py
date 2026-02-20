import db_lib,Bot
import gachalib.cards, gachalib.cards_inventory, gachalib.gacha_user, gachalib.types, gachalib.trade
import discord
from random import randint
from typing import Literal
import math
import textwrap
import io
import os

import moneylib

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

#########################
#      Inventory UI     #
#########################

class SortSelect(discord.ui.Select):
    def __init__(self, user: discord.User | discord.Member,  sort: str, button: bool) -> None:
        self.user = user
        self.button = button
        options = [
            discord.SelectOption(label="Rarity (ascending)"),
            discord.SelectOption(label="Rarity (descending)"),
            discord.SelectOption(label="Quantity (ascending)"),
            discord.SelectOption(label="Quantity (descending)"),
            discord.SelectOption(label="ID (ascending)"),
            discord.SelectOption(label="ID (descending)"),
        ]
        super().__init__(placeholder=sort,max_values=1,min_values=1,options=options)

    async def callback(self, interaction: discord.Interaction):
        layout = InventoryView(self.user, self.values[0], self.button, 1)
        await interaction.response.edit_message(view=layout)

class BrowseRow(discord.ui.ActionRow):
    def __init__(self, view, page: int, num_pages: int, *args) -> None:
        super().__init__()
        self.args = args
        self.page = page
        self.mView = view
        self.num_pages = num_pages

    async def edit(self, interaction, page):
        layout = self.mView(*self.args, page=page)
        await interaction.response.edit_message(
            view=layout,
            allowed_mentions=discord.AllowedMentions(users=False)
        )

    @discord.ui.button(emoji="⬅️", style=discord.ButtonStyle.primary, custom_id="left_btn")
    async def left_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        page = max(self.page-1, 1)
        await self.edit(interaction, page)

    @discord.ui.button(emoji="➡️", style=discord.ButtonStyle.primary, custom_id="right_btn")
    async def right_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        page = min(self.page+1, self.num_pages)
        await self.edit(interaction, page)

class viewCardButton(discord.ui.Button):
    def __init__(self, card: gachalib.types.Card) -> None:
        super().__init__(label="View", style=discord.ButtonStyle.secondary)
        self.card = card

    async def callback(self, interaction: discord.Interaction) -> None:
        image=get_small_thumbnail(self.card)
        await interaction.response.send_message(
            view=GachaView(self.card, image), file=image, ephemeral=True,
            allowed_mentions=discord.AllowedMentions(users=False)
        )

class InventoryView(discord.ui.LayoutView):
    def __init__(self, user: discord.User | discord.Member, sort: str="Rarity (descending)", button: bool=True, page: int=1,):
        super().__init__(timeout=None)
        per_page = 5 - button
        self.images: list[str] = []

        cards = gachalib.cards_inventory.get_users_cards(user.id)[1]
        cards_grouped = gachalib.cards.group_like_cards(cards)
        num_pages = math.ceil(len(cards_grouped) / per_page)

        if "Rarity" in sort:
            cards_grouped = sorted(cards_grouped, key=lambda b: gachalib.rarity_order[gachalib.cards.get_card_by_id(card_id=b[0].card_id)[1].rarity])
        elif "Quantity" in sort:
            cards_grouped = sorted(cards_grouped, key=lambda b: b[1])
        else:
            cards_grouped = sorted(cards_grouped, key=lambda b: b[0].card_id)

        if "descending" in sort:
            cards_grouped.reverse()

        cards_page: list[tuple[gachalib.types.Card, int]] = cards_grouped[(page-1)*per_page:page*per_page]

        items = [
            discord.ui.TextDisplay("## Inventory Bowser!"),
            discord.ui.Separator(),
            discord.ui.ActionRow(SortSelect(user, sort, button)),
            discord.ui.TextDisplay(f"Page {page}/{num_pages}"),
            discord.ui.Separator(),
        ]
        for card in cards_page:
            image = f"{Bot.DeweyConfig["imageurl"]}/small/{get_small_filename(card[0])}"
            self.images.append(image)
            items.append(discord.ui.Section(
                f"### {card[1]} × {card[0].name}",
                f"({card[0].rarity})\n"
                f"-# ID: {card[0].card_id}",
                accessory=discord.ui.Thumbnail(image)
            ))
            items.append(discord.ui.ActionRow(viewCardButton(card[0]))) if button else None
            items.append(discord.ui.Separator())
        if num_pages > 1:
            browse_row = BrowseRow(InventoryView, page, num_pages, user, sort, button)
            if type(browse_row.children[0]) == discord.ui.Button and type(browse_row.children[1]) == discord.ui.Button:
                browse_row.children[0].disabled = page == 1
                browse_row.children[1].disabled = page == num_pages
            items.append(browse_row)

        container = discord.ui.Container(*items)
        self.add_item(container)

#########################
#     Unnaccepted UI    #
#########################

class AdminSelect(discord.ui.Select):
    def __init__(self, page: int, card_id) -> None:
        self.page = page
        self.card_id = card_id
        options = [
            discord.SelectOption(label="Deny"),
            discord.SelectOption(label="Common"),
            discord.SelectOption(label="Uncommon"),
            discord.SelectOption(label="Rare"),
            discord.SelectOption(label="Epic"),
            discord.SelectOption(label="Legendary")
        ]
        super().__init__(placeholder="Rarity",max_values=1,min_values=1,options=options)

    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == "Deny":
            await gachalib.cards.approve_card(False, gachalib.cards.get_card_by_id(self.card_id)[1])
        else:
            gachalib.cards.update_card(self.card_id, "rarity", self.values[0])
            await gachalib.cards.approve_card(True, gachalib.cards.get_card_by_id(self.card_id)[1])
        layout = UnacceptedView(self.page)
        await interaction.response.edit_message(
            view=layout,
            allowed_mentions=discord.AllowedMentions(users=False)
        )

class UnacceptedView(discord.ui.LayoutView):
    def __init__(self, page: int=1):
        super().__init__(timeout=None)
        per_page = 4
        self.images: list[str] = []
        cards = gachalib.cards.get_unapproved_cards()[1]
        num_pages = math.ceil(len(cards) / per_page)
        cards_page = cards[(page-1)*per_page:page*per_page]

        items = [
            discord.ui.TextDisplay("## Unapproved cards"),
            discord.ui.Separator(),
            discord.ui.TextDisplay(f"Page {page}/{num_pages}"),
            discord.ui.Separator(),
        ]
        for card in cards_page:
            image = f"{Bot.DeweyConfig["imageurl"]}/small/{get_small_filename(card)}"
            self.images.append(image)
            items.append(discord.ui.Section(
                f"### {card.name}",
                f"{card.description}",
                f"-# ID: {card.card_id} by: <@{card.maker_id}>",
                accessory=discord.ui.Thumbnail(image)
            ))
            items.append(discord.ui.ActionRow(AdminSelect(page, card.card_id)))
            items.append(discord.ui.Separator())
        if num_pages > 1:
            browse_row = BrowseRow(UnacceptedView, page, num_pages)
            if type(browse_row.children[0]) == discord.ui.Button and type(browse_row.children[1]) == discord.ui.Button:
                browse_row.children[0].disabled = page == 1
                browse_row.children[1].disabled = page == num_pages
            items.append(browse_row)

        container = discord.ui.Container(*items)
        self.add_item(container)

#########################

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
                    self.cards = gachalib.cards_inventory.sort_cards_by_id(self.cards)
                elif sort == "Rarity":
                    self.cards = gachalib.cards_inventory.sort_cards_by_rarity(self.cards)
            else:
                _, self.cards = gachalib.cards.get_cards()
        else:
            self.cards = cards
    
    def getPage(self):
        return cardBrowserEmbed(uid=self.uid,cards=self.cards,page=self.page,inventory=self.isInventory)


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
        self.message: discord.Message | None = None

    @discord.ui.button(label="Approve", style=discord.ButtonStyle.success, row=0, custom_id="approve_btn")
    async def approve_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        assert interaction.message, "no interaction.message"
        a = gacha_database.read_data(f"SELECT id FROM gacha WHERE (request_message_id) = (?)", (interaction.message.id,))[0]
        #print("I believe this is id ", a[0])

        _, card = gachalib.cards.get_card_by_id(a[0])
        _, status = await gachalib.cards.approve_card(True, card)

        await interaction.response.send_message(status)

        self.disable()


    @discord.ui.button(label="Deny", style=discord.ButtonStyle.secondary, row=0, custom_id="deny_btn")
    async def deny_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        assert interaction.message, "no interaction.message"
        a = gacha_database.read_data(f"SELECT id FROM gacha WHERE (request_message_id) = (?)", (interaction.message.id,))[0]

        _, card = gachalib.cards.get_card_by_id(a[0])
        _, status = await gachalib.cards.approve_card(False, card)
        
        await interaction.response.send_message(status)

        self.disable()

    #@discord.ui.button(label="BAN FROM DEWEY", style=discord.ButtonStyle.danger, row=1, custom_id="ban_btn")
    #async def ban_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
    #    await interaction.response.send_message(f"not implemented", ephemeral=True)
    #    self.disable()
    
    def disable(self):
        for child in self.children:
            if type(child) == discord.ui.Button:
                child.disabled=True


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
        if interaction.data and "custom_id" in interaction.data:
            card = self.cards[int(interaction.data["custom_id"])]
            image=get_small_thumbnail(card)
            await interaction.response.send_message(
                view=GachaView(card,image), file=image, ephemeral=True
            )

if Bot.DeweyConfig["deweycoins-enabled"]:
    class CardSellConfirmation(discord.ui.View):
        def __init__(self,owner: int, inventory_ids: list[gachalib.types.CardsInventory], rarity: str):
            super().__init__(timeout=None)
            self.message = None
            self.owner: int = owner
            self.inventory_ids: list[gachalib.types.CardsInventory] = inventory_ids
            self.rarity: str = rarity
        
        def isowner(self,interaction):
            assert interaction.user, "interaction had no user"
            return True if self.owner == interaction.user.id else False

        @discord.ui.button(label="SELL! SELL! SELL!", style=discord.ButtonStyle.green)
        async def sell_callback(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
            assert Bot.client.user, "bot has no user"
            if not self.isowner(interaction=interaction):
                await interaction.response.send_message(content="You don't own this view!", ephemeral=True)
                return
            
            users_cards = gachalib.cards_inventory.get_users_cards(user_id=self.owner)[1]
            for i in self.inventory_ids:
                if not i in users_cards:
                    await interaction.response.send_message(content=f"You ain't own some the card you sellin'")
                    return

            owed = rarity_costs[self.rarity] * len(self.inventory_ids)
            for i in self.inventory_ids:
                botaccount = moneylib.getUserInfo(Bot.client.user.id)
                if botaccount.balance < owed: 
                    await interaction.response.send_message(content=f"I don't actually have enough money to buy this from you!")
                    return

                gachalib.cards_inventory.change_card_owner(user_id=Bot.client.user.id, inv_id=i.inv_id)
                print("GAVE TO DEWEY")

            moneylib.giveCoins(user=self.owner, coins=owed)
            moneylib.giveCoins(user=Bot.client.user.id, coins=-owed)
            await interaction.response.send_message(content=f"Success! +D¢{owed} (now D¢{moneylib.getUserInfo(self.owner).balance})")
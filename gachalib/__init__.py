from commands import Gacha
import db_lib,Bot
import gachalib.cards, gachalib.cards_user, gachalib.gacha_timeout, gachalib.types, gachalib.trade
import discord
from random import randint
from typing import Literal
import math

Rarities = Literal["Common", "Uncommon", "Rare", "Epic", "Legendary"]

#name, card_description, rarity, filename, title: str = "None", description: str = "None"
def gacha_embed(title:str, description:str, card:gachalib.types.Card, show_rarity:bool=True, show_desc:bool=True, show_name:bool=True) -> discord.Embed:
    embed = discord.Embed(title=title, description=description)
    if show_name:   embed.add_field(name="Name!", value=card.name)
    if show_desc:   embed.add_field(name="Description!", value=card.description)
    if show_rarity: embed.add_field(name="Rarity!", value=card.rarity)
    embed.set_image(url=Bot.DeweyConfig["httpurl"] + card.filename)
    return embed

def card_browser_embed(cards:list[gachalib.types.Card], page:int=1) -> discord.Embed | str:
    startpage = (5*(page-1))+1

    if page == 1:
        cards_a = cards[0:5]
    elif page > 1:
        cards_a = cards[startpage-1:startpage+5]

    embed = discord.Embed(title="Card bowser!", description=f"page {page}/{math.ceil(len(cards)/5)}")

    for i in cards_a:
        embed.add_field(name=f'{i.name} (ID: {i.card_id}) | {i.rarity}', value=f'{i.description}', inline=False)
    if len(embed.fields) > 0:
        return embed
    
    return f"(There are no cards on page {page}!)"

def card_inventory_embed(uid:int, cards:list[gachalib.types.Card], page:int) -> discord.Embed | str:
    card_grouped = gachalib.cards.group_like_cards(cards)

    startpage = (5*(page-1))+1

    if page == 1:
        cards_a = card_grouped[0:5]
    elif page > 1:
        cards_a = card_grouped[startpage-1:startpage+5]

    embed = discord.Embed(title="Card (inventory) bowser!", description=f"page {page}/{math.ceil(len(card_grouped)/5)}")
    
    for i in cards_a:
        embed.add_field(name=f'{i[0].name} (ID: {i[0].card_id}) | {i[0].rarity}  x{i[1]}', value=f'', inline=False)

    if len(embed.fields) > 0:
        return embed
    
    return f"(There are no cards on page {page}!)"

async def get_card_maker_channel(id:int) -> discord.User:
    return await Bot.client.fetch_user(id)

def random_rarity() -> str:
    number = randint(1,100)
    
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
    

#[id_start-1:id_end]

class BrowserView(discord.ui.View):
    def __init__(self,inventory:bool,uid:int=0,manual:bool=False):
        super().__init__()
        if not manual:
            self.message = None
            self.page = 1

            self.isInventory = inventory
            self.uid = uid
            
            if self.isInventory:
                _, self.cards = gachalib.cards_user.get_users_cards(self.uid)
                self.cards = gachalib.cards_user.sort_userlist_cards(self.cards)
            else:
                _, self.cards = gachalib.cards.get_cards()

    async def getPage(self,interaction:discord.Interaction):
        if self.isInventory:
            embed = card_inventory_embed(self.uid,self.cards,self.page) # pyright: ignore[reportArgumentType]
        else:
            embed = card_browser_embed(self.cards,self.page) # pyright: ignore[reportArgumentType]

        if type(embed) == discord.Embed:
            await interaction.response.edit_message(content="", embed=embed)
        else:
            await interaction.response.edit_message(content=embed, embed=None)

    @discord.ui.button(emoji="⬅️", style=discord.ButtonStyle.secondary, row=0, custom_id="backbtn")
    async def back_call(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:

        if self.page <= 0 or self.page - 1 <= 0:
            button.disabled = True
        else:
            button.disabled = False
            self.page -= 1

        await self.getPage(interaction)


    @discord.ui.button(emoji="➡️", style=discord.ButtonStyle.secondary, row=0, custom_id="fwdbtn")
    async def forward_call(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        self.page += 1
        await self.getPage(interaction)



class RequestView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.message = None

    @discord.ui.button(label="Approve", style=discord.ButtonStyle.success, row=0, custom_id="approve_btn")
    async def approve_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        a = db_lib.read_data(f"SELECT id, maker_id, accepted, rarity, name FROM gacha WHERE (request_message_id) = (?)", (interaction.message.id,))[0] # pyright: ignore[reportOptionalMemberAccess]
        #print("I believe this is id ", a[0])

        if a[3] == "None":
            await interaction.response.send_message("Please set a rarity first! /z-gacha-admin-setrarity")
            return

        if not a[2]:
            gachalib.cards.update_card(a[0], "accepted", "1")
            await interaction.response.send_message(f"{interaction.user.mention} approved ID {a[0]} by ID {a[1]}!", ephemeral=False, silent=True)
            userchannel = await get_card_maker_channel(a[1])
            await userchannel.send(f"Your card \"{a[4]}\" ({a[0]}) has been ACCEPTED!!! GOOD JOB!!!")
        else:
            await interaction.response.send_message(f"This card was already accepted", ephemeral=True)
        self.disable()


    @discord.ui.button(label="Deny", style=discord.ButtonStyle.secondary, row=0, custom_id="deny_btn")
    async def deny_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        a = db_lib.read_data(f"SELECT id,maker_id,name FROM gacha WHERE (request_message_id) = (?)", (interaction.message.id,))[0] # pyright: ignore[reportOptionalMemberAccess]

        userchannel = await get_card_maker_channel(a[1])
        await userchannel.send(f"Your card \"{a[2]}\" ({a[0]}) has been denied. Sorry for your loss.")

        if gachalib.cards.delete_card(a[0]):
            await interaction.response.send_message(f"Card DENIED and DELETED!", ephemeral=False)
            self.disable()
        else:
            await interaction.response.send_message(f"I couldn't find it???", ephemeral=False)

    @discord.ui.button(label="BAN FROM DEWEY", style=discord.ButtonStyle.danger, row=1, custom_id="ban_btn")
    async def ban_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.send_message(f"not implemented", ephemeral=True)
        self.disable()

    def disable(self):
        for child in self.children:
            child.disabled=True # pyright: ignore[reportAttributeAccessIssue]

class PackView(discord.ui.View):
    def __init__(self,cards:list[gachalib.types.Card]):
        super().__init__()
        self.message = None
        self.cards = cards

        for i in range(len(cards)):
            button = discord.ui.Button(label=f"Card #{i+1}", style=discord.ButtonStyle.blurple, custom_id=f"{i}")

            button.callback = self.btn_callback
            self.add_item(button)
    
    async def btn_callback(self, interaction: discord.Interaction) -> None:
        card = self.cards[int(interaction.data["custom_id"])]  # pyright: ignore[reportOptionalSubscript, reportGeneralTypeIssues]
        await interaction.response.send_message(embed=gacha_embed(card=card, title="gacha card", description=f"ID {card.card_id}{' !DRAFT!' if not card.accepted else ''}"), ephemeral=True)
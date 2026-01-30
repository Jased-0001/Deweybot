import db_lib,Bot
import gachalib.cards, gachalib.cards_user, gachalib.types
import discord
import re

async def do_trade(trade: gachalib.types.Trade, interaction: discord.Interaction):
    for a in trade.user1_cards:
        gachalib.cards_user.change_card_owner(trade.user2.id, a.inv_id) # pyright: ignore[reportOptionalMemberAccess]
    for b in trade.user2_cards:
        gachalib.cards_user.change_card_owner(trade.user1.id, b.inv_id) # pyright: ignore[reportOptionalMemberAccess]
    await trade.accept_message.delete() # pyright: ignore[reportOptionalMemberAccess]
    await trade.message.delete() # pyright: ignore[reportOptionalMemberAccess]
    embed = discord.Embed(
        title="Trade complete!",
        color=0x008447
    )
    build_embed(embed, trade)
    await interaction.response.send_message(embed=embed)

async def check_user(trade: gachalib.types.Trade, interaction: discord.Interaction, user: discord.User | None = None):
    if user and interaction.user.id != user.id:
        await interaction.response.send_message("You can't do this!!", ephemeral=True)
        return False
    if interaction.user.id == trade.user1.id or interaction.user.id == trade.user2.id: # pyright: ignore[reportOptionalMemberAccess]
        return True
    await interaction.response.send_message("You can't interact with this trade", ephemeral=True)
    return False

def build_embed(embed: discord.Embed, trade: gachalib.types.Trade):
    card_grouped1 = gachalib.cards.group_like_cards(trade.user1_cards) # pyright: ignore[reportArgumentType]
    card_grouped2 = gachalib.cards.group_like_cards(trade.user2_cards) # pyright: ignore[reportArgumentType]

    field1 = ""
    for a in card_grouped1:
        field1 += f"> {a[1]} × `{a[0].name}` ({a[0].rarity})\n"
    if len(field1) < 1:
        field1 = "> [...]"

    field2 = ""
    for b in card_grouped2:
        field2 += f"> {b[1]} × `{b[0].name}` ({b[0].rarity})\n"
    if len(field2) < 1:
        field2 = "> [...]"

    embed.add_field(name=f"- {trade.user1.display_name} {'-'*(40-len(trade.user1.display_name))}\n", value=field1, inline=False) # pyright: ignore[reportOptionalMemberAccess]
    embed.add_field(name=f"- {trade.user2.display_name} {'-'*(40-len(trade.user2.display_name))}\n", value=field2, inline=False) # pyright: ignore[reportOptionalMemberAccess]

#########################
#     Add Trade UI      #
#########################

class TradeAddModal(discord.ui.Modal):
    def __init__(self, trade: gachalib.types.Trade) -> None:
        super().__init__(title="Add card to trade")
        self.trade = trade

        self.add_item(discord.ui.TextInput(label="Card ID"))
        self.add_item(discord.ui.TextInput(label="Ammount"))

    async def on_submit(self, interaction: discord.Interaction):
        cards = gachalib.cards_user.get_users_cards_by_card_id(interaction.user.id, self.children[0].value)[1]

        t_cards = self.trade.user1_cards
        if interaction.user.id == self.trade.user2.id: # pyright: ignore[reportOptionalMemberAccess]
            t_cards = self.trade.user2_cards

        a_cards = []
        for card in cards:
            if card not in t_cards:
                a_cards.append(card)

        a_cards = a_cards[0:int(self.children[1].value)]

        if len(gachalib.cards.group_like_cards(t_cards + a_cards)) > 10: # pyright: ignore[reportArgumentType]
            await interaction.response.send_message("You can only have up to 10 different cards per trade.", ephemeral=True)
            return

        t_cards.extend(a_cards)
        await interaction.response.defer()
        await unaccept_trade(self.trade)
        await self.trade.message.edit(embed=trade_embed(self.trade), view=TradeView(self.trade)) # pyright: ignore[reportArgumentType, reportOptionalMemberAccess]

#########################
#    Remove card UI     #
#########################

# Would have used a modal, but discord.py hasn't added support for it yet (afaik)
class Select(discord.ui.Select):
    def __init__(self, trade: gachalib.types.Trade, embed_interact: discord.Interaction):
        self.trade = trade
        self.embed_interact = embed_interact

        self.t_cards = trade.user1_cards
        if embed_interact.user.id == trade.user2.id: # pyright: ignore[reportOptionalMemberAccess]
            self.t_cards = trade.user2_cards

        options = []
        for card in gachalib.cards.group_like_cards(self.t_cards): # pyright: ignore[reportArgumentType]
            options.append(discord.SelectOption(
                label=f"[{card[0].card_id}] {card[1]} × {card[0].name} ({card[0].rarity})\n"
            ))

        super().__init__(placeholder="Select a card to remove",max_values=1,min_values=1,options=options)
    async def callback(self, interaction: discord.Interaction):
        await self.embed_interact.delete_original_response()
        await interaction.response.defer()
        sel_id = re.search("(?<=^\[)\d+(?=])", self.values[0]).group() # pyright: ignore[reportOptionalMemberAccess]

        n_cards = list(self.t_cards)
        for card in n_cards:
            if card.card_id == int(sel_id):
                self.t_cards.remove(card)
        await unaccept_trade(self.trade)
        await self.trade.message.edit(embed=trade_embed(self.trade), view=TradeView(self.trade)) # pyright: ignore[reportArgumentType, reportOptionalMemberAccess]

class TradeRemoveView(discord.ui.View):
    def __init__(self, trade: gachalib.types.Trade, embed_interact: discord.Interaction) -> None:
        super().__init__()
        self.add_item(Select(trade, embed_interact))

#########################
#    Trade request UI   #
#########################

class TradeRequestView(discord.ui.View):
    def __init__(self, trade: gachalib.types.Trade):
        self.trade = trade
        super().__init__()

    @discord.ui.button(label="Accept", style=discord.ButtonStyle.success, row=0, custom_id="accept_btn")
    async def add_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        if await check_user(self.trade, interaction, self.trade.user2): # pyright: ignore[reportArgumentType]
            embed = trade_embed(self.trade)
            view = TradeView(self.trade)
            msg = await interaction.response.send_message(embed=embed, view=view) # pyright: ignore[reportArgumentType]
            self.trade.message = await interaction.channel.fetch_message(msg.message_id)# pyright: ignore[reportArgumentType, reportAttributeAccessIssue, reportOptionalMemberAccess]
            await interaction.message.delete() # pyright: ignore[reportOptionalMemberAccess]

    @discord.ui.button(label="Decline", style=discord.ButtonStyle.danger, row=0, custom_id="decline_btn")
    async def remove_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        if await check_user(self.trade, interaction):
            await interaction.response.defer()
            await interaction.message.delete() # pyright: ignore[reportOptionalMemberAccess]

def trade_request_embed(trade: gachalib.types.Trade) -> discord.Embed | str:
    embed = discord.Embed(
        title="Trade request",
        color=0x5865f2,
        description=f"{trade.user1.mention} sent {trade.user2.mention} a trade request!" # pyright: ignore[reportOptionalMemberAccess]
    )

    return embed

#########################
#       Accept UI       #
#########################

async def accept_trade(trade: gachalib.types.Trade, interaction: discord.Interaction):
    if trade.accepted_user and trade.accepted_user.id != interaction.user.id:
        await do_trade(trade, interaction)
    elif trade.accept_message:
        await interaction.response.defer()
    else:
        trade.accepted_user = interaction.user # pyright: ignore[reportAttributeAccessIssue]
        embed = trade_accept_embed(trade)
        view = TradeAcceptView(trade)
        msg = await interaction.response.send_message(embed=embed, view=view) # pyright: ignore[reportArgumentType]
        trade.accept_message = await interaction.channel.fetch_message(msg.message_id) # pyright: ignore[reportAttributeAccessIssue, reportArgumentType, reportOptionalMemberAccess]

async def unaccept_trade(trade: gachalib.types.Trade):
    if trade.accept_message:
        await trade.accept_message.delete()
        trade.accept_message = None
        trade.accepted_user = None

class TradeAcceptView(discord.ui.View):
    def __init__(self, trade: gachalib.types.Trade):
        self.trade = trade

        super().__init__()

    @discord.ui.button(label="Accept", style=discord.ButtonStyle.success, row=0, custom_id="accept_btn")
    async def add_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        if await check_user(self.trade, interaction):
            await accept_trade(self.trade, interaction)

    @discord.ui.button(label="Decline", style=discord.ButtonStyle.danger, row=0, custom_id="decline_btn")
    async def remove_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        if await check_user(self.trade, interaction):
            await interaction.response.defer()
            await unaccept_trade(self.trade)

def trade_accept_embed(trade: gachalib.types.Trade) -> discord.Embed | str:
    embed = discord.Embed(
        title="Accept trade?",
        color=0x008447,
        description=f"{trade.accepted_user.mention} would like to agree to this trade!"  # pyright: ignore[reportOptionalMemberAccess]
    )
    build_embed(embed, trade)

    return embed

#########################
#     Main Trade UI     #
#########################

class TradeView(discord.ui.View):
    def __init__(self, trade: gachalib.types.Trade):
        super().__init__()
        self.trade = trade
        self.message = None

    @discord.ui.button(label="Add card", style=discord.ButtonStyle.primary, row=0, custom_id="add_btn")
    async def add_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        if await check_user(self.trade, interaction):
            await interaction.response.send_modal(TradeAddModal(trade=self.trade))

    @discord.ui.button(label="Remove card", style=discord.ButtonStyle.danger, row=0, custom_id="remove_btn")
    async def remove_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        if await check_user(self.trade, interaction):
            t_cards = self.trade.user1_cards
            if interaction.user.id == self.trade.user2.id: # pyright: ignore[reportOptionalMemberAccess]
                t_cards = self.trade.user2_cards
            if len(t_cards) < 1:
                await interaction.response.send_message("No cards to remove", ephemeral=True)
                return
            await interaction.response.send_message("Remove card from trade", view=TradeRemoveView(trade=self.trade, embed_interact=interaction), ephemeral=True)

    @discord.ui.button(label="Accept", style=discord.ButtonStyle.success, row=0, custom_id="accept_btn")
    async def accept_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        if await check_user(self.trade, interaction):
            await accept_trade(self.trade, interaction)

    def disable(self):
        for child in self.children:
            child.disabled=True # pyright: ignore[reportAttributeAccessIssue]

def trade_embed(trade: gachalib.types.Trade) -> discord.Embed | str:
    embed = discord.Embed(title="⚠️ TRADE OFFER ⚠️", color=0xffcb4e)
    build_embed(embed, trade)

    return embed

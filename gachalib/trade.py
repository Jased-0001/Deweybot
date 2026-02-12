import db_lib,Bot
import gachalib.cards, gachalib.cards_inventory, gachalib.types
import discord
import math

async def check_user(trade: gachalib.types.Trade, interaction: discord.Interaction, user: discord.User | None = None):
    if user and interaction.user.id != user.id:
        await interaction.response.send_message("You can't do this!!", ephemeral=True)
        return False
    if interaction.user.id == trade.user1.id or interaction.user.id == trade.user2.id: # pyright: ignore[reportOptionalMemberAccess]
        return True
    await interaction.response.send_message("You can't interact with this trade", ephemeral=True)
    return False

def get_user_cards(trade: gachalib.types.Trade, interaction: discord.Interaction):
    t_cards = trade.user1_cards
    if interaction.user.id == trade.user2.id: # pyright: ignore[reportOptionalMemberAccess]
        t_cards = trade.user2_cards
    return t_cards

def get_user(trade: gachalib.types.Trade, interaction: discord.Interaction):
    user = trade.user1
    if interaction.user.id == trade.user2.id: # pyright: ignore[reportOptionalMemberAccess]
        user = trade.user2
    return user

def user_cards_text(cards: list[gachalib.types.CardsInventory]):
    card_grouped = gachalib.cards.group_like_cards(cards) # pyright: ignore[reportArgumentType]

    field = ""
    for a in card_grouped:
        field += f"> {a[1]} × `{a[0].name}` ({a[0].rarity})\n"
    if len(field) < 1:
        field = "> [...]"

    return field

#########################
#       Success UI      #
#########################

class TradeSucessView(discord.ui.LayoutView):
    def __init__(self, trade: gachalib.types.Trade):
        super().__init__(timeout=None)

        container = discord.ui.Container(
            discord.ui.TextDisplay("## Successful trade!"),
            discord.ui.Separator(),
            discord.ui.TextDisplay(f"### {trade.user1.display_name}"),
            discord.ui.TextDisplay(user_cards_text(trade.user1_cards)),
            discord.ui.Separator(),
            discord.ui.TextDisplay(f"### {trade.user2.display_name}"),
            discord.ui.TextDisplay(user_cards_text(trade.user2_cards)),
            accent_color=0x008447
        )
        self.add_item(container)

async def do_trade(trade: gachalib.types.Trade, interaction: discord.Interaction):
    for a in trade.user1_cards:
        gachalib.cards_inventory.change_card_owner(trade.user2.id, a.inv_id) # pyright: ignore[reportOptionalMemberAccess]
    for b in trade.user2_cards:
        gachalib.cards_inventory.change_card_owner(trade.user1.id, b.inv_id) # pyright: ignore[reportOptionalMemberAccess]
    await trade.accept_message.delete() # pyright: ignore[reportOptionalMemberAccess]
    await trade.message.delete() # pyright: ignore[reportOptionalMemberAccess]
    await interaction.response.send_message(view=TradeSucessView(trade))

#########################
#     Add Trade UI      #
#########################

async def add_cards_to_trade(trade: gachalib.types.Trade, interaction: discord.Interaction, card_id: int, ammount: int):
    cards = gachalib.cards_inventory.get_users_cards_by_card_id(interaction.user.id, card_id)[1]

    t_cards = get_user_cards(trade, interaction)

    a_cards = []
    for card in cards:
        if card not in t_cards:
            a_cards.append(card)

    a_cards = a_cards[0:ammount]

    if len(gachalib.cards.group_like_cards(t_cards + a_cards)) > 10: # pyright: ignore[reportArgumentType]
        await interaction.response.send_message("You can only have up to 10 different cards per trade.", ephemeral=True)
        return

    t_cards.extend(a_cards)
    await interaction.response.defer()
    await unaccept_trade(trade)
    await trade.message.edit(view=TradeView(trade)) # pyright: ignore[reportArgumentType, reportOptionalMemberAccess]

class TradeAddModal(discord.ui.Modal):
    def __init__(self, trade: gachalib.types.Trade) -> None:
        super().__init__(title="Add card to trade")
        self.trade = trade

        self.add_item(discord.ui.TextInput(label="Card ID"))
        self.add_item(discord.ui.TextInput(label="Ammount"))

    async def on_submit(self, interaction: discord.Interaction):
        await add_cards_to_trade(self.trade, interaction, int(self.children[0].value), int(self.children[1].value))

#########################
#    Remove card UI     #
#########################

class TradeRemoveSelect(discord.ui.Select):
    def __init__(self, trade: gachalib.types.Trade, embed_interact: discord.Interaction):
        self.trade = trade
        self.embed_interact = embed_interact

        self.t_cards = get_user_cards(trade, embed_interact)

        options = []
        for card in gachalib.cards.group_like_cards(self.t_cards): # pyright: ignore[reportArgumentType]
            options.append(discord.SelectOption(
                label=f"{card[1]} × {card[0].name} ({card[0].rarity})\n",
                value=card[0].card_id
            ))

        super().__init__(placeholder="Select a card to remove",max_values=1,min_values=1,options=options)

    async def callback(self, interaction: discord.Interaction):
        await self.embed_interact.delete_original_response()
        await interaction.response.defer()
        sel_id = int(self.values[0])    

        n_cards = list(self.t_cards)
        for card in n_cards:
            if card.card_id == sel_id:
                self.t_cards.remove(card)
        await unaccept_trade(self.trade)
        await self.trade.message.edit(view=TradeView(self.trade)) # pyright: ignore[reportArgumentType, reportOptionalMemberAccess]

class TradeRemoveView(discord.ui.LayoutView):
    def __init__(self, trade: gachalib.types.Trade, embed_interact: discord.Interaction) -> None:
        super().__init__(timeout=None)
        container = discord.ui.Container(
            discord.ui.TextDisplay("## Remove cards from trade"),
            discord.ui.TextDisplay("Select a card to remove from the trade offer"),
            discord.ui.ActionRow(
                TradeRemoveSelect(trade, embed_interact)
            )
        )
        self.add_item(container)

#########################
#      Add card UI2     #
#########################

class TradeAddRow(discord.ui.ActionRow):
    def __init__(self, page: int, cards: tuple[int, list[gachalib.types.Card]], trade: gachalib.types.Trade, embed_interact: discord.Interaction):
        super().__init__()
        self.page = page
        self.cards = cards
        self.trade = trade
        self.embed_interact = embed_interact

    @discord.ui.button(label="⬅️", style=discord.ButtonStyle.primary, custom_id="left_btn")
    async def left_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        page = max(self.page-1, 1)
        await interaction.response.edit_message(view=TradeAddView(page, self.trade, self.embed_interact))

    @discord.ui.button(label="➡️", style=discord.ButtonStyle.primary, custom_id="right_btn")
    async def right_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        page = min(self.page+1, math.ceil(len(self.cards)/25))
        await interaction.response.edit_message(view=TradeAddView(page, self.trade, self.embed_interact))

class TradeAddNumberSelect(discord.ui.Select):
    def __init__(self, card_id: int, page:int, trade: gachalib.types.Trade, embed_interact: discord.Interaction):
        self.card_id = card_id
        self.page = page
        self.trade = trade
        self.embed_interact = embed_interact
        cards = gachalib.cards_inventory.get_users_cards_by_card_id(get_user(trade, embed_interact).id, card_id)[1]

        options = []
        for i in range(1, min(len(cards)+1, 25)): # pyright: ignore[reportArgumentType]
            options.append(discord.SelectOption(
                label=i
            ))

        super().__init__(placeholder="Select number of cards to add",max_values=1,min_values=1,options=options)

    async def callback(self, interaction: discord.Interaction):
        await add_cards_to_trade(self.trade, interaction, self.card_id, int(self.values[0]))
        await interaction.delete_original_response()

class TradeAddNumber(discord.ui.LayoutView):
    def __init__(self, card_id: int, page:int, trade: gachalib.types.Trade, embed_interact: discord.Interaction) -> None:
        super().__init__(timeout=None)
        card = gachalib.cards.get_card_by_id(card_id)[1]

        container = discord.ui.Container(
            discord.ui.TextDisplay("## Choose ammount"),
            discord.ui.TextDisplay(f"How many {card.name}s would you like to add?"),
            discord.ui.Separator(),
            discord.ui.ActionRow(
                TradeAddNumberSelect(card_id, page, trade, embed_interact)
            ),  
        )
        self.add_item(container)

class TradeAddSelect(discord.ui.Select):
    def __init__(self, page:int, cards: tuple[int, list[gachalib.types.Card]], trade: gachalib.types.Trade, embed_interact: discord.Interaction):
        self.page = page
        self.trade = trade
        self.embed_interact = embed_interact

        options = []
        for card in cards: # pyright: ignore[reportArgumentType]
            options.append(discord.SelectOption(
                label=f"[{card[1]}x] {card[0].name} ({card[0].rarity})\n",
                value=card[0].card_id
            ))

        super().__init__(placeholder="Select a card to add",max_values=1,min_values=1,options=options)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.edit_message(view=TradeAddNumber(int(self.values[0]), self.page, self.trade, self.embed_interact))

class TradeAddID(discord.ui.Button):
    def __init__(self, trade: gachalib.types.Trade) -> None:
        super().__init__(label="Add card by Id",style=discord.ButtonStyle.primary, custom_id="id_btn")
        self.trade = trade

    async def callback(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_modal(TradeAddModal(self.trade))
        await interaction.delete_original_response()

class TradeAddView(discord.ui.LayoutView):
    def __init__(self, page:int, trade: gachalib.types.Trade, embed_interact: discord.Interaction) -> None:
        super().__init__(timeout=None)
        cards = gachalib.cards_inventory.get_users_cards(get_user(trade, embed_interact).id)[1]
        cards = gachalib.cards.group_like_cards(cards)

        items = [
            discord.ui.Section(
                "## Add cards to trade",
                "Select a card to add to the trade offer",
                accessory=(TradeAddID(trade))
            ),
            discord.ui.Separator(),
            discord.ui.ActionRow(
                TradeAddSelect(page, cards[page*25-25:page*25], trade, embed_interact)
            ),  
        ]

        if len(cards) > 25:
            items.insert(2, discord.ui.TextDisplay(f"Page {page}"))
            items.insert(3, discord.ui.TextDisplay(f"-# Viewing cards {page*25-24}-{min(page*25, len(cards))}"))
            items.append(TradeAddRow(page, cards, trade, embed_interact))

        container = discord.ui.Container(*items)
        self.add_item(container)

#########################
#    Trade request UI   #
#########################

class TradeReqestRow(discord.ui.ActionRow):
    def __init__(self, trade: gachalib.types.Trade):
        super().__init__()
        self.trade = trade

    @discord.ui.button(label="Accept", style=discord.ButtonStyle.success, row=0, custom_id="accept_btn")
    async def add_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        if await check_user(self.trade, interaction, self.trade.user2): # pyright: ignore[reportArgumentType]
            await interaction.message.delete() # pyright: ignore[reportOptionalMemberAccess]
            msg = await interaction.response.send_message(view=TradeView(self.trade)) # pyright: ignore[reportArgumentType]
            self.trade.message = await interaction.channel.fetch_message(msg.message_id)# pyright: ignore[reportArgumentType, reportAttributeAccessIssue, reportOptionalMemberAccess]

    @discord.ui.button(label="Decline", style=discord.ButtonStyle.danger, row=0, custom_id="decline_btn")
    async def remove_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        if await check_user(self.trade, interaction):
            await interaction.response.defer()
            await interaction.message.delete() # pyright: ignore[reportOptionalMemberAccess]

class TradeRequestView(discord.ui.LayoutView):
    def __init__(self, trade: gachalib.types.Trade):
        super().__init__(timeout=None)

        container = discord.ui.Container(
            discord.ui.TextDisplay("## Trade request"),
            discord.ui.TextDisplay(f"{trade.user1.mention} sent {trade.user2.mention} a trade request!"),
            discord.ui.Separator(),
            TradeReqestRow(trade)
        )
        self.add_item(container)


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
        msg = await interaction.response.send_message(view=TradeAcceptView(trade)) # pyright: ignore[reportArgumentType]
        trade.accept_message = await interaction.channel.fetch_message(msg.message_id) # pyright: ignore[reportAttributeAccessIssue, reportArgumentType, reportOptionalMemberAccess]

async def unaccept_trade(trade: gachalib.types.Trade):
    if trade.accept_message:
        await trade.accept_message.delete()
        trade.accept_message = None
        trade.accepted_user = None

class TradeAcceptRow(discord.ui.ActionRow):
    def __init__(self, trade: gachalib.types.Trade):
        super().__init__()
        self.trade = trade

    @discord.ui.button(label="Accept", style=discord.ButtonStyle.success, row=0, custom_id="accept_btn")
    async def add_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        if await check_user(self.trade, interaction):
            await accept_trade(self.trade, interaction)

    @discord.ui.button(label="Decline", style=discord.ButtonStyle.danger, row=0, custom_id="decline_btn")
    async def remove_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        if await check_user(self.trade, interaction):
            await interaction.response.defer()
            await unaccept_trade(self.trade)

class TradeAcceptView(discord.ui.LayoutView):
    def __init__(self, trade: gachalib.types.Trade):
        super().__init__(timeout=None)
        self.trade = trade

        container = discord.ui.Container(
            discord.ui.TextDisplay("## Accept trade?"),
            discord.ui.TextDisplay(f"{trade.accepted_user.mention} would like to agree to this trade!"),
            discord.ui.Separator(),
            TradeAcceptRow(trade),
            accent_color=0x008447
        )
        self.add_item(container)

    async def on_timeout(self):
        await unaccept_trade(trade)

#########################
#     Main Trade UI     #
#########################

class TradeActionRow(discord.ui.ActionRow):
    def __init__(self, trade: gachalib.types.Trade):
        self.trade = trade
        super().__init__()

    @discord.ui.button(label="Add card", style=discord.ButtonStyle.primary)
    async def add_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        if await check_user(self.trade, interaction):
            await interaction.response.send_message(view=TradeAddView(1, self.trade, interaction), ephemeral=True)

    @discord.ui.button(label="Remove card", style=discord.ButtonStyle.danger)
    async def remove_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        if await check_user(self.trade, interaction):
            t_cards = get_user_cards(self.trade, interaction)
            if len(t_cards) < 1:
                await interaction.response.send_message("No cards to remove", ephemeral=True)
                return
            await interaction.response.send_message(view=TradeRemoveView(trade=self.trade, embed_interact=interaction), ephemeral=True)

    @discord.ui.button(label="Accept", style=discord.ButtonStyle.success)
    async def accept_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        if await check_user(self.trade, interaction):
            await accept_trade(self.trade, interaction)

class TradeView(discord.ui.LayoutView):
    def __init__(self, trade: gachalib.types.Trade):
        super().__init__(timeout=None)
        self.trade = trade

        container = discord.ui.Container(
            discord.ui.TextDisplay("# ⚠️ TRADE OFFER ⚠️"),
            discord.ui.Separator(),
            discord.ui.TextDisplay(f"### {trade.user1.display_name}"),
            discord.ui.TextDisplay(user_cards_text(trade.user1_cards)),
            discord.ui.Separator(),
            discord.ui.TextDisplay(f"### {trade.user2.display_name}"),
            discord.ui.TextDisplay(user_cards_text(trade.user2_cards)),
            accent_color=0xffcb4e
        )

        self.add_item(container)
        self.add_item(TradeActionRow(trade))

    async def on_timeout(self):
        await unaccept_trade(self.trade)
        await self.trade.message.delete()
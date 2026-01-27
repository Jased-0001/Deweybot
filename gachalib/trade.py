import db_lib,Bot
import gachalib.cards, gachalib.cards_user, gachalib.types
import discord

class TradeAddModal(discord.ui.Modal):
    def __init__(self, trade, embed_interact) -> None:
        super().__init__(title="Add card to trade")
        self.trade = trade
        self.embed_interact = embed_interact

        self.add_item(discord.ui.TextInput(label="Card ID"))
        self.add_item(discord.ui.TextInput(label="Ammount"))

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        cards = gachalib.cards_user.get_users_cards_by_card_id(interaction.user.id, self.children[0].value)[1]

        t_cards = self.trade.user1_cards
        if interaction.user.id == self.trade.user2.id:
            t_cards = self.trade.user2_cards

        # TODO: remove duplicates

        cards = cards[0:int(self.children[1].value)]
        t_cards.extend(cards)

        await self.embed_interact.edit_original_response(embed=trade_embed(self.trade), view=TradeView(self.trade))

class TradeRemoveModal(discord.ui.Modal):
    def __init__(self, trade) -> None:
        super().__init__(title="Remove card from trade")

        self.add_item(discord.ui.InputText(label="Card ID"))

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer

class TradeView(discord.ui.View):
    def __init__(self, trade:gachalib.types.Trade):
        super().__init__()
        self.trade = trade
        self.message = None

    async def checkUser(self, interaction):
        if interaction.user.id == self.trade.user1.id or interaction.user.id == self.trade.user2.id:
            return True
        await interaction.response.send_message("You can't interact with this trade", ephemeral=True)
        return False

    @discord.ui.button(label="Add card", style=discord.ButtonStyle.primary, row=0, custom_id="add_btn")
    async def add_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        if await self.checkUser(interaction):
            await interaction.response.send_modal(TradeAddModal(trade=self.trade, embed_interact=interaction))

    @discord.ui.button(label="Remove card", style=discord.ButtonStyle.danger, row=0, custom_id="remove_btn")
    async def remove_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        if await self.checkUser(interaction):
            await interaction.response.send_modal(TradeRemoveModal(trade=self.trade, embed_interact=interaction))

    @discord.ui.button(label="Accept", style=discord.ButtonStyle.success, row=0, custom_id="accept_btn")
    async def accept_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        if await self.checkUser(interaction):
            await interaction.response.send_message(f"not implemented", ephemeral=True)
            self.disable()

    def disable(self):
        for child in self.children:
            child.disabled=True

def trade_embed(trade:gachalib.types.Trade) -> discord.Embed | str:
    # Convert user_cards to cards
    cards1 = []
    for user_card in trade.user1_cards:
        cards1.append(gachalib.cards.get_card_by_id(user_card.card_id))
    cards2 = []
    for user_card in trade.user2_cards:
        cards2.append(gachalib.cards.get_card_by_id(user_card.card_id))

    card_grouped1 = gachalib.cards.group_like_cards(trade.user1_cards)
    card_grouped2 = gachalib.cards.group_like_cards(trade.user2_cards)

    # Display cards
    field1 = ""
    for a in card_grouped1:
        field1 += f"> {a[1]} × `{a[0].name}` ({a[0].rarity})\n"
    if len(field1) < 1:
        field1 = "> "

    field2 = ""
    for b in card_grouped2:
        field2 += f"> {b[1]} × `{b[0]}` ({b[0].rarity})\n"
    if len(field2) < 1:
        field2 = "> "

    embed = discord.Embed(title="⚠️ TRADE OFFER ⚠️", color=0xffcb4e)
    embed.add_field(name=f"= {trade.user1.display_name} {'='*(25-len(trade.user1.display_name))}\n", value=field1, inline=False)
    embed.add_field(name=f"= {trade.user2.display_name} {'='*(25-len(trade.user2.display_name))}\n", value=field2, inline=False)

    return embed

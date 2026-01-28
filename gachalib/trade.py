import db_lib,Bot
import gachalib.cards, gachalib.cards_user, gachalib.types
import discord
import re

class TradeAddModal(discord.ui.Modal):
    def __init__(self, trade: gachalib.types.Trade) -> None:
        super().__init__(title="Add card to trade")
        self.trade = trade

        self.add_item(discord.ui.TextInput(label="Card ID"))
        self.add_item(discord.ui.TextInput(label="Ammount"))

    async def on_submit(self, interaction: discord.Interaction):
        cards = gachalib.cards_user.get_users_cards_by_card_id(interaction.user.id, self.children[0].value)[1]

        t_cards = self.trade.user1_cards
        if interaction.user.id == self.trade.user2.id:
            t_cards = self.trade.user2_cards

        a_cards = []
        for card in cards:
            if card not in t_cards:
                a_cards.append(card)

        a_cards = a_cards[0:int(self.children[1].value)]

        if len(gachalib.cards.group_like_cards(t_cards + a_cards)) > 10:
            await interaction.response.send_message("You can only have up to 10 different cards per trade.", ephemeral=True)
            return

        t_cards.extend(a_cards)
        await interaction.response.defer()
        await self.trade.message.edit(embed=trade_embed(self.trade), view=TradeView(self.trade))


# Would have used a modal, but discord.py hasn't added support for it yet (afaik)
class Select(discord.ui.Select):
    def __init__(self, trade: gachalib.types.Trade, embed_interact: discord.Interaction):
        self.trade = trade
        self.embed_interact = embed_interact

        self.t_cards = trade.user1_cards
        if embed_interact.user.id == trade.user2.id:
            self.t_cards = trade.user2_cards

        options = []
        for card in gachalib.cards.group_like_cards(self.t_cards):
            options.append(discord.SelectOption(
                label=f"[{card[0].card_id}] {card[1]} × {card[0].name} ({card[0].rarity})\n"
            ))

        super().__init__(placeholder="Select a card to remove",max_values=1,min_values=1,options=options)
    async def callback(self, interaction: discord.Interaction):
        await self.embed_interact.delete_original_response()
        await interaction.response.defer()
        sel_id = re.search("(?<=^\[)\d+(?=\])", self.values[0]).group()

        n_cards = list(self.t_cards)
        for card in n_cards:
            if card.card_id == int(sel_id):
                self.t_cards.remove(card)
        await self.trade.message.edit(embed=trade_embed(self.trade), view=TradeView(self.trade))

class TradeRemoveView(discord.ui.View):
    def __init__(self, trade: gachalib.types.Trade, embed_interact: discord.Interaction) -> None:
        super().__init__()
        self.add_item(Select(trade, embed_interact))



class TradeView(discord.ui.View):
    def __init__(self, trade: gachalib.types.Trade):
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
            await interaction.response.send_modal(TradeAddModal(trade=self.trade))

    @discord.ui.button(label="Remove card", style=discord.ButtonStyle.danger, row=0, custom_id="remove_btn")
    async def remove_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        if await self.checkUser(interaction):
            t_cards = self.trade.user1_cards
            if interaction.user.id == self.trade.user2.id:
                t_cards = self.trade.user2_cards
            if len(t_cards) < 1:
                await interaction.response.send_message("No cards to remove", ephemeral=True)
                return
            await interaction.response.send_message("Remove card from trade", view=TradeRemoveView(trade=self.trade, embed_interact=interaction), ephemeral=True)

    @discord.ui.button(label="Accept", style=discord.ButtonStyle.success, row=0, custom_id="accept_btn")
    async def accept_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        if await self.checkUser(interaction):
            await interaction.response.send_message(f"not implemented", ephemeral=True)
            self.disable()

    def disable(self):
        for child in self.children:
            child.disabled=True

def trade_embed(trade: gachalib.types.Trade) -> discord.Embed | str:
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
    embed.add_field(name=f"= {trade.user1.display_name} {'='*(40-len(trade.user1.display_name))}\n", value=field1, inline=False)
    embed.add_field(name=f"= {trade.user2.display_name} {'='*(40-len(trade.user2.display_name))}\n", value=field2, inline=False)

    return embed

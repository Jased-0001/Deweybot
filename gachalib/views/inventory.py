import discord, math, Bot

import gachalib.cards
import gachalib.cards_inventory
import gachalib, gachalib.types
import gachalib.views.browserow
import gachalib.views.card


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

class viewCardButton(discord.ui.Button):
    def __init__(self, card: gachalib.types.Card) -> None:
        super().__init__(label="View", style=discord.ButtonStyle.secondary)
        self.card = card

    async def callback(self, interaction: discord.Interaction) -> None:
        image=gachalib.get_small_thumbnail(self.card)
        await interaction.response.send_message(
            view=gachalib.views.card.GachaView(self.card, image), file=image, ephemeral=True,
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
            image = f"{Bot.DeweyConfig["imageurl"]}/small/{gachalib.get_small_filename(card[0])}"
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
            browse_row = gachalib.views.browserow.BrowseRow(InventoryView, page, num_pages, user, sort, button)
            if type(browse_row.children[0]) == discord.ui.Button and type(browse_row.children[1]) == discord.ui.Button:
                browse_row.children[0].disabled = page == 1
                browse_row.children[1].disabled = page == num_pages
            items.append(browse_row)

        container = discord.ui.Container(*items)
        self.add_item(container)
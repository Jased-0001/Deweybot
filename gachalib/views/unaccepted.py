import discord, Bot
import gachalib.types, gachalib.cards_inventory, gachalib.cards
import math
import gachalib.views.browserow


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
            image = f"{Bot.DeweyConfig["imageurl"]}/small/{gachalib.get_small_filename(card)}"
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
            browse_row = gachalib.views.browserow.BrowseRow(UnacceptedView, page, num_pages)
            if type(browse_row.children[0]) == discord.ui.Button and type(browse_row.children[1]) == discord.ui.Button:
                browse_row.children[0].disabled = page == 1
                browse_row.children[1].disabled = page == num_pages
            items.append(browse_row)

        container = discord.ui.Container(*items)
        self.add_item(container)
import discord
import gachalib
import gachalib.types, gachalib.cards_inventory, gachalib.cards

class BrowserView(discord.ui.View):
    def __init__(self,inventory:bool=False,uid:int=0,cards:list[gachalib.types.Card]=[],page:int=1,sort:gachalib.SortOptions="ID"):
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
        return gachalib.cardBrowserEmbed(uid=self.uid,cards=self.cards,page=self.page,inventory=self.isInventory)


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
import discord
import gachalib
import gachalib.types, gachalib.views.card

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
            image=gachalib.get_small_thumbnail(card)
            await interaction.response.send_message(
                view=gachalib.views.card.GachaView(card,image), file=image, ephemeral=True
            )
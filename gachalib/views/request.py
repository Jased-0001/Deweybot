import discord
import gachalib
import gachalib.types, gachalib.cards

class RequestView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.message: discord.Message | None = None

    @discord.ui.button(label="Approve", style=discord.ButtonStyle.success, row=0, custom_id="approve_btn")
    async def approve_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        assert interaction.message, "no interaction.message"
        a = gachalib.gacha_database.read_data(f"SELECT id FROM gacha WHERE (request_message_id) = (?)", (interaction.message.id,))[0]
        #print("I believe this is id ", a[0])

        _, card = gachalib.cards.get_card_by_id(a[0])
        _, status = await gachalib.cards.approve_card(True, card)

        await interaction.response.send_message(status)

        self.disable()


    @discord.ui.button(label="Deny", style=discord.ButtonStyle.secondary, row=0, custom_id="deny_btn")
    async def deny_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        assert interaction.message, "no interaction.message"
        a = gachalib.gacha_database.read_data(f"SELECT id FROM gacha WHERE (request_message_id) = (?)", (interaction.message.id,))[0]

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
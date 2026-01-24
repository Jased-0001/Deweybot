import db_lib,Bot
import gachalib.cards, gachalib.cards_user, gachalib.types
import discord

#name, card_description, rarity, filename, title: str = "None", description: str = "None"
def gacha_embed(title:str, description:str, card:gachalib.types.Card) -> discord.Embed:
    embed = discord.Embed(title=title, description=description)
    embed.add_field(name="Name!", value=card.name)
    embed.add_field(name="Description!", value=card.description)
    embed.add_field(name="Rarity!", value=card.rarity)
    embed.set_image(url=Bot.DeweyConfig["httpurl"] + card.filename)
    return embed


class RequestView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.message = None

    @discord.ui.button(label="Approve", style=discord.ButtonStyle.success, row=0, custom_id="approve_btn")
    async def approve_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        a = db_lib.read_data(f"SELECT id, maker_id, accepted FROM gacha WHERE (request_message_id) = (?)", (interaction.message.id,))[0] # pyright: ignore[reportOptionalMemberAccess]
        #print("I believe this is id ", a[0])

        if not a[2]:
            gachalib.cards.update_card(a[0], "accepted", "1")
            await interaction.response.send_message(f"{interaction.user.mention} approved ID {a[0]} by ID {a[1]}!", ephemeral=False, silent=True)
        else:
            await interaction.response.send_message(f"This card was already accepted", ephemeral=True)


    @discord.ui.button(label="Deny", style=discord.ButtonStyle.secondary, row=0, custom_id="deny_btn")
    async def deny_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        a = db_lib.read_data(f"SELECT id FROM gacha WHERE (request_message_id) = (?)", (interaction.message.id,))[0] # pyright: ignore[reportOptionalMemberAccess]

        if gachalib.cards.delete_card(a[0]):
            await interaction.response.send_message(f"Card DENIED and DELETED!", ephemeral=False)
        else:
            await interaction.response.send_message(f"I couldn't find it???", ephemeral=False)

    @discord.ui.button(label="BAN FROM DEWEY", style=discord.ButtonStyle.danger, row=1, custom_id="ban_btn")
    async def ban_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.send_message(f"not implemented", ephemeral=True)

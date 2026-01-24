import db_lib,Bot
import discord
import os

def get_card_by_id(id:int) -> dict | bool:
    try:
        a = db_lib.read_data(f"SELECT name,description,rarity,filename,maker_id,accepted FROM gacha WHERE (id) = (?)", (id,))[0]
        return {'name':a[0],'description':a[1],'rarity':a[2],'filename':a[3],'maker_id':a[4],'accepted':a[5],'id':id}
    except IndexError:
        return False


def get_card_by_id_range(id_start:int, id_end:int) -> list[dict] | bool:
    try:
        a = db_lib.read_data(f"SELECT name,description,rarity,filename,maker_id,accepted,id FROM gacha WHERE (id) BETWEEN (?) AND (?);", (id_start,id_end)) # type: ignore
        b = []

        for c in a:
            b.append( {'name':c[0],'description':c[1],'rarity':c[2],'filename':c[3],'maker_id':c[4],'accepted':c[5], 'id':c[6] })

        return b
    except IndexError:
        return False

def make_new_card(userid:int, messageid:int, id:int, name:str, description:str, rarity:str, filename:str):
    db_lib.write_data("INSERT INTO gacha \
(maker_id, request_message_id, id, accepted, \
name, description, rarity, filename) \
VALUES (?,?,?,?,?,?,?,?)", (userid,messageid,id,False,name,description,rarity,filename)) # type: ignore
    
def update_card(id, update, value):
    db_lib.write_data(f"UPDATE gacha SET {update}='{value}' WHERE id={id};", ()) # type: ignore
    
def delete_card(id):
    filename = get_card_by_id(id)['filename']
    try:
        os.remove("images/" + filename)
    except FileNotFoundError:
        pass
    db_lib.write_data(f"DELETE FROM gacha WHERE id={id};", ()) # type: ignore


def gacha_embed(name, card_description, rarity, filename, title: str = "None", description: str = "None") -> discord.Embed:
    embed = discord.Embed(title=title, description=description)
    embed.add_field(name="Name!", value=name)
    embed.add_field(name="Description!", value=card_description)
    embed.add_field(name="Rarity!", value=rarity)
    embed.set_image(url=Bot.DeweyConfig["httpurl"] + filename)
    return embed

class RequestView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.message = None
    #TODO: dm maker about status of thing :)
    @discord.ui.button(label="Approve", style=discord.ButtonStyle.success, row=0, custom_id="approve_btn")
    async def approve_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        a = db_lib.read_data(f"SELECT id, maker_id, accepted FROM gacha WHERE (request_message_id) = (?)", (interaction.message.id,))[0]
        #print("I believe this is id ", a[0])

        if not a[2]:
            update_card(a[0], "accepted", "1")
            await interaction.response.send_message(f"{interaction.user.mention} approved ID {a[0]} by ID {a[1]}!", ephemeral=False, silent=True)
        else:
            await interaction.response.send_message(f"This card was already accepted", ephemeral=True)


    @discord.ui.button(label="Deny", style=discord.ButtonStyle.secondary, row=0, custom_id="deny_btn")
    async def deny_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        a = db_lib.read_data(f"SELECT id, maker_id, accepted FROM gacha WHERE (request_message_id) = (?)", (interaction.message.id,))[0]
        delete_card(a[1])
        await interaction.response.send_message(f"Card DENIED and DELETED!", ephemeral=False)

    @discord.ui.button(label="BAN FROM DEWEY", style=discord.ButtonStyle.danger, row=1, custom_id="ban_btn")
    async def ban_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.send_message(f"not implemented", ephemeral=True)

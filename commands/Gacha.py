import sqlite3
import discord
from discord.ext import commands, tasks
import Bot
import other.Permissions as Permissions
from typing import Literal
import db_lib

import gachalib

@Bot.tree.command(name="gacha-viewcard", description="View a gacha card!")
async def self(ctx : discord.Interaction, id: int): # type: ignore
    if not Permissions.banned(ctx):
        a = gachalib.get_card_by_id(id)
        if a:
            if a["accepted"] or Permissions.is_override(ctx) or ctx.user.id == a['maker_id']: # type: ignore
                await ctx.response.send_message(
                    embed=gachalib.gacha_embed(a['name'],a['description'],a['rarity'],a['filename'],"gacha card", f"ID {id}{' !DRAFT!' if not a['accepted'] else ''}") # type: ignore
                )
                return

        await ctx.response.send_message("Card doesn't exist!")
        

@Bot.tree.command(name="gacha-newcard", description="Submit a new gatcha card!")
async def self(ctx : discord.Interaction, name: str, description: str, rarity: Literal["Common", "Uncommon", "Rare", "Epic", "Legendary"], image: discord.Attachment): # type: ignore
    if not Permissions.banned(ctx):
        if Bot.DeweyConfig["review"][0] == "dm":
            approval_channel = await Bot.client.fetch_user(Bot.DeweyConfig["review"][1])
        elif Bot.DeweyConfig["review"][0] == "channel":
            approval_channel = await Bot.client.fetch_channel(Bot.DeweyConfig["review"][1])
        else: raise Exception("Dewey config option \"review\" is not set to 'channel' or 'dm'")

        
        a = db_lib.read_data(f"SELECT id FROM gacha;", ()) # type: ignore
        if len(a) == 0:
            next_id = 1
        else:
            next_id = a[len(a)-1][0] + 1
        
        if image.content_type.split("/")[0] != "image": # type: ignore
            await ctx.response.send_message(
                f"Your \"IMAGE\" was not an image. I think. Try again with a REAL image.", ephemeral=True,
            )
            return
        
        extension = image.filename.split(".")
        extension = extension[len(extension)-1]

        filename = f'CARD-{next_id}.{extension}'
        with open(f"images/{filename}", "wb") as f:
            await image.save(f)

        embed = gachalib.gacha_embed(name, description,rarity,filename,"gacha request!!", f"New request for a gacha card from <@{ctx.user.id}> (id = {next_id})")
        message_view = gachalib.RequestView()
        message_view.message = await approval_channel.send(embed=embed,view=message_view) # type: ignore

        try:
            gachalib.make_new_card(ctx.user.id,message_view.message.id,next_id,name,description,rarity,filename) # type: ignore
        except sqlite3.OperationalError as e:
            await message_view.message.reply("FALSE ALARM I ERROR " + str(e)) # type: ignore
            raise e
        
        
        await ctx.response.send_message(
            f"Dewey submitted your gacha card for approval!!! (ID of {next_id})", ephemeral=True,
        )

            
        


#admin commands

@Bot.tree.command(name="gacha-deletecard", description="!MOD ONLY! Delete a card")
async def self(ctx : discord.Interaction, id:int): # type: ignore
    if not Permissions.banned(ctx):
        if Permissions.is_override(ctx):
            gachalib.delete_card(id)
            await ctx.response.send_message("Deleted card.", ephemeral=True)


@Bot.tree.command(name="gacha-approvecard", description="!MOD ONLY! Force an action on a card (use when buttons don't work)")
async def self(ctx : discord.Interaction, id:int, action: Literal["Approve","Deny"]): # type: ignore
    if not Permissions.banned(ctx):
        if Permissions.is_override(ctx):
            card = gachalib.get_card_by_id(id)
            if card:
                if not card["accepted"]:
                    if action == "Approve":
                        gachalib.update_card(id, "accepted", "1")
                        await ctx.response.send_message("Okay!", ephemeral=True)
                    elif action == "Deny":
                        gachalib.delete_card(id)
                        await ctx.response.send_message("Deleted card", ephemeral=True)
                else:
                    await ctx.response.send_message("Card was already accepted, use gacha-deletecard", ephemeral=True)
            else:
                await ctx.response.send_message("Does not exist", ephemeral=True)
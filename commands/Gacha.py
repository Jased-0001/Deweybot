import sqlite3
import discord
from discord.ext import commands, tasks
import Bot
import other.Permissions as Permissions
from typing import Literal
import db_lib

from gachalib import *

# General card commands 
#######################################

@Bot.tree.command(name="gacha-viewcard", description="View a gacha card!")
async def self(ctx : discord.Interaction, id: int): # type: ignore
    if not Permissions.banned(ctx):
        success,card = gachalib.cards.get_card_by_id(id)
        if success:
            if card.accepted or Permissions.is_override(ctx) or ctx.user.id == a['maker_id']: # type: ignore
                await ctx.response.send_message(
                    embed=gachalib.gacha_embed(card=card, title="gacha card", description=f"ID {id}{' !DRAFT!' if not card.accepted else ''}") # type: ignore
                )
        else:
            await ctx.response.send_message("Card doesn't exist!")


@Bot.tree.command(name="gacha-browsecards", description="Look through cards")
async def self(ctx : discord.Interaction, page:int = 1): # type: ignore
    if not Permissions.banned(ctx):
        embed = discord.Embed(title="Card bowser!", description="page #")
        if page == 1:
            success, cards = gachalib.cards.get_card_by_id_range(1,5)
        elif page > 1:
            startpage = (5*(page-1))+1 # FUCKED
            success, cards = gachalib.cards.get_card_by_id_range(startpage,startpage+4)
        else:
            await ctx.response.send_message("Do you know your numbers?", ephemeral=True)

        if success:
            for i in cards:
                embed.add_field(name="Name (ID)", value=f'{i.name} ({i.card_id})', inline=True)
                embed.add_field(name="Rarity", value=i.rarity, inline=True)
                embed.add_field(name="By", value=f'<@{i.maker_id}>', inline=True)
            await ctx.response.send_message(embed=embed)
        else:
            await ctx.response.send_message("(There are no cards on this page!)", ephemeral=True)


@Bot.tree.command(name="gacha-submitcard", description="Submit a new gatcha card!")
async def self(ctx : discord.Interaction, name: str, description: str, rarity: Literal["Common", "Uncommon", "Rare", "Epic", "Legendary"], image: discord.Attachment): # type: ignore
    if not Permissions.banned(ctx):
        if Bot.DeweyConfig["review"][0] == "dm":
            approval_channel = await Bot.client.fetch_user(Bot.DeweyConfig["review"][1])
        elif Bot.DeweyConfig["review"][0] == "channel":
            approval_channel = await Bot.client.fetch_channel(Bot.DeweyConfig["review"][1])
        else: raise Exception("Dewey config option \"review\" is not set to 'channel' or 'dm'")

        
        a = db_lib.read_data(f"SELECT id FROM gacha;", ())
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

        embed = gachalib.gacha_embed(
            card=gachalib.types.Card(name=name, description=description,rarity=rarity,filename=filename),
            title="gacha request!!", description=f"New request for a gacha card from <@{ctx.user.id}> (id = {next_id})"
            )
        message_view = gachalib.RequestView()
        message_view.message = await approval_channel.send(embed=embed,view=message_view) # type: ignore

        try:
            gachalib.cards.register_new_card(ctx.user.id,message_view.message.id,next_id,name,description,rarity,filename) # type: ignore
        except sqlite3.OperationalError as e:
            await message_view.message.reply("FALSE ALARM I ERROR " + str(e)) # type: ignore
            raise e
        
        
        await ctx.response.send_message(
            f"Dewey submitted your gacha card for approval!!! (ID of {next_id})", ephemeral=True,
        )






# Self card management
#######################################


@Bot.tree.command(name="gacha-my-inventory", description="View your inventory!")
async def self(ctx : discord.Interaction, user: discord.Member = None, id: int = 0): # type: ignore
    if not Permissions.banned(ctx):
        uid = user.id if user else ctx.user.id
        await ctx.response.send_message(gachalib.cards_user.get_users_cards(uid))






# Admin commands
#######################################

@Bot.tree.command(name="z-gacha-admin-deletecard", description="!MOD ONLY! (Ask us!) Delete a card")
async def self(ctx : discord.Interaction, id:int): # type: ignore
    if not Permissions.banned(ctx):
        if Permissions.is_override(ctx):
            gachalib.cards.delete_card(id)
            await ctx.response.send_message("Deleted card.", ephemeral=True)


@Bot.tree.command(name="z-gacha-admin-approvecard", description="!MOD ONLY! Force an action on a card (use when buttons don't work)")
async def self(ctx : discord.Interaction, id:int, action: Literal["Approve","Deny"]): # type: ignore
    if not Permissions.banned(ctx):
        if Permissions.is_override(ctx):
            success,card = gachalib.cards.get_card_by_id(id)
            if success:
                if not card.accepted:
                    if action == "Approve":
                        gachalib.cards.update_card(id, "accepted", "1")
                        await ctx.response.send_message(f"Approved card ID {id}!", ephemeral=False)
                    elif action == "Deny":
                        gachalib.cards.delete_card(id)
                        await ctx.response.send_message(f"Deleted card ID {id}", ephemeral=False)
                else:
                    await ctx.response.send_message("Card was already accepted, use gacha-deletecard", ephemeral=True)
            else:
                await ctx.response.send_message("Does not exist", ephemeral=True)


@Bot.tree.command(name="z-gatcha-admin-givecard", description="!MOD ONLY! Just give someone a card")
async def self(ctx : discord.Interaction, id:int, user:discord.Member): # type: ignore
    if not Permissions.banned(ctx):
        if Permissions.is_override(ctx):
            cardid = gachalib.cards_user.give_user_card(user_id=user.id, card_id=id)
            await ctx.response.send_message(f"Just condensed card {cardid} out of thin air, yo (i control the elements)")
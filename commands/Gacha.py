import sqlite3
import discord
from discord.ext import commands, tasks
import Bot
import other.Permissions as Permissions
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
        if page <= 0: page = 1

        view = gachalib.BrowsePageView()
        view.page = page

        embed = gachalib.card_browser_embed(view.cards, page)

        if type(embed) == discord.Embed:
            await ctx.response.send_message(content="", embed=embed, view=view)
        else:
            await ctx.response.send_message(content=embed, embed=None, view=view) # pyright: ignore[reportArgumentType]


@Bot.tree.command(name="gacha-submitcard", description="Submit a new gatcha card!")
async def self(ctx : discord.Interaction, name: str, description: str, image: discord.Attachment): # type: ignore
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
        with open(f"gachalib/images/{filename}", "wb") as f:
            await image.save(f)

        embed = gachalib.gacha_embed(
            card=gachalib.types.Card(name=name, description=description,rarity="None",filename=filename),
            title="gacha request!!", description=f"New request for a gacha card from <@{ctx.user.id}> (id = {next_id})"
            )
        message_view = gachalib.RequestView()
        message_view.message = await approval_channel.send(embed=embed,view=message_view) # type: ignore

        try:
            gachalib.cards.register_new_card(ctx.user.id,message_view.message.id,next_id,name,description,"None",filename) # type: ignore
        except sqlite3.OperationalError as e:
            await message_view.message.reply("FALSE ALARM I ERROR " + str(e)) # type: ignore
            raise e
        
        
        await ctx.response.send_message(
            f"Dewey submitted your gacha card for approval!!! (ID of {next_id})", ephemeral=True,
        )


@Bot.tree.command(name="gacha-editcard", description="Re-submit an edited gacha card (or admin)!")
async def self(ctx : discord.Interaction, id: int, name: str = "", description: str = ""): # type: ignore
    if not Permissions.banned(ctx):
        if Bot.DeweyConfig["review"][0] == "dm":
            approval_channel = await Bot.client.fetch_user(Bot.DeweyConfig["review"][1])
        elif Bot.DeweyConfig["review"][0] == "channel":
            approval_channel = await Bot.client.fetch_channel(Bot.DeweyConfig["review"][1])
        else: raise Exception("Dewey config option \"review\" is not set to 'channel' or 'dm'")

        success, card = gachalib.cards.get_card_by_id(id)

        if success and card.maker_id == ctx.user.id:
            changed_anything = False
            if name != "" and name != card.name:
                gachalib.cards.update_card(id,"name",name)
                changed_anything = True
            if description != "" and description != card.description:
                gachalib.cards.update_card(id,"description",description)
                changed_anything = True
            
            await ctx.response.send_message("Updated")
            if changed_anything:
                gachalib.cards.update_card(id,"accepted",False)
                _, card = gachalib.cards.get_card_by_id(id)

                embed = gachalib.gacha_embed(
                card=card,
                title="gacha EDIT request!!", description=f"New EDIT request for a gacha card from <@{ctx.user.id}> (id = {id})"
                )
                message_view = gachalib.RequestView()
                message_view.message = await approval_channel.send(embed=embed,view=message_view) # type: ignore
                gachalib.cards.update_card(id,"request_message_id",message_view.message.id) # pyright: ignore[reportAttributeAccessIssue]
        else:
            await ctx.response.send_message("Card does not exist or you don't own it!")


# Self card management
#######################################


@Bot.tree.command(name="gacha-inventory", description="View your inventory!")
async def self(ctx : discord.Interaction, user: discord.Member = None, page: int = 0): # type: ignore
    if not Permissions.banned(ctx):
        if page <= 0: page = 1

        view = gachalib.InventoryPageView(user.id if user else ctx.user.id)
        view.page = page
            
        await ctx.response.send_message(embed=gachalib.card_inventory_embed(view.uid,view.cards,view.page), view=view) # pyright: ignore[reportArgumentType]


@Bot.tree.command(name="gacha-roll", description="Roll for a card!")
async def self(ctx : discord.Interaction): # type: ignore
    if not Permissions.banned(ctx):
        success, card = gachalib.cards.random_card_by_rarity(gachalib.random_rarity())

        gachalib.cards_user.give_user_card(ctx.user.id, card.card_id)

        await ctx.response.send_message(
            embed=gachalib.gacha_embed(card=card, title="Gacha roll!", description=f"You rolled a{"n" if card.rarity == "Epic" else ""} {card.rarity} {card.name}! ({card.card_id})",
                                       show_rarity=False, show_name=False)
            )


# Admin commands
#######################################

@Bot.tree.command(name="z-gacha-admin-deletecard", description="!MOD ONLY! (Ask us!) Delete a card")
async def self(ctx : discord.Interaction, id:int): # type: ignore
    if not Permissions.banned(ctx):
        if Permissions.is_override(ctx):
            gachalib.cards.delete_card(id)
            await ctx.response.send_message("Deleted card.", ephemeral=True)


@Bot.tree.command(name="z-gacha-admin-approvecard", description="!MOD ONLY! Force an action on a card (use when buttons don't work)")
async def self(ctx : discord.Interaction, id:int, action: gachalib.Literal["Approve","Deny"]): # type: ignore
    if not Permissions.banned(ctx):
        if Permissions.is_override(ctx):
            success,card = gachalib.cards.get_card_by_id(id)
            if success:
                if not card.accepted:
                    if action == "Approve":
                        if card.rarity == "None":
                            await ctx.response.send_message("Please set a rarity first! /z-gacha-admin-setrarity")
                        else:
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


@Bot.tree.command(name="z-gatcha-admin-setrarity", description="!MOD ONLY! Set the rarity of a card")
async def self(ctx : discord.Interaction, id:int, rarity:gachalib.Rarities): # type: ignore
    if not Permissions.banned(ctx):
        if Permissions.is_override(ctx):
            success,card = gachalib.cards.get_card_by_id(id)
            if success:
                gachalib.cards.update_card(id, "rarity", rarity)
                await ctx.response.send_message(f"Card is now {rarity}", ephemeral=False)
            else:
                await ctx.response.send_message("Does not exist", ephemeral=True)
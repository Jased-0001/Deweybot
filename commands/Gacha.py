from socket import timeout
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

        view = gachalib.BrowserView(False)
        view.page = page

        embed = gachalib.card_browser_embed(view.cards, page) # pyright: ignore[reportArgumentType]

        if type(embed) == discord.Embed:
            await ctx.response.send_message(content="", embed=embed, view=view)
        else:
            await ctx.response.send_message(content=embed, embed=None, view=view) # pyright: ignore[reportArgumentType]


@Bot.tree.command(name="gacha-submitcard", description="Submit a new gacha card!")
async def self(ctx : discord.Interaction, name: str, description: str, image: discord.Attachment, additional_info:str=""): # type: ignore
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
        with open(f"{Bot.DeweyConfig["image-save-path"]}/{filename}", "wb") as f:
            await image.save(f)

        gachalib.cards.register_new_card(ctx.user.id,-1,next_id,name,description,"None",filename)

        embed = gachalib.gacha_embed(
            card=gachalib.types.Card(name=name, description=description,rarity="None",filename=filename),
            title="gacha request!!", description=f"New request for a gacha card from <@{ctx.user.id}> (id = {next_id})"
            )
        message_view = gachalib.RequestView()
        message_view.message = await approval_channel.send(f"```{additional_info}```" if additional_info else "", embed=embed,view=message_view) # type: ignore

        gachalib.cards.update_card(next_id,"request_message_id", message_view.message.id) # pyright: ignore[reportAttributeAccessIssue]
        
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

        if success and (card.maker_id == ctx.user.id or Permissions.is_override(ctx)):
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
        
        view = gachalib.BrowserView(True, user.id if user else ctx.user.id)
        view.page = page
        
        embed = gachalib.card_inventory_embed(view.uid,view.cards,view.page) # pyright: ignore[reportArgumentType]

        if type(embed) == discord.Embed:
            await ctx.response.send_message(content="", embed=embed, view=view)
        else:
            await ctx.response.send_message(content=embed, embed=None, view=view) # pyright: ignore[reportArgumentType]


@Bot.tree.command(name="gacha-roll", description="Roll for a card!")
async def self(ctx : discord.Interaction): # type: ignore
    if not Permissions.banned(ctx):
        timestamp = gachalib.gacha_timeout.get_timestamp()
        last_use = gachalib.gacha_timeout.get_user_timeout(ctx.user.id).last_use
        time_out = 3600 # 1 hour (seconds)
        if (timestamp - last_use) > (time_out) or last_use == -1:
            embed = discord.Embed(title="Gacha roll!", description="You rolled 3 cards!")
            cards = [
                gachalib.cards.random_card_by_rarity(gachalib.random_rarity())[1],
                gachalib.cards.random_card_by_rarity(gachalib.random_rarity())[1],
                gachalib.cards.random_card_by_rarity(gachalib.random_rarity())[1]
            ]
            for i in cards:
                gachalib.cards_user.give_user_card(ctx.user.id, i.card_id)
                embed.add_field(name=f"Pulled '{i.name}' ({i.card_id}, {i.rarity})", value=f"{i.description}")

            await ctx.response.send_message(embed=embed, view=gachalib.PackView(cards))
            
            gachalib.gacha_timeout.set_user_timeout(ctx.user.id,gachalib.gacha_timeout.get_timestamp())
        else:
            await ctx.response.send_message(
                f"Aw! You're in Dewey Timeout! Try again <t:{last_use+time_out}:R>"
            )


# Trading
#######################################

@Bot.tree.command(name="gacha-trade", description="Trade with someone (Really fucking sketchy, ping if i break!)")
async def self(ctx : discord.Interaction, user:discord.Member): # type: ignore
    if not Permissions.banned(ctx) and ctx.user.id != user.id:
        trade = gachalib.types.Trade(user1=ctx.user, user2=user) # pyright: ignore[reportArgumentType]
        embed = gachalib.trade.trade_request_embed(trade)
        view = gachalib.trade.TradeRequestView(trade)
        await ctx.response.send_message(embed=embed, view=view) # pyright: ignore[reportArgumentType]

@Bot.tree.command(name="gacha-send-card", description="Give someone a card")
async def self(ctx : discord.Interaction, inv_id:int, user:discord.Member): # type: ignore
    test = gachalib.cards_user.change_card_owner(user.id, inv_id)
    await ctx.response.send_message(test)


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
    if Permissions.is_override(ctx):
        success,card = gachalib.cards.get_card_by_id(id)
        if success:
            if not card.accepted:
                if action == "Approve":
                    if card.rarity == "None":
                        await ctx.response.send_message("Please set a rarity first! /z-gacha-admin-setrarity", ephemeral=True)
                    else:
                        gachalib.cards.update_card(id, "accepted", "1")
                        await ctx.response.send_message(f"Approved card ID {id}!", ephemeral=True)

                        userchannel = await gachalib.get_card_maker_channel(card.maker_id)
                        await userchannel.send(f"Your card \"{card.name}\" ({card.card_id}) has been ACCEPTED!!! GOOD JOB!!!")
                elif action == "Deny":
                    gachalib.cards.delete_card(id)
                    await ctx.response.send_message(f"Deleted card ID {id}", ephemeral=True)
                        
                    userchannel = await gachalib.get_card_maker_channel(card.maker_id)
                    await userchannel.send(f"Your card \"{card.name}\" ({card.card_id}) has been denied. Sorry for your loss.")
            else:
                await ctx.response.send_message("Card was already accepted, use gacha-deletecard", ephemeral=True)
        else:
            await ctx.response.send_message("Does not exist", ephemeral=True)
    else:
        await ctx.response.send_message("Yo. You not part of the \"Gang\"", ephemeral=True)


@Bot.tree.command(name="z-gacha-admin-givecard", description="!MOD ONLY! Just give someone a card")
async def self(ctx : discord.Interaction, id:int, user:discord.Member): # type: ignore
    if Permissions.is_override(ctx):
        cardid = gachalib.cards_user.give_user_card(user_id=user.id, card_id=id)
        await ctx.response.send_message(f"Just condensed card {cardid} out of thin air, yo (i control the elements)")
    else:
        await ctx.response.send_message("Yo. You not part of the \"Gang\"", ephemeral=True)


@Bot.tree.command(name="z-gacha-admin-setrarity", description="!MOD ONLY! Set the rarity of a card")
async def self(ctx : discord.Interaction, id:int, rarity:gachalib.Rarities): # type: ignore
    if Permissions.is_override(ctx):
        success,card = gachalib.cards.get_card_by_id(id)
        if success:
            gachalib.cards.update_card(id, "rarity", rarity)
            await ctx.response.send_message(f"Card is now {rarity}", ephemeral=True)
        else:
            await ctx.response.send_message("Does not exist", ephemeral=True)
    else:
        await ctx.response.send_message("Yo. You not part of the \"Gang\"", ephemeral=True)

@Bot.tree.command(name="z-gacha-admin-unapproved-cards", description="!MOD ONLY! See all non-approved cards")
async def self(ctx : discord.Interaction, id:int, rarity:gachalib.Rarities): # type: ignore
    if Permissions.is_override(ctx):
        
        view = gachalib.BrowserView(True,manual=True)
        _,cards = gachalib.cards.get_unapproved_cards()
        view.cards = cards
        view.page = 1
        view.isInventory = True
        
        embed = gachalib.card_inventory_embed(-1,view.cards,view.page) # pyright: ignore[reportArgumentType]

        if type(embed) == discord.Embed:
            await ctx.response.send_message(content="", embed=embed, view=view)
        else:
            await ctx.response.send_message(content=embed, embed=None, view=view) # pyright: ignore[reportArgumentType]
    else:
        await ctx.response.send_message("Yo. You not part of the \"Gang\"", ephemeral=True)

import Bot
import other.Permissions as Permissions

import discord
from discord.abc import PrivateChannel
from discord.ext import commands, tasks

from typing import get_args
from PIL import Image, ImageSequence, ImageOps
import io

import gachalib
import gachalib.types
import gachalib.cards_inventory
import gachalib.cards
import gachalib.gacha_user
import gachalib.trade

import gachalib.views
import gachalib.views.card
import gachalib.views.inventory
import gachalib.views.pack
import gachalib.views.request
import gachalib.views.unaccepted
if Bot.DeweyConfig["deweycoins-enabled"]: import gachalib.views.cardsell

gacha_settings = gachalib.gacha_settings

# General card commands 
#######################################

gacha_group = discord.app_commands.Group(name="gacha", description="Dewey GACHA!!!")


@gacha_group.command(name="help", description="What is a gacha?")
async def gacha_help(ctx : discord.Interaction):
    if not Permissions.banned(ctx):
        embed = discord.Embed(title="Dewey Gacha!",description="""Gacha cards are a collection of different characters on cards that you get randomly from packs. Like pokemon but without playing with them.

### *How do I play?*
Use the `/gacha-roll` command! You get 3 cards, 2 of them will be common or uncommon, and one of them can be Rare, Epic, or even Legendary
                              
### *How do I view my cards?*
Use `/gacha-inventory` to view your inventory as a whole. Use the ID to see your full card, and the page buttons to scroll through all your cards.

### *How do I submit my own card?*
The `/gacha-submitcard` command allows you to submit a card for approval. You give your card a name, a description, and a picture. You can add a note for the reviewer on how rare the card is or provide context on a card.
""")
        
        await ctx.response.send_message(embed=embed,ephemeral=True)



@gacha_group.command(name="viewcard", description="View a gacha card!")
async def gacha_viewcard(ctx : discord.Interaction, id: int, show:bool=False):
    if not Permissions.banned(ctx):
        success,card = gachalib.cards.get_card_by_id(id)
        if success:
            if gachalib.cards_inventory.ownsCard(id=card.card_id,uid=ctx.user.id)[0] or Permissions.is_override(ctx) or ctx.user.id == card.maker_id:
                image=gachalib.get_small_thumbnail(card)
                await ctx.response.send_message(
                    view=gachalib.views.card.GachaView(card, image), file=image, ephemeral=not show,
                    allowed_mentions=discord.AllowedMentions(users=False)
                )
            else:
                await ctx.response.send_message("YOU DON'T OWN THIS CARD YOU PIRATE",ephemeral=True)
        else:
            await ctx.response.send_message("Card doesn't exist!",ephemeral=True)


#@gacha_group.command(name="browsecards", description="Look through cards")
#async def gacha_browsecards(ctx : discord.Interaction, page:int = 1):
#    if not Permissions.banned(ctx):
#        await ctx.response.send_message("command disabled!", ephemeral=True)
#        if page <= 0: page = 1
#
#        view = gachalib.BrowserView(False,page=page)
#
#        embed = gachalib.cardBrowserEmbed(uid=-1, cards=view.cards, page=page,inventory=False)
#
#        if type(embed) == discord.Embed:
#            await ctx.response.send_message(content="", embed=embed, view=view)
#        else:
#            await ctx.response.send_message(content=embed, embed=None, view=view)


@gacha_group.command(name="submitcard", description="Submit a new gacha card!")
async def gacha_submitcard(ctx : discord.Interaction, name: str, description: str, image: discord.Attachment, additional_info:str=""):
    if ctx.guild_id != Bot.DeweyConfig["main-guild"]: 
        await ctx.response.send_message("You can only run this in the main server!!!!!", ephemeral=True)
        return
    if not Permissions.banned(ctx):
        if Bot.DeweyConfig["review"][0] == "dm":
            approval_channel = await Bot.client.fetch_user(Bot.DeweyConfig["review"][1])
        elif Bot.DeweyConfig["review"][0] == "channel":
            approval_channel = await Bot.client.fetch_channel(Bot.DeweyConfig["review"][1])
        else: raise Exception("Dewey config option \"review\" is not set to 'channel' or 'dm'")

        
        a = gachalib.gacha_database.read_data(f"SELECT id FROM gacha;", ())
        if len(a) == 0:
            next_id = 1
        else:
            next_id = a[len(a)-1][0] + 1
        
        if not image.content_type or image.content_type.split("/")[0] != "image":
            await ctx.response.send_message(
                f"Your \"IMAGE\" was not an image. I think. Try again with a REAL image.", ephemeral=True,
            )
            return
        await ctx.response.defer()

        extension = image.filename.split(".")
        extension = extension[len(extension)-1]

        filename = f'CARD-{next_id}'
        with open(f"{Bot.DeweyConfig["image-save-path"]}/{filename}.{extension}", "wb") as f:
            await image.save(f)

        small = []
        inv_frames = []
        inv_small = []
        durations = []
        # Loop over each frame in the animated image
        data = await image.read()
        img = Image.open(io.BytesIO(data))

        for frame in ImageSequence.Iterator(img):
            small.append(ImageOps.contain(frame, (350, 500)))
            inv_frames.append(ImageOps.invert(frame.convert("RGB")))
            inv_small.append(ImageOps.contain(inv_frames[-1], (350, 500)))
            durations.append(frame.info.get("duration", 40))
        path = f"{Bot.DeweyConfig["image-save-path"]}"
        ext = "png"
        if len(small) > 1:
            ext = "gif"
            small[0].save(
                f"{path}/small/{filename}.{ext}",format="GIF",save_all=True,append_images=small[1:],loop=0,durations=durations,disposal=2
            )
            inv_frames[0].save(
                f"{path}/E{filename}.{ext}",format="GIF",save_all=True,append_images=inv_frames[1:],loop=0,durations=durations
            )
            inv_small[0].save(
                f"{path}/small/E{filename}.{ext}",format="GIF",save_all=True,append_images=inv_small[1:],loop=0,durations=durations
            )
        else:
            small[0].save(f"{path}/small/{filename}.{ext}", format="png")
            inv_frames[0].save(f"{path}/E{filename}.{ext}", format="png")
            inv_small[0].save(f"{path}/small/E{filename}.{ext}", format="png")
        filename += f".{ext}"

        gachalib.cards.register_new_card(ctx.user.id,-1,next_id,name,description,"None",filename)

        embed = gachalib.gacha_embed(
            card=gachalib.types.Card(name=name, description=description,rarity="None",filename=filename),
            title="gacha request!!", description=f"New request for a gacha card from <@{ctx.user.id}> (id = {next_id})"
            )
        message_view = gachalib.views.request.RequestView()
        assert not isinstance(approval_channel,(discord.ForumChannel,discord.CategoryChannel,PrivateChannel)), "approval channel assertion"
        message_view.message = await approval_channel.send(f"```{additional_info}```" if additional_info else "", embed=embed,view=message_view)

        gachalib.cards.update_card(next_id,"request_message_id", message_view.message.id)
        
        await ctx.followup.send(
            f"Dewey submitted your gacha card for approval!!! (ID of {next_id})", ephemeral=True,
        )


@gacha_group.command(name="editcard", description="Re-submit an edited gacha card (or admin)!")
async def gacha_editcard(ctx : discord.Interaction, id: int, name: str = "", description: str = ""):
    if ctx.guild_id != Bot.DeweyConfig["main-guild"]: 
        await ctx.response.send_message("You can only run this in the main server!!!!!", ephemeral=True)
        return
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
                message_view = gachalib.views.request.RequestView()
                assert not isinstance(approval_channel,(discord.ForumChannel,discord.CategoryChannel,PrivateChannel)), "approval channel assertion"
                message_view.message = await approval_channel.send(embed=embed,view=message_view)
                gachalib.cards.update_card(id,"request_message_id",message_view.message.id)
        else:
            await ctx.response.send_message("Card does not exist or you don't own it!")


@gacha_group.command(name="stats", description="card stats")
async def gacha_stats(ctx : discord.Interaction):
    if not Permissions.banned(ctx):
        embed = discord.Embed(title="Statistics", description="WIP, i was just curious abpuit these :) stats :)")
        embed.add_field(name="Total Cards", value=len(gachalib.cards.get_cards()[1]))
        embed.add_field(name="Total issued cards", value=len(gachalib.cards_inventory.get_all_issued()))
        embed.add_field(name="Total held cards (waiting)", value=len(gachalib.cards.get_unapproved_cards()[1]))
        embed.add_field(name="How many cards **YOU** have (excl. evil)", value=len(gachalib.cards_inventory.get_users_cards(user_id=ctx.user.id,include_evil=False)[1]))
        embed.add_field(name="How many cards **YOU** have (incl. evil)", value=len(gachalib.cards_inventory.get_users_cards(user_id=ctx.user.id,include_evil=True)[1]))

        await ctx.response.send_message(embed=embed)


@gacha_group.command(name="stats-spread", description="card spread")
async def gacha_stats_spread(ctx : discord.Interaction):
    if not Permissions.banned(ctx):
        embed = discord.Embed(title="Statistics", description="WIP, i was just curious abpuit these :) stats :)")
        spread = {}

        for i in get_args(gachalib.Rarities):
            spread[i] = 0

        cards = gachalib.cards_inventory.get_all_issued()
        cards_ = []

        for i in cards:
            success, card = gachalib.cards.get_card_by_id(card_id=i.card_id)
            if success: cards_.append(card)

        for card in cards_:
            spread[card.rarity] += 1

        for rarityname,count in spread.items():
            embed.add_field(name=rarityname, value=f"has {count}")

        await ctx.response.send_message(embed=embed)

@gacha_group.command(name="stats-accepted-spread", description="accepted card spread")
async def gacha_stats_accepted_spread(ctx : discord.Interaction):
    if not Permissions.banned(ctx):
        embed = discord.Embed(title="Statistics", description="WIP, i was just curious abpuit these :) stats :)")
        spread = {}

        for i in get_args(gachalib.Rarities):
            spread[i] = 0

        _, cards = gachalib.cards.get_cards()

        for card in cards:
            spread[card.rarity] += 1

        for rarityname,count in spread.items():
            embed.add_field(name=rarityname, value=f"has {count}")

        await ctx.response.send_message(embed=embed)

# Self card management
#######################################


@gacha_group.command(name="inventory", description="View your inventory!")
async def gacha_inventory(ctx : discord.Interaction, show: bool=True, view_button: bool=False):
    if not Permissions.banned(ctx):
        layout = gachalib.views.inventory.InventoryView(ctx.user, button=view_button, page=1)
        await ctx.response.send_message(view=layout, ephemeral=not show)


@gacha_group.command(name="inventory-completion", description="View your progress in collecting!")
async def gacha_inventory_completion(ctx : discord.Interaction):
    if not Permissions.banned(ctx):
        _,a = gachalib.cards_inventory.get_users_cards(ctx.user.id)
        _,b = gachalib.cards.get_approved_cards()
        c = []
        cards_had,evil_cards_had,cards_total = 0,0,len(b)

        for i in a:
            c.append(i.tocard()[1])

        c = gachalib.cards.group_like_cards(a=c)

        for i in c:
            if i[0].accepted:
                if i[0].card_id < 0:
                    evil_cards_had += 1
                else:
                    cards_had += 1

        await ctx.response.send_message(f"You have {cards_had}/{cards_total} ({round((cards_had/cards_total)*100,2)}%)\n\
Evil cards: {evil_cards_had}/{cards_total} ({round((evil_cards_had/cards_total)*100,2)}%)")


@gacha_group.command(name="roll", description="Roll for a card!")
async def gacha_roll(ctx : discord.Interaction):
    if ctx.guild_id != Bot.DeweyConfig["main-guild"]: 
        await ctx.response.send_message("You can only run this in the main server!!!!!", ephemeral=True)
        return
    if not Permissions.banned(ctx):
        timestamp = gachalib.gacha_user.get_timestamp()
        last_use = gachalib.gacha_user.get_user_timeout(ctx.user.id).last_use
        time_out = Bot.DeweyConfig["roll-timeout"] # 3600 seconds for 1 hr
        if (timestamp - last_use) > (time_out) or last_use == -1:
            cards = []
            for i in range(3):
                success, got_card = gachalib.cards.random_card_by_rarity(gachalib.random_rarity(restraint=False if i >= 2 else True))
                if success:
                    cards.append(got_card)

            embed = discord.Embed(title="Gacha roll!", description=f"You rolled {len(cards)} cards!", color=gachalib.rarityColors[gachalib.rarest_card(cards).rarity])

            for i in cards:
                gachalib.cards_inventory.give_user_card(ctx.user.id, i.card_id)
                user_cards = gachalib.cards_inventory.get_users_cards_by_card_id(ctx.user.id, i.card_id)
                numText = "[New]" if len(user_cards[1]) < 2 else f"[{len(user_cards[1])}x]"
                embed.add_field(name=f"{numText} {i.name}\n({i.rarity})", value=f"{i.description}\n-# ID: {i.card_id}")

            await ctx.response.send_message(embed=embed, view=gachalib.views.pack.PackView(cards))
            
            gachalib.gacha_user.set_user_timeout(ctx.user.id,gachalib.gacha_user.get_timestamp())
        else:
            await ctx.response.send_message(
                f"Aw! You're in Dewey Timeout! Try again <t:{last_use+time_out}:R>"
            )


if Bot.DeweyConfig["deweycoins-enabled"]:
    @gacha_group.command(name="sellcard", description="Sell a card!")
    async def gacha_sell_card(ctx : discord.Interaction, card_id : int, quantity : int = 1):
        success, card = gachalib.cards.get_card_by_id(card_id=card_id)
        user_owns_card, user_quantity = gachalib.cards_inventory.ownsCard(id=card_id, uid=ctx.user.id)

        if not success:
            await ctx.response.send_message("That card doesn't exist", ephemeral=False)
            return
        
        if quantity < 0: 
            await ctx.response.send_message("You can't sell negative cards", ephemeral=False)
            return
        
        if user_owns_card:
            if user_quantity >= quantity:
                _, user_cards = gachalib.cards_inventory.get_users_cards_by_card_id(user_id=ctx.user.id,card_id=card_id)
                cards_to_be_sold = user_cards[0:quantity]
                view = gachalib.views.cardsell.CardSellConfirmation(owner=ctx.user.id,inventory_ids=cards_to_be_sold,rarity=card.rarity)
                await ctx.response.send_message(f"Do you want to sell sell {'this' if quantity == 1 else f'these x{quantity}'} {card.rarity} '\
{card.name + ("" if quantity == 1 else "s")}' for D¢{gachalib.getCardCost(card=card) * quantity}", ephemeral=False,view=view)
            else:
                await ctx.response.send_message("You don't have enough of this card to sell!", ephemeral=False)
        else:
            await ctx.response.send_message("You don't own any of this card!", ephemeral=False)

    @gacha_group.command(name="buypack", description="!TODO! Buy a special PACK of Deweycards")
    async def gacha_buy_pack(ctx : discord.Interaction):
        await ctx.response.send_message("TO BE IMPLEMENTED", ephemeral=True)

    @gacha_group.command(name="valuecard", description="Check the value of a card in DeweyCoin")
    async def gacha_get_price(ctx : discord.Interaction):
        await ctx.response.send_message("TO BE IMPLEMENTED", ephemeral=True)

# Trading
#######################################

@gacha_group.command(name="trade", description="Trade with someone")
async def gacha_trade(ctx : discord.Interaction, user:discord.Member):
    if ctx.guild_id != Bot.DeweyConfig["main-guild"]: 
        await ctx.response.send_message("You can only run this in the main server!!!!!", ephemeral=True)
        return
    if not Permissions.banned(ctx):
        if ctx.user.id == user.id:
            await ctx.response.send_message("you can't send a trade request to yurself, dummy!!", ephemeral=True)
            return
        trade = gachalib.types.Trade(user1=ctx.user, user2=user)
        await ctx.response.send_message(view=gachalib.trade.TradeRequestView(trade))

#@gacha_group.command(name="send-card", description="Give someone a card")
#async def gacha_send_card(ctx : discord.Interaction, inv_id:int, user:discord.Member):
#    if ctx.guild_id != Bot.DeweyConfig["main-guild"]: 
#        await ctx.response.send_message("You can only run this in the main server!!!!!", ephemeral=True)
#        return
#    test = gachalib.cards_inventory.change_card_owner(user.id, inv_id)
#    await ctx.response.send_message(test)



# Settings
#######################################


gacha_settings_group = discord.app_commands.Group(name="settings", description="Dewey GACHA!!! SETTINGS!!!")

@gacha_settings_group.command(name="roll-reminders", description="Enable/disable gacha rolling reminders")
async def gacha_settings_roll_reminders(ctx : discord.Interaction, set:bool):
    if not Permissions.banned(ctx):
        gacha_settings.set_setting(uid=ctx.user.id, name="roll_reminder_dm", value=set)
        await ctx.response.send_message("Okay, you will be reminded when you can roll." if set else "Okay, you won't be reminded when you can roll")





# Admin commands
#######################################

@gacha_group.command(name="z-admin-deletecard", description="!MOD ONLY! (Ask us!) Delete a card")
async def z_gacha_admin_deletecard(ctx : discord.Interaction, id:int):
    if Permissions.is_override(ctx):
        gachalib.cards.delete_card(id)
        await ctx.response.send_message("Deleted card.", ephemeral=True)
    else:
        await ctx.response.send_message("Yo. You not part of the \"Gang\" (ask for your card to be deleted)", ephemeral=True)


@gacha_group.command(name="z-admin-approvecard", description="!MOD ONLY! Force an action on a card (use when buttons don't work)")
async def z_gacha_admin_approvecard(ctx : discord.Interaction, id:int, approved: bool):
    if Permissions.is_override(ctx):
        success,card = gachalib.cards.get_card_by_id(id)
        if success:
            _, status = await gachalib.cards.approve_card(approved, card)
            await ctx.response.send_message(status, ephemeral=True)
        else:
            await ctx.response.send_message("Does not exist", ephemeral=True)
    else:
        await ctx.response.send_message("Yo. You not part of the \"Gang\"", ephemeral=True)


@gacha_group.command(name="z-admin-givecard", description="!MOD ONLY! Just give someone a card")
async def z_gacha_admin_givecard(ctx : discord.Interaction, id:int, user:discord.Member):
    if Permissions.is_override(ctx):
        cardid = gachalib.cards_inventory.give_user_card(user_id=user.id, card_id=id)
        await ctx.response.send_message(f"Just condensed card {cardid} out of thin air, yo (i control the elements)")
    else:
        await ctx.response.send_message("Yo. You not part of the \"Gang\"", ephemeral=True)


@gacha_group.command(name="z-admin-setrarity", description="!MOD ONLY! Set the rarity of a card")
async def z_gacha_admin_setrarity(ctx : discord.Interaction, id:int, rarity:gachalib.Rarities):
    if Permissions.is_override(ctx):
        success,card = gachalib.cards.get_card_by_id(id)
        if success:
            gachalib.cards.update_card(id, "rarity", rarity)
            await ctx.response.send_message(f"Card is now {rarity}", ephemeral=True)
        else:
            await ctx.response.send_message("Does not exist", ephemeral=True)
    else:
        await ctx.response.send_message("Yo. You not part of the \"Gang\"", ephemeral=True)

@gacha_group.command(name="z-admin-unapproved-cards", description="!MOD ONLY! See all non-approved cards")
async def z_gacha_admin_unapproved_cards(ctx : discord.Interaction):
    if Permissions.is_override(ctx):
            layout = gachalib.views.unaccepted.UnacceptedView()
            await ctx.response.send_message(
                view=layout,
                ephemeral=True if ctx.guild else False,
                allowed_mentions=discord.AllowedMentions(users=False)
            )
    else:
        await ctx.response.send_message("Yo. You not part of the \"Gang\"", ephemeral=True)

gacha_group.add_command(gacha_settings_group)
Bot.tree.add_command(gacha_group)
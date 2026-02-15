import discord
from discord.abc import PrivateChannel
from discord.ext import commands, tasks
import Bot
import other.Permissions as Permissions

from gachalib import *

# General card commands 
#######################################

gacha_group = discord.app_commands.Group(name="gacha", description="Dewey GACHA!!!", allowed_installs=)


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
            if gachalib.cards_inventory.ownsCard(id=card.card_id,uid=ctx.user.id) or Permissions.is_override(ctx) or ctx.user.id == card.maker_id:
                image=gacha_crop_image(card)
                await ctx.response.send_message(
                    view=GachaView(card, image), file=image, ephemeral=not show,
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
        assert not isinstance(approval_channel,(discord.ForumChannel,discord.CategoryChannel,PrivateChannel)), "approval channel assertion"
        message_view.message = await approval_channel.send(f"```{additional_info}```" if additional_info else "", embed=embed,view=message_view)

        gachalib.cards.update_card(next_id,"request_message_id", message_view.message.id)
        
        await ctx.response.send_message(
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
                message_view = gachalib.RequestView()
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



# Self card management
#######################################


@gacha_group.command(name="inventory", description="View your inventory!")
async def gacha_inventory(ctx : discord.Interaction, show: bool=True):
    if not Permissions.banned(ctx):
        layout = InventoryView(ctx.user, 1)
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

            await ctx.response.send_message(embed=embed, view=gachalib.PackView(cards))
            
            gachalib.gacha_user.set_user_timeout(ctx.user.id,gachalib.gacha_user.get_timestamp())
        else:
            await ctx.response.send_message(
                f"Aw! You're in Dewey Timeout! Try again <t:{last_use+time_out}:R>"
            )


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
        _,cards = gachalib.cards.get_unapproved_cards()
        view = gachalib.BrowserView(inventory=False,cards=cards)
        
        embed = view.getPage()

        if type(embed) == discord.Embed:
            await ctx.response.send_message(content="", embed=embed, view=view)
        else:
            await ctx.response.send_message(content=embed, suppress_embeds=True, view=view)
    else:
        await ctx.response.send_message("Yo. You not part of the \"Gang\"", ephemeral=True)

Bot.tree.add_command(gacha_group)
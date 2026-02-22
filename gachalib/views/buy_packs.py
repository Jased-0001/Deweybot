from PIL.ImageFont import Layout
from PIL.ImageOps import contain
import discord, Bot

import gachalib.views.pack
import gachalib.cards
import gachalib.cards_inventory
import moneylib
import gachalib.gacha_user
import gachalib, gachalib.types

prices = {
    "premium": 50,
    "evil": 50
}

class BuyButton(discord.ui.Button):
    def __init__(self, pack_type: str, disabled: bool) -> None:
        self.pack_type = pack_type
        label = {
            "hourly": "Roll!",
            "premium": "D¢" + str(prices["premium"]),
            "evil": "D¢" + str(prices["evil"])
        }
        super().__init__(label=label[pack_type], style=discord.ButtonStyle.primary, disabled=disabled)

    async def roll_do(self, cards: list[gachalib.types.Card], interaction: discord.Interaction):
        embed = discord.Embed(title="Gacha roll!", description=f"You rolled {len(cards)} cards!", color=gachalib.rarityColors[gachalib.rarest_card(cards).rarity])
        for i in cards:
            gachalib.cards_inventory.give_user_card(interaction.user.id, i.card_id)
            user_cards = gachalib.cards_inventory.get_users_cards_by_card_id(interaction.user.id, i.card_id)
            numText = "[New]" if len(user_cards[1]) < 2 else f"[{len(user_cards[1])}x]"
            embed.add_field(name=f"{numText} {i.name}\n({i.rarity})", value=f"{i.description}\n-# ID: {i.card_id}")
        await interaction.response.edit_message(view=BuyPackView(interaction.user))
        await interaction.followup.send(embed=embed, view=gachalib.views.pack.PackView(cards))

    async def callback(self, interaction: discord.Interaction) -> None:
        cards = []
        assert Bot.client.user, "bot has no user"
        if self.pack_type == "hourly":
            timestamp = gachalib.gacha_user.get_timestamp()
            last_use = gachalib.gacha_user.get_user_timeout(interaction.user.id).last_use
            time_out = Bot.DeweyConfig["roll-timeout"]
            if (timestamp - last_use) > (time_out) or last_use == -1:
                for i in range(3):
                    success, got_card = gachalib.cards.random_card_by_rarity(gachalib.random_rarity(restraint=False if i >= 2 else True))
                    if success:
                        cards.append(got_card)
                gachalib.gacha_user.set_user_timeout(interaction.user.id,gachalib.gacha_user.get_timestamp())
                await self.roll_do(cards, interaction)
            else:
                await interaction.response.send_message(
                    f"Aw! You're in Dewey Timeout! Try again <t:{last_use+time_out}:R>"
                )

        elif self.pack_type == "premium":
            balance = moneylib.getUserInfo(user=interaction.user.id).balance
            if balance > prices["premium"]:
                for i in range(3):
                    success, got_card = gachalib.cards.random_card_by_rarity(gachalib.random_rarity(restraint=False))
                    if success:
                        cards.append(got_card)
                moneylib.giveCoins(user=interaction.user.id, coins=-prices["premium"])
                moneylib.giveCoins(user=Bot.client.user.id, coins=prices["premium"])
                await self.roll_do(cards, interaction)
        else:
            balance = moneylib.getUserInfo(user=interaction.user.id).balance
            if balance > prices["evil"]:
                for i in range(3):
                    success, got_card = gachalib.cards.random_card_by_rarity(gachalib.random_rarity(restraint=False if i >= 2 else True), evil_chance=12)
                    if success:
                        cards.append(got_card)
                moneylib.giveCoins(user=interaction.user.id, coins=-prices["evil"])
                moneylib.giveCoins(user=Bot.client.user.id, coins=prices["evil"])
                await self.roll_do(cards, interaction)
    
class BuyPackView(discord.ui.LayoutView):
    def __init__(self, user: discord.User | discord.Member) -> None:
        super().__init__(timeout=None)
        self.user = user
        items = [
            discord.ui.TextDisplay("# Buy a pack!"),
            discord.ui.Separator(),
        ]
        balance = moneylib.getUserInfo(user=user.id).balance

        # hourly
        timestamp = gachalib.gacha_user.get_timestamp()
        last_use = gachalib.gacha_user.get_user_timeout(user.id).last_use
        time_out = Bot.DeweyConfig["roll-timeout"]
        ready = (timestamp - last_use) > (time_out) or last_use == -1
        items.append(discord.ui.Section(
            "### Hourly roll",
            "Free hourly roll. " + ("" if ready else f"\n-# You can roll again <t:{last_use+time_out}:R>"),
            accessory=BuyButton("hourly", not ready)
        ))
        items.append(discord.ui.Separator())

        # premium
        has_funds = balance >= prices["premium"]
        items.append(discord.ui.Section(
            "### Premium roll",
            "All rolled cards have a chance of being rare, epic and legendary." + ("" if has_funds else f"\n-# You don't have enough coins! (D¢{balance})"),
            accessory=BuyButton("premium", not has_funds)
        ))
        items.append(discord.ui.Separator())

        # evil
        has_funds = balance >= prices["evil"]
        items.append(discord.ui.Section(
            "### Evil roll",
            "Increased chances of rolling an EVIL card." + ("" if has_funds else f"\n-# You don't have enough coins! (D¢{balance})"),
            accessory=BuyButton("evil", not has_funds)
        ))
        
        container = discord.ui.Container(*items)
        self.add_item(container)
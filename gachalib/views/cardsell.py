import Bot

if Bot.DeweyConfig["deweycoins-enabled"]:
    import discord, moneylib
    import gachalib, gachalib.cards_inventory, gachalib.types


    class CardSellConfirmation(discord.ui.View):
        def __init__(self,owner: int, inventory_ids: list[gachalib.types.CardsInventory], rarity: str):
            super().__init__(timeout=None)
            self.message = None
            self.owner: int = owner
            self.inventory_ids: list[gachalib.types.CardsInventory] = inventory_ids
            self.rarity: str = rarity
        
        def isowner(self,interaction):
            assert interaction.user, "interaction had no user"
            return True if self.owner == interaction.user.id else False

        @discord.ui.button(label="SELL! SELL! SELL!", style=discord.ButtonStyle.green)
        async def sell_callback(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
            assert Bot.client.user, "bot has no user"
            if not self.isowner(interaction=interaction):
                await interaction.response.send_message(content="You don't own this view!", ephemeral=True)
                return
            
            users_cards = gachalib.cards_inventory.get_users_cards(user_id=self.owner)[1]
            for i in self.inventory_ids:
                if not i in users_cards:
                    await interaction.response.send_message(content=f"You ain't own some the card you sellin'")
                    return

            owed = gachalib.rarity_costs[self.rarity] * len(self.inventory_ids)
            for i in self.inventory_ids:
                botaccount = moneylib.getUserInfo(Bot.client.user.id)
                if botaccount.balance < owed: 
                    await interaction.response.send_message(content=f"I don't actually have enough money to buy this from you!")
                    return

                gachalib.cards_inventory.change_card_owner(user_id=Bot.client.user.id, inv_id=i.inv_id)
                print("GAVE TO DEWEY")

            moneylib.giveCoins(user=self.owner, coins=owed)
            moneylib.giveCoins(user=Bot.client.user.id, coins=-owed)
            await interaction.response.send_message(content=f"Success! +D¢{owed} (now D¢{moneylib.getUserInfo(self.owner).balance})")
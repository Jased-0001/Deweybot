import db_lib,Bot
import discord
import math

import random

import moneylib.types


class DoorsView(discord.ui.View):
    def __init__(self, message:discord.Interaction, bet:int, cheat:bool=False):
        # 1: Lose all bet
        # 2: Lose half bet
        # 3: Double bet

        super().__init__(timeout=120)
        self.message: discord.Interaction = message
        self.doors: list[int] = [1,2,3]
        self.enabled = True
        self.bet = bet

        random.shuffle(self.doors)

        for i in range(3):
            button = discord.ui.Button(emoji="🚪", style=discord.ButtonStyle.blurple, custom_id=f"{self.doors[i]}")

            if cheat:
                if self.doors[i] == 1:
                    button.label = "LOSE ALL"
                elif self.doors[i] == 2:
                    button.label = "LOSE HALF"
                elif self.doors[i] == 3:
                    button.label = "DOLLA DOLLA, DOLLA DOLLA"
                else:
                    button.label = "It is known."

            button.callback = self.door_callback
            self.add_item(button)
    
    def mkembed(self) -> discord.Embed:
        return discord.Embed(title="DOORS [BATTLE MODE QUEUE 🎮]", description="Pick a door! Any door!\nOne door leads to riches, one door leads to sadness, and the other leads to 1/2 sadness")
    
    async def door_callback(self, interaction: discord.Interaction):
        assert Bot.client.user, "bot has no user"
        if interaction.user.id == self.message.user.id:
            if self.enabled:
                assert interaction.data and "custom_id" in interaction.data, "button callback called for non button (maybe?)"
                self.enabled = False
                
                modifier = int(interaction.data["custom_id"])
                if modifier == 1:
                    await interaction.response.send_message(f"Im sorry but you lost it all :(")


                    moneylib.updateValues(update=["lostgambling"],values=[
                        moneylib.getUserInfo(user=self.message.user.id).statistics.lostgambling + self.bet
                    ],id=self.message.user.id)

                    moneylib.updateValues(update=["gainedgambling"],values=[
                        moneylib.getUserInfo(user=Bot.client.user.id).statistics.gainedgambling + self.bet
                    ],id=Bot.client.user.id)
                elif modifier == 2:
                    await interaction.response.send_message(f"Im sorry but you lost half of it all...")
                    # give half of the money back (round up)
                    moneylib.giveCoins(user=self.message.user.id, coins=math.ceil(self.bet/2)) # return rounded up half bet
                    moneylib.giveCoins(user=Bot.client.user.id, coins=-(math.ceil(self.bet/2)))  # keep rounded down half bet


                    moneylib.updateValues(update=["lostgambling"],values=[
                        moneylib.getUserInfo(user=self.message.user.id).statistics.lostgambling + math.floor(self.bet/2)
                    ],id=self.message.user.id)

                    moneylib.updateValues(update=["gainedgambling"],values=[
                        moneylib.getUserInfo(user=Bot.client.user.id).statistics.gainedgambling + math.floor(self.bet/2)
                    ],id=Bot.client.user.id)
                elif modifier == 3:
                    await interaction.response.send_message(":slot_machine: :slot_machine: :slot_machine: :slot_machine: :slot_machine: YOU WIN!!!!!!!!!!!!!!!!!! DOUBLE!")
                    # take the money given to dewey away and give 2x back
                    moneylib.giveCoins(user=self.message.user.id, coins=self.bet*2) # return rounded up half bet
                    moneylib.giveCoins(user=Bot.client.user.id, coins=-self.bet*2)


                    moneylib.updateValues(update=["lostgambling"],values=[
                        moneylib.getUserInfo(user=Bot.client.user.id).statistics.lostgambling + self.bet
                    ],id=Bot.client.user.id)

                    moneylib.updateValues(update=["gainedgambling"],values=[
                        moneylib.getUserInfo(user=self.message.user.id).statistics.gainedgambling + self.bet
                    ],id=self.message.user.id)
                else:
                    await interaction.response.send_message("It is known.")
                    raise Exception(f"door callback modifier is '{modifier}'")

            await self.disable(reveal=True)
        else:
            await interaction.response.send_message("YOU CANT RUN THIS")


    async def on_timeout(self) -> None:
        await self.disable(reveal=True)

        if self.enabled:
            await self.message.edit_original_response(content="(Timed out! You lost it all.)")

            self.enabled = False

    async def disable(self, reveal:bool):
        for child in self.children:
            if type(child) == discord.ui.Button:
                child.disabled=True

                if reveal:
                    if child.custom_id == "1":
                        child.label = "LOSE ALL"
                    elif child.custom_id == "2":
                        child.label = "LOSE HALF"
                    elif child.custom_id == "3":
                        child.label = "DOLLA DOLLA, DOLLA DOLLA"
                    else:
                        child.label = "It is known."

        await self.message.edit_original_response(view=self)

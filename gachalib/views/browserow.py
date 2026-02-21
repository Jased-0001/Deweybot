import discord

class BrowseRow(discord.ui.ActionRow):
    def __init__(self, view, page: int, num_pages: int, *args) -> None:
        super().__init__()
        self.args = args
        self.page = page
        self.mView = view
        self.num_pages = num_pages

    async def edit(self, interaction, page):
        layout = self.mView(*self.args, page=page)
        await interaction.response.edit_message(
            view=layout,
            allowed_mentions=discord.AllowedMentions(users=False)
        )

    @discord.ui.button(emoji="⬅️", style=discord.ButtonStyle.primary, custom_id="left_btn")
    async def left_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        page = max(self.page-1, 1)
        await self.edit(interaction, page)

    @discord.ui.button(emoji="➡️", style=discord.ButtonStyle.primary, custom_id="right_btn")
    async def right_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        page = min(self.page+1, self.num_pages)
        await self.edit(interaction, page)
import discord
import Bot

import other.Permissions as Permissions
import other.Settings as Settings




gfad_group = discord.app_commands.Group(name="settings", description="Settings")

@gfad_group.command(name="z-debug-get", description="cause uptown funk gonna give it to ya")
async def get(ctx : discord.Interaction,name:str):
    if Permissions.is_override(ctx):
        a = Settings.Settings().get_setting(uid=ctx.user.id, name=name)
        await ctx.response.send_message(content=a, ephemeral=True)


@gfad_group.command(name="z-debug-set", description="cause uptown funk gonna give it to ya")
async def set(ctx : discord.Interaction,name:str,value:bool):
    if Permissions.is_override(ctx):
        Settings.Settings().set_setting(uid=ctx.user.id, name=name, value=value)
        await ctx.response.send_message(content="ok", ephemeral=True)


Bot.tree.add_command(gfad_group)
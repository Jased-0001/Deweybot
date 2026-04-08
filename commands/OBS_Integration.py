from io import BytesIO

import discord
import Bot

import other.Permissions as Permissions

import subprocess, requests

aa = None
running = False


obs_group = discord.app_commands.Group(name="obs", description="obs grop")

@obs_group.command(name="z-launch-server", description="cause uptown funk gonna give it to ya")
async def launch(ctx : discord.Interaction):
    if Permissions.is_override(ctx):
        global aa
        aa = subprocess.Popen([
            f"./server.py",
            "-H", Bot.DeweyConfig["obs-integration-host"],
            "-P", str(Bot.DeweyConfig["obs-integration-port"]),
            "-s", Bot.DeweyConfig["obs-integration-secret"]], cwd="./other/dewey_obs")
        print(" [OBS_Integration] launched Dewey OBS PID ", aa.pid)
        await ctx.response.send_message(f"i started it {aa.pid}")
        running = True


@obs_group.command(name="z-kill-server", description="cause uptown funk gonna give it to ya")
async def kill(ctx : discord.Interaction):
    if Permissions.is_override(ctx):
        if aa:
            aa.kill()
            running = False
            await ctx.response.send_message(content=f"i KILL ED it {aa.pid}")

@obs_group.command(name="z-send-image", description="cause uptown funk gonna give it to ya")
async def send(ctx : discord.Interaction, image : discord.Attachment):
    if Permissions.is_override(ctx):
        imaaage = BytesIO()
        await image.save(fp=imaaage)

        resp = requests.post(Bot.DeweyConfig["obs-integration-post-host"] + "/image",
                             headers={"Authorization": f"Bearer {Bot.DeweyConfig["obs-integration-secret"]}"},
                             files={"image": imaaage})
        if resp.status_code == 201:
            await ctx.response.send_message('Successfully sent image')
        elif resp.status_code == 401:
            await ctx.response.send_message('Error (incorrect secret)!!!!! ' + resp.content.decode())
        elif resp.status_code == 400:
            await ctx.response.send_message('Error (missing image)!!!!! ' + resp.content.decode())
        else:
            await ctx.response.send_message('Error (unknown)!!!!! ' + resp.content.decode())
        
        imaaage.close()


Bot.tree.add_command(obs_group)
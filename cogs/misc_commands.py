import datetime

import disnake as discord
from disnake.ext import commands

import config
from utils.bot_utils import load_cogs
from utils.chicopee_work_sched import work_embed
from utils.database_handler import check_for_channel, add_user_channel, remove_channel
from utils.print_screen import get_image

from utils.probability import one_in


class Misc_Slash_Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(description="Flip a coin")
    async def flip_a_coin(self, inter):
        choice = await one_in()
        coin = "Heads" if choice else "Tails"
        await inter.response.send_message(f"You got {coin}")

    # Creates the /reload Command
    # Reloads the bots cogs
    @commands.slash_command(description="Reloads the bots cogs")
    @commands.default_member_permissions(administrator=True)
    async def reload(self, inter: discord.ApplicationCommandInteraction):
        load_cogs(self.bot, True)
        await inter.response.send_message("Reloaded cogs.", ephemeral=True, delete_after=5)

    @commands.Cog.listener()
    async def on_button_click(self, inter: discord.MessageInteraction):
        # This is for the Again button on /prnt.sc
        if inter.component.custom_id == "Again":
            await self.prntsc(inter)
        if inter.component.label == "Refresh":
            name = inter.component.custom_id
            url = inter.message.embeds[0].url
            embed = work_embed(url, name)
            await inter.response.defer()
            await inter.message.edit(embed=embed)

    # Creates the /prntsc Command
    # Gets a random image from https://prnt.sc
    @commands.slash_command(description="Scrapes a random image from Prnt.sc")
    async def prntsc(self, inter: discord.ApplicationCommandInteraction):
        try:
            await inter.response.defer(with_message=True)
            # Builds the Embed
            embed = discord.Embed(title="Print-screen Image", color=discord.Color.blue(),
                                  timestamp=datetime.datetime.now())
            # Gets image from prnt.sc
            image = await get_image()
            # Set the image of the embed to the one we got from prnt.sc
            embed.set_image(file=discord.File(image))

            # Sends a message embed that has a button
            await inter.followup.send(embed=embed, components=[
                discord.ui.Button(label="Again", style=discord.ButtonStyle.blurple, custom_id="Again")
            ])
        except discord.errors.NotFound:
            await self.prntsc(inter)

    # Creates the /work_sched Command
    # Displays the work schedule(For Chicopee employees only)
    @commands.slash_command(description="Displays your work schedule (For Chicopee employees only)")
    async def work_sched(self, inter: discord.ApplicationCommandInteraction, url: str, name: str):
        embed = work_embed(url, name)
        await inter.response.send_message("Schedule sent", ephemeral=True, delete_after=3)
        await inter.user.send(embed=embed, components=[
            discord.ui.Button(label="Refresh", style=discord.ButtonStyle.gray, custom_id=f"{name}")
        ])

    # Creates the /delete Command
    # Deletes a message in a DM Channel
    # Only works in a DM Channel and on a message created by the bot
    @commands.message_command(name="Delete")
    async def delete_dm(self, inter: discord.MessageCommandInteraction, message: discord.Message):
        author = message.author
        bot = self.bot.user
        channel_type = inter.channel.type

        if author == bot and channel_type is discord.ChannelType.private:
            await inter.response.send_message("Message deleted", ephemeral=True, delete_after=1)
            await message.delete()
        else:
            await inter.response.send_message("Must be used in a DM Channel and on a message created by the bot.",
                                              ephemeral=True, delete_after=5)

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        is_private_vc = await check_for_channel(channel_id=channel.id)
        if is_private_vc:
            await remove_channel(channel.id)

    @commands.slash_command(description="Creates a private vc for you. Must be a server booster or council member.",
                            name="create-private-vc")
    async def create_private_vc(self, inter: discord.MessageCommandInteraction, name: str = None):
        allowed_roles = [900094202816372746, 658493803073634304, 602668901452611590, 595460458421420060,
                         1055268820048162867]
        category_id = config.VC_CATEGORY
        command_user = inter.user

        for role in allowed_roles:
            is_allowed = command_user.get_role(role) is not None
            if is_allowed:
                break

        if is_allowed is True:
            has_channel = await check_for_channel(command_user.id)
            if not has_channel:
                name = name if name is not None else f"{command_user.name}'s VC"
                new_vc = await command_user.guild.get_channel(category_id).create_voice_channel(name)
                await new_vc.set_permissions(target=command_user, view_channel=True,
                                             manage_channels=True,
                                             manage_permissions=True,
                                             )
                await add_user_channel(command_user.id, new_vc.id)
                await inter.response.send_message("Channel created.", ephemeral=True, delete_after=2)
            else:
                await inter.response.send_message("You already have a channel silly.", ephemeral=True, delete_after=2)
        else:
            await inter.response.send_message("You are not a booster of the server. ;(", ephemeral=True, delete_after=2)


def setup(bot):
    bot.add_cog(Misc_Slash_Commands(bot))

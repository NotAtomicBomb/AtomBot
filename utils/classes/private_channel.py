from __future__ import annotations

import disnake as discord

from utils.database_handler import DataBase_Handler


class Private_Channel:
    private_channels: list[Private_Channel] = []

    def __init__(self, member: discord.Member, channel: discord.VoiceChannel):
        Private_Channel.private_channels.append(self)
        self.private_channels = Private_Channel.private_channels
        self.member = member
        self.channel = channel
        print(self)

    def __str__(self):
        return f"\nChannel Name: \t{self.channel.name}\nOwner Name: \t{self.member.name}\n"

    # Creates a new record on the database and returns a Private_Channel object
    @classmethod
    async def new(cls, member: discord.Member, channel: discord.VoiceChannel) -> Private_Channel:
        await DataBase_Handler.add_user_channel(member.id, channel.id)
        return cls(member, channel)

    async def delete(self, reason: str = None):
        reason = "Channel deleted by bot." if reason is None else reason
        Private_Channel.private_channels.remove(self)
        self.private_channels = Private_Channel.private_channels
        try:
            await self.channel.delete(reason=reason)
        except:
            print("Channel already deleted")
        await self.member.send(reason, delete_after=120)
        await DataBase_Handler.remove_channel_record(self.channel.id)

    @staticmethod
    def find_channel(member: discord.Member = None, channel: discord.VoiceChannel = None) -> Private_Channel | None:
        if member is not None:
            for private_channel in Private_Channel.private_channels:
                if private_channel.member == member:
                    return private_channel
        elif channel is not None:
            for private_channel in Private_Channel.private_channels:
                if private_channel.channel == channel:
                    return private_channel
        return None

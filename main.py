import datetime
import enum
import json
import discord
from discord.abc import GuildChannel
from discord import Permissions, Embed, Interaction, app_commands, Guild, SelectOption, VoiceChannel
from discord.ext.commands import Bot, Context, has_permissions, bot_has_guild_permissions, check
from discord.ext import tasks, commands
from discord.ui import View, Button, Select, TextInput, ChannelSelect
from discord.ui.button import ButtonStyle

"""
██    ██  █████  ██████  ██  █████  ██████  ██      ███████ ███████ 
██    ██ ██   ██ ██   ██ ██ ██   ██ ██   ██ ██      ██      ██      
██    ██ ███████ ██████  ██ ███████ ██████  ██      █████   ███████ 
 ██  ██  ██   ██ ██   ██ ██ ██   ██ ██   ██ ██      ██           ██ 
  ████   ██   ██ ██   ██ ██ ██   ██ ██████  ███████ ███████ ███████
"""

bot = Bot(
    owner_id=365489975573348353,
    command_prefix="!",
    help_command=None,
    intents=discord.Intents.all()
)

data = {}


class CustomIDs(enum.Enum):
    SHOWCHANNELS = "showchannels"
    ADDCHANNELS = "addchannels"
    REMOVECHANNELS = "removechannels"
    BACK = "back"
    SELECTADDCHANNELS = "selectaddchannels"
    SELECTREMCHANNELS = "selectremchannels"

    def __str__(self):
        return self.value

    def __int__(self, value: str):
        return CustomIDs.__getitem__(value.upper())


"""
████████  █████  ███████ ██   ██ ███████ 
   ██    ██   ██ ██      ██  ██  ██      
   ██    ███████ ███████ █████   ███████ 
   ██    ██   ██      ██ ██  ██       ██ 
   ██    ██   ██ ███████ ██   ██ ███████
"""


@tasks.loop(minutes=1)
async def get_json_data():
    global data
    if data == {}:
        with open("data.json", "r") as f:
            data = json.load(f)

    with open("data.json", "w") as ff:
        json.dump(data, ff, indent=4)


"""
 ██████  ██████  ███    ███ ███    ███  █████  ███    ██ ██████  ███████ 
██      ██    ██ ████  ████ ████  ████ ██   ██ ████   ██ ██   ██ ██      
██      ██    ██ ██ ████ ██ ██ ████ ██ ███████ ██ ██  ██ ██   ██ ███████ 
██      ██    ██ ██  ██  ██ ██  ██  ██ ██   ██ ██  ██ ██ ██   ██      ██ 
 ██████  ██████  ██      ██ ██      ██ ██   ██ ██   ████ ██████  ███████
"""


def check_json(ctx: Context):
    if str(ctx.guild.id) not in data["servers"]:
        data["servers"][str(ctx.guild.id)] = {
            "channels": [],
            "config": []
        }


def check_perms(ctx: Context):
    return ctx.author.guild_permissions.manage_channels and ctx.guild.me.guild_permissions.manage_channels


def create_view(show: bool = False, add: bool = False, remove: bool = False, back: bool = True):
    v = View()
    v.add_item(
        Button(style=ButtonStyle.blurple, label="Show Channels", custom_id=str(CustomIDs.SHOWCHANNELS), emoji="📜",
               disabled=show))
    v.add_item(
        Button(style=ButtonStyle.green, label="Add Channel", custom_id=str(CustomIDs.ADDCHANNELS), emoji="✔️",
               disabled=add))
    v.add_item(
        Button(style=ButtonStyle.red, label="Remove Channel", custom_id=str(CustomIDs.REMOVECHANNELS), emoji="❌",
               disabled=remove))
    v.add_item(
        Button(style=ButtonStyle.grey, label="Back", custom_id=str(CustomIDs.BACK), emoji="🔙", disabled=back))
    return v


def create_embed(color, author):
    emb = Embed(colour=color, title="VoiceManager", timestamp=datetime.datetime.now())
    emb.add_field(name="Show Channels", value="Zeigt dir alle verwalteten Channels an", inline=False)
    emb.add_field(name="Add Channel", value="Füge neue Channel hinzu", inline=False)
    emb.add_field(name="Remove Channels", value="Entferne Channels", inline=False)
    emb.set_footer(text=f"Angefragt von {author.display_name} ID:{author.id}")
    return emb


@bot.hybrid_command(name="manage")
@check(check_perms)
async def manage(ctx: Context):
    emb = create_embed(ctx.author.roles[0].color, ctx.author)
    v = create_view()

    await ctx.send(embed=emb, view=v)


"""
███████ ██    ██ ███████ ███    ██ ████████ ███████ 
██      ██    ██ ██      ████   ██    ██    ██      
█████   ██    ██ █████   ██ ██  ██    ██    ███████ 
██       ██  ██  ██      ██  ██ ██    ██         ██ 
███████   ████   ███████ ██   ████    ██    ███████ 
"""


@bot.event
async def on_ready():
    get_json_data.start()
    print(f"Ready as {bot.user.name}({bot.user.id}) {round(bot.latency * 1000)}ms")
    try:
        await bot.tree.sync(guild=discord.Object(id=915698061530001448))
        print(f'Synced')
    except Exception as e:
        print(e)


@bot.event
async def on_interaction(i: Interaction):
    if i.is_expired():
        return
    if i.user.bot:
        return
    if i.user.id != int(i.message.embeds[0].footer.text.split("ID:")[1]):
        await i.message.reply(f"{i.user.mention} Du hast dieses Panel nicht angefordert!", delete_after=5)
    custom_id = i.data["custom_id"]
    ####################################################################################################################
    if CustomIDs(custom_id) == CustomIDs.SHOWCHANNELS:
        s = ""
        for chid in data["servers"][str(i.guild_id)]["channels"]:
            channel = i.guild.get_channel(int(chid))
            s += channel.mention
            s += "\n"
        if s == "":
            s = "Es sind keine Channel verwaltet!"
        emb = Embed(colour=i.message.embeds[0].colour,
                    title="VoiceManager",
                    description=s,
                    timestamp=datetime.datetime.now())
        emb.set_footer(text=f"Angefragt von {i.user.display_name} ID:{i.user.id}")
        await i.response.edit_message(embed=emb, view=create_view(show=True, back=False))
    ####################################################################################################################
    if CustomIDs(custom_id) == CustomIDs.ADDCHANNELS:
        emb = Embed(colour=i.message.embeds[0].colour,
                    title="VoiceManager",
                    description="Wähle die Channel aus welche du Verwalten möchtest!",
                    timestamp=datetime.datetime.now())
        emb.set_footer(text=f"Angefragt von {i.user.display_name} ID:{i.user.id}")

        channels: list = []
        for channel in i.guild.voice_channels:
            if channel.id not in data["servers"][str(i.guild_id)]["channels"]:
                op = SelectOption(
                    label=channel.name,
                    value=str(channel.id),
                    description=str(channel.id),
                    emoji="🔊"
                )
                channels.append(op)

        if len(channels) < 1:
            emb.description = "Du verwaltest schon alle Channel!"
            return await i.response.edit_message(embed=emb, view=create_view(add=True, back=False))
        view = create_view(add=True, back=False)
        view.add_item(
            Select(
                custom_id=str(CustomIDs.SELECTADDCHANNELS),
                placeholder="Choose wisely...",
                min_values=1,
                max_values=len(channels),
                options=channels,
                disabled=False
            )
        )
        await i.response.edit_message(embed=emb, view=view)
    ####################################################################################################################
    if CustomIDs(custom_id) == CustomIDs.REMOVECHANNELS:
        emb = Embed(colour=i.message.embeds[0].colour, title="VoiceManager",
                    description="Wähle die Channel aus welche du nicht mehr Verwalten möchtest!",
                    timestamp=datetime.datetime.now())
        emb.set_footer(text=f"Angefragt von {i.user.display_name} ID:{i.user.id}")
        if len(data["servers"][str(i.guild_id)]["channels"]) < 1:
            emb.description = "Du hast keine Channel Verwaltet!"
            return await i.response.edit_message(embed=emb, view=create_view(remove=True, back=False))

        channels: list = []
        for x in data["servers"][str(i.guild_id)]["channels"]:
            channel = i.guild.get_channel(x)
            op = SelectOption(
                label=channel.name,
                value=str(channel.id),
                description=str(channel.id),
                emoji="🔊"
            )
            channels.append(op)

        view = create_view(remove=True, back=False)
        view.add_item(
            Select(
                custom_id=str(CustomIDs.SELECTREMCHANNELS),
                placeholder="Choose wisely...",
                min_values=1,
                max_values=len(channels),
                options=channels,
                disabled=False
            )
        )
        await i.response.edit_message(embed=emb, view=view)
    ####################################################################################################################
    if CustomIDs(custom_id) == CustomIDs.BACK:
        await i.response.edit_message(embed=create_embed(i.user.roles[0].color, i.user), view=create_view())

    if CustomIDs(custom_id) == CustomIDs.SELECTADDCHANNELS:
        chs = [i.guild.get_channel(int(x)) for x in i.data["values"]]
        desc = "Du hast: \n"
        for ch in chs:
            desc += ch.mention + "\n"
            data["servers"][str(i.guild_id)]["channels"].append(ch.id)
        desc += "hinzugefügt"
        emb = Embed(color=i.message.embeds[0].colour,
                    title="VoiceManager",
                    description=desc,
                    timestamp=datetime.datetime.now())
        emb.set_footer(text=f"Angefragt von {i.user.display_name} ID:{i.user.id}")
        view = create_view(back=False)

        await i.response.edit_message(embed=emb, view=view)

    if CustomIDs(custom_id) == CustomIDs.SELECTREMCHANNELS:
        chs = [i.guild.get_channel(int(x)) for x in i.data["values"]]
        desc = "Du hast: \n"
        for ch in chs:
            desc += ch.mention + "\n"
            data["servers"][str(i.guild_id)]["channels"].remove(ch.id)
        desc += "entfernt"
        emb = Embed(color=i.message.embeds[0].colour,
                    title="VoiceManager",
                    description=desc,
                    timestamp=datetime.datetime.now())
        emb.set_footer(text=f"Angefragt von {i.user.display_name} ID:{i.user.id}")
        view = create_view(back=False)

        await i.response.edit_message(embed=emb, view=view)


@bot.event
async def on_guild_channel_delete(ch: GuildChannel):
    if type(ch) == VoiceChannel:
        if ch.id in data["servers"][str(ch.guild.id)]["channels"]:
            data["servers"][str(ch.guild.id)]["channels"].remove(ch.id)

bot.run("MTIzMDIwNzQ0NTUxOTk1ODE0OA.GjnMzd.lcZyXrnR8yRmWJCMIDDwg1e-MWLi6t1dYCB87E")

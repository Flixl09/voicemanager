import datetime
import enum
import json
from configparser import ConfigParser
import discord
from discord.abc import GuildChannel
from discord import Permissions, Embed, Interaction, app_commands, Guild, SelectOption, VoiceChannel, Member, \
    VoiceState, PermissionOverwrite, TextStyle, Role, InteractionType
from discord.ext.commands import Bot, Context, has_permissions, bot_has_guild_permissions, check
from discord.ext import tasks, commands
from discord.ui import View, Button, Select, TextInput, ChannelSelect, RoleSelect, Modal
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
config: ConfigParser = ConfigParser()
config.read("some.ini")
voiceperms = []
for x in Permissions.voice():
    if x[1]:
        voiceperms.append(x[0])


class CustomIDs(enum.Enum):
    ## Main Buttons
    SHOWCHANNELS = "showchannels"
    ADDCHANNELS = "addchannels"
    REMOVECHANNELS = "removechannels"
    CONFIGPERMISSIONS = "configpermissions"
    BUTTONFORSELECTROLE = "buttonforselectrole"
    BACK = "back"
    ## Selects
    SELECTADDCHANNELS = "selectaddchannels"
    SELECTREMCHANNELS = "selectremchannels"
    SELECTADDOWNERPERMISSIONS = "selectaddownerpermissions"
    SELECTREMOWNERPERMISSIONS = "selectremownerpermissions"
    SELECTROLEFORPERMISSIONS = "selectroleforpermissions"
    SELECTADDROLEPERMISSIONS = "selectaddrolepermissions"
    SELECTREMROLEPERMISSIONS = "selectremrolepermissions"
    ## Perms
    ROLEPERMISSIONS = "rolepermissions"
    OWNERPERMISSIONS = "ownerpermissions"
    ## User Temp Config
    CHANNELNAME = "channelname"
    MEMBERLIMIT = "memberlimit"
    MANAGERS = "managers"
    VISIBILITY = "visibility"
    USERBACK = "userback"

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


@tasks.loop(seconds=20)
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


def create_view(show: bool = False, add: bool = False, remove: bool = False, back: bool = True, config: bool = False):
    v = View()
    v.add_item(
        Button(style=ButtonStyle.blurple,
               label="Show Channels",
               custom_id=str(CustomIDs.SHOWCHANNELS),
               emoji="📜",
               disabled=show))
    v.add_item(
        Button(style=ButtonStyle.green,
               label="Add Channel",
               custom_id=str(CustomIDs.ADDCHANNELS),
               emoji="✔️",
               disabled=add))
    v.add_item(
        Button(style=ButtonStyle.red,
               label="Remove Channel",
               custom_id=str(CustomIDs.REMOVECHANNELS),
               emoji="❌",
               disabled=remove))
    v.add_item(
        Button(style=ButtonStyle.primary,
               label="Config Permissions",
               custom_id=str(CustomIDs.CONFIGPERMISSIONS),
               emoji="⚖️",
               disabled=config))
    v.add_item(
        Button(style=ButtonStyle.grey,
               label="Back",
               custom_id=str(CustomIDs.BACK),
               emoji="🔙",
               disabled=back))
    return v


def create_admin_panel(color, author, guild: Guild):
    emb = Embed(colour=color,
                title="VoiceManager",
                timestamp=datetime.datetime.now(),
                description="Manage deinen Server") \
        .add_field(name="Show Channels", value="Zeigt dir alle verwalteten Channels an", inline=False) \
        .add_field(name="Add Channel", value="Füge neue Channel hinzu", inline=False) \
        .add_field(name="Remove Channels", value="Entferne Channels", inline=False) \
        .add_field(name="Config Permissions",
                   value="Konfiguriere die Permissions für die Besitzer der Channels und andere", inline=False)
    if data["servers"][str(guild.id)]["temps"]:
        chs = ""
        for a in data["servers"][str(guild.id)]["temps"]:
            chs += guild.get_channel(int(a)).mention + "\n"
        emb.add_field(name="Active Temps", value=chs)
    emb.set_footer(text=f"Angefragt von {author.display_name} ID:{author.id}")
    return emb


def create_user_panel(author: Member):
    return Embed(color=discord.Color.green(),
                title="VoiceManager",
                timestamp=datetime.datetime.now(),
                description="Manage deinen Temp Channel") \
        .add_field(name="Channel Name", value="Change Channel Name", inline=False) \
        .add_field(name="Member Limit", value="Change Member Limit", inline=False) \
        .add_field(name="Managers", value="Add Managers to this Channel", inline=False) \
        .add_field(name="Visibillity", value="Change Channel visibillity for other users", inline=False) \
        .set_footer(text=f"Angefragt von {author.display_name} ID:{author.id}")


def create_user_view():
    return View() \
        .add_item(
        Button(
            style=ButtonStyle.blurple,
            label="Channel Name",
            custom_id=str(CustomIDs.CHANNELNAME))) \
        .add_item(
        Button(
            style=ButtonStyle.green,
            label="Member Limit",
            custom_id=str(CustomIDs.MEMBERLIMIT))) \
        .add_item(
        Button(
            style=ButtonStyle.success,
            label="Managers",
            custom_id=str(CustomIDs.MANAGERS))) \
        .add_item(
        Button(
            style=ButtonStyle.red,
            label="Visibillity",
            custom_id=str(CustomIDs.VISIBILITY))) \
        .add_item(
        Button(
            style=ButtonStyle.grey,
            label="Back",
            custom_id=str(CustomIDs.USERBACK)))


@bot.hybrid_command(name="manage", description="Manage the Tempchannels of your Server")
@commands.guild_only()
@check(check_perms)
async def manage(ctx: Context):
    emb = create_admin_panel(discord.Color.green(), ctx.author, ctx.guild)
    v = create_view()
    data["commands"] += 1
    await ctx.send(embed=emb, view=v)


@bot.hybrid_command(name="stats", description="Stats of the Bot")
async def stats(ctx: Context):
    data["commands"] += 1
    emb = Embed(title="VoiceManager Stats",
                color=discord.Color.green(),
                description="Hier sind die Stats vom Bot!",
                timestamp=datetime.datetime.now())
    emb.add_field(name="Commands used", value=str(data["commands"]))
    emb.add_field(name="Interactions used", value=str(data["interactions"]))
    emb.add_field(name="Servers", value=str(len(data["servers"])))
    emb.add_field(name="Temp Channels created", value=str(data["temps"]))
    emb.set_footer(text=f"Angefragt von {ctx.author.display_name} ID:{ctx.author.id}")
    await ctx.send(embed=emb)


@bot.hybrid_command(name="tempmanager", description="Manage your Tempchannel")
async def tempmanager(ctx: Context):
    data["commands"] += 1
    if ctx.author.voice:
        if str(ctx.author.voice.channel.id) in data["servers"][str(ctx.guild.id)]["temps"]:
            if ctx.author.id in data["servers"][str(ctx.guild.id)]["temps"][str(ctx.author.voice.channel.id)]:
                emb = create_user_panel(ctx.author)
                view = create_user_view()
                await ctx.send(embed=emb, view=view)
            else:
                await ctx.reply("Du bist kein Manager von diesem Channel", ephemeral=True, delete_after=5)
        else:
            await ctx.reply("Du bist in keinem Tempchannel!", ephemeral=True, delete_after=5)
    else:
        await ctx.reply("Du bist in keinem VoiceChannel", ephemeral=True, delete_after=5)


"""
███████ ██    ██ ███████ ███    ██ ████████ ███████ 
██      ██    ██ ██      ████   ██    ██    ██      
█████   ██    ██ █████   ██ ██  ██    ██    ███████ 
██       ██  ██  ██      ██  ██ ██    ██         ██ 
███████   ████   ███████ ██   ████    ██    ███████ 
"""


@bot.event
async def on_ready():
    get_json_data.start()  # starting the loop for gathering and saving data
    print(f"Ready as {bot.user.name}({bot.user.id}) {round(bot.latency * 1000)}ms")
    await bot.tree.sync()
    print("synced")


async def create_emb_owner(i: Interaction):
    userperms = Permissions(data["servers"][str(i.guild_id)]["config"]["owner"])
    userpermstext = "```"
    for x in userperms:
        if x[0] in voiceperms:
            userpermstext += x[0]
            if x[1]:
                userpermstext += "✔️"
            else:
                userpermstext += "❌"
            userpermstext += "\n"
    userpermstext += "```"
    emb = Embed(title="VoiceManager",
                color=i.message.embeds[0].colour,
                description="Wähle alle Permissions aus, welche der **Owner** vom Tempchannel haben darf!\n"
                            "Derzeit hat der Owner diese Permissions: \n" + userpermstext,
                timestamp=datetime.datetime.now())
    emb.set_footer(text=f"Angefragt von {i.user.display_name} ID:{i.user.id}")

    remperms = Permissions.voice() & userperms
    rempermsop = []
    for x in remperms:
        if x[1]:
            op = SelectOption(
                label=x[0],
                value=x[0],
                emoji="🔨"
            )
            rempermsop.append(op)

    experms = Permissions.voice() & ~userperms
    expermsop = []
    for x in experms:
        if x[1]:
            op = SelectOption(
                label=x[0],
                value=x[0],
                emoji="🔨"
            )
            expermsop.append(op)
    view = View()
    if len(expermsop) > 0:
        view.add_item(
            Select(
                custom_id=str(CustomIDs.SELECTADDOWNERPERMISSIONS),
                placeholder="Add Permissions to the Owner ...",
                min_values=1,
                max_values=len(expermsop),
                options=expermsop))
    if len(rempermsop) > 0:
        view.add_item(
            Select(
                custom_id=str(CustomIDs.SELECTREMOWNERPERMISSIONS),
                placeholder="Remove Permissions from the Owner ...",
                min_values=1,
                max_values=len(rempermsop),
                options=rempermsop))
    view.add_item(
        Button(style=ButtonStyle.grey,
               label="Back",
               custom_id=str(CustomIDs.BACK),
               emoji="🔙"))
    await i.response.edit_message(embed=emb, view=view)


async def create_emb_role(i: Interaction, role: Role):
    if str(role.id) not in data["servers"][str(i.guild_id)]["config"]:
        data["servers"][str(i.guild_id)]["config"][str(role.id)] = 40136506081792
    userperms = Permissions(data["servers"][str(i.guild_id)]["config"][str(role.id)])
    userpermstext = "```"
    for x in userperms:
        if x[0] in voiceperms:
            userpermstext += x[0]
            if x[1]:
                userpermstext += "✔️"
            else:
                userpermstext += "❌"
            userpermstext += "\n"
    userpermstext += "```"
    emb = Embed(title=f"VoiceManager {role.id}",
                color=i.message.embeds[0].colour,
                description=f"Wähle alle Permissions aus, welche die Rolle {role.mention} vom Tempchannel haben darf!\n"
                            f"Derzeit hat {role.mention} diese Permissions: \n" + userpermstext,
                timestamp=datetime.datetime.now())
    emb.set_footer(text=f"Angefragt von {i.user.display_name} ID:{i.user.id}")

    remperms = Permissions.voice() & userperms
    rempermsop = []
    for x in remperms:
        if x[1]:
            op = SelectOption(
                label=x[0],
                value=x[0],
                description=str(role.id),
                emoji="🔨"
            )
            rempermsop.append(op)

    experms = Permissions.voice() & ~userperms
    expermsop = []
    for x in experms:
        if x[1]:
            op = SelectOption(
                label=x[0],
                value=x[0],
                description=str(role.id),
                emoji="🔨"
            )
            expermsop.append(op)
    view = View()
    if len(expermsop) > 0:
        view.add_item(
            Select(
                custom_id=str(CustomIDs.SELECTADDROLEPERMISSIONS),
                placeholder="Add Permissions to the User ...",
                min_values=1,
                max_values=len(expermsop),
                options=expermsop))
    if len(rempermsop) > 0:
        view.add_item(
            Select(
                custom_id=str(CustomIDs.SELECTREMROLEPERMISSIONS),
                placeholder="Remove Permissions from the User ...",
                min_values=1,
                max_values=len(rempermsop),
                options=rempermsop))
    view.add_item(
        Button(style=ButtonStyle.grey,
               label="Back",
               custom_id=str(CustomIDs.BACK),
               emoji="🔙"))
    await i.response.edit_message(embed=emb, view=view)


@bot.event
async def on_interaction(i: Interaction):
    if i.is_expired():
        return
    if i.user.bot:
        return
    if i.type == InteractionType.application_command:
        return
    if i.user.id != int(i.message.embeds[0].footer.text.split("ID:")[1]):
        await i.message.reply(f"{i.user.mention} Du hast dieses Panel nicht angefordert!", delete_after=5)
        return
    data["interactions"] += 1
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
            if channel.id not in data["servers"][str(i.guild_id)]["channels"] and channel.id not in \
                    data["servers"][str(i.guild_id)]["temps"] and channel is not i.guild.afk_channel:
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
        await i.response.edit_message(embed=create_admin_panel(i.user.roles[0].color, i.user, i.guild),
                                      view=create_view())

    ####################################################################################################################
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
    ####################################################################################################################
    if CustomIDs(custom_id) == CustomIDs.SELECTREMCHANNELS:
        chs: list[VoiceChannel] = [i.guild.get_channel(int(x)) for x in i.data["values"]]
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
    ####################################################################################################################
    if CustomIDs(custom_id) == CustomIDs.CONFIGPERMISSIONS:
        emb = Embed(title="VoiceManager",
                    color=i.message.embeds[0].colour,
                    description="Wähle wessen Rechte du bearbeiten möchtest. (Tempchannel Owner, Tempchannel User)",
                    timestamp=datetime.datetime.now())
        emb.set_footer(text=f"Angefragt von {i.user.display_name} ID:{i.user.id}")
        view = View()
        view.add_item(
            Button(style=ButtonStyle.blurple,
                   label="Owner",
                   custom_id=str(CustomIDs.OWNERPERMISSIONS),
                   emoji="👑",
                   row=0))
        view.add_item(
            Button(style=ButtonStyle.green,
                   label="Role",
                   custom_id=str(CustomIDs.BUTTONFORSELECTROLE),
                   emoji="🧑",
                   row=0))
        view.add_item(
            Button(style=ButtonStyle.grey,
                   label="Back",
                   custom_id=str(CustomIDs.BACK),
                   emoji="🔙",
                   row=1))
        await i.response.edit_message(embed=emb, view=view)
    ####################################################################################################################
    if CustomIDs(custom_id) == CustomIDs.OWNERPERMISSIONS:
        await create_emb_owner(i)
    ####################################################################################################################
    if CustomIDs(custom_id) == CustomIDs.SELECTADDOWNERPERMISSIONS:
        owner = Permissions(data["servers"][str(i.guild_id)]["config"]["owner"])
        pp = {}
        for x in i.data["values"]:
            pp[x] = True
        owner.update(**pp)
        data["servers"][str(i.guild_id)]["config"]["owner"] = owner.value

        await create_emb_owner(i)

        await i.response.send_message(f"{i.user.mention} Es wurden erfolgreich die Permissions geupdated!",
                                      delete_after=5)
    ####################################################################################################################
    if CustomIDs(custom_id) == CustomIDs.SELECTREMOWNERPERMISSIONS:
        owner = Permissions(data["servers"][str(i.guild_id)]["config"]["owner"])
        pp = {}
        for x in i.data["values"]:
            pp[x] = False
        owner.update(**pp)
        data["servers"][str(i.guild_id)]["config"]["owner"] = owner.value

        await create_emb_owner(i)

        await i.response.send_message(f"{i.user.mention} Es wurden erfolgreich die Permissions geupdated!",
                                      delete_after=5)
    ####################################################################################################################

    if CustomIDs(custom_id) == CustomIDs.BUTTONFORSELECTROLE:
        m = Modal(title=f"Gib die Rolle ein welche du verwalten willst!",
                  custom_id=str(CustomIDs.SELECTROLEFORPERMISSIONS))
        m.add_item(
            TextInput(
                label="Gib die Rolle ein welche du verwalten willst!",
                placeholder="Gib die Rolle ein welche du verwalten willst!",
                style=TextStyle.short))
        await i.response.send_modal(m)

    ####################################################################################################################

    if CustomIDs(custom_id) == CustomIDs.SELECTROLEFORPERMISSIONS:
        ch: str = i.data["components"][0]["components"][0]["value"]
        if ch == "default" or ch == "everyone":
            role = i.guild.default_role
        elif ch.isdigit():
            role = i.guild.get_role(int(ch))
        else:
            role = discord.utils.get(i.guild.roles, name=ch)

        if role is None:
            await i.response.send_message(f"{i.user.mention} Du hast eine falsche Rolle angegeben!", delete_after=5)
            return

        await create_emb_role(i, role)

    ####################################################################################################################

    if CustomIDs(custom_id) == CustomIDs.SELECTADDROLEPERMISSIONS:
        role = i.message.embeds[0].title.split(" ")[1]
        owner = Permissions(data["servers"][str(i.guild_id)]["config"][role])
        pp = {}
        for x in i.data["values"]:
            pp[x] = True
        owner.update(**pp)
        data["servers"][str(i.guild_id)]["config"][role] = owner.value

        await create_emb_role(i, i.guild.get_role(int(role)))

        await i.response.send_message(f"{i.user.mention} Es wurden erfolgreich die Permissions geupdated!",
                                      delete_after=5)

    ####################################################################################################################

    if CustomIDs(custom_id) == CustomIDs.SELECTREMROLEPERMISSIONS:
        role = i.message.embeds[0].title.split(" ")[1]
        owner = Permissions(data["servers"][str(i.guild_id)]["config"][role])
        pp = {}
        for x in i.data["values"]:
            pp[x] = False
        owner.update(**pp)
        data["servers"][str(i.guild_id)]["config"][role] = owner.value

        await create_emb_role(i, i.guild.get_role(int(role)))

        await i.response.send_mesage(f"{i.user.mention} Es wurden erfolgreich die Permissions geupdated!",
                                     delete_after=5)

    ####################################################################################################################
    ####################################################################################################################
    ####################################################################################################################

    if CustomIDs(custom_id) == CustomIDs.CHANNELNAME:



@bot.event
async def on_guild_channel_delete(ch: GuildChannel):
    if type(ch) == VoiceChannel:
        if ch.id in data["servers"][str(ch.guild.id)]["channels"]:
            data["servers"][str(ch.guild.id)]["channels"].remove(ch.id)
        if str(ch.id) in data["servers"][str(ch.guild.id)]["temps"]:
            data["servers"][str(ch.guild.id)]["temps"].pop(str(ch.id))


@bot.event
async def on_guild_remove(guild: Guild):
    if str(guild.id) in data["servers"]:
        data["servers"].remove(str(guild.id))


@bot.event
async def on_guild_join(guild: Guild):
    data["servers"][str(guild.id)] = {
        "channels": [],
        "config": {
            "owner": Permissions.voice().value
        },
        "temps": []}


async def create_channel(memb: Member, cat: discord.CategoryChannel):
    guild = memb.guild
    ch = await guild.create_voice_channel(name=memb.display_name + "'s Channel",
                                          category=cat,
                                          user_limit=5,
                                          reason="VoiceManager Temp Channel")

    for x in data["servers"][str(memb.guild.id)]["config"]:
        perms = Permissions(data["servers"][str(memb.guild.id)]["config"][x])
        permso = PermissionOverwrite()
        for y in perms:
            if y[0] in voiceperms:
                permso.__setattr__(y[0], y[1])
        if x == "owner":
            await ch.set_permissions(memb, overwrite=permso)
        else:
            await ch.set_permissions(memb.guild.get_role(int(x)), overwrite=permso)
    x = {}
    data["servers"][str(guild.id)]["temps"][str(ch.id)] = [memb.id]
    data["temps"] += 1
    return ch


@bot.event
async def on_voice_state_update(memb: Member, bef: VoiceState, aft: VoiceState):
    guild = memb.guild
    if bef.channel:
        if str(bef.channel.id) in data["servers"][str(guild.id)]["temps"]:
            if len(bef.channel.members) == 0:
                await bef.channel.delete()
                data["servers"][str(guild.id)]["temps"].pop(str(bef.channel.id))

    if aft.channel:
        if aft.channel.id in data["servers"][str(guild.id)]["channels"]:
            ch = await create_channel(memb, aft.channel.category)
            await memb.move_to(ch)


####################################################################################################################


"""
███████ ██████  ██████   ██████  ██████      ██   ██  █████  ███    ██ ██████  ██      ██ ███    ██  ██████  
██      ██   ██ ██   ██ ██    ██ ██   ██     ██   ██ ██   ██ ████   ██ ██   ██ ██      ██ ████   ██ ██       
█████   ██████  ██████  ██    ██ ██████      ███████ ███████ ██ ██  ██ ██   ██ ██      ██ ██ ██  ██ ██   ███ 
██      ██   ██ ██   ██ ██    ██ ██   ██     ██   ██ ██   ██ ██  ██ ██ ██   ██ ██      ██ ██  ██ ██ ██    ██ 
███████ ██   ██ ██   ██  ██████  ██   ██     ██   ██ ██   ██ ██   ████ ██████  ███████ ██ ██   ████  ██████  
"""


####################################################################################################################

@manage.error
async def manage_error(ctx: Context, err):
    if isinstance(err, commands.NoPrivateMessage):
        await ctx.send("Keine DMS!!", delete_after=5)
    elif isinstance(err, commands.CheckFailure):
        await ctx.send("Du hast keine Berechtigung für diesen Command!", ephemeral=True, delete_after=5)
        await ctx.message.delete()


bot.run(config["token"]["token"])

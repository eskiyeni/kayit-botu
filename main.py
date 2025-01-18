import discord
from discord.ext import commands
from discord.ui import Button, View
import json
import time

start_time = time.time()

def json_load(file) -> dict:
    try:
        with open(file, "r", encoding="UTF-8") as f:
            return json.load(f)

    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Json yüklenirken hata oluştu: {e}")
        exit()

def return_uptime() -> str:
    uptime_seconds = int(time.time() - start_time)
    days = uptime_seconds // (24 * 3600)
    hours = (uptime_seconds % (24 * 3600)) // 3600
    minutes = (uptime_seconds % 3600) // 60

    return f"{days} gün, {hours} saat, {minutes} dakika"

config = json_load("config.json")
intents = discord.Intents.all()
bot = commands.Bot(command_prefix=config["prefix"], intents=intents, help_command=None)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"{bot.user.name} aktif!")

@bot.event
async def on_member_join(member : discord.Member):
    avatar = member.avatar.url if member.avatar.url else member.default_avatar.url
    guild_avatar = member.guild.icon.url

    await member.add_roles(
        discord.utils.get(member.guild.roles, id=config["unregistered_role"])
    )

    try:
        await member.send(
            embed=discord.Embed(
                title="HOŞGELDİN",
                description=f"Sunucumuza hoşgeldin! Artık sohbete katılabilirsin.\nKayıt olmak için ismini ve yaşını kayıt kanalında bize söylemen yeterli.",
                color=0xF6F478
            ).set_thumbnail(url=guild_avatar),

            view=View().add_item(
                Button(
                    label=f"{member.guild.name}",
                    style=discord.ButtonStyle.grey,
                    disabled=True
                )
            )
        )
    except:
        pass

    unregistered_channel = await bot.fetch_channel(config["unregistered_channel"])
    await unregistered_channel.send(
        f"{member.mention}, <@&{config['staff_role']}> rolündeki yetkililer seninle ilgilenecektir.",
        embed=discord.Embed(
            title="YENİ ÜYE",
            description=f"{member.mention} aramıza katıldı.\nHoşgeldin, kayıt olmak için lütfen ismini ve yaşını söyle.",
            color=0xF6F478
        ).set_footer(text=member.guild.name
        ).set_thumbnail(url=avatar)
    )

@bot.command()
async def info(ctx: commands.Context):
    avatar = bot.user.avatar.url if bot.user.avatar.url else bot.user.default_avatar.url
    await ctx.send(
        embed=discord.Embed(
            title="INFO",
            description=f"""
Prefix: {config['prefix']}
Uptime: {return_uptime()}
Kaynak kodları: {config["github_link"]}
"""         ,
            color=0xF6F478
        ).set_thumbnail(url=avatar
        ).set_footer(text=bot.user.name)
    )

@bot.command()
async def kayıt(ctx : commands.Context, user : discord.Member, *name : str):
    if ctx.guild:
        name = " ".join(name)
        if any(role.id == config["staff_role"] for role in ctx.author.roles):
            await user.edit(nick=name)
            await user.remove_roles(
                await discord.utils.get(ctx.guild, id=config["unregistered_role"])
            )
            await user.add_roles(
                await discord.utils.get(ctx.guild, id=config["member_role"])
            )

            avatar = user.avatar.url if user.avatar.url else user.default_avatar.url

            embed = discord.Embed(
                title="KULLANICI KAYDEDİLDİ",
                description=f"""
Kayıt eden: {ctx.author.mention},
kayıt olan: {user.mention}
"""             ,
                color=0x00FF00
            ).set_thumbnail(url=avatar
            ).set_footer(text="Aramıza hoşgeldin!")

            chat = await bot.fetch_channel(config["chat_channel"])
            await chat.send(
                embed=discord.Embed(
                    title="Aramıza Hoşgeldin!",
                    description=f"{user.mention} aramıza katıldı!\nHadi ne bekliyorsun sohbete katıl.",
                    color=0xf6f478
                ).set_thumbnail(url=avatar
                ).set_footer(text=ctx.guild.name)
            )
        else:
            embed = discord.Embed(
                title="HATA!",
                description=f"Bu komutu kullanmak için <@&{config['staff_role']}> rolüne sahip olmanız lazım!",
                color=0xFF0000
            ).set_footer(text=f"Komut {ctx.author.mention} tarafından kullanıldı!")
    else:
        embed = discord.Embed(
            title="HATA",
            description="Bu komut DM üzerinde kullanılamaz.",
            color=0xFF0000
        )

    await ctx.send(embed=embed)

@bot.command()
async def join_channel(ctx : commands.Context, channel : discord.VoiceChannel = None):
    channel = channel or (ctx.author.voice.channel if ctx.author.voice else None)
    if channel:
        if ctx.guild:
            if any(role.id == config["staff_role"] for role in ctx.author.roles):
                await channel.connect(timeout=99999999999999999)
                embed = discord.Embed(
                    title="KANALA KATILINDI",
                    description=f"{ctx.author.mention} kanala katıldı.",
                    color=0x00FF00
                ).set_footer(text=ctx.guild.name)
            else:
                embed = discord.Embed(
                    title="HATA!",
                    description=f"Bu komutu kullanmak için <@&{config['staff_role']}> rolüne sahip olmanız lazım!",
                    color=0xFF0000
                ).set_footer(text=f"Komut {ctx.author.mention} tarafından kullanıldı!")
        else:
            embed = discord.Embed(
                title="HATA",
                description="Bu komut DM üzerinde kullanılamaz.",
                color=0xFF0000
            )
    else:
        embed = discord.Embed(
            title="HATA",
            description="Bir ses kanalına katılmadınız veya bir ses kanalı belirtmediniz!",
            color=0xFF0000
        )

    await ctx.send(embed=embed)

@bot.tree.command(
    name="info",
    description="Bot hakkında bilgi verir."
)
async def info_slash(interaction : discord.Interaction):
    await interaction.response.defer()

    avatar = bot.user.avatar.url if bot.user.avatar.url else bot.user.default_avatar.url

    await interaction.followup.send(
        embed=discord.Embed(
            title="INFO",
            description=f"""
Prefix(ler): {config['prefix']}
Uptime: {return_uptime()}
Kaynak kodları: {config["github_link"]}
"""         ,
            color=0xF6F478
        ).set_thumbnail(url=avatar
        ).set_footer(text=bot.user.name)
    )

@bot.tree.command(
    name="kayıt",
    description="Kullanıcıyı kayıt eder."
)
async def kayıt_slash(interaction : discord.Interaction, user : discord.Member, name : str):
    await interaction.response.defer()

    if interaction.guild:
        if any(role.id == config["staff_role"] for role in interaction.user.roles):
            await user.edit(nick=name)
            await user.remove_roles(
                discord.utils.get(interaction.guild.roles, id=config["unregistered_role"])
            )
            await user.add_roles(
                discord.utils.get(interaction.guild.roles, id=config["member_role"])
            )

            avatar = user.avatar if user.avatar else user.default_avatar

            embed = discord.Embed(
                title="KULLANICI KAYDEDİLDİ",
                description=f"""
Kayıt eden: {interaction.user.mention},
kayıt olan: {user.mention}
"""         ,
                color=0x00FF00
            ).set_thumbnail(url=avatar
            ).set_footer(text="Aramıza hoşgeldin!")

            chat = await bot.fetch_channel(config["chat_channel"])
            await chat.send(
                embed=discord.Embed(
                    title="Aramıza Hoşgeldin!",
                    description=f"{user.mention} aramıza katıldı. Hadi ne bekliyorsun sohbete katıl!",
                    color=0xf6f478
                ).set_thumbnail(url=avatar
                ).set_footer(text=interaction.guild.name)
            )
        else:
            embed = discord.Embed(
                title="HATA!",
                description=f"Bu komutu kullanmak için <@&{config['staff_role']}> rolüne sahip olmanız lazım!",
                color=0xFF0000
            ).set_footer(text=f"Komut {user.mention} tarafından kullanıldı!")
    else:
        embed = discord.Embed(
            title="HATA",
            description="Bu komut DM üzerinde kullanılamaz.",
            color=0xFF0000
        )

    await interaction.followup.send(embed=embed)

@bot.tree.command(
    name="join_channel",
    description="Ses kanalına katılır."
)
async def join_channel_slash(interaction : discord.Interaction, channel : discord.VoiceChannel = None):
    await interaction.response.defer()
    channel = channel or (interaction.user.voice.channel if interaction.user.voice else None)

    if channel:
        if interaction.guild:
            if any(role.id == config["staff_role"] for role in interaction.user.roles):
                await interaction.user.move_to(channel)
                embed = discord.Embed(
                    title="KANALA KATILINDI",
                    description=f"{interaction.user.mention} kanala katıldı.",
                    color=0x00FF00
                ).set_footer(text=interaction.guild.name)
            else:
                embed = discord.Embed(
                    title="HATA!",
                    description=f"Bu komutu kullanmak için <@&{config['staff_role']}> rolüne sahip olmanız lazım!",
                    color=0xFF0000
                ).set_footer(text=f"Komut {interaction.user.mention} tarafından kullanıldı!")
        else:
            embed = discord.Embed(
                title="HATA",
                description="Bu komut DM üzerinde kullanılamaz.",
                color=0xFF0000
            )
    else:
        embed = discord.Embed(
            title="HATA",
            description="Bir ses kanalına katılmadınız veya bir ses kanalı belirtmediniz!",
            color=0xFF0000
        )

    await interaction.followup.send(embed=embed)

bot.run(config["token"])
import discord
from discord.ext import commands
import json
import time

start_time = time.time()

def json_load(file) -> dict:
    try:
        with open(file, "r") as f:
            return json.load(f)

    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Config yüklenirken hata oluştu: {e}")
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

@bot.command()
async def info(ctx: commands.Context):
    avatar = bot.user.avatar.url if bot.user.avatar.url else bot.user.default_avatar.url
    await ctx.send(
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

@bot.command()
async def kayıt(ctx : commands.Context, user : discord.Member, *name : str):
    if ctx.guild:
        name = " ".join(name)
        if any(role.id == config["role_id"] for role in ctx.author.roles):
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
"""         ,
                color=0x00FF00
            ).set_thumbnail(url=avatar
            ).set_footer(text="Aramıza hoşgeldin!")
        else:
            embed = discord.Embed(
                title="HATA!",
                description=f"Bu komutu kullanmak için <@&{config['role_id']}> rolüne sahip olmanız lazım!",
                color=0xFF0000
            ).set_footer(text=f"Komut {ctx.author.mention} tarafından kullanıldı!")
    else:
        embed = discord.Embed(
            title="HATA",
            description="Bu komut DM üzerinde kullanılamaz.",
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
        if any(role.id == config["role_id"] for role in interaction.user.roles):
            await user.edit(nick=name)
            await user.remove_roles(
                await discord.utils.get(interaction.guild.id, id=config["unregistered_role"])
            )
            await user.add_roles(
                await discord.utils.get(interaction.guild.id, id=config["member_role"])
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
        else:
            embed = discord.Embed(
                title="HATA!",
                description=f"Bu komutu kullanmak için <@&{config['role_id']}> rolüne sahip olmanız lazım!",
                color=0xFF0000
            ).set_footer(text=f"Komut {user.mention} tarafından kullanıldı!")
    else:
        embed = discord.Embed(
            title="HATA",
            description="Bu komut DM üzerinde kullanılamaz.",
            color=0xFF0000
        )

    await interaction.followup.send(embed=embed)

bot.run(config["token"])
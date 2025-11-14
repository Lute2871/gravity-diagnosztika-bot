import discord
from discord.ext import commands
import datetime
import asyncio

TOKEN = "MTQzODYwMDUxNzc4NDk2NTM1NA.Ggsaj0.-k5FvZb_5BIZZdW7LaiA6N2V1TSLyJygA4trXw"

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"[INFO] Bejelentkezve: {bot.user}")
    await bot.tree.sync()
    print("[INFO] Slash parancsok szinkronizálva.")


# Szín a pontszám alapján
def score_color(score):
    if score >= 85:
        return discord.Color.green()
    elif score >= 60:
        return discord.Color.orange()
    else:
        return discord.Color.red()


# GUILD ELEMZŐ ASYNC FÜGGVÉNY
async def analyze_guild(guild: discord.Guild):
    problems = []
    suggestions = []
    score = 100

    # --- 1. SECURITY ---
    everyone = guild.default_role.permissions

    if everyone.administrator:
        problems.append("⚠ @everyone ADMIN jogosultsággal rendelkezik!")
        suggestions.append("🔒 Vond vissza az admin jogot.")
        score -= 40

    if everyone.manage_guild:
        problems.append("⚠ @everyone Manage Server joggal rendelkezik.")
        suggestions.append("🔒 Csak vezetők kapjanak ilyen jogot.")
        score -= 15

    # Bot admin ellenőrzés
    admin_bots = [m.name for m in guild.members if m.bot and m.guild_permissions.administrator]
    if admin_bots:
        problems.append("⚠ Admin jogú botok: " + ", ".join(admin_bots))
        suggestions.append("💡 Vedd el az admin jogot a botoktól.")
        score -= 20

    # --- 2. STRUCTURE ---
    if len(guild.channels) > 80:
        problems.append("⚠ 80+ csatorna túl sok.")
        suggestions.append("🧹 Archiválj vagy törölj néhányat.")
        score -= 10

    # Üres csatornák ellenőrzése
    empty_channels = []
    for ch in guild.text_channels:
        try:
            last_msg = None
            async for msg in ch.history(limit=1):
                last_msg = msg

            if last_msg is None:
                empty_channels.append(ch.name)

        except:
            pass

    if len(empty_channels) > 5:
        problems.append(f"⚠ {len(empty_channels)} üres csatorna található.")
        suggestions.append("📁 Archiváld ezeket: " + ", ".join(empty_channels[:10]))
        score -= 10

    # --- 3. LOG SYSTEM ---
    log_names = ["log", "mod-log", "server-log", "message-log"]
    has_log = any(any(word in ch.name for word in log_names) for ch in guild.text_channels)

    if not has_log:
        problems.append("⚠ Nincs log csatorna a szerveren!")
        suggestions.append("📘 Adj hozzá: #mod-log, #server-log")
        score -= 10

    # --- 4. ROLE SYSTEM ---
    if len(guild.roles) > 50:
        problems.append("⚠ 50+ rang túl sok.")
        suggestions.append("🧹 Törölj ritka vagy felesleges rangokat.")
        score -= 5

    unused_roles = [r.name for r in guild.roles if len(r.members) == 0 and r.name != "@everyone"]
    if len(unused_roles) > 5:
        problems.append(f"⚠ {len(unused_roles)} rangot senki sem használ.")
        suggestions.append("📎 Töröld a felesleges rangokat.")
        score -= 5

    return problems, suggestions, score


# --- DIAGNOSZTIKA PARANCS ---
@bot.tree.command(name="diagnosztika_pro", description="Professzionális szerver audit futtatása.")
async def diagnosztika_pro(interaction: discord.Interaction):

    # --- 1. AZONNALI VÁLASZ (kötelező!) ---
    await interaction.response.send_message("🔍 Diagnosztika folyamatban... kérlek várj 3-5 másodpercet!", ephemeral=True)

    # --- 2. ELEMZÉS ---
    guild = interaction.guild
    problems, suggestions, score = await analyze_guild(guild)

    # Embed készítése
    embed = discord.Embed(
        title="🔍 PROFIL SZINTŰ SZERVER DIAGNOSZTIKA 4.0",
        description=f"Értékelés: **{score}/100**",
        color=score_color(score)
    )

    if problems:
        embed.add_field(name="⚠ Talált hibák:", value="\n".join(problems), inline=False)
    else:
        embed.add_field(name="🟢 Hibátlan!", value="A szerver remek állapotban van!", inline=False)

    if suggestions:
        embed.add_field(name="🛠 Ajánlott javítások:", value="\n".join(suggestions), inline=False)

    embed.set_footer(text=f"Készült: {datetime.datetime.now().strftime('%Y.%m.%d %H:%M:%S')}")

    # --- 3. ÚJ ÜZENETBEN KÜLDJÜK KI ---
    await interaction.followup.send(embed=embed)


bot.run(TOKEN)

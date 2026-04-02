import discord
from discord.ext import commands
import asyncio
import difflib
import json
import os

TOKEN = os.getenv("TOKEN")
CHANNEL_ID = 1478505267737006173

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# =========================
# QUIZ VRAGEN
# =========================

quiz_vragen = [
    {"vraag": "In what year did lewis Hamilton win his first wdc?", "antwoord": "2008"},
    {"vraag": "In what year did mika hakkinen win his first wdc?", "antwoord": "1998"},
    {"vraag": "What's the maximum amount of points a driver can get in 2026, assuming no more races will be cancelled in or past may", "antwoord": "598"},
    {"vraag": "Racing kill the radio star! Which *driver* said the following? Engineer: Sainz 1,4 behind. Driver: You want me to let him past as well?", "antwoord": ["Lewis Hamilton","Hamilton"]},
    {"vraag": "Which driver has driven the most races before his first race win?", "antwoord": ["SERGIO CHECOOO PEREEZZZZ","Sergio Perez","Checo","Perez", "Checo Perez","Sergio Checo Perez"]},
    {"vraag": "Racing kill the radio star! who said the following? K1 available", "antwoord": ["Ricciardo Adami","Ricci Adami","Ricci","Adami"]},
    {"vraag": "In full seconds, how long did Sauber's longest pit stop in 2024 take", "antwoord": "52"},
    {"vraag": "Racing kill the radio star! who said the following? I'm hanging here like a cow", "antwoord": ["Nico Hulkenberg","Hulkenberg","GOAT"]},
    {"vraag": "Which driver on the current grid has driven for the most different constructors?", "antwoord": ["Fernando Alonso","Alonso"]},
    {"vraag": "Racing kill the radio star! who's engineer said the following? No, you will not have the drink", "antwoord": ["Kimi Raikkonen","Kimi", "Raikkonen"]},
    {"vraag": "Which team won the 2025 DHL Fastest Pit Stop award?", "antwoord": "Ferrari"},
    {"vraag": "Racing kill the radio star! who said the following? All the time you have to leave a space", "antwoord": ["Fernando Alonso", "Alonso"]},
    {"vraag": "What team is based in endstone?", "antwoord": "Alpine"},
    {"vraag": "Racing kill the radio star! who said the following? Are you upset with me or something", "antwoord": ["Lewis Hamilton", "hamilton"]},
    {"vraag": "Which (recent) f1 driver shares the record for most points without a podium?", "antwoord": ["Yuki Tsunoda","Yuki","tsunoda"]},
    {"vraag": "Racing kill the radio star (press conference edidion)! who said the following? You gotta be either blind or stupid to not see me...", "antwoord": ["Juan Pablo Montoya", "Montoya"]},

    {"vraag": "Racing kill the radio star! who said the following? Yeah that's fine. send them my regards :)!", "antwoord": ["Max Verstappen", "Verstappen"]},
    {"vraag": "In which city/town is Racing Bulls based?", "antwoord": "Faenza"},
    {"vraag": "Racing kill the radio star! In 2017, who said the following? I'm gonna pee in your seat", "antwoord": ["Jenson Button", "Button"]},
    {"vraag": "In 2007 f1 had a dutch f1 team, spyker. What’s this team called now?", "antwoord": ["Aston Martin","Aston Martin F1"]},
    {"vraag": "Racing kill the radio star! who said the following? Ahh, I got damage! I GOT DAMAGEE!! Argh", "antwoord": ["Max Verstappen", "Verstappen"]},
 
    {"vraag": "Racing kill the radio star! who said the following? WHO THE ****! Oh, I'm out!! Crashed! Somebody hit me in the ******* rear! Turn 2... And then somebody hit me in the ******* reag again in turn 3! for ***** sake", "antwoord": ["Fernando Alonso", "Alonso"]},
    {"vraag": "What’s the full name of the track that hosts the us gp?", "antwoord": "Circuit of the Americas"},
    {"vraag": "Racing kill the radio star! who said the following? All the time you have to leave a space", "antwoord": ["Fernando Alonso", "Alonso"]},
    {"vraag": "In which country was the first ever night F1 race hosted?", "antwoord": "Singapore"},
    {"vraag": "Racing kill the radio star (meme edition)! who said the following? I knew this I studied this at school! I knew what this meant, but not anymore... I forgot", "antwoord": ["Carlos Sainz Vázquez de Castro Cenamor Rincón Rebollo Birto Moreno de Aranda de Anteriuga Tiapera Deltún", "Carlos sainz jr", "carlos sainz","sainz","smooth operator"]},
    {"vraag": "What’s the last name (surname) of a father and a son that both won the wdc?", "antwoord": ["Rosberg","Keke rosberg","Nico rosberg"]},

]

vraag_index = 0
huidige_vraag = None
antwoorden_gegeven = set()
correcte_namen = set()

SCORE_FILE = "scores.json"

# =========================
# SCORES OPSLAAN / LADEN
# =========================

def load_scores():
    try:
        with open(SCORE_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_scores():
    with open(SCORE_FILE, "w") as f:
        json.dump(scorebord, f)

scorebord = load_scores()

# =========================
# ANTWOORD CHECK
# =========================

def antwoord_correct(user_answer, correct):
    user_answer = user_answer.strip().lower()

    if isinstance(correct, list):
        antwoorden = [a.lower() for a in correct]
    else:
        antwoorden = [correct.lower()]

    # 🔢 check: als ALLE antwoorden cijfers zijn → exacte match
    if all(a.isdigit() for a in antwoorden):
        return user_answer in antwoorden

    # normale exacte check
    if user_answer in antwoorden:
        return True

    # fuzzy check alleen voor tekst
    for a in antwoorden:
        similarity = difflib.SequenceMatcher(None, user_answer, a).ratio()
        if similarity >= 0.75:
            return True

    return False

    return False

# =========================
# LEADERBOARD
# =========================

def leaderboard_text():
    if not scorebord:
        return "No scores yet!"

    sorted_scores = sorted(scorebord.items(), key=lambda x: x[1]["score"], reverse=True)

    text = "🏆 **Quiz Leaderboard** 🏆\n\n"

    for i, (user_id, data) in enumerate(sorted_scores, start=1):
        name = data["name"]
        points = data["score"]

        if i == 1:
            pos = "🥇"
        elif i == 2:
            pos = "🥈"
        elif i == 3:
            pos = "🥉"
        else:
            pos = f"{i}."

        text += f"{pos} {name} — {points} pts\n"

    return text

# =========================
# MODAL
# =========================

class AnswerModal(discord.ui.Modal, title="Answer question"):

    answer = discord.ui.TextInput(label="Your answer")

    async def on_submit(self, interaction: discord.Interaction):
        global huidige_vraag, scorebord, antwoorden_gegeven, correcte_namen

        if huidige_vraag is None:
            await interaction.response.send_message("No active question", ephemeral=True)
            return

        user_id = str(interaction.user.id)
        username = interaction.user.name

        print(f"{username} answered: {self.answer.value}")

        # ❌ al geantwoord?
        if user_id in antwoorden_gegeven:
            await interaction.response.send_message("❗ You already answered!", ephemeral=True)
            return

        antwoorden_gegeven.add(user_id)

        # ✅ correct?
        if antwoord_correct(self.answer.value, huidige_vraag["antwoord"]):

            correcte_namen.add(username)

            if user_id not in scorebord:
                scorebord[user_id] = {"name": username, "score": 0}

            scorebord[user_id]["score"] += 1
            scorebord[user_id]["name"] = username

            save_scores()

            print(f"{username} CORRECT")

            await interaction.response.send_message("✅ Correct!", ephemeral=True)

        else:
            print(f"{username} WRONG")
            await interaction.response.send_message("❌ Wrong!", ephemeral=True)

# =========================
# BUTTON VIEW
# =========================

class QuizView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Answer", style=discord.ButtonStyle.primary, custom_id="quiz_answer")
    async def answer_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(AnswerModal())

# =========================
# QUIZ LOOP
# =========================

async def quiz_loop():
    global huidige_vraag, vraag_index, antwoorden_gegeven, correcte_namen

    await bot.wait_until_ready()
    channel = await bot.fetch_channel(CHANNEL_ID)

    while True:

        if vraag_index >= len(quiz_vragen):
            vraag_index = 0

        huidige_vraag = quiz_vragen[vraag_index]
        vraag_index += 1
        antwoorden_gegeven.clear()
        correcte_namen.clear()

        await channel.send(
            f"📢 **Quiz Question**\n\n{huidige_vraag['vraag']}",
            view=QuizView()
        )

        await asyncio.sleep(30)  # 23 uur is 82800

        correct = huidige_vraag["antwoord"]
        if isinstance(correct, list):
            correct = correct[0]

        huidige_vraag = None

        if correcte_namen:
            await channel.send(
                f"⏱ Time's up! Answer: **{correct}**\n"
                f"Correct players: {', '.join(correcte_namen)}"
            )
        else:
            await channel.send(
                f"⏱ Time's up! Answer: **{correct}**\nNo correct answers."
            )

        await channel.send(leaderboard_text())

        await asyncio.sleep(10)  # pauze tussen vragen, uur is 3600

# =========================
# COMMAND
# =========================

@bot.command()
async def score(ctx):
    await ctx.send(leaderboard_text())

# =========================
# READY
# =========================

@bot.event
async def on_ready():
    print(f"Bot online as {bot.user}")
    bot.add_view(QuizView())
    bot.loop.create_task(quiz_loop())

bot.run(TOKEN)

import discord
from discord.ext import tasks, commands
import asyncio
import difflib
import json
import os

TOKEN = os.getenv("TOKEN")
CHANNEL_ID = 148165243xxx8346764400

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# =========================
# QUIZ VRAGEN
# =========================

quiz_vragen = [
    {"vraag": "Who said: Must be the water", "antwoord": ["Bryan Bozzi","Bozzi"]},
    {"vraag": "What does DRS stand for?", "antwoord": ["Drag Reduction System","DRS System"]},
    {"vraag": "Who said: Honestly what are we doing? Racing or pingpong?", "antwoord": ["Sebastian Vettel","Vettel","Seb"]},
    {"vraag": "Which driver has most podiums without a win?", "antwoord": ["Nick Heidfeld","Heidfeld"]},
    {"vraag": "Who said: I think Ericsson hit us?", "antwoord": ["Romain Grosjean","Grosjean"]},
    {"vraag": "Which driver had, at the start of the 2026 season, the most points without a race win", "antwoord": ["Nico Hulkenberg","Hulkenberg","GOAT"]},
    {"vraag": "Racing kill the radio star! who said the following? That’s for all the kids out there who dream the impossible, you can do it too, man!", "antwoord": ["Lewis Hamilton","Hamilton"]},

]

vraag_index = 0
huidige_vraag = None
antwoorden_gegeven = set()

SCORE_FILE = "scores.json"

# =========================
# SCORES OPSLAAN / LADEN
# =========================

def load_scores():
    try:
        with open(SCORE_FILE,"r") as f:
            return json.load(f)
    except:
        return {}

def save_scores():
    with open(SCORE_FILE,"w") as f:
        json.dump(scorebord,f)

scorebord = load_scores()

# =========================
# FUZZY CHECK
# =========================

def antwoord_correct(user_answer, correct):
    user_answer = user_answer.strip().lower()

    if isinstance(correct,list):
        antwoorden = [a.lower() for a in correct]
    else:
        antwoorden = [correct.lower()]

    if user_answer in antwoorden:
        return True

    for a in antwoorden:
        similarity = difflib.SequenceMatcher(None,user_answer,a).ratio()
        if similarity >= 0.65:
            return True

    return False

# =========================
# LEADERBOARD
# =========================

def leaderboard_text():
    if not scorebord:
        return "No scores yet!"

    sorted_scores = sorted(scorebord.items(), key=lambda x:x[1], reverse=True)

    text = "🏆 **Quiz Leaderboard** 🏆\n\n"

    for i,(name,points) in enumerate(sorted_scores,start=1):

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

class AnswerModal(discord.ui.Modal,title="Answer question"):

    answer = discord.ui.TextInput(label="Your answer")

    async def on_submit(self, interaction: discord.Interaction):
        global huidige_vraag

        if huidige_vraag is None:
            await interaction.response.send_message("No active question",ephemeral=True)
            return

        user = interaction.user.name

        if antwoord_correct(self.answer.value,huidige_vraag["antwoord"]):

            if user not in antwoorden_gegeven:

                antwoorden_gegeven.add(user)

                if user not in scorebord:
                    scorebord[user] = 0

                scorebord[user]+=1
                save_scores()

            await interaction.response.send_message("✅ Correct!",ephemeral=True)

        else:
            await interaction.response.send_message("❌ Wrong",ephemeral=True)

class QuizView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Answer",style=discord.ButtonStyle.primary,custom_id="quiz_answer")
    async def answer_button(self,interaction:discord.Interaction,button:discord.ui.Button):
        await interaction.response.send_modal(AnswerModal())

# =========================
# QUIZ ENGINE
# =========================

async def quiz_loop():
    global huidige_vraag,vraag_index,antwoorden_gegeven

    await bot.wait_until_ready()
    channel = await bot.fetch_channel(CHANNEL_ID)

    while True:

        if vraag_index >= len(quiz_vragen):
            vraag_index = 0

        huidige_vraag = quiz_vragen[vraag_index]
        vraag_index += 1
        antwoorden_gegeven.clear()

        await channel.send(
            f"📢 **Quiz Question**\n\n{huidige_vraag['vraag']}",
            view=QuizView()
        )

        await asyncio.sleep(82800)

        correct = huidige_vraag["antwoord"]
        if isinstance(correct,list):
            correct = correct[0]

        huidige_vraag = None

        if antwoorden_gegeven:
            await channel.send(
                f"⏱ Time's up! Answer: **{correct}**\n"
                f"Correct players: {', '.join(antwoorden_gegeven)}"
            )
        else:
            await channel.send(
                f"⏱ Time's up! Answer: **{correct}**\nNo correct answers."
            )

        await channel.send(leaderboard_text())

        await asyncio.sleep(3600)

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

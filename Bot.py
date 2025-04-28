import discord
from discord.ext import commands
import requests
import asyncio  # یادت نره

TOKEN = "bot TOKEN"
API_URL = "http://127.0.0.1:5000/validate"

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)
bot.current_code = None  # اضافه شده برای ذخیره کد

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

def validate_code(code):
    try:
        response = requests.post(API_URL, json={"code": code})
        if response.status_code != 200:
            return None
        return response.json()
    except Exception as e:
        print(f"Error contacting API: {e}")
        return None

@bot.command()
async def join(ctx, code):
    data = validate_code(code)
    if not data:
        await ctx.send("Error: could not connect to server.")
        return
    if not data.get("valid") or data.get("type") != "voice":
        await ctx.send("Invalid or non-voice code.")
        return

    user_id = data["user_id"]
    await ctx.send(f"Code accepted. Connecting to user: {user_id}")

    if ctx.author.voice:
        channel = ctx.author.voice.channel
        await channel.connect()
        await ctx.send("Connected to voice channel!")
    else:
        await ctx.send("You are not in a voice channel.")

@bot.command()
async def message(ctx, code):
    data = validate_code(code)
    if not data or not data.get("valid") or data.get("type") != "message":
        await ctx.send("Invalid or non-message code.")
        return

    bot.current_code = code
    user_id = data["user_id"]
    await ctx.send(f"Message tunnel established with user: {user_id}")

    async def listen_for_messages():
        last = 0
        while True:
            try:
                res = requests.post("http://127.0.0.1:5000/get_messages", json={"code": code, "last": last})
                if res.status_code == 200:
                    result = res.json()
                    for m in result["messages"]:
                        if m["from"] == "web":
                            await ctx.send(m["content"])
                    last = result["new_last"]
            except Exception as e:
                print(f"Error fetching messages: {e}")
            await asyncio.sleep(2)

    bot.loop.create_task(listen_for_messages())

@bot.event
async def on_message(message):
    await bot.process_commands(message)
    if message.content.startswith("!") or message.author.bot:
        return

    if bot.current_code:
        try:
            requests.post("http://127.0.0.1:5000/send_message", json={
                "code": bot.current_code,
                "message": message.content,
                "sender": "discord"
            })
        except Exception as e:
            print(f"Error sending message to API: {e}")

bot.run(TOKEN)
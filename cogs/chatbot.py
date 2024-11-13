import discord
from discord.ext import commands
import json
from groq import Groq

import os


class chatbot(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author == self.bot.user:
            return
        """
          Listen any message mention or reply to bot
        """
        if any(m.id == self.bot.user.id for m in message.mentions):
            await self.process_message(message)  # getting the message

    async def process_message(self, message: discord.Message):
        msg = message.content.replace("<@1303202968228724756>", "")
        chunk_message = json.load(open("chat_data/chunk_message.json"))
        trained_message = json.load(open("chat_data/trained_message.json"))

        if len(chunk_message) == 40:
            print("true")
            chunk_message = []
            with open("chat_data/chunk_message.json", "w", encoding="utf-8") as f:
                json.dump(chunk_message, f, ensure_ascii=False, indent=4)
        else:
            for i in chunk_message:
                trained_message.append(i)
        trained_message.append({"role": "user", "content": msg})
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        completion = client.chat.completions.create(
            model="gemma2-9b-it",
            messages=trained_message,
            temperature=1,
            max_tokens=1024,
            top_p=1,
            stream=False,
            stop=None,
        )
        chunk_message.append({"role": "user", "content": msg})
        chunk_message.append(
            {"role": "assistant", "content": completion.choices[0].message.content}
        )
        with open("chat_data/chunk_message.json", "w", encoding="utf-8") as f:
            json.dump(chunk_message, f, ensure_ascii=False, indent=4)
        await message.reply(completion.choices[0].message.content)


async def setup(bot):
    await bot.add_cog(chatbot(bot))

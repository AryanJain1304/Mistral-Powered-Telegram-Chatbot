import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.filters import Command
import aiohttp
import json

API_TOKEN = '7857036500:AAE0YEaFQHh5HPitWHbazJv4bGx4KkjinrE'
OLLAMA_URL = 'http://localhost:11434/api/chat'
OLLAMA_MODEL = 'mistral'

user_conversations = {}

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start_handler(message: Message):
    await message.answer("👋 Welcome! I am a bot created by Aryan.\n Ask me anything.")
    print(f"[{message.from_user.id}] /start")

@dp.message(Command("help"))
async def help_handler(message: Message):
    await message.answer("🛠 Available Commands:\n/start - Start the bot\n/help - Get help\nJust send a message to ask a question!")
    print(f"[{message.from_user.id}] /help")

@dp.message()
async def handle_message(message: Message):
    user_id = str(message.from_user.id)
    user_input = message.text.strip()

    print(f"[{user_id}] User: {user_input}")

    if user_id not in user_conversations:
        user_conversations[user_id] = []

    user_conversations[user_id].append({"role": "user", "content": user_input})

    response_text = await query_ollama(user_conversations[user_id])

    user_conversations[user_id].append({"role": "assistant", "content": response_text})

    await message.answer(response_text)
    print(f"[{user_id}] Bot: {response_text}")

async def query_ollama(messages):
    payload = {
        "model": OLLAMA_MODEL,
        "messages": messages,
        "stream": True
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(OLLAMA_URL, json=payload) as resp:
            if resp.status != 200:
                return f"[Error] Ollama returned status {resp.status}"

            response_text = ""
            async for line in resp.content:
                if not line:
                    continue
                try:
                    data = json.loads(line.decode("utf-8"))
                    content = data.get("message", {}).get("content")
                    if content:
                        response_text += content
                except Exception as e:
                    print(f"Error decoding line: {e}")

            return response_text or "[Error] Empty response from Ollama"

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
import discord
import aiohttp
import random
import io

import os
TOKEN = os.environ.get("TOKEN")

# Вставь сюда всю строку целиком из настроек gelbooru, например:
# "&api_key=01738cb5...&user_id=1920749"
API_CREDENTIALS = "&api_key=01738cb51b3a55d57979e7ab75cb5434248f2b4410e22b3529acb5701ff901c4f86c03d4c90f18959522cca0faa6d844c33344550fbd2863155f7aaf812323e1&user_id=1920749"

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)


async def get_random_image() -> str | None:
    page = random.randint(0, 20)

    api_url = (
        f"https://gelbooru.com/index.php"
        f"?page=dapi&s=post&q=index&json=1"
        f"&tags=yuri+kiss&pid={page}&limit=42"
        f"{API_CREDENTIALS}"
    )

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    print(f"[DEBUG] Запрос: {api_url}")

    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(api_url) as resp:
            print(f"[DEBUG] Статус: {resp.status}")
            text = await resp.text()
            print(f"[DEBUG] Ответ (первые 500 символов): {text[:500]}")

            if resp.status != 200:
                return None

            try:
                data = await resp.json(content_type=None)
            except Exception as e:
                print(f"[DEBUG] Ошибка парсинга JSON: {e}")
                return None

    posts = data.get("post", [])
    print(f"[DEBUG] Найдено постов: {len(posts)}")

    if not posts:
        return None

    post = random.choice(posts)
    url = post.get("file_url")
    print(f"[DEBUG] URL картинки: {url}")
    return url


@client.event
async def on_ready():
    print(f"Logged in as {client.user}")


@client.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return

    if client.user in message.mentions:
        async with message.channel.typing():
            img_url = await get_random_image()

            if not img_url:
                await message.channel.send("Не удалось найти картинку, попробуй ещё раз 😔")
                return

            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36", "Referer": "https://gelbooru.com/"}
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.get(img_url) as resp:
                    if resp.status == 200:
                        data = await resp.read()
                        ext = img_url.split(".")[-1].split("?")[0].lower()
                        if ext not in ("jpg", "jpeg", "png", "gif", "webp"):
                            ext = "jpg"
                        file = discord.File(fp=io.BytesIO(data), filename=f"image.{ext}")
                        await message.channel.send(file=file)
                    else:
                        await message.channel.send("Не удалось скачать картинку, попробуй ещё раз 😔")


client.run(TOKEN)

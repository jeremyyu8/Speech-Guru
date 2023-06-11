import os
import discord
import openai
from pydub import AudioSegment

from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
openai.api_key = os.getenv("API_KEY")

# Discord client setup
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')

@client.event
async def on_message(message):
    username = str(message.author).split('#')[0]
    user_message = str(message.content)
    channel = str(message.channel.name)
    print(f'{username}: {user_message} ({channel})')
    
    if message.author == client.user:
        return

    # Handle text messages
    if message.content:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
            {"role": "system", "content": "You are a helpful assistant designed to provide feedback on people's speeches."},
            {"role": "user", "content": str(message.content)}],
            temperature=0.3,
            max_tokens=100
        )

        await message.channel.send(response.choices[0].message.content.strip())

    # Handle audio messages
    if message.attachments and message.attachments[0].content_type.startswith('audio'):
        attachment = message.attachments[0]
        temp_path = "audio.wav"
        await attachment.save(temp_path)
        transcript = transcribe_audio(temp_path)
        await message.channel.send("Transcript of the audio message: " + str(transcript))

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
            {"role": "system", "content": "You are a helpful assistant designed to provide feedback on people's speeches."},
            {"role": "user", "content": "Please provide feedback on the following speech: " + str(transcript)}
        ],
        temperature=0.3,
        )

        await message.channel.send(response.choices[0].message.content.strip())

        os.remove("audio.wav")
        os.remove("out.wav")


def transcribe_audio(file_path):
    audio_copy = AudioSegment.from_file(file_path)
    audio_copy.export("out.wav", format="wav")
    audio = open("out.wav", 'rb')
    transcript = openai.Audio.transcribe("whisper-1", audio).text
    
    return transcript

client.run(DISCORD_TOKEN)
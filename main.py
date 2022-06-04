import discord
from discord import message
from discord.ext import commands
from discord.utils import get
from discord.utils import get
from discord.ext import commands
from discord import NotFound
from discord.utils import get
import os
import subprocess
import json
from bs4 import BeautifulSoup
import requests
import sys
import time
import os
import sys
import moviepy.editor as mpe
import ffmpeg

def compress_video(video_full_path, output_file_name, target_size):
    min_audio_bitrate = 32000
    max_audio_bitrate = 256000

    probe = ffmpeg.probe(video_full_path)
    duration = float(probe['format']['duration'])
    audio_bitrate = float(next((s for s in probe['streams'] if s['codec_type'] == 'audio'), None)['bit_rate'])
    target_total_bitrate = (target_size * 1024 * 8) / (1.073741824 * duration)
    if 10 * audio_bitrate > target_total_bitrate:
        audio_bitrate = target_total_bitrate / 10
        if audio_bitrate < min_audio_bitrate < target_total_bitrate:
            audio_bitrate = min_audio_bitrate
        elif audio_bitrate > max_audio_bitrate:
            audio_bitrate = max_audio_bitrate
    video_bitrate = target_total_bitrate - audio_bitrate

    i = ffmpeg.input(video_full_path)
    ffmpeg.output(i, os.devnull,
                  **{'c:v': 'libx264', 'b:v': video_bitrate, 'pass': 1, 'f': 'mp4'}
                  ).overwrite_output().run()
    ffmpeg.output(i, output_file_name,
                  **{'c:v': 'libx264', 'b:v': video_bitrate, 'pass': 2, 'c:a': 'aac', 'b:a': audio_bitrate}
                  ).overwrite_output().run()

bot = commands.Bot(command_prefix="?")
bot.remove_command("help")

@bot.event
async def on_ready():
    print("Bot online!")
    print("------------------------------")

@bot.command()
async def video(ctx, url):

    if url == None:
        await ctx.reply("Make sure you paste in a URL.")
        return

    path = 'C:\\Desktop\\reddit_media\\'



    headers = {'User-Agent':'Mozilla/5.0'}
    response = requests.get(url,headers = headers)

    os.environ['PATH'] += ';'+path
    sys.path.insert(0,'path/to/ffmpeg')

    post_id = url[url.find('comments/') + 9:]
    post_id = f"t3_{post_id[:post_id.find('/')]}"


    if(response.status_code == 200):
        soup = BeautifulSoup(response.text,'lxml')
        required_js = soup.find('script',id='data') 
        
        json_data = json.loads(required_js.text.replace('window.___r = ','')[:-1])
        title = json_data['posts']['models'][post_id]['title']
        title = title.replace(' ','_')
        dash_url = json_data['posts']['models'][post_id]['media']['dashUrl']
        height  = json_data['posts']['models'][post_id]['media']['height']
        dash_url = dash_url[:int(dash_url.find('DASH')) + 4]
        video_url = f'{dash_url}_{height}.mp4'
        audio_url = f'{dash_url}_audio.mp4'


    msg = await ctx.reply("Downloading..")


    with open(f'{title}_video.mp4','wb') as file:
        print('downloading..',end='',flush = True)
        response = requests.get(video_url,headers=headers)
        if(response.status_code == 200):
            file.write(response.content)
            print('\rDownloaded!')
        else:
            print('\rno wey mane brodere')
            msg.edit(content="Failed downloading, please try again.")

    with open(f'{title}_audio.mp3','wb') as file:
        print('Downloading Audio...',end = '',flush = True)
        response = requests.get(audio_url,headers=headers)
        if(response.status_code == 200):
            file.write(response.content)
            print('\rAudio Downloaded!')
        else:
            print('\raudio no download')
            msg.edit(content="Failed downloading, please try again.")




    def combine_audio(vidname, audname, outname, fps=60):
        my_clip = mpe.VideoFileClip(vidname)
        audio_background = mpe.AudioFileClip(audname)
        final_clip = my_clip.set_audio(audio_background)
        final_clip.write_videofile(outname,fps=fps)


    combine_audio(f"{title}_video.mp4", f"{title}_audio.mp3", f"{title}.mp4")

    os.remove(f"{title}_video.mp4")
    os.remove(f"{title}_audio.mp3")
    msg.edit(content="Success!")
    await ctx.reply(file=discord.File(f'{title}_c.mp4'))
    os.remove(f"{title}.mp4")
    os.remove(f"{title}_c.mp4")


bot.run("token")

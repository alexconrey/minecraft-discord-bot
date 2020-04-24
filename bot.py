#!/usr/bin/env python3
import argparse
import os
import re
import yaml

from discord.ext import commands
from mcrcon import MCRcon

cfg = {}

client = commands.Bot(command_prefix='!')

def loadCfg(file_name):
    data = None
    with open(file_name, 'r') as f:
        data = yaml.safe_load(f)
    return data

def runMCCommand(command):
    with MCRcon('minecraft01-home.home.myhomelab.network', 'Remote1') as mcr:
        resp = mcr.command(command)
        resp = re.sub(r'§(\w|\d)?', '', resp)
        return resp

def getCommandsFromMC():
    commands = runMCCommand("help")
    index_pages = 0
    output = []
    for i in commands.splitlines():
        if 'Index' in i:
            r = re.search('.*Help: Index \(\d\/(.*)\).*', i)
            max_page = int(r.group(1))
            if max_page:
                for i in range(max_page):
                    help_page = runMCCommand("help {}".format(i+1)).splitlines()
                    for c in help_page:
                        if 'Index' in c:
                            continue
                        if 'Use /help' in c:
                            continue
                        if c[0] != '/':
                            continue
                        output.append(c)
    out_str = '\n'.join(output)
    max_chars = 1800

    format_output = [(out_str[i:i+max_chars]) for i in range(0, len(out_str), max_chars)]

    return format_output

def formatMessage(message):
    fmt = """```
    {}
    ```""".format(message)

    return fmt

@client.event
async def on_ready():
    for guild in client.guilds:
        if guild.id == cfg['discord']['server_id']:
            break

    print(f'{client.user} has connected!')
    print(f'{guild.name}')

@client.command(name='mc_commands', help='Shows available minecraft server commands')
async def show_mc_commands(message):
    commands = getCommandsFromMC()
    #print(getCommandsFromMC())
    for i in commands:
        await message.channel.send(formatMessage(i))

@client.command(name='mc_save', help='Runs save-all in Minecraft')
async def run_mc_save(message):
    if runMCCommand('save-all'):
        await message.channel.send('Minecraft save point created.')

@client.command(name='mc_online', help='Shows online players')
async def show_online_players(message):
    players = runMCCommand('list')
    await message.channel.send(formatMessage(players))

def main():
    parser = argparse.ArgumentParser(description='Minecraft Discord Bot')
    parser.add_argument('--config', required=True, help='Path to config.yaml')
    args = parser.parse_args()

    global cfg
    cfg = loadCfg(args.config)

    client.run(cfg['discord']['token'])

if __name__ == "__main__":
    main()


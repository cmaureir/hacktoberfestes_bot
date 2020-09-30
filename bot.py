import asyncio
import configparser
from enum import Enum

import discord
import pandas as pd
from discord.ext import commands

config = configparser.ConfigParser()
config.read("config.ini")

TOKEN = config["DEFAULT"]["Token"]
GUILD = config["DEFAULT"]["Guild"]
CHANNEL = config["DEFAULT"]["Channel"]
ADMIN_CHANNEL = config["DEFAULT"]["AdminChannel"]
ROLE = config["DEFAULT"]["Role"]
LIST = config["DEFAULT"]["List"]

RIDS = set(pd.read_csv(LIST)["Order ID"].apply(int))

bot = commands.Bot(command_prefix="!")


class RegistrationStatus(Enum):
    OK = 0
    NOT_FOUND = 1
    ALREADY_REGISTERED = 2


def get_ready_tickets():
    registered = set()
    with open("ready.csv", "r") as f:
        try:
            registered = set(int(line) for line in (tmp_line.strip() for tmp_line in f) if line)
        except ValueError:
            print("Error converting lines to integeres")
    return registered


def register_user(n):
    registered = get_ready_tickets()
    remaining = RIDS - registered
    if n in remaining:
        with open("ready.csv", "a") as f:
            f.write(str(n))
            f.write("\n")
        return RegistrationStatus.OK
    else:
        if n in registered:
            return RegistrationStatus.ALREADY_REGISTERED
        else:
            return RegistrationStatus.NOT_FOUND


@bot.command(name="estado", help="Comando para ver el estado actual de regitros", pass_context=True)
async def estado(ctx):
    if str(ctx.channel) == ADMIN_CHANNEL:
        registered = get_ready_tickets()
        total = len(RIDS)
        ready = len(registered)
        msg = f"Registros {ready}/{total} ({(ready/total)*100:.1f}%)"
        await ctx.send(msg)


@bot.command(name="registro", help="Comando de registro", pass_context=True)
async def registro(ctx, ticket_number: str):

    if str(ctx.channel) != CHANNEL:
        # Remove messages when not on the specific registration channel
        await discord.Message.delete(ctx.message)
    else:
        number = None
        # Allow people adding the '#' at the beginning of the ticket number
        if ticket_number.startswith("#"):
            ticket_number = ticket_number[1:].strip()
        try:
            number = int(ticket_number)
        except ValueError:
            await ctx.send("Ticket incorrecto, ingresa solo números.\n\t" "`!registro 123456`")

        # Load special role to give permissions
        role = discord.utils.get(ctx.message.author.guild.roles, name=ROLE)

        msg = None
        status = register_user(number)

        if status == RegistrationStatus.OK:
            msg = f"Usuario {ctx.message.author.mention} registrado! :)"
            # TODO: Check if user already has the role
            await ctx.author.add_roles(role)

            # Send final response
            await ctx.send(msg)
        elif status == RegistrationStatus.ALREADY_REGISTERED:
            msg = "Ticket ya registrado"
            message = await ctx.send(msg)
            await asyncio.sleep(2)
            await discord.Message.delete(message)
        elif status == RegistrationStatus.NOT_FOUND:
            msg = "El ticket no existe, revise su número."
            message = await ctx.send(msg)
            await asyncio.sleep(2)
            await discord.Message.delete(message)
        else:
            # This should never happens, I Promise
            pass

        # Remove command after parsing it
        await discord.Message.delete(ctx.message)


# Removing help command
bot.remove_command("help")

# Starting the bot
print("Running...")
print(f"Total: {len(RIDS)}")
print(f"Ready: {len(get_ready_tickets())}")
bot.run(TOKEN)

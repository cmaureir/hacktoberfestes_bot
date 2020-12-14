import csv
import json
import os
import re
from datetime import datetime
from pathlib import Path
import argparse

import discord
from config import load_config
from logger import get_logger

LOGGER = get_logger(__name__)

config = load_config()
TOKEN = config['DEFAULT']['Token']
GUILD = int(config["DEFAULT"]["Guild"])


DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S,%f"
log_regex = re.compile(r'(?P<datetime>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3})')

def build_activity_csv(logfile_path: Path,
                       discord_members_path: Path,
                       discord_channels_path: Path,
                       output_path: Path):
    LOGGER.info("Loading channels data")
    with open(discord_channels_path) as csvfile:
        reader = csv.reader(csvfile)

        channels = {c[0]: {'name': c[1], 'category': c[2]} for c in reader}


    LOGGER.info("Loading members data")
    with open(discord_members_path) as csvfile:
        reader = csv.reader(csvfile)

        members = {c[1] or c[2] or c[3]: {'roles': c[4]} for c in reader}

    LOGGER.info("Loading metrics data")
    members_not_found = []
    with open(logfile_path) as csvfile:
        lines = []
        for line in csvfile.readlines():
            if 'Message' in line:
                log_data = line.split('Message - ')

                data = dict((el.split('=') for el in log_data[1].split('; ')))
                data['words_count'] = sum(json.loads(data['words']).values())
                del data['words']
                if data['author'] in members_not_found:
                    continue

                data['timestamp'] = log_regex.match(log_data[0]).group()
                member_data = members.get(data['author'])
                channel_data = channels.get(data['channel'])

                if not member_data:
                    members_not_found.append(data['author'])
                    continue

                if not channel_data:
                    LOGGER.error("Channel not found",
                                 extra={'channel_id': data['channel']})
                    continue

                lines.append(
                    [data['timestamp'],
                     channel_data['name'],
                     channel_data['category'],
                     data['author'],
                     member_data['roles'],
                     data['words_count']])

    LOGGER.info("Messages loaded", extra={'messages_count': len(lines)})
    LOGGER.warning("Members not found", extra={'members_not_found': members_not_found})


    output_filename = f"activty_metrics_{datetime.now().strftime('%Y%m%d')}.csv"
    with open(output_path / output_filename, "w") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(
            ["timestamp",
             "channel_name",
             "channel_category",
             "author",
             "author_roles",
             "words_count"])

        for line in lines:
            writer.writerow(line)

    LOGGER.info("Done!")


def get_server_members_and_channels(output_path: Path):
    client = discord.Client()

    @client.event
    async def on_ready():
        LOGGER.info('We have logged in as {0.user}'.format(client))

        # List all members in server and write csv
        LOGGER.info("Downloading members from server")
        server = client.get_guild(GUILD)
        server._members = {m.id: m async for m in server.fetch_members()}
        members_lines = []
        for member in client.get_all_members():
            members_lines.append(
                [member.id, member.nick, member.name, member.display_name, ' | '.join(r.name for r in member.roles)])

        with open(output_path / "server_members.csv", "w") as f:
            writer = csv.writer(f)
            writer.writerow(['id', 'nick', 'name', 'display_name', 'roles'])
            for line in members_lines:
                writer.writerow(line)
        LOGGER.info("Members found in server",
                    extra={'members_count': len(members_lines)})

        # List all text channels in server and write csv
        LOGGER.info("Downloading channels from server")
        channels_lines = []
        for channel in client.get_all_channels():
            if isinstance(channel, discord.TextChannel):
                channels_lines.append([channel.id, channel.name, channel.category.name])

        with open(output_path / "server_channels.csv", "w") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['channel_id', 'channel_name', 'category'])
            for line in channels_lines:
                writer.writerow(line)
        LOGGER.info("Channels found in server",
                    extra={'channels_count': len(channels_lines)})

        await client.close()
        LOGGER.info("Client closed")

    client.run(TOKEN)


def main():
    parser = argparse.ArgumentParser(prog='discord-metrics')
    parser.add_argument(
        '--logfile',
        default='./metrics-stdout.log',
        help="metrics logfile")
    parser.add_argument(
        '--output-folder',
        default='./tmp',
        help="metrics logfile")

    args = parser.parse_args()

    logfile_path = Path(args.logfile)
    output_folder = Path(args.output_folder)

    get_server_members_and_channels(output_folder)
    build_activity_csv(logfile_path,
                       output_folder / "server_members.csv",
                       output_folder / "server_channels.csv",
                       output_folder)



if __name__ == '__main__':
    main()

import json
import re
import string
from collections import Counter

import discord
from config import load_config
from logger import get_logger

config = load_config()
TOKEN = config["DEFAULT"]["Token"]
LOGGER = get_logger(__name__)

class ActivityMonitor(discord.Client):

    async def on_message(self, message):
        if message.channel.type == discord.ChannelType.private:
            return
        words = self.tokenize_message(message.content)
        counter = Counter(words.split(' '))
        LOGGER.info("Message", extra={'channel': message.channel.id,
                                      'author': message.author.name,
                                      'words': json.dumps(counter)})

    async def on_raw_reaction_add(self, payload):
        if payload.event_type == 'REACTION_ADD':
            LOGGER.info("Reaction",
                        extra={'channel': payload.channel_id,
                               'dmessage': payload.message_id,
                               'user': payload.member.name,
                               'emoji': payload.emoji})

    @staticmethod
    def tokenize_message(message):
        # Remove punctuation and other stuff that we don't want to include
        excluded_chars = str.maketrans('', '', string.punctuation + "·¡¿1234567890\\\"")
        words = message.translate(excluded_chars).strip().lower().replace('\n', ' ')
        # Remove duplicated spaces
        words = re.sub(' +', ' ', words)
        # exclude words of two characters or less
        words = ' '.join([w for w in words.split(' ') if len(w) > 2])
        return words

client = ActivityMonitor()
client.run(TOKEN)

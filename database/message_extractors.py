import re

# Regular expressions to match mentions and links
MENTION_PATTERN = re.compile(r'(<@!?(\d+)>|<@&(\d+)>|<#(\d+)>)')
LINK_PATTERN = re.compile(r'https?://\S+')


def extract_mentions(message_content):
    mentions_tuples = MENTION_PATTERN.findall(message_content)
    # Extract entire mention strings from the tuples
    mentions = [tup[0] for tup in mentions_tuples]
    return mentions


def extract_links(message_content):
    links = LINK_PATTERN.findall(message_content)
    return [link for link in links if link]

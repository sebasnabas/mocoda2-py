import dataclasses
from pprint import pprint
import json

import jsonpath_ng
import requests

from mocoda2.definitions import SEARCH_ENDPOINT, CHAT_ENDPOINT, LANG_ENDPOINT
from mocoda2.utils import (
    read_csv,
    write_to_csv,
    get_participants_with_messages,
    merge_participants,
    filter_participants,
    BearerAuth,
    Participant
)


def get_translations(bearer_auth: BearerAuth, language: str = 'de') -> dict:
    response = requests.get(url=f"{LANG_ENDPOINT}/{language}", auth=bearer_auth)
    return json.loads(response.content)

def get_chats(bearer_auth: BearerAuth, search_params: dict = None):
    search_params = search_params if search_params else {}
    response = requests.post(url=SEARCH_ENDPOINT, json=search_params, auth=bearer_auth)
    results = response.json()['result']
    chat_ids = [r['public_code'] for r in results]
    chats = []

    for chat_id in chat_ids:
        response = requests.get(url=f"{CHAT_ENDPOINT}/{chat_id}", auth=bearer_auth)
        chat_results = response.json()['meta']
        chats.append(chat_results)

    return chats

def parse_attribute(attribute_value, lang_keys: dict):
    try:
        jsonpath_expr = jsonpath_ng.parse(attribute_value)
        match = jsonpath_expr.find(lang_keys)[0].value
        return match
    except Exception:
        return attribute_value

def update_csv(bearer_auth: BearerAuth, filenames: list[str], attributes: list[str], inplace: bool):
    p_id_key = '_id'
    all_headers = []
    participants_per_file = []
    ids = []

    for filename in filenames:
        header, content = read_csv(filename)
        all_headers.append(header)
        participants_per_file.append(content)
        ids.extend([c[p_id_key] for c in content])

    lang_keys = get_translations(bearer_auth)
    print('Downloading chats')
    chats = get_chats(bearer_auth)
    print('Downloaded chats')
    participants = {}

    for chat in chats:
        for participant in filter(lambda x: x[p_id_key] in ids, chat['participants']):
            participants[participant[p_id_key]] = participant

    print('Filtered chats')

    for filename, headers, file_participants in zip(filenames, all_headers, participants_per_file):
        print(f"Updating {filename}")
        updated_filename = f"{filename.rsplit('.', 1)[0]}_updated.csv" if not inplace else filename
        data=[]
        for file_participant in file_participants:
            participant_data = file_participant.copy()
            participant = participants[file_participant[p_id_key]]
            for attribute in attributes:
                try:
                    attribute_value = participant[attribute]
                except KeyError:
                    attribute_value = None
                parsed_attribute = None

                if isinstance(attribute_value, list):
                    parsed_attribute = [parse_attribute(a, lang_keys) for a in attribute_value]
                elif attribute_value:
                    parsed_attribute = parse_attribute(attribute_value, lang_keys)

                participant_data[attribute] = parsed_attribute

            data.append(participant_data)

        updated_headers = headers.copy()
        updated_headers.extend(attributes)
        write_to_csv(updated_filename, data, updated_headers)

        print(f"Wrote updated participants to {updated_filename}")

def download_messages(age_groups: list, max_participants: int,
                      min_messages: int, max_messages: int, bearer_auth: BearerAuth):
    search_params = {
        "meta.participants.age": {
            "$in": age_groups
        }
    }

    print('Search options: ')
    pprint(search_params)

    chats = get_chats(bearer_auth, search_params)

    print(f"Found {len(chats)} chats")

    total_participants = []
    for chat in chats:
        chat_participants = chat['participants']
        chat_messages = chat['messages']

        total_participants.append(
            get_participants_with_messages(chat_participants, chat_messages, age_groups)
        )

    participants = merge_participants([p for p_list in total_participants for p in p_list])

    print(f"Found {len(participants)} participants with total {sum([len(p.messages) for p in participants])} messages")

    max_participants = min(len(participants), max_participants)

    filtered_participants = filter_participants(participants, age_groups, max_participants,
                                                max_messages, min_messages)

    messages_average = sum([
        len(p.messages) for p in filtered_participants
    ]) / len(filtered_participants)

    filename = f"mocoda2_aged_{age_groups}_participants_{len(filtered_participants)}_messages_{int(messages_average)}.csv"

    write_to_csv(filename, data=[dataclasses.asdict(p) for p in filtered_participants],
                 headers=[field.name for field in dataclasses.fields(Participant)])

    print(f"Wrote {len(filtered_participants)} participants with {int(messages_average)} messages on average to {filename}")

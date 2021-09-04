import argparse
from csv import DictWriter
import dataclasses
import getpass
from pprint import pprint
import requests
import sys

from mocoda2.utils import (
    BearerAuth,
    get_participants_with_messages,
    merge_participants,
    filter_participants,
    Participant
)


LOGIN_ENDPOINT = 'https://db.mocoda2.de/api/auth/login'
SEARCH_ENDPOINT = 'https://db.mocoda2.de/api/conversation/search'
CHAT_ENDPOINT = 'https://db.mocoda2.de/api/conversation/view'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--username', type=str, required=True)
    parser.add_argument('--max-messages', type=int, default=10,
                        help='Max number of messages per chat participant')
    parser.add_argument('--min-messages', type=int, default=10,
                        help='Min number of messages per chat participant')
    parser.add_argument('-p', '--max-participants', type=int, default=20,
                        help='Max number of participants')
    parser.add_argument('--age-groups', type=str, default='')
    args = parser.parse_args()

    age_groups = args.age_groups.replace('-', ' - ').split(',')
    search_params = {
        "meta.participants.age": {
            "$in": age_groups
        }
    }

    print('Search options: ')
    pprint(search_params)

    password = getpass.getpass()

    response = requests.post(url=LOGIN_ENDPOINT,
                             json={'username': args.username, 'password': password})
    try:
        bearer_auth = BearerAuth(response.json()['accessToken'])
    except KeyError:
        sys.exit('Password or username invalid')

    response = requests.post(url=SEARCH_ENDPOINT, json=search_params, auth=bearer_auth)
    results = response.json()['result']
    chat_ids = [r['public_code'] for r in results]

    print(f"Found {len(chat_ids)} chats")

    total_participants = []
    for chat_id in chat_ids:
        response = requests.get(url=f"{CHAT_ENDPOINT}/{chat_id}", auth=bearer_auth)
        chat_results = response.json()['meta']
        chat_participants = chat_results['participants']
        chat_messages = chat_results['messages']

        total_participants.append(get_participants_with_messages(chat_participants, chat_messages, age_groups))

    participants = merge_participants([p for p_list in total_participants for p in p_list])

    print(f"Found {len(participants)} participants with total {sum([len(p.messages) for p in participants])} messages")

    max_participants = min(len(participants), args.max_participants)

    filtered_participants = filter_participants(participants, age_groups, max_participants,
                                                args.max_messages, args.min_messages)

    messages_average = sum([
        len(p.messages) for p in filtered_participants
    ]) / len(filtered_participants)

    filename = f"mocoda2_aged_{args.age_groups}_participants_{len(filtered_participants)}_messages_{int(messages_average)}.csv"

    with open(filename, 'w') as csv_file:
        fieldnames = [field.name for field in dataclasses.fields(Participant)]
        writer = DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows([dataclasses.asdict(p) for p in filtered_participants])

    print(f"Wrote {len(filtered_participants)} participants with {int(messages_average)} messages on average to {filename}")


if __name__ == "__main__":
    main()
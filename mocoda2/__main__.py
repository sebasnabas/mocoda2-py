import argparse
import getpass
import os
import sys

from mocoda2.utils import login
from mocoda2.actions import (
    download_messages,
    update_csv
)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--username', type=str, required=True)
    subparsers = parser.add_subparsers(dest='action', help='action help', required=True)

    download_parser = subparsers.add_parser('download')
    download_parser.add_argument('--max-messages', type=int, default=10,
                        help='Max number of messages per chat participant')
    download_parser.add_argument('--min-messages', type=int, default=10,
                        help='Min number of messages per chat participant')
    download_parser.add_argument('-p', '--max-participants', type=int, default=20,
                        help='Max number of participants')
    download_parser.add_argument('--age-groups', type=str, default='')

    update_parser = subparsers.add_parser('update')
    update_parser.add_argument('filenames', type=str, nargs='+')
    update_parser.add_argument('-a', '--attribute', action='extend', nargs='+',
                               choices=['motherlanguage', 'language', 'name', 'first', 'last'
                                        'age', 'city', 'education', 'gender', 'job',
                                        'participant_active'],
                               type=str, required=True)

    args = parser.parse_args()
    password = os.getenv('MOCODA2_PASSWORD')

    if not password:
        password = getpass.getpass()

    try:
        bearer_auth = login(args.username, password)
    except ValueError as error:
        sys.exit(error)

    if args.action == 'download':
        age_groups = args.age_groups.replace('-', ' - ').split(',')
        download_messages(age_groups,  args.max_participants, args.min_messages, args.max_messages,
                          bearer_auth)

    elif args.action == 'update':
        update_csv(bearer_auth, args.filenames, args.attribute)


if __name__ == "__main__":
    main()

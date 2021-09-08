import argparse
import csv
import ast
import re

from tabulate import tabulate


EMOJI_PATTERN = re.compile(
    "["
    "\U0001F1E0-\U0001F1FF"  # flags (iOS)
    "\U0001F300-\U0001F5FF"  # symbols & pictographs
    "\U0001F600-\U0001F64F"  # emoticons
    "\U0001F680-\U0001F6FF"  # transport & map symbols
    "\U0001F700-\U0001F77F"  # alchemical symbols
    "\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
    "\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
    "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
    "\U0001FA00-\U0001FA6F"  # Chess Symbols
    "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
    "\U00002702-\U000027B0"  # Dingbats
    "\U000024C2-\U0001F251"
    "]+"
)
def get_average_message_length(messages: list[str]):
    return sum([len(message) for message in messages]) / len(messages)

def get_median_message_length(messages: list[str]):
    return sorted([len(message) for message in messages])[int(len(messages) / 2)]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('file', type=str, help='CSV file to analyze')
    args = parser.parse_args()

    table_headers = ['name', 'average message length', 'median message length',
                        'average message length (without emojis)', 'median message length (without emojis)']
    fieldnames = []

    csv_data = []

    with open(args.file, newline='') as csv_file:
        reader = csv.DictReader(csv_file)
        fieldnames = reader.fieldnames
        data = []
        for row in reader:
            csv_row = row.copy()
            data_row = []
            data_row.append(row['name'])
            parsed_messages = row['messages']
            messages = ast.literal_eval(parsed_messages)
            messages_without_emojis = [re.sub(EMOJI_PATTERN, '', message) for message in messages]

            data_row.append(get_average_message_length(messages))
            data_row.append(get_median_message_length(messages))
            data_row.append(get_average_message_length(messages_without_emojis))
            data_row.append(get_median_message_length(messages_without_emojis))

            for field, value in zip(table_headers, data_row):
                csv_row[field] = value

            data.append(data_row)
            csv_data.append(csv_row)

        print(tabulate(data, headers=table_headers))

    fieldnames = set(fieldnames + table_headers)

    with open(args.file, 'w', newline='') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(csv_data)




if __name__ == "__main__":
    main()

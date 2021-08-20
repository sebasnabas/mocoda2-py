import dataclasses
import random
import requests

class BearerAuth(requests.auth.AuthBase):
    def __init__(self, token):
        self.token = token
    def __call__(self, r):
        r.headers["authorization"] = "Bearer " + self.token
        return r

@dataclasses.dataclass(frozen=True)
class Participant:
    name: str
    age_group: str
    _id: str = dataclasses.field(compare=True)
    messages: list[str] = dataclasses.field(default_factory=list)

    def __hash__(self):
        return hash(self._id)

def get_participants_with_messages(chat_participants: list[dict], chat_messages: list[dict], age_groups: list[str]):
    participants = []

    for participant in chat_participants:
        p_id = participant['_id']

        if not 'age' in participant.keys() or (p_age := participant['age'][0]) not in age_groups:
            continue

        participants.append(
            Participant(
                _id=p_id,
                age_group=p_age,
                name=participant['name'],
                messages=[
                    message['text_pseudo']
                    for message in filter(
                        lambda m: m['type'] != 'file' and \
                            'participant' in m.keys() and \
                            m['participant'] == p_id,
                        chat_messages
                    )
                ]
            )
        )
    return participants

def merge_participants(total_participants: list[Participant]):
    participants = []

    for i, participant in enumerate(total_participants):
        if participant._id in [p._id for p in participants]:
            continue
        for j in range(i + 1, len(total_participants)):
            second_p = total_participants[j]
            if participant._id != second_p._id:
                continue
            participant.messages.extend(second_p.messages)
        participants.append(participant)

    return participants

def filter_participants(participants: list[Participant], age_groups: list[str],
                        max_participants: int, max_messages: int, min_messages: int):
    distinct_participants = set(participants)
    filtered_participants = []

    for participant in distinct_participants:
        messages = list(set(participant.messages))
        if len(messages) < min_messages or participant.age_group not in age_groups:
            continue

        filtered_participants.append(
            Participant(
                name=participant.name,
                _id=participant._id,
                age_group=participant.age_group,
                messages=random.choices(messages,
                    k=min(len(messages), max_messages)
                )
            )
        )

    return random.sample(filtered_participants, min(len(filtered_participants), max_participants))

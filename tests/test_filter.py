import unittest
from mocoda2.utils import Participant, filter_participants


class TestFilterCase(unittest.TestCase):
    def test_filter(self):
        participants = [
            Participant(
                name='John',
                _id='5bf52e1f59d87c000b776013',
                age_group='26 - 30',
                messages=['😂😂😂😂😂']
            ),
            Participant(
                name='John',
                _id='5bf52e1f59d87c000b776013',
                age_group='26 - 30',
                messages=['😂😂😂😂😂']
            ),
            Participant(
                name='Salz',
                _id='5cb6cf7b2e2b21000b5e4602',
                age_group='51 - 55',
                messages=['Hey ho']
            ),
            Participant(
                name='Salz',
                _id='5cb6cf7b2e2b21000b5e4602',
                age_group='51 - 55',
                messages=['Hey ho']
            ),
            Participant(
                name='Mehl',
                _id='5cb6cf7b2e2b21000b5e5713',
                age_group='21 - 25',
                messages=['Du wieder...']
            ),
            Participant(
                name='Zucker',
                _id='5cb6cf7b2e2b21000b5e5702',
                age_group='56 - 60',
                messages=['Lala']
            )
        ]

        filtered_participants = filter_participants(participants, ['51 - 55', '56 - 60'], 10, 10)

        expected_participants = [
            Participant(
                name='Salz',
                _id='5cb6cf7b2e2b21000b5e4602',
                age_group='51 - 55',
                messages=['Hey ho']
            ),
            Participant(
                name='Zucker',
                _id='5cb6cf7b2e2b21000b5e5702',
                age_group='56 - 60',
                messages=['Lala']
            )
        ]

        self.assertEqual(len(filtered_participants), 2)
        self.assertEqual(filtered_participants[0], expected_participants[0])
        self.assertEqual(filtered_participants[1], expected_participants[1])

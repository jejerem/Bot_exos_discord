from functions import delete_spaces_from_list
from private_files.private_constants import *
from shared.constants import *
from shared.context_actions import ContextActions


class UserArguments:
    def __init__(self):
        self.dic_arguments = {}
        self.dic_subjects_topics = {}

    async def store_year(self, year):
        """Check and store 1 <= year <= 3"""
        # Object related to the author of the request.
        author_object = ContextActions.author_object

        # If last info is digit then it's year
        if len([char for char in year if year == DIGITS]) == len(year):
            year = int(year) if 1 <= int(year) <= 3 else 0

        else:
            year = 0

        # default year
        if year == 0:
            # We browse author's roles to find degree role.
            for author_role in author_object.roles:
                # We found the year role => the user is in the license.
                if author_role.id == YEAR_ROLE_ID:
                    # Year's position in the role's name ("L1", "L2," "L3").
                    year = int(author_role.name[1])
                # If the author is a moderator.
                elif author_role.id == MODERATOR_ROLE_ID:
                    pass

        # Year is not specified and has not been found in roles.
        if year == 0:
            await ContextActions.send_mention_message("you are not in the license anymore"
                                                      f"so you must specify a year as first information.")
            return -1

        self.dic_arguments["year"] = year
        self.dic_subjects_topics = L1_SUBJECTS_TOPICS if year == 1 else L2_SUBJECTS_TOPICS if year == 2 \
            else L3_SUBJECTS_TOPICS

    async def store_difficulty(self, difficulty):
        """Check and stores in the dictionary 0 <= difficulty <= 5."""

        if len([char for char in difficulty if char in DIGITS]) != len(difficulty):
            await ContextActions.send_mention_message("difficulty must be 0 <= difficulty <= 5")

        difficulty = int(difficulty)

        # Difficulty given > 5.
        if difficulty > 5:
            await ContextActions.send_mention_message("maximum difficulty is 5.\n"
                                                      f"We all know you are smart af stop showing off.")
            difficulty = 5

        # Difficulty given < 0.
        elif difficulty < 0:
            await ContextActions.send_mention_message("minimum difficulty is 0.\n"
                                                      f"Come on don't underestimate yourself.)")

            difficulty = 0

        self.dic_arguments["difficulty"] = difficulty

    async def store_nearest_content_type(self, user_content_type):
        """get nearest content type from user content type and stores it in the dic."""

        if user_content_type[0] == "d" or user_content_type[0] == "t":
            nearest_content_type = "tests"
        else:
            nearest_content_type = "exercises"

        self.dic_arguments["content_type"] = nearest_content_type

    async def store_nearest_subject(self, user_subject):
        """get nearest subject from user subject and stores it in the dic."""

        year = self.dic_arguments["year"]
        # We create a variable to consider the good dictionary variable according to the year.

        # The program will take the subject which is the closest to the subject_name variable.
        first_subject_letters = user_subject[:2]
        nearest_subject = ""

        # We browse the dictionary by diminishing length of shortened subject names.
        for short, subject, in sorted(DIC_SHORT_SUBJECTS.items(), key=lambda x: -len(x[0])):
            if first_subject_letters[:len(short)] == short:
                nearest_subject = subject
                break

        if len(nearest_subject) == 0:
            await ContextActions.send_mention_message("Please enter a valid subject name.")
            return

        self.dic_arguments["subject"] = nearest_subject

    async def store_nearest_topic(self, user_topic):
        """get nearest topic from user topic and stores it in the dic."""

        nearest_subject = self.dic_arguments["subject"]
        current_topics = self.dic_subjects_topics[nearest_subject]

        # It's the chapter's number because the variable topic_user only contains digits.
        if len([char for char in user_topic if char in DIGITS]) == len(user_topic):
            topic_index = int(user_topic) - 1

            if len(current_topics) <= topic_index or topic_index <= -1:
                await ContextActions.send_mention_message("Please enter a positive integer.\n"
                                                          f"And don't forget you're not a computer you begin to count "
                                                          f"from 1.")
                return

            nearest_topic = current_topics[topic_index]

        else:
            topics_match = [topic for topic in current_topics if user_topic in topic]

            if len(topics_match) == 0:
                await ContextActions.send_mention_message("Please enter a valid topic.")

            nearest_topic = topics_match[0]

        self.dic_arguments["topic"] = nearest_topic

    async def store_arguments(self, info):
        list_user_path = delete_spaces_from_list(info.split("/"))

        # Filename is included
        if len(list_user_path) == 5:
            user_subject, user_topic, user_content_type, user_filename\
                = list_user_path[0], list_user_path[1], list_user_path[2], list_user_path[-1]
            self.dic_arguments["filename"] = user_filename
        # Filename is not included
        if len(list_user_path) == 4:
            user_subject, user_topic, user_content_type \
                = list_user_path[0], list_user_path[1], list_user_path[2]
        # Wrong info argument : we warn the user about it.
        else:
            await ContextActions.send_mention_message("invalid command please see help command for more information")
            return

        user_difficulty = list_user_path[3]
        # We parse and store all the arguments.
        await self.store_difficulty(user_difficulty)
        await self.store_nearest_subject(user_subject)
        await self.store_nearest_topic(user_topic)
        await self.store_nearest_content_type(user_content_type)

    def get_firestore_path(self):
        """All the arguments must already be stored in the dictionary before c  alling it."""

        firestore_path = f"degrees/" \
                         f"l{self.dic_arguments['year']}/" \
                         f"{self.dic_arguments['subject']}/" \
                         f"files/" \
                         f"{self.dic_arguments['content_type']}" \


        return firestore_path

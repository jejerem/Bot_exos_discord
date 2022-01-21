import asyncio
import io
import random
import aiohttp
import firebase_admin
from firebase_admin import firestore, credentials

from shared.discord_related.context_actions import ContextActions


class FirestoreStorage:

    def __init__(self, storage, db):
        self.storage = storage
        self.db = db

    async def add_attachment_storage_db(self, firestore_path, attachment, **data):
        """ This function is meant to post attachments in the storage and to store
        the infos which define them more accurately in firestore database.

        - Each path doesn't include filename.
        - The variable db is a web API for firestore.
        - The variable storage is a web API for storage.
        - data variable (dict with key parameters):
            - topic related to the document (chapter or notion) must be in the tuple of topics.
            - difficulty :  1 <= difficulty <= 5. Default value = 0 (in case we don't consider it for the current file).
        """

        # We browse path, attachments in order to store them in the database one by one.
        filename = attachment.filename

        if attachment.content_type != "application/pdf" or attachment.size >= 1e6:
            # ctx.send() giving tips with pictures for example
            return

        refs = self.db.collection(firestore_path).where("id", "==", filename).get()

        # We consider that in one folder there can't be two resources with same id
        if len(refs) > 0:
            await ContextActions.send_mention_message("error : filename already existing.")
            return

        elif not 1 <= data["difficulty"] <= 5:
            await ContextActions.send_mention_message("error : 1 <= difficulty <= 5")
            return

        # Now we are sure we have correct information about the file.
        file_data = await attachment.read()

        # Last string of the path will be interpreted as the filename.
        storage_path = f"{firestore_path}/{filename}"
        self.storage.child(storage_path).put(file_data)

        # We add the document in the firestore db with its name as id.
        self.db.collection(firestore_path).document(filename).set(
            {"storage_path": firestore_path, "topic": data["topic"],
             "difficulty": data["difficulty"]})

    # just for me
    def add_file_storage_db(self, path: str, **data):
        """ This function is meant to post a file in the storage and to store
        the infos which define it more accurately in firestore database.

        - The variable path includes new file's name.
        - The variable db is a web interface with firestore.
        - The variable storage is a web interface with storage.
        - data variable (dict with key parameters):
            - topic related to the document (chapter or notion) must be in the tuple of topics.
            - difficulty :  0 <= difficulty <= 5. Default value = 0 (in case we don't consider it for the current file).
        """

        if "file_object" in data:
            file = data["file_object"]

        else:
            file = path.split("/")[-1]

        collection_path = "/".join(path.split("/")[:-1])

        refs = self.db.collection(collection_path).where("id", "==", file).get()

        # We consider that in one folder there can't be two ressources with same id
        if len(refs) > 0:
            ContextActions.send_mention_message("a file under this name in this folder is already existing.")

        # We check what's in key parameters.
        if "topic" not in data:
            ContextActions.send_mention_message(f"please specify a topic for {file}.")

        # If difficulty is not specified we affect 1, the default value, to the variable.
        if "difficulty" not in data:
            data["difficulty"] = 1

        # Last name of path will be interpreted as the file's name.
        self.storage.child(path).put(file)

        # We add the document in the firestore db with its name as id.
        self.db.collection(collection_path).document(file).set({"storage_path": path, "topic": data["topic"],
                                                                "difficulty": data["difficulty"]})

    def del_file_storage_db(self, firestore_path: str, filename):
        """ This function deletes the file entered in parameter both in the storage
        and the firestore db.

        - The variable path includes file's variable"""

        refs = self.db.collection(firestore_path).where("id", "==", filename).get()

        # We consider that in one folder there can't be two ressources with same id
        if len(refs) > 1:
            ContextActions.send_mention_message("Two files with same name were found")
            ContextActions.send_warning("Two files with same id in the same folder were found !")
            return

        elif len(refs) == 0:
            ContextActions.send_mention_message("File not found.")
            return

        # Delete file from storage.
        storage_path = f"{firestore_path}/{filename}"
        self.storage.delete(storage_path, None)

        # Delete document from firestore.
        self.db.collection(firestore_path).document(refs[0].id).delete()

    async def choose_get_file(self, firestore_path, topic, difficulty, filename=""):
        if difficulty == 0:
            query_difficulty = self.db.collection(firestore_path).where("difficulty", ">=", 0)
        else:
            query_difficulty = \
                self.db.collection(firestore_path).where("difficulty", "==", difficulty)

        query_topic = query_difficulty.where("topic", "==", topic)

        if filename != "":
            list_refs = query_topic.where(filename, "in", "id").get()
        else:
            list_refs = query_topic.get()

        if len(list_refs) == 0:
            # No files for the queries we warn the user and get out of the function.
            asyncio.create_task(ContextActions.send_mention_message("sorry but I didn't find any files matching with your query :'(."
                                                      "You can still add files if you want with !add command."))
            return

        ref_choice = random.choice(list_refs)
        filename = ref_choice.id
        url = self.storage.child(f"{ref_choice.to_dict()['storage_path']}/{filename}").get_url(None)
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    return -1
                data = io.BytesIO(await resp.read())
                return data, filename


if __name__ == "__main__":
    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    ref_choice = db.collection("degrees/l1/mathematics/files/exercise").where("difficulty", ">=", 0).where("topic",
                                                                                                           "==",
                                                                                                           "topic").get()

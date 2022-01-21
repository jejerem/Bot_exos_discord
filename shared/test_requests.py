import pyrebase
import firebase_admin
from firebase_admin import firestore
from firebase_admin import credentials
from shared.firebase_storage_db import FirestoreStorage
from private_files.private_constants import *
from shared.constants import *

# We first initialize the Cloud.
cred = credentials.Certificate("private_files/serviceAccountKey.json")
firebase_admin.initialize_app(cred)

# Then we initialize the storage part.
firebase_config = {FIREBASE_CONFIG}

firebase = pyrebase.initialize_app(firebase_config)

db = firestore.client()
storage = firebase.storage()

firestore_storage = FirestoreStorage(storage, db)

#firestore_storage.add_file_storage_db("degrees/l1/maths/files/exercises/td1_calculs_2021.pdf", topic="calcul algebrique")


"""ref = db.collection("degrees/l1/maths/files/exercises").where("storage_path", ">", "").get()[0]
print(f"Link retrieved : {storage.child(ref.to_dict()['storage_path']).get_url(None)}")"""

# To create the whole structure of the db.
"""for i in range(1, 4):
    db.collection("degrees").document(f"l{i}").set({})"""

"""db.collection("degrees").document(f"l1").set({})
for subject in L1_SUBJECTS_TOPICS:
    db.collection("degrees").document(f"l1").collection(f"{subject}").document("files").set({})
    db.document(f"degrees/l1/{subject}/files").collection("exercises").add({})
    db.document(f"degrees/l1/{subject}/files").collection("tests").add({})"""

# url = storage.child(ref.to_dict()["ds2"])
# print(url.get_url(None))


"""for s in L1_SUBJECTS_TOPICS:
    storage.child("degrees").child(f"l1/{s}").put(None)"""

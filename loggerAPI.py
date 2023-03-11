import openai
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import auth
import requests
import os, random, string, time

openai.api_key = os.environ['OPEN_AI_KEY']

def delete_old_file(name):
    #Deleting the specfic file from ElasticSearch using Haystack API
    url = 'http://44.203.174.37:8000/documents/delete_by_filters'
    headers = {'accept': 'application/json', 'Content-Type': 'application/json'}

    data = {'filters': { "name":["{}.txt".format(name)] }}

    response = requests.post(url, headers=headers, json=data)

    return response.json()


def add_new_file(name):
    #Adding new file to ElasticSearch using Haystack API
    url = 'http://44.203.174.37:8000/file-upload'
    headers = {'accept': 'application/json'}

    file = open('{}.txt'.format(name), 'rb')
    files = {'files': ('{}.txt'.format(name), file, 'text/plain')}
    data = {
    'split_overlap': '',
    'meta': 'null',
    'split_respect_sentence_boundary': '',
    'split_length': '',
    'remove_numeric_tables': '',
    'clean_whitespace': '',
    'clean_header_footer': '',
    'clean_empty_lines': '',
    'valid_languages': '',
    'split_by': '' }
    
    response = requests.post(url, headers=headers, data=data, files=files)

    file.close()
    
    os.remove("{}.txt".format(name))
    return response.json()


def to_gpt(query,context):
   
    responsex=openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are a helpful virtual assistant for senior citizens. \
         You are going answer any query based on the query and context provided to you. \
          If there is no context and the question is about something that can be stored in the app, tell user to add it using voice note feature\
            If there is no context and it is a general question, just answer it normally\
          Context: {}".format(context)},
        {"role": "user", "content": f"{query}"},
    ]
)
    #have to return content under choice only
    return responsex['choices'][0]['message']['content']

def extract_content(data):
    content_str = ""
    for doc in data['documents']:
        content_str += doc['content'] + '\n'
    return content_str.strip()


def get_highest_score_content(input_dict):
    max_score = max(answer["score"] for answer in input_dict["documents"])
    
    highest_score_doc = next((doc for doc in input_dict["documents"] if doc["score"] == max_score), None)

    return highest_score_doc["content"] if highest_score_doc else None

def query_response(x):
    query=x.input
    #Querying the ElasticSearch using Haystack API
    url = 'http://44.203.174.37:8000/query'
    headers = {'accept': 'application/json', 'Content-Type': 'application/json'}
    data = {'query': query, 'params':{},'debug':False}
    response=requests.post(url, headers=headers, json=data)
    content=response.json()
    if len(content['documents'])==0:
        return to_gpt(query,None) #No Context
    context=extract_content(content)
    return to_gpt(query,context)
# print(query_response("What medicies were prescribed for Anomitro?"))

def generate_random_string(length):
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for _ in range(length))


def generate_file(info):
    text = info.input
    name = generate_random_string(10)
    file_path = f"{name}.txt"
    with open(file_path, "w") as f:
        f.write(text)

    add_new_file(name)
    
    print(f"File {name}.txt removed successfully!")


def generate_medication_file(med_dict, name, user_id):
    filename = name.replace(" ","") + "_medLog"

    with open(f"{filename}.txt", "w") as f:
        f.write(f"Patient Name: {name}\n")
        f.write("Medicines for the week:\n\n")
        for day, meds in med_dict[user_id]["medLog"].items():
            f.write(f"{day.capitalize()}: ")
            if meds:
                med_info = [f"{med['Name']} - Dosage:{med['Dosage']} - When:{med['When']} - Frequency:{med['Frequency']}" for med in meds]
                f.write(", ".join(med_info))
            else:
                f.write("None")
            f.write("\n")
    
    
def init_firebase():
    #Initializes Firebase connection and sets the database up
    cred_obj = firebase_admin.credentials.Certificate('./fbaseAccountKey.json')
    default_app = firebase_admin.initialize_app(cred_obj, {'databaseURL':'https://testapi-15563-default-rtdb.firebaseio.com/'})
    ref = db.reference('/')
    data ={"USERNAME": struct }
    ref.set(data)

    #Creating test user
    # user = auth.create_user(uid='uid2', email='user2@example.com', phone_number='+12675671818', display_name='Jason Derulo')
    return ref


class MedicineLog(BaseModel):
    user_id: str
    name: str
    when: str
    dosage: str
    weekly: list
    freq: int

def logMedsToFirebase(item: MedicineLog):
    #Logs the data to firebase
    weekly_schedule = item.weekly
    user_id = item.user_id

    medData = ref.get()
    #only called once in the first run
    if not medData:
        medData = { user_id : struct }
    
    if user_id not in medData.keys():
        medData[user_id] = struct
    # print(medData)
    
    medDetails = {"Name": item.name, "Dosage": item.dosage, "When": item.when, "Frequency": item.freq}

    for day in weekly_schedule:
        day_details = ref.child(user_id).child("medLog").child(day).get()

        if not day_details:
            day_details = []
        
        day_details.append(medDetails)
        ref.child(user_id).child("medLog").child(day).set(day_details)
        
        if day not in medData[user_id]["medLog"].keys():
            medData[user_id]["medLog"][day] = []
        medData[user_id]["medLog"][day].append(medDetails)

    # print(medData)

    return medData
   


def logMedsToElastic(user_id, medLogDict):
    #Logs the data to Elastic Search
    #Have to delete old medLog file and add new one
    user = auth.get_user(user_id)
    patient_name = user.display_name
    generate_medication_file(medLogDict, patient_name, user_id)

    filename = patient_name.replace(" ","") + "_medLog"
    delete_old_file(filename)
    add_new_file(filename)

#struct
struct = { "medLog" : {
      "MON": [],
      "TUE": [],
      "WED": [],
      "THU": [],
      "FRI": [],
      "SAT": [],
      "SUN": []
    }
}






app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ref = init_firebase()

@app.get("/")
def root():
    return {"Goldy Wrapper API" : 'homepage'}

class StrInput(BaseModel):
    input : str
    
@app.get("/get-data-by-day/{day}")
def get_data_by_day(day: str, user_id: StrInput):
    weekly_plan = ref.child(user_id.input).child("medLog").get()
    for key in weekly_plan.keys():
        if key == day:
            return weekly_plan[key]
        

@app.get("/get-data")
def get_data(user_id : StrInput):
    weekly_plan = ref.child(user_id.input).child("medLog").get()
    return weekly_plan


@app.post("/log-med")
def log_med(item: MedicineLog):
    medData = logMedsToFirebase(item)
    user_id = item.user_id
    logMedsToElastic(user_id, medData)

@app.post("/recall-chat")
def recall_chat(query: StrInput):
    return query_response(query)

@app.post("/voice-note")
def voice_note(info : StrInput):
    generate_file(info)
     








    

    
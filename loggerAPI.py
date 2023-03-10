from fastapi import FastAPI
from pydantic import BaseModel
import json
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import requests


def delete_old_file(name):
    url = 'http://44.203.174.37:8000/documents/delete_by_filters'
    headers = {'accept': 'application/json', 'Content-Type': 'application/json'}

    data = {'filters': { "name":["{}.txt".format(name)] }}

    response = requests.post(url, headers=headers, json=data)

    print(response.json())


def add_new_file(name):
    url = 'http://44.203.174.37:8000/file-upload'
    headers = {'accept': 'application/json'}

    files = {'files': ('{}.txt'.format(name), open('{}.txt'.format(name), 'rb'), 'text/plain')}
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
    print(response.json())

  
def json_to_text(dictionary, name):
    #INCOMPLETE, DON'T KNOW THE FORMATTING TO SEND TO HAYSTACK

    with open('{}.txt'.format(name),'w') as data:
        data.write(str(dictionary))
    
    
def init_firebase(data):
    cred_obj = firebase_admin.credentials.Certificate('./fbaseAccountKey.json')
    default_app = firebase_admin.initialize_app(cred_obj, {'databaseURL':'https://testapi-15563-default-rtdb.firebaseio.com/'})
    ref = db.reference('/')
    ref.set(data)

    return ref


class MedicineLog(BaseModel):
    name: str
    when: str
    dosage: str
    weekly: list
    freq: int

def log_to_firebase(item: MedicineLog):
    weekly_schedule = item.weekly

    medDetails = {"Name": item.name, "Dosage": item.dosage, "When": item.when, "Frequency": item.freq}

    for day in weekly_schedule:
        day_details = ref.child("medLog").child(day).get()

        if not day_details:
            day_details = []
        
        day_details.append(medDetails)
        ref.child("medLog").child(day).set(day_details)

        data["medLog"][day].append(medDetails)     
   

def log_to_elastic(name):
    json_to_text(data, name)
    delete_old_file(name)
    add_new_file(name)


data = {"medLog": 
        {
    "MON":[],
    "TUE":[],
    "WED":[],
    "THU":[],
    "FRI":[],
    "SAT":[],
    "SUN":[]
    }
}


app = FastAPI()
ref = init_firebase(data)

@app.get("/")
def root():
    return {"Data":"Hi this is a test."}


@app.get("/get-data-by-day/{day}")
def get_data_by_day(day: str):
    weekly_plan = ref.child("medLog").get()
    for key in weekly_plan.keys():
        if key == day:
            return weekly_plan[key]
        

@app.get("/get-data")
def get_data():
    weekly_plan = ref.child("medLog").get()
    return weekly_plan


@app.post("/log-data/{name}")
def log_data(name):
    log_to_elastic(name)


@app.post("/log-med")
def log_med(item: MedicineLog):
    log_to_firebase(item)
    log_to_elastic("medLog")






    

    
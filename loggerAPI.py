from fastapi import FastAPI
from pydantic import BaseModel
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import requests


def delete_old_file(name):
    #Deleting the specfic file from ElasticSearch using Haystack API
    url = 'http://44.203.174.37:8000/documents/delete_by_filters'
    headers = {'accept': 'application/json', 'Content-Type': 'application/json'}

    data = {'filters': { "name":["{}.txt".format(name)] }}

    response = requests.post(url, headers=headers, json=data)

    print(response.json())


def add_new_file(name):
    #Adding new file to ElasticSearch using Haystack API
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

  
def generate_medication_file(med_dict, name):
    # patient_name = input("Enter patient name: ")
    with open(f"{name}.txt", "w") as f:
        f.write(f"Patient Name: {name}\n")
        f.write("Medicines for the week:\n\n")
        for day, meds in med_dict["medLog"].items():
            f.write(f"{day.capitalize()}: ")
            if meds:
                med_info = [f"{med['Name']} - Dosage:{med['Dosage']} - When:{med['When']} - Frequency:{med['Frequency']}" for med in meds]
                f.write(", ".join(med_info))
            else:
                f.write("None")
            f.write("\n")
    
    
def init_firebase(data):
    #Initializes Firebase connection and sets the database up
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

def logMedsToFirebase(item: MedicineLog):
    #Logs the data to firebase
    weekly_schedule = item.weekly

    medData = ref.get()
    if not medData:
        medData = data
   
    

    medDetails = {"Name": item.name, "Dosage": item.dosage, "When": item.when, "Frequency": item.freq}

    for day in weekly_schedule:
        day_details = ref.child("medLog").child(day).get()

        if not day_details:
            day_details = []
        
        day_details.append(medDetails)
        ref.child("medLog").child(day).set(day_details)
        
        if day not in medData["medLog"].keys():
            medData["medLog"][day] = []
        medData["medLog"][day].append(medDetails)
        print(medData)


    return medData
   


def logMedsToElastic(name, medLogDict):
    #Logs the data to Elastic Search
    #Have to delete old medLog file and add new one
    generate_medication_file(medLogDict, name)
    delete_old_file(name)
    add_new_file(name)

def logDataToElastic(name):
    pass

#struct
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
    logDataToElastic(name)


@app.post("/log-med")
def log_med(item: MedicineLog):
    medData = logMedsToFirebase(item)
    user_id = "USER1" # have to edit for specific users from endpoint?? idk
    name_of_file = user_id + "_medLog"
    logMedsToElastic(name_of_file, medData)


@app.get("/med-query")
def medLog_query(query: str):
    #Query -> Firebase -> back to API
    #API -> GPT -> API -> Client
    pass
     








    

    
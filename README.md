
# AidaAPI

This repository contains the Aida Wrapper API, an essential component of the [Aida](https://devpost.com/software/aida-grbcfu) project built for Philly Codefest 2023. Aida is designed to support senior citizens in managing their healthcare needs through a virtual assistant. The API facilitates various functionalities to handle tasks such as medication logging, file management, and conversational AI. By integrating services like OpenAI, Firebase, and ElasticSearch, Aida ensures that users receive timely and context-aware assistance, making it a valuable tool in promoting independent living among the elderly.

## Features

- **Medication Logging**: Store and manage weekly medication schedules for users in Firebase and ElasticSearch.
- **Conversational AI**: Leverage OpenAI's GPT model to answer user queries and provide context-aware responses.
- **Voice Note Processing**: Convert user voice notes into text files and store them in ElasticSearch.
- **Firebase Integration**: Securely store user data and medication logs in Firebase Realtime Database.
- **ElasticSearch Integration**: Efficiently manage and search through large sets of data using ElasticSearch.

## API Endpoints

- **GET** `/`  
  Root endpoint. Returns a welcome message.

- **GET** `/get-data/{user_id}`  
  Retrieves the weekly medication log for the specified user.

- **GET** `/get-data-by-day/{user_id}/{day}`  
  Retrieves the medication log for the specified user on a particular day.

- **POST** `/log-med`  
  Logs medication details for a user in Firebase and ElasticSearch.

- **POST** `/recall-chat`  
  Sends a query to the GPT-3 model and returns the response.

- **POST** `/voice-note`  
  Processes a voice note, converts it to text, and stores it in ElasticSearch.

- **POST** `/chat`  
  Processes a chatbot conversation based on the provided input and context.

## Technologies Used

- **Python**: Core programming language.
- **FastAPI**: Framework used to build the API.
- **Firebase**: Used for user management and storing medication logs.
- **ElasticSearch**: Used for storing and querying large sets of data.
- **OpenAI GPT-3.5**: Provides AI-driven responses for user queries.
- **Haystack API**: Utilized for interacting with ElasticSearch for document management.

## Acknowledgments

This API is part of the Aida project, which was developed to assist senior citizens in managing their health care and daily routines.

## Links

- [Aida Devpost](https://devpost.com/software/aida-grbcfu)

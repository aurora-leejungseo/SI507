# SI507


## Needed Python packages
Secret
Requests
Sqlite3
Flask
Plotly

## Demo Video
https://drive.google.com/file/d/1u_hEB65Eo6uofJYLEaZgKguCShawNB9J/view?usp=sharing

## Data source
####	Base URL: 
I used Web API, Yelp fusion, for this project. For more information, please refer to the description of this API via https://www.yelp.com/developers/documentation/v3/get_started.

#### Authentication
The API uses private key authentication to authenticate all endpoints. You can be provided your API Key with creating your app via the link. For this project, I have saved my authentication as a separate file, secret.py so the python file can access the data. 
For authenticating API calls with the API keys, the “Authorization HTTP” header value is “Bearer API_KEY”.


#### Interactive Presentation Design:
1.	Questions for users to answer for getting relevant data
The program or the website which is built asks a question to the users. According to the answer that the user gave, the relevant dataset will be generated from the API.

2.	Show the distribution of the categories and price range with a pie plot
Once the user types in “location” information, it will show the bar chart of the distribution of categories and price range of the restaurants

3.	Show the distribution of the ratings with a bar plot
it will show the bar chart of the distribution of ratings of the restaurants

4.	Open the website link 
Embed the link to the web browser and the user can open the website 

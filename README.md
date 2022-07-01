For this project to work, PubNub account is required.
1. Make the PubNub account using the following link https://www.pubnub.com/
2. After making an acoount open the Apps section and click on "Create New App" button
3. After creation of app successfully, provide the subscriber and publisher keys as SUBSCRIBE_KEY and PUBLISH_KEY in the KEY.py file in the root directory. Also provide UUID which is required.

The KEY.py file should look like this:
```
PUBLISH_KEY = "Your Publish Key"
SUBSCRIBE_KEY = "Your Subscribe Key"
UUID = "Any String"
```


**Activate the Virtual Environment**
***( In Windows )***
```
.\blockchain-env\Sripts\activate.bat
```

**Install all packages**
```
pip install -r requirements.txt
```

**Run the Tests**
(Make sure the virtual environment is activated.)
```
python -m pytest backend/tests
```
**Run the Application and API**
(Make sure the virtual environment is activated.)
```
python -m backend.app
```
**Run a peer instance**
(Make sure the virtual environment is activated.)
```
python -m backend.app PEER=True
```
**Run the Frontend**
```
cd .\frontend
npm run start
```
**SEED the backend with data**
(Make sure the virtual environment is activated.)
```
python -m backend.app SEED=True
```

**Activate the Virtual Environment**
***In Windows***
```
.\blockchain-env\Sripts\activate.bat
```

**Install all packages**
```
pip install -r requirements.txt
```

**Run the Tests**
Make sure the virtual environment is activated.
```
python -m pytest backend/tests
```
**Run the Application and API**
Make sure the activate the virtual environment
```
python -m backend.app
```
**Run a peer instance**
Make sure the activate the virtual environment
```
python -m backend.app PEER=True
```
**Run the Frontend**
```
cd .\frontend
npm run start
```
**SEED the backend with data**
Make sure the activate the virtual environment
```
python -m backend.app SEED=True
```
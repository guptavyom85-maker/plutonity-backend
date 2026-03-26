from fastapi import FastAPI
# from app/schemas.py import 
app = FastAPI()

@app.get('/')
def root():
    return {'message': 'Plutonity backend is alive'}

@app.get('/leaderboard')
def root():
    return {}

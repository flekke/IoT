from fastapi import FastAPI, Request, Body
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import os
import pandas as pd
from fastapi.responses import JSONResponse

app = FastAPI()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(BASE_DIR, "data", "data.txt")
FEEDBACK_FILE = os.path.join(BASE_DIR, "data", "feedback.txt")

class Feedback(BaseModel):
    temp: int
    hum: int

# 요청 에러 처리 핸들러 등록
@app.exception_handler(Exception)
async def validation_exception_handler(request: Request, exc: Exception):
    print("에러 발생:", exc)  # 터미널에 로그 찍기
    return JSONResponse(
        status_code=422,
        content={"detail": str(exc)},
    )

# static 폴더 연결
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

# 첫 화면 (index.html 전달)
@app.get("/", response_class=HTMLResponse)
def read_root():
    return FileResponse(os.path.join(BASE_DIR, "static", "index.html"))

# 최신 온습도 데이터 제공 API
@app.get("/latest")
def get_latest_data():
    if not os.path.exists(DATA_FILE):
        return {"error": "no data file."}

    with open(DATA_FILE, "r") as f:
        lines = f.readlines()

    if not lines:
        return {"error": "data is empty."}

    last = lines[-1].strip().split(',')
    return {
        "timestamp": last[0],
        "temp": float(last[1]),
        "hum": float(last[2])
    }

@app.get("/recommendation")
def get_recommendation():
    if not os.path.exists(DATA_FILE):
        return {"error": "no data file."}

    df = pd.read_csv(DATA_FILE, names=["timestamp", "temp", "hum"])
    avg_temp = df["temp"].mean()
    avg_hum = df["hum"].mean()

    temp_adjust = 0
    hum_adjust = 0

    if os.path.exists(FEEDBACK_FILE):
        with open(FEEDBACK_FILE, "r") as f:
            lines = f.readlines()[-5:]  # 최근 5개만 사용

        weight = [5,4,3,2,1]

        temp_feedbacks = []
        hum_feedbacks = []

        for line in lines:
            temp_fb, hum_fb = map(int, line.strip().split(','))
            temp_feedbacks.append(temp_fb)
            hum_feedbacks.append(hum_fb)

       #가중 이동 평균 계산 
        temp_adjust = sum(w * fb for w, fb in zip(weight[-len(temp_feedbacks):], temp_feedbacks)) / sum(weight[-len(temp_feedbacks):])
        hum_adjust = sum(w * fb for w, fb in zip(weight[-len(hum_feedbacks):], hum_feedbacks)) / sum(weight[-len(hum_feedbacks):])

    #평균값 + 피드백 반영값
    rec_temp = round(avg_temp + temp_adjust, 1)
    rec_hum = round(avg_hum + hum_adjust,1)

    return{
        "recommended_temp" : rec_temp,
        "recommended_hum" : rec_hum
    }
'''
@app.post("/feedback")
async def receive_feedback(request: Request):
    json_data = await request.json()
    print("받은 데이터:", json_data)
    return {"status": "received"}
'''
@app.post("/feedback")
def receive_feedback(feedback: Feedback = Body(...)):
    print("Received:", feedback.dict())
    with open(FEEDBACK_FILE, "a") as f:   # feedback.txt 파일 append 모드
        f.write(f"{feedback.temp},{feedback.hum}\n")  # 온도, 습도 같이 저장
    return {"status": "feedback saved"}

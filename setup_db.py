from fastapi import FastAPI, Depends, HTTPException, WebSocket
from sqlalchemy import create_engine, Column, Integer, String,ForeignKey
from typing import List, Dict
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, mapped_column, relationship
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from random import randint
from time import sleep
import json
import time
import asyncio


app = FastAPI()

origins = [
    "http://127.0.0.1",
    "http://localhost",
    "http://127.0.0.1:8000",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8080",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


DATABASE_URL = "sqlite:///./pics.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()



class Rect(Base):
    __tablename__ = "rects"
    id = mapped_column(Integer, primary_key=True)
    x=mapped_column(Integer)
    y=mapped_column(Integer)
    w=mapped_column(Integer)
    h=mapped_column(Integer)
    color=mapped_column(String(20))
    
    pic_id = mapped_column(Integer, ForeignKey('pics.id'))
    
class Pic(Base):
    __tablename__ = "pics"
    id = mapped_column(Integer, primary_key=True)
    rects = relationship('Rect', backref='pics')
    
    



Base.metadata.create_all(bind=engine)


def get_db():
	db = SessionLocal()
	try:
		yield db
	finally:
		db.close()


 
@app.post("/pics/")
async def create_pic(pic : List[Dict], db: Session = Depends(get_db)):
    
    p = Pic()
    for d in pic:
        r=Rect(x=int(d['x']),y=int(d['y']),w=int(d['w']),h=int(d['h']),color=d['color'])
        p.rects.append(r)
    
    db.add(p)
    db.commit()
    db.refresh(p)
    return p

@app.get("/pics/{pic_id}")
async def ret_pic(pic_id : int, db: Session = Depends(get_db)):
    err_type = randint(0,9)
    if err_type<2:
        sleep(3)
    elif err_type<4:
        raise HTTPException(status_code=500, detail="Random error")
    elif err_type<6:
        f = open('large_file.json')
        data = json.load(f)
        f.close()
        return data
    rects = db.query(Rect).filter(Rect.pic_id == pic_id).all()
    if rects is None:
        raise HTTPException(status_code=404, detail="Pic not found")
    ret=[]
    for r in rects:
        ret.append({"x":str(r.x),"y":str(r.y),"w":str(r.w),"h":str(r.h),"color":r.color})
    return ret

@app.get("/pics/")
async def ret_number_of_pics(db: Session = Depends(get_db)):
    return db.query(Pic).count()



@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, db: Session = Depends(get_db)):
    await websocket.accept()
    try:
        while True:
            m_id = db.query(Pic).count()
            resp=[]
            for i in range(m_id-2,m_id+1):
                rects = db.query(Rect).filter(Rect.pic_id == i).all()
                if rects is None:
                    raise HTTPException(status_code=404, detail="Pic not found")
                ret=[]
                for r in rects:
                    ret.append({"x":str(r.x),"y":str(r.y),"w":str(r.w),"h":str(r.h),"color":r.color})
                resp.append(ret)
            await websocket.send_text(json.dumps(resp))
            await asyncio.sleep(1)
    except Exception as e:
        print(f"Connection closed: {e}")
    finally:
        await websocket.close()
        
@app.websocket("/ws2")
async def websocket_endpoint_2(websocket: WebSocket, db: Session = Depends(get_db)):
    await websocket.accept()
    try:
        while True:
            cnt = db.query(Pic).count()
            await websocket.send_text(json.dumps(str(cnt)))
            await asyncio.sleep(1)
    except Exception as e:
        print(f"Connection closed: {e}")
    finally:
        await websocket.close()


@app.get("/get_all_pics/")
async def ret_pic(db: Session = Depends(get_db)):
    pic_nr = db.query(Pic).count()
    ret=[]
    for i in range(pic_nr+1):
        rects = db.query(Rect).filter(Rect.pic_id == i).all()
        if rects is None:
            raise HTTPException(status_code=404, detail="Pic not found")
        pic_ret=[]
        for r in rects:
            pic_ret.append({"x":str(r.x),"y":str(r.y),"w":str(r.w),"h":str(r.h),"color":r.color})
        ret.append(pic_ret)
    return ret

from fastapi.responses import JSONResponse
from starlette.requests import Request
from starlette.responses import Response

@app.options("/get_all_pics/")
async def options_get_all_pics(request: Request):
    return JSONResponse(status_code=200)

if __name__ == "__main__":
	import uvicorn

	# Run the FastAPI application using Uvicorn
	uvicorn.run(app, host="127.0.0.1", port=8000)

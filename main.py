from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import models, database

# Create the database tables
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()
templates = Jinja2Templates(directory="templates")


@app.get("/")
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/reserve")
async def create_reservation(
    first_name: str = Form(...),
    last_name: str = Form(...),
    date: str = Form(...),
    time: str = Form(...),
    email: str = Form(...),
    db: Session = Depends(database.get_db)
):
    new_res = models.Reservation(first_name=first_name, last_name=last_name, date=date, time=time, email=email)
    db.add(new_res)
    db.commit()
    db.refresh(new_res)
    return {"status": "success", "reservation_id": new_res.id}


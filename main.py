from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import models, database

import os
import requests
from fastapi import BackgroundTasks, Body
from dotenv import load_dotenv

from fastapi.middleware.cors import CORSMiddleware


# Load environment variables
load_dotenv()

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

@app.post("/verify-payment")
async def verify_payment( payload: dict = Body(...), db: Session = Depends(database.get_db), background_tasks: BackgroundTasks = None):
    order_id = payload.get("paypal_order_id")

    # 1. Verify the payment with PayPal
    paypal_client_id = os.getenv("PAYPAL_CLIENT_ID")
    paypal_client_secret = os.getenv("PAYPAL_CLIENT_SECRET")    

    # 2. Update the reservation in the database
    new_res = models.Reservation(
        first_name=payload.get("first_name"),
        last_name=payload.get("last_name"),
        date=payload.get("date"),
        time=payload.get("time"),
        email=payload.get("email"),
        paid=True,
        paypal_order_id=order_id
    )
    db.add(new_res)
    db.commit()

    # 3. Send confirmation email in the background
    background_tasks.add_task(send_confirmation_email, payload.get("email"), payload.get("first_name"), payload.get("last_name"))

    return {"status": "payment verified"}

def send_confirmation_email(email: str, first_name: str, last_name: str):
    # Implement your email sending logic here (e.g., using SMTP or an email service API)
    print(f"Sending confirmation email to {email} for {first_name} {last_name}")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://reservation-buffet.ip-ddns.com"],
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)

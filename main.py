from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import models, database

import os
import requests
from fastapi import BackgroundTasks, Body
from dotenv import load_dotenv

from fastapi.middleware.cors import CORSMiddleware
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from fastapi.staticfiles import StaticFiles


# Load environment variables
load_dotenv()

# Create the database tables
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
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

# Function to get PayPal access token
def get_paypal_access_token():
    client_id = os.getenv("PAYPAL_CLIENT_ID")
    secret = os.getenv("PAYPAL_CLIENT_SECRET")
    url = "https://api-m.sandbox.paypal.com/v1/oauth2/token"
    headers = {"Accept": "application/json", "Accept-Language": "en_US"}
    data = {"grant_type": "client_credentials"}
    response = requests.post(url, headers=headers, data=data, auth=(client_id, secret))
    return response.json().get("access_token")

@app.post("/verify-payment")
async def verify_payment( payload: dict = Body(...), db: Session = Depends(database.get_db), background_tasks: BackgroundTasks = None):
    order_id = payload.get("paypal_order_id")
    token = get_paypal_access_token()

    # Verify order with Paypal
    url = f"https://api-m.sandbox.paypal.com/v2/checkout/orders/{order_id}"    
    headers = {"Authorization": f"Bearer {token}"}
    res = requests.get(url, headers=headers).json()

    if res.get("status") == "COMPLETED":
        # Create the reservation in DB
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

        return {"status": "success"}
    raise HTTPException(status_code=400, detail="Payment verification failed")

 

def send_confirmation_email(email: str, first_name: str, last_name: str):
    # Implement your email sending logic here (e.g., using SMTP or an email service API)
    print(f"Sending confirmation email to {email} for {first_name} {last_name}")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://reservation-buffet.ip-ddns.com"],
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)


conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_FROM=os.getenv("MAIL_FROM"),
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True
)

async def send_confirmation_email(email_to: str, name: str):
    message = MessageSchema(
        subject="Reservation confirmed! 🎉",
        recipients=[email_to],
        body=f"Hello {name}, your reservation at the buffet is successful!",
        subtype=MessageType.html)
    
    fm = FastMail(conf)
    await fm.send_message(message)

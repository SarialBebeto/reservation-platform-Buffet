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
from pydantic import BaseModel


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
    if response.status_code != 200:
        return response.json().get("access_token")
    else:
        print(f"DEBUG: Failed to get PayPal token: {response.status_code} - {response.text}")
        return None

token = get_paypal_access_token()
if token:
    print(f"DEBUG: Token obtained: {token[:10]}...")  # Print the first 10 characters of the token for debugging
else:
    print("DEBUG: Failed to obtain PayPal access token.")

class PaymentPayload(BaseModel):
    first_name: str
    last_name: str
    email: str
    date: str
    time: str
    package_type: str
    paypal_order_id: str

@app.post("/verify-payment")
async def verify_payment( payload: PaymentPayload, db: Session = Depends(database.get_db), background_tasks: BackgroundTasks = None):
    order_id = payload.paypal_order_id
    token = get_paypal_access_token()

    # Verify order with Paypal
    url = f"https://api-m.sandbox.paypal.com/v2/checkout/orders/{order_id}"    
    headers = {"Authorization": f"Bearer {token}"}
    res = requests.get(url, headers=headers).json()
    print(f"DEBUG: PayPal response: {res}")  # Print the entire response for debugging

    if res.get("status") == "COMPLETED":
        # Create the reservation in DB
        new_res = models.Reservation(
            first_name=payload.first_name,
            last_name=payload.last_name,
            date=payload.date,
            time=payload.time,
            email=payload.email,
            package_type=payload.package_type,
            paid=True,
            paypal_order_id=order_id
        )
        db.add(new_res)
        db.commit()

        # 3. Send confirmation email in the background
        background_tasks.add_task(send_confirmation_email, payload.email, payload.first_name, payload.last_name, payload.package_type)

        return {"status": "success"}
    else:
        raise HTTPException(status_code=400, detail=f"PayPal status: {res.get('status')} - Full Error: {res}")

 

async def send_confirmation_email(email: str, last_name: str, package: str):
    # Implement your email sending logic here (e.g., using SMTP or an email service API)
    print(f"Hello {last_name}, your reservation for {package} is successful!")


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

async def send_confirmation_email(email_to: str, name: str, package: str):

    pretty_package = package.replace("_", " ").title()

    message = MessageSchema(
        subject="Reservation confirmed! 🎉",
        recipients=[email_to],
        body=f"Hello {name}, your reservation  for <strong>{pretty_package}</strong> is successful!",
        subtype=MessageType.html)
    
    fm = FastMail(conf)
    await fm.send_message(message)

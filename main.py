from fastapi import FastAPI, Request, Form, Depends, HTTPException, BackgroundTasks, Body
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import models, database

import os
import requests
from dotenv import load_dotenv

from fastapi.middleware.cors import CORSMiddleware
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel


# 1. Setup and Configuration
load_dotenv()

# Create the database tables
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://reservation-buffet.ip-ddns.com"],
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)

# Email Configuration
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


# 2. Pydantic Models
class PaymentPayload(BaseModel):
    first_name: str
    last_name: str
    email: str
    date: str
    time: str
    package_type: str
    paypal_order_id: str

# 3. Helper Functions
def get_paypal_access_token():
    # Fetches a fresh access token from PayPal using client credentials
    client_id = os.getenv("PAYPAL_CLIENT_ID", "").strip()
    secret = os.getenv("PAYPAL_SECRET", "").strip()

    if not client_id or not secret:
        print("ERROR: PayPal credentials are not set in environment variables.")
        return None
    
    url = "https://api-m.sandbox.paypal.com/v1/oauth2/token"
    headers = {"Accept": "application/json", "Accept-Language": "en_US"}
    data = {"grant_type": "client_credentials"}

    try: 
        response = requests.post(url, headers=headers, data=data, auth=(client_id,secret))
        if response.status_code == 200:
            return response.json().get("access_token")
        else:
            print(f"PAYPAL AUTH ERROR: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"NETWORK ERROR: Could not reach PayPal: {e}")
        return None

async def send_confirmation_email(email_to: str, name: str, package: str):
    """Sends a confirmation email to the user after successful reservation."""
    pretty_package = package.replace("_", " ").title()
    message = MessageSchema(
        subject="Reservation confirmed! 🎉",
        recipients=[email_to],
        body=f"Hello {name}, your reservation for <strong>{pretty_package}</strong> is successful!",
        subtype=MessageType.html
    )
    try:
        fm = FastMail(conf)
        await fm.send_message(message)
        print(f"Confirmation email sent to {email_to}")
    except Exception as e:
        print(f"ERROR: Failed to send confirmation email to {email_to}: {e}")
  
# 4. Routes
@app.get("/")
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/verify-payment")
async def verify_payment( payload: PaymentPayload, db: Session = Depends(database.get_db), background_tasks: BackgroundTasks = None):
    
    # 1. Get Access Token
    token = get_paypal_access_token()
    if not token:
        raise HTTPException(status_code=500, detail="Could not authenticate with PayPal. Please try again later.")

    # 2. Verify order with Paypal
    order_id = payload.paypal_order_id
    url = f"https://api-m.sandbox.paypal.com/v2/checkout/orders/{order_id}"    
    headers = {"Authorization": f"Bearer {token}"}

    try:
        res: requests.get(url, headers=headers).json()
        print(f"DEBUG:Paypal verification response: {res}")
    except Exception as e:
        print(f"DEBUG ERROR: Connection to PayPal failed during verification: {e}")
        raise HTTPException(status_code=503, detail="Payment verification service unavailable")
  
    # 3. Check Status and update DB
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

        # 4. Trigger Email
        background_tasks.add_task(
            send_confirmation_email,
            payload.email,
            payload.first_name,
            payload.package_type
        )

        return {"status": "success"}
    else:
        error_msg = res.get('status', 'UNKNOWN')
        raise HTTPException(status_code=400, detail=f"PayPal verification failed. Status: {error_msg}")

#  @app.post("/reserve")
# async def create_reservation(
#     first_name: str = Form(...),
#     last_name: str = Form(...),
#     date: str = Form(...),
#     time: str = Form(...),
#     email: str = Form(...),
#     db: Session = Depends(database.get_db)
# ):
#     new_res = models.Reservation(first_name=first_name, last_name=last_name, date=date, time=time, email=email)
#     db.add(new_res)
#     db.commit()
#     db.refresh(new_res)
#     return {"status": "success", "reservation_id": new_res.id}
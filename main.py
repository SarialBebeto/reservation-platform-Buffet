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

import secrets
from fastapi.security import HTTPBasic, HTTPBasicCredentials


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

security = HTTPBasic()

def generate_transaction_code():
    # Generates a code like "BUF-A1B2C3"
    return f"BUF-{secrets.token_hex(3).upper()}" 


def check_admin(credentials: HTTPBasicCredentials = Depends(security)):
    # Simple hardcoded admin check
    if credentials.username != "admin" or credentials.password != "secretpassword":
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    return credentials.username


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

@app.post("/reserve")
async def create_reservation(
    first_name: str = Form(...),
    last_name: str = Form(...),
    date: str = Form(...),
    time: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    db: Session = Depends(database.get_db)
):
    code = generate_transaction_code()
    new_res = models.Reservation(
        first_name=first_name, 
        last_name=last_name, 
        date=date, 
        time=time, 
        email=email,
        phone_number=phone,
        package_type=package_type,
        transaction_code=code,
        status="pending_payment"
    )
    db.add(new_res)
    db.commit()
    
    return {"status": "success", 
    "transaction_code": code
    }


# --- ADMIN ROUTES ---

@app.get("/admin/dashboard")
async def admin_dashboard(request: Request, db: Session = Depends(database.get_db),user: str = Depends(check_admin)):
    # Fetch only pending reservations
    reservations = db.query(models.Reservation).filter(models.Reservation.status == "pending_payment").all()
    return templates.TemplateResponse("admin.html", {"request": request, "reservations": reservations})


@app.post("/admin/confirm/{res_id}")
async def confirm_payment(res_id: int, db: Session = Depends(database.get_db), background_tasks: BackgrondTasks = None, user: str = Depends(check_admin)):
    res = db.query(models.Reservation).filter(models.Reservation.id == res_id).first()
    if not res:
        raise HTTPException(status_code=404, detail="Reservation not found")

    res.status = "Success_payment"
    db.commit()

    # Trigger explicit email notification to user about manual confirmation
    background_tasks.add_task(
        send_confirmation_email,
        res.email,
        res.first_name,
        res.package_type
    )
    return {"status": "success", "message": "Reservation Confirmed and Email Sent!"}

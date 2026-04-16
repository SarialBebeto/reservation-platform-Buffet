from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime
from database import Base

class Reservation(Base):
    __tablename__ = "reservations"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, index=True)
    last_name = Column(String, index=True)
    date = Column(String)
    time = Column(String)
    email = Column(String, index=True)
    phone_number = Column(String)
    package_type = Column(String)

    # Logic Fields
    transaction_code = Column(String, unique=True, index=True)
    status = Column(String, default="pending_payment")  
    created_at = Column(DateTime, default=datetime.utcnow)


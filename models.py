from sqlalchemy import Column, Integer, String, Boolean
from database import Base

class Reservation(Base):
    __tablename__ = "reservations"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, index=True)
    last_name = Column(String, index=True)
    date = Column(String, index=True)
    time = Column(String, index=True)
    email = Column(String, index=True)
    package_type = Column(String, nullable=True)
    paid = Column(Boolean, default=False)
    paypal_order_id = Column(String, unique=True, nullable=True)

    

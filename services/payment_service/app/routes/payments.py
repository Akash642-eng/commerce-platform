from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models, schemas
import uuid

router = APIRouter(prefix="/payments", tags=["Payments"])

@router.post("/")
def create_payment(payment: schemas.PaymentCreate, db: Session = Depends(get_db)):
    txn_id = str(uuid.uuid4())

    new_payment = models.Payment(
        order_id=payment.order_id,
        payment_method=payment.payment_method,
        payment_status="SUCCESS",
        amount=payment.amount,
        transaction_id=txn_id
    )
    db.add(new_payment)
    db.commit()
    db.refresh(new_payment)

    txn = models.Transaction(
        payment_id=new_payment.id,
        gateway="FAKE_GATEWAY",
        gateway_response="Payment Successful"
    )
    db.add(txn)
    db.commit()

    return {"payment_id": new_payment.id, "status": "SUCCESS"}
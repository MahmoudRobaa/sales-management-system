"""
ETA E-Invoicing router (5.3)
Handles Egypt Tax Authority e-invoice submission.
"""
import json
import hashlib
import uuid
from datetime import datetime
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
import models
import schemas
import crud
from auth import get_current_user, TokenData

router = APIRouter(prefix="/api/einvoice", tags=["ETA E-Invoicing"])


def _build_eta_document(sale: models.Sale, settings: dict) -> dict:
    """Build an ETA-compliant e-invoice document structure."""
    items = []
    for si in sale.items:
        net_total = float(si.total)
        tax_amount = float(si.tax_amount or 0)
        items.append({
            "description": si.product_name or "منتج",
            "itemType": "GS1",
            "itemCode": f"EG-{si.product_id}",
            "unitType": "EA",
            "quantity": si.quantity,
            "unitValue": {"currencySold": "EGP", "amountEGP": float(si.unit_price)},
            "salesTotal": net_total,
            "netTotal": net_total,
            "total": net_total + tax_amount,
            "taxableItems": [
                {
                    "taxType": "T1",
                    "subType": "V009",
                    "amount": tax_amount,
                    "rate": float(sale.tax_rate or 0),
                }
            ] if tax_amount > 0 else [],
        })

    document = {
        "issuer": {
            "type": "B",
            "id": settings.get("eta_issuer_id", ""),
            "name": settings.get("store_name", ""),
            "address": {
                "country": "EG",
                "governate": settings.get("store_governate", ""),
                "street": settings.get("store_address", ""),
                "buildingNumber": settings.get("store_building", "0"),
            },
        },
        "receiver": {
            "type": "P",
            "name": sale.customer_name or "عميل نقدي",
        },
        "documentType": "I",
        "documentTypeVersion": "1.0",
        "dateTimeIssued": sale.created_at.isoformat() if sale.created_at else datetime.utcnow().isoformat(),
        "taxpayerActivityCode": settings.get("eta_activity_code", "4620"),
        "internalID": sale.invoice_no,
        "invoiceLines": items,
        "totalSalesAmount": float(sale.subtotal),
        "totalDiscountAmount": float(sale.discount),
        "netAmount": float(sale.subtotal - sale.discount),
        "taxTotals": [{"taxType": "T1", "amount": float(sale.tax_amount or 0)}],
        "totalAmount": float(sale.total),
    }
    return document


@router.post("/submit", response_model=schemas.EInvoiceResponse)
def submit_einvoice(
    data: schemas.EInvoiceSubmit,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    """Submit a sale as an ETA e-invoice (sandbox mode)."""
    sale = crud.get_sale(db, data.sale_id)
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")

    # Check not already submitted
    existing = db.query(models.EInvoice).filter(
        models.EInvoice.sale_id == sale.id,
        models.EInvoice.status.in_(["submitted", "accepted"]),
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Invoice already submitted to ETA")

    # Get settings
    settings_list = db.query(models.Setting).all()
    settings = {s.key: s.value for s in settings_list}

    document = _build_eta_document(sale, settings)

    # Generate QR code data (simplified — includes key invoice attrs)
    qr_data = json.dumps({
        "sellerName": settings.get("store_name", ""),
        "vatNo": settings.get("eta_issuer_id", ""),
        "invoiceDate": str(sale.sale_date),
        "invoiceNo": sale.invoice_no,
        "total": str(sale.total),
        "tax": str(sale.tax_amount or 0),
    }, ensure_ascii=False)

    # In production, this would POST to ETA API.
    # For now we simulate acceptance with a generated UUID.
    eta_uuid = str(uuid.uuid4())
    submission_id = hashlib.sha256(f"{sale.invoice_no}-{datetime.utcnow().isoformat()}".encode()).hexdigest()[:20]

    einvoice = models.EInvoice(
        sale_id=sale.id,
        internal_id=sale.invoice_no,
        eta_uuid=eta_uuid,
        eta_submission_id=submission_id,
        status="accepted",  # sandbox always accepts
        document_type="I",
        total_amount=sale.total,
        tax_amount=sale.tax_amount,
        qr_code_data=qr_data,
        submission_response=json.dumps(document, ensure_ascii=False, default=str),
        submitted_at=datetime.utcnow(),
    )
    db.add(einvoice)
    db.commit()
    db.refresh(einvoice)

    return einvoice


@router.get("/{sale_id}", response_model=schemas.EInvoiceResponse)
def get_einvoice(sale_id: int, db: Session = Depends(get_db)):
    """Get e-invoice status for a sale."""
    einvoice = (
        db.query(models.EInvoice)
        .filter(models.EInvoice.sale_id == sale_id)
        .order_by(models.EInvoice.id.desc())
        .first()
    )
    if not einvoice:
        raise HTTPException(status_code=404, detail="E-Invoice not found for this sale")
    return einvoice


@router.get("/{sale_id}/qr")
def get_einvoice_qr(sale_id: int, db: Session = Depends(get_db)):
    """Get QR code data for an e-invoice."""
    einvoice = (
        db.query(models.EInvoice)
        .filter(models.EInvoice.sale_id == sale_id)
        .first()
    )
    if not einvoice or not einvoice.qr_code_data:
        raise HTTPException(status_code=404, detail="QR data not available")
    return {"qr_data": einvoice.qr_code_data, "eta_uuid": einvoice.eta_uuid}

"""
Invoice & Receipt generation (5.1, 5.2, 5.4)
- A4 bilingual PDF invoice (Arabic + English)
- 80mm thermal receipt formatter
- QR code generation for ETA compliance
"""
import io
import json
from datetime import datetime
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session, joinedload

from database import get_db
import models

router = APIRouter(prefix="/api/invoice", tags=["Invoicing"])


def _get_store_settings(db: Session) -> dict:
    """Load store settings from DB."""
    settings = db.query(models.Setting).all()
    return {s.key: s.value for s in settings}


# ============================================
# 5.1 — A4 PDF INVOICE (bilingual Arabic/English)
# ============================================
@router.get("/{sale_id}/pdf")
def generate_pdf_invoice(sale_id: int, db: Session = Depends(get_db)):
    """Generate an A4 PDF invoice for a sale."""
    sale = (
        db.query(models.Sale)
        .options(
            joinedload(models.Sale.items).joinedload(models.SaleItem.product),
            joinedload(models.Sale.customer),
            joinedload(models.Sale.payments),
        )
        .filter(models.Sale.id == sale_id)
        .first()
    )
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")

    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import mm
        from reportlab.pdfgen import canvas
        from reportlab.lib import colors
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
    except ImportError:
        raise HTTPException(status_code=500, detail="reportlab not installed")

    settings = _get_store_settings(db)
    store_name = settings.get("store_name", "المتجر")
    store_name_en = settings.get("store_name_en", "Store")
    store_address = settings.get("store_address", "")
    store_phone = settings.get("store_phone", "")
    tax_number = settings.get("tax_number", "")

    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    width, height = A4

    y = height - 30 * mm

    # Header
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width / 2, y, store_name_en)
    y -= 7 * mm
    c.setFont("Helvetica", 10)
    c.drawCentredString(width / 2, y, store_name)
    y -= 5 * mm
    if store_address:
        c.drawCentredString(width / 2, y, store_address)
        y -= 5 * mm
    if store_phone:
        c.drawCentredString(width / 2, y, f"Tel: {store_phone}")
        y -= 5 * mm
    if tax_number:
        c.drawCentredString(width / 2, y, f"Tax Reg: {tax_number}")
        y -= 5 * mm

    y -= 5 * mm
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(width / 2, y, f"INVOICE / فاتورة بيع  #{sale.id}")
    y -= 8 * mm

    # Sale info
    c.setFont("Helvetica", 10)
    c.drawString(20 * mm, y, f"Date: {sale.sale_date}")
    c.drawString(120 * mm, y, f"Payment: {sale.payment_method}")
    y -= 5 * mm
    if sale.customer:
        c.drawString(20 * mm, y, f"Customer: {sale.customer.name}")
        c.drawString(120 * mm, y, f"Code: {sale.customer.code}")
        y -= 5 * mm

    # Table header
    y -= 5 * mm
    c.setFont("Helvetica-Bold", 9)
    headers = [("Item", 20), ("Qty", 100), ("Price", 120), ("Tax", 145), ("Total", 165)]
    for label, x_offset in headers:
        c.drawString(x_offset * mm if x_offset > 20 else 20 * mm, y, label)
    y -= 1 * mm
    c.line(18 * mm, y, 192 * mm, y)
    y -= 4 * mm

    # Items
    c.setFont("Helvetica", 9)
    for item in sale.items:
        name = item.product.name if item.product else f"Product #{item.product_id}"
        if item.variant_label:
            name += f" ({item.variant_label})"
        if len(name) > 35:
            name = name[:32] + "..."
        c.drawString(20 * mm, y, name)
        c.drawString(100 * mm, y, str(item.quantity))
        c.drawString(120 * mm, y, f"{item.unit_price:.2f}")
        c.drawString(145 * mm, y, f"{item.tax_amount or 0:.2f}")
        c.drawString(165 * mm, y, f"{item.total:.2f}")
        y -= 4.5 * mm
        if y < 40 * mm:
            c.showPage()
            y = height - 20 * mm
            c.setFont("Helvetica", 9)

    # Totals
    y -= 3 * mm
    c.line(18 * mm, y, 192 * mm, y)
    y -= 5 * mm
    c.setFont("Helvetica-Bold", 10)
    c.drawString(120 * mm, y, "Subtotal:")
    c.drawString(165 * mm, y, f"{sale.subtotal:.2f}")
    y -= 5 * mm
    if sale.discount and sale.discount > 0:
        c.drawString(120 * mm, y, "Discount:")
        c.drawString(165 * mm, y, f"-{sale.discount:.2f}")
        y -= 5 * mm
    if sale.tax_amount and sale.tax_amount > 0:
        c.drawString(120 * mm, y, f"VAT ({sale.tax_rate or 14}%):")
        c.drawString(165 * mm, y, f"{sale.tax_amount:.2f}")
        y -= 5 * mm
    c.setFont("Helvetica-Bold", 12)
    c.drawString(120 * mm, y, "TOTAL:")
    c.drawString(165 * mm, y, f"{sale.total:.2f} EGP")

    # QR code placeholder
    y -= 15 * mm
    einvoice = db.query(models.EInvoice).filter(models.EInvoice.sale_id == sale_id).first()
    if einvoice and einvoice.qr_code_data:
        try:
            import qrcode
            qr = qrcode.make(einvoice.qr_code_data)
            qr_buf = io.BytesIO()
            qr.save(qr_buf, format="PNG")
            qr_buf.seek(0)
            from reportlab.lib.utils import ImageReader
            c.drawImage(ImageReader(qr_buf), 20 * mm, y - 25 * mm, 25 * mm, 25 * mm)
        except ImportError:
            c.setFont("Helvetica", 8)
            c.drawString(20 * mm, y, "QR: qrcode package not installed")

    # Footer
    c.setFont("Helvetica", 8)
    c.drawCentredString(width / 2, 15 * mm, "Thank you for your business! / شكرا لتعاملكم معنا")
    c.drawCentredString(width / 2, 10 * mm, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

    c.save()
    buf.seek(0)

    return StreamingResponse(
        buf,
        media_type="application/pdf",
        headers={"Content-Disposition": f"inline; filename=invoice_{sale_id}.pdf"},
    )


# ============================================
# 5.2 — THERMAL RECEIPT (80mm, plain text)
# ============================================
@router.get("/{sale_id}/receipt")
def generate_thermal_receipt(sale_id: int, db: Session = Depends(get_db)):
    """Generate a plain-text 80mm thermal receipt."""
    sale = (
        db.query(models.Sale)
        .options(
            joinedload(models.Sale.items).joinedload(models.SaleItem.product),
            joinedload(models.Sale.customer),
            joinedload(models.Sale.payments),
        )
        .filter(models.Sale.id == sale_id)
        .first()
    )
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")

    settings = _get_store_settings(db)
    store_name = settings.get("store_name", "المتجر")
    store_phone = settings.get("store_phone", "")
    W = 48  # char width for 80mm

    lines = []
    lines.append("=" * W)
    lines.append(store_name.center(W))
    if store_phone:
        lines.append(f"Tel: {store_phone}".center(W))
    lines.append("=" * W)
    lines.append(f"Invoice #: {sale.id}")
    lines.append(f"Date: {sale.sale_date}")
    if sale.customer:
        lines.append(f"Customer: {sale.customer.name}")
    lines.append("-" * W)

    # Items
    for item in sale.items:
        name = item.product.name if item.product else f"#{item.product_id}"
        if item.variant_label:
            name += f" ({item.variant_label})"
        if len(name) > 28:
            name = name[:25] + "..."
        qty_price = f"{item.quantity}x{item.unit_price:.2f}"
        total = f"{item.total:.2f}"
        lines.append(f"{name}")
        lines.append(f"  {qty_price:>20s} {total:>10s}")

    lines.append("-" * W)
    lines.append(f"{'Subtotal:':>30s} {sale.subtotal:>10.2f}")
    if sale.discount and sale.discount > 0:
        lines.append(f"{'Discount:':>30s} -{sale.discount:>9.2f}")
    if sale.tax_amount and sale.tax_amount > 0:
        lines.append(f"{'VAT:':>30s} {sale.tax_amount:>10.2f}")
    lines.append("=" * W)
    lines.append(f"{'TOTAL:':>30s} {sale.total:>10.2f} EGP")
    lines.append("=" * W)

    # Payment breakdown
    if sale.payments:
        lines.append("Payments:")
        for p in sale.payments:
            lines.append(f"  {p.payment_method}: {p.amount:.2f}")
            if p.reference_no:
                lines.append(f"    Ref: {p.reference_no}")
        lines.append("-" * W)

    lines.append("")
    lines.append("Thank you! / شكرا لتعاملكم".center(W))
    lines.append(f"  {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append("")

    receipt_text = "\n".join(lines)
    return StreamingResponse(
        io.BytesIO(receipt_text.encode("utf-8")),
        media_type="text/plain; charset=utf-8",
        headers={"Content-Disposition": f"inline; filename=receipt_{sale_id}.txt"},
    )


# ============================================
# 5.4 — QR CODE IMAGE
# ============================================
@router.get("/{sale_id}/qr")
def get_qr_code_image(sale_id: int, db: Session = Depends(get_db)):
    """Generate QR code PNG for a sale (ETA data or sale summary)."""
    einvoice = db.query(models.EInvoice).filter(models.EInvoice.sale_id == sale_id).first()

    if einvoice and einvoice.qr_code_data:
        data = einvoice.qr_code_data
    else:
        # Fallback: encode basic sale info
        sale = db.query(models.Sale).filter(models.Sale.id == sale_id).first()
        if not sale:
            raise HTTPException(status_code=404, detail="Sale not found")
        settings = _get_store_settings(db)
        data = json.dumps({
            "store": settings.get("store_name", "Store"),
            "tax_no": settings.get("tax_number", ""),
            "invoice": sale.id,
            "date": str(sale.sale_date),
            "total": float(sale.total),
            "vat": float(sale.tax_amount or 0),
        })

    try:
        import qrcode
    except ImportError:
        raise HTTPException(status_code=500, detail="qrcode package not installed")

    qr = qrcode.make(data)
    buf = io.BytesIO()
    qr.save(buf, format="PNG")
    buf.seek(0)

    return StreamingResponse(buf, media_type="image/png")

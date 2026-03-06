"""
Product router — CRUD + CSV import/export + barcode lookup.
"""
from typing import List, Optional
import csv
import io

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from database import get_db
import models
import schemas
import crud

router = APIRouter(prefix="/api/products", tags=["Products"])


@router.get("", response_model=List[schemas.ProductSimple])
def get_products(
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
    db: Session = Depends(get_db),
):
    return crud.get_products_with_details(db, skip=skip, limit=limit, category=category)


# NOTE: generate-code must come BEFORE {product_id} to avoid route conflict
@router.get("/generate-code", response_model=dict)
def generate_product_code(db: Session = Depends(get_db)):
    return {"code": crud.generate_product_code(db)}


@router.get("/export-csv")
def export_products_csv(db: Session = Depends(get_db)):
    """Export all products to CSV with UTF-8 BOM for Arabic Excel support."""
    products = crud.get_products_with_details(db, skip=0, limit=10000)

    output = io.StringIO()
    output.write("\ufeff")  # UTF-8 BOM for Excel

    writer = csv.writer(output)
    writer.writerow([
        "Code", "Name", "Category", "Supplier", "Purchase Price",
        "Sale Price", "Quantity", "Min Quantity", "Description",
    ])

    for p in products:
        writer.writerow([
            p.get("code", ""),
            p.get("name", ""),
            p.get("category", ""),
            p.get("supplier", ""),
            p.get("purchase_price", 0),
            p.get("sale_price", 0),
            p.get("quantity", 0),
            p.get("min_quantity", 5),
            p.get("description", ""),
        ])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": "attachment; filename=products_export.csv"},
    )


@router.post("/import-csv")
async def import_products_csv(
    file: UploadFile = File(...), db: Session = Depends(get_db)
):
    """Import products from CSV file with validation."""
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="File must be a CSV")

    content = await file.read()

    # Try different encodings
    decoded: str = ""
    for encoding in ["utf-8-sig", "utf-8", "cp1256", "iso-8859-6"]:
        try:
            decoded = content.decode(encoding)
            break
        except UnicodeDecodeError:
            continue
    else:
        raise HTTPException(
            status_code=400, detail="Could not decode file. Please use UTF-8 encoding."
        )

    reader = csv.DictReader(io.StringIO(decoded))

    imported = 0
    errors: list[str] = []

    for row_num, row in enumerate(reader, start=2):
        try:
            code = row.get("Code") or row.get("code") or row.get("الكود") or ""
            name = row.get("Name") or row.get("name") or row.get("الاسم") or ""
            purchase_price = (
                row.get("Purchase Price") or row.get("purchase_price") or row.get("سعر الشراء") or "0"
            )
            sale_price = (
                row.get("Sale Price") or row.get("sale_price") or row.get("سعر البيع") or "0"
            )
            quantity = row.get("Quantity") or row.get("quantity") or row.get("الكمية") or "0"
            min_quantity = (
                row.get("Min Quantity") or row.get("min_quantity") or row.get("الحد الأدنى") or "5"
            )
            description = row.get("Description") or row.get("description") or row.get("الوصف") or ""

            if not code.strip():
                errors.append(f"Row {row_num}: Code is required")
                continue
            if not name.strip():
                errors.append(f"Row {row_num}: Name is required")
                continue

            existing = crud.get_product_by_code(db, code.strip())
            if existing:
                errors.append(f"Row {row_num}: Code '{code}' already exists")
                continue

            product_data = schemas.ProductCreate(
                code=code.strip(),
                name=name.strip(),
                purchase_price=float(purchase_price) if purchase_price else 0,
                sale_price=float(sale_price) if sale_price else 0,
                quantity=int(float(quantity)) if quantity else 0,
                min_quantity=int(float(min_quantity)) if min_quantity else 5,
                description=description.strip() if description else None,
            )
            crud.create_product(db, product_data)
            imported += 1

        except Exception as e:
            errors.append(f"Row {row_num}: {str(e)}")

    return {
        "imported": imported,
        "errors": errors[:20],
        "total_errors": len(errors),
    }


@router.get("/{product_id}", response_model=schemas.ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = crud.get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.post("", response_model=schemas.ProductResponse)
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    existing = crud.get_product_by_code(db, product.code)
    if existing:
        raise HTTPException(status_code=400, detail="Product code already exists")
    return crud.create_product(db, product)


@router.put("/{product_id}", response_model=schemas.ProductResponse)
def update_product(
    product_id: int, product: schemas.ProductUpdate, db: Session = Depends(get_db)
):
    updated = crud.update_product(db, product_id, product)
    if not updated:
        raise HTTPException(status_code=404, detail="Product not found")
    return updated


@router.delete("/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    if not crud.delete_product(db, product_id):
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Product deleted successfully"}


# ============================================
# 5.28 — BARCODE LOOKUP
# ============================================
@router.get("/barcode/{barcode}")
def lookup_by_barcode(barcode: str, db: Session = Depends(get_db)):
    """Find product by barcode — checks product code, name, and variant barcode."""
    # Check product code first
    product = db.query(models.Product).filter(models.Product.code == barcode).first()
    if product:
        return {"type": "product", "product": schemas.ProductResponse.model_validate(product)}

    # Check variant barcode
    variant = (
        db.query(models.ProductVariant)
        .filter(models.ProductVariant.barcode == barcode)
        .first()
    )
    if variant:
        product = db.query(models.Product).filter(models.Product.id == variant.product_id).first()
        return {
            "type": "variant",
            "product": schemas.ProductResponse.model_validate(product),
            "variant": {
                "id": variant.id,
                "name": variant.name,
                "sku": variant.sku,
                "sale_price": float(variant.sale_price),
                "quantity": variant.quantity,
            },
        }

    raise HTTPException(status_code=404, detail="Product not found for barcode")

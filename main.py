import os
from typing import List, Optional
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="Arabic Dresses API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Local Pydantic models for responses (mirroring schemas.Product)
class ProductOut(BaseModel):
    title_ar: str
    description_ar: Optional[str] = None
    price: float
    original_price: Optional[float] = None
    discount_percent: Optional[int] = None
    category: Optional[str] = None
    in_stock: bool = True
    sizes: List[str] = []
    images: List[str] = []
    sku: Optional[str] = None


def _db_available():
    try:
        from database import db  # type: ignore
        return db is not None
    except Exception:
        return False


def _fetch_products_from_db() -> List[ProductOut]:
    from database import get_documents  # type: ignore
    docs = get_documents("product", {})
    items: List[ProductOut] = []
    for d in docs:
        # remove MongoDB ObjectId for JSON-compat
        d.pop("_id", None)
        items.append(ProductOut(**d))
    return items


def _seed_products() -> List[ProductOut]:
    # Sample products with Arabic content and SAR pricing
    return [
        ProductOut(
            title_ar="فستان سهرة وردي",
            description_ar="فستان أنيق بقصة انسيابية يناسب جميع المناسبات",
            price=517.39,
            original_price=739.13,
            discount_percent=30,
            category="فساتين",
            in_stock=True,
            sizes=["S", "M", "L", "XL"],
            images=[
                "https://images.unsplash.com/photo-1515378791036-0648a3ef77b2?w=1200&q=80&auto=format&fit=crop",
            ],
            sku="OL-DR-001",
        ),
        ProductOut(
            title_ar="عباية خضراء فاخرة",
            description_ar="عباية بتفاصيل راقية ولمسة عصرية",
            price=420.00,
            original_price=560.00,
            discount_percent=25,
            category="عبايات",
            in_stock=True,
            sizes=["S", "M", "L"],
            images=[
                "https://images.unsplash.com/photo-1503342217505-b0a15cf70489?w=1200&q=80&auto=format&fit=crop",
            ],
            sku="OL-AB-002",
        ),
        ProductOut(
            title_ar="فستان أسود كلاسيكي",
            description_ar="إطلالة راقية تناسب الأمسيات الخاصة",
            price=599.00,
            original_price=None,
            discount_percent=None,
            category="فساتين",
            in_stock=True,
            sizes=["M", "L"],
            images=[
                "https://images.unsplash.com/photo-1483985988355-763728e1935b?w=1200&q=80&auto=format&fit=crop",
            ],
            sku="OL-DR-003",
        ),
        ProductOut(
            title_ar="فستان وردي مطرز",
            description_ar="تطريز دقيق يبرز جمال التصميم",
            price=480.00,
            original_price=600.00,
            discount_percent=20,
            category="فساتين",
            in_stock=False,
            sizes=["S", "M", "L", "XL"],
            images=[
                "https://images.unsplash.com/photo-1520975916090-3105956dac38?w=1200&q=80&auto=format&fit=crop",
            ],
            sku="OL-DR-004",
        ),
    ]


@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI Backend!"}


@app.get("/api/hello")
def hello():
    return {"message": "Hello from the backend API!"}


@app.get("/api/products", response_model=List[ProductOut])
def list_products():
    # Try DB first; if unavailable or empty, return seed data
    if _db_available():
        try:
            items = _fetch_products_from_db()
            if items:
                return items
        except Exception:
            pass
    return _seed_products()


@app.get("/schema")
def get_schema():
    # Expose schemas for admin/viewer tooling
    try:
        from schemas import User, Product  # type: ignore
        return {
            "user": User.schema(),
            "product": Product.schema(),
        }
    except Exception as e:
        return {"error": str(e)}


@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        from database import db  # type: ignore
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = getattr(db, 'name', "✅ Connected")
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except ImportError:
        response["database"] = "❌ Database module not found (run enable-database first)"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    # Check environment variables
    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    return response


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

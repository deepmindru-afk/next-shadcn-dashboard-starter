"""FastAPI backend for the Next.js shadcn dashboard.

Provides CRUD endpoints for Products and Users, mirroring the same
response shapes as the original mock data so the frontend drops in seamlessly.

Run with::

    uvicorn backend.main:app --reload --port 8000
"""

import json
from datetime import datetime, timezone

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import or_
from sqlalchemy.orm import Session

from .database import get_db, init_db
from .models import Product, User
from .schemas import (
    DeleteResponse,
    ProductCreate,
    ProductDetailData,
    ProductListData,
    ProductResponse,
    ProductUpdate,
    UserCreate,
    UserDetailData,
    UserListData,
    UserResponse,
    UserUpdate,
    utcnow,
)

# ── App ───────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="Dashboard API",
    description="Python backend for the Next.js shadcn dashboard starter",
    version="1.0.0",
)

# Allow direct browser access when needed (e.g., during development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    """Ensure tables exist on first run."""
    init_db()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


# ── Helpers ────────────────────────────────────────────────────────────────────


def _parse_sort(sort_raw: str | None) -> list[tuple[str, bool]]:
    """Parse a JSON sort array like ``[{"id":"price","desc":true}]``."""
    if not sort_raw:
        return []
    try:
        items = json.loads(sort_raw)
        return [(item["id"], item.get("desc", False)) for item in items if "id" in item]
    except (json.JSONDecodeError, KeyError, TypeError):
        return []


def _apply_sort(query, model, sort_items: list[tuple[str, bool]]):
    """Apply sort clauses to a query in a safe way.

    Only allows sorting by columns that actually exist on the model.
    """
    for col_name, desc in sort_items:
        if hasattr(model, col_name):
            col = getattr(model, col_name)
            query = query.order_by(col.desc() if desc else col.asc())
        elif col_name == "name" and model is User:
            # Special case: 'name' maps to first_name + last_name
            expr = User.first_name + " " + User.last_name
            query = query.order_by(expr.desc() if desc else expr.asc())
    return query


# ══════════════════════════════════════════════════════════════════════════════
#  PRODUCTS
# ══════════════════════════════════════════════════════════════════════════════


@app.get("/api/products", response_model=ProductListData)
def list_products(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    categories: str | None = Query(None, description="Comma-separated category names"),
    search: str | None = Query(None),
    sort: str | None = Query(None, description='JSON: [{"id":"price","desc":true}]'),
    db: Session = Depends(get_db),
):
    q = db.query(Product)

    # Category filter
    if categories:
        cat_list = [c.strip() for c in categories.split(",") if c.strip()]
        if cat_list:
            q = q.filter(Product.category.in_(cat_list))

    # Search
    if search:
        pattern = f"%{search}%"
        q = q.filter(
            or_(
                Product.name.ilike(pattern),
                Product.description.ilike(pattern),
                Product.category.ilike(pattern),
            )
        )

    # Sort
    sort_items = _parse_sort(sort)
    if sort_items:
        q = _apply_sort(q, Product, sort_items)

    total = q.count()
    offset = (page - 1) * limit
    products = q.offset(offset).limit(limit).all()

    return ProductListData(
        time=_now(),
        total_products=total,
        offset=offset,
        limit=limit,
        products=[ProductResponse(**p.to_dict()) for p in products],
    )


@app.get("/api/products/{product_id}", response_model=ProductDetailData)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail=f"Product with ID {product_id} not found")
    return ProductDetailData(
        time=_now(),
        message=f"Product with ID {product_id} found",
        product=ProductResponse(**product.to_dict()),
    )


@app.post("/api/products", response_model=ProductDetailData, status_code=201)
def create_product(payload: ProductCreate, db: Session = Depends(get_db)):
    # Determine next ID for the photo_url
    max_id = db.query(Product.id).order_by(Product.id.desc()).first()
    next_id = (max_id[0] + 1) if max_id else 1

    product = Product(
        name=payload.name,
        description=payload.description,
        price=payload.price,
        category=payload.category,
        photo_url=f"https://api.slingacademy.com/public/sample-products/{next_id}.png",
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return ProductDetailData(
        time=_now(),
        message="Product created successfully",
        product=ProductResponse(**product.to_dict()),
    )


@app.put("/api/products/{product_id}", response_model=ProductDetailData)
def update_product(product_id: int, payload: ProductUpdate, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail=f"Product with ID {product_id} not found")

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)

    db.commit()
    db.refresh(product)
    return ProductDetailData(
        time=_now(),
        message="Product updated successfully",
        product=ProductResponse(**product.to_dict()),
    )


@app.delete("/api/products/{product_id}", response_model=DeleteResponse)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail=f"Product with ID {product_id} not found")
    db.delete(product)
    db.commit()
    return DeleteResponse(
        success=True, message="Product deleted successfully"
    )


# ══════════════════════════════════════════════════════════════════════════════
#  USERS
# ══════════════════════════════════════════════════════════════════════════════


@app.get("/api/users", response_model=UserListData)
def list_users(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    roles: str | None = Query(None, description="Comma-separated role names"),
    search: str | None = Query(None),
    sort: str | None = Query(None, description='JSON: [{"id":"first_name","desc":false}]'),
    db: Session = Depends(get_db),
):
    q = db.query(User)

    # Role filter
    if roles:
        role_list = [r.strip() for r in roles.split(",") if r.strip()]
        if role_list:
            q = q.filter(User.role.in_(role_list))

    # Search
    if search:
        pattern = f"%{search}%"
        q = q.filter(
            or_(
                User.first_name.ilike(pattern),
                User.last_name.ilike(pattern),
                User.email.ilike(pattern),
            )
        )

    # Sort
    sort_items = _parse_sort(sort)
    if sort_items:
        q = _apply_sort(q, User, sort_items)

    total = q.count()
    offset = (page - 1) * limit
    users = q.offset(offset).limit(limit).all()

    return UserListData(
        time=_now(),
        total_users=total,
        offset=offset,
        limit=limit,
        users=[UserResponse(**u.to_dict()) for u in users],
    )


@app.get("/api/users/{user_id}", response_model=UserDetailData)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"User with ID {user_id} not found")
    return UserDetailData(
        time=_now(),
        message=f"User with ID {user_id} found",
        user=UserResponse(**user.to_dict()),
    )


@app.post("/api/users", response_model=UserDetailData, status_code=201)
def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    user = User(
        first_name=payload.first_name,
        last_name=payload.last_name,
        email=payload.email,
        phone=payload.phone,
        status=payload.status,
        role=payload.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return UserDetailData(
        time=_now(),
        message="User created successfully",
        user=UserResponse(**user.to_dict()),
    )


@app.put("/api/users/{user_id}", response_model=UserDetailData)
def update_user(user_id: int, payload: UserUpdate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"User with ID {user_id} not found")

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)
    return UserDetailData(
        time=_now(),
        message="User updated successfully",
        user=UserResponse(**user.to_dict()),
    )


@app.delete("/api/users/{user_id}", response_model=DeleteResponse)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"User with ID {user_id} not found")
    db.delete(user)
    db.commit()
    return DeleteResponse(
        success=True, message="User deleted successfully"
    )


# ── Health ─────────────────────────────────────────────────────────────────────


@app.get("/api/health")
def health():
    return {"status": "ok", "timestamp": _now()}

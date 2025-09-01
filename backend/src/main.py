from fastapi import FastAPI
from src.auth.router import router as auth_router
from src.transactions.router import router as transactions_router
from src.categories.router import router as categories_router
from src.charts.router import router as charts_router
from src.uploads.router import router as uploads_router
from src.imports.router import router as imports_router
from src.core.errors import install_exception_handlers
from src.core.exceptions import install_domain_exception_handlers
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Personal Finance Assistant", version="0.1.0")
install_exception_handlers(app)
install_domain_exception_handlers(app)

allowed_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins, 
    allow_credentials=False,             
    allow_methods=["*"],                 
    allow_headers=["*"],                 
)

app.include_router(auth_router)
app.include_router(transactions_router)
app.include_router(categories_router)
app.include_router(charts_router)
app.include_router(uploads_router)
app.include_router(imports_router)

@app.get("/health")
def health():
    return {"status": "ok"}

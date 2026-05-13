from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from database import init_db, ProductManager, WarehouseManager, TransactionManager, InventoryManager

app = FastAPI()

# Налаштування папки для HTML-шаблонів
templates = Jinja2Templates(directory="templates")

# Ініціалізація бази даних
init_db()

# Створення екземплярів для роботи з БД
product_manager = ProductManager()
warehouse_manager = WarehouseManager()
transaction_manager = TransactionManager()
inventory_manager = InventoryManager()

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    # Отримуємо всі товари та склади з бази
    products = product_manager.get_all()
    warehouses = warehouse_manager.get_all()
    
    # Віддаємо HTML-сторінку і передаємо туди дані
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"products": products, "warehouses": warehouses}
    )

@app.post("/add_product")
def add_product(
    name: str = Form(...),
    article_number: str = Form(...),
    price: float = Form(...)
):
    # Додаємо новий товар в базу
    product_manager.create(name, article_number, price)
    
    # Робимо перенаправлення назад на головну сторінку
    return RedirectResponse(url="/", status_code=303)

@app.get("/delete_product/{product_id}")
def delete_product(product_id: int):
    # Видаляємо товар за його ID
    product_manager.delete(product_id)
    
    # Робимо перенаправлення назад на головну сторінку
    return RedirectResponse(url="/", status_code=303)

@app.get("/edit_product/{product_id}", response_class=HTMLResponse)
def edit_product_page(request: Request, product_id: int):
    # Шукаємо конкретний товар для форми
    products = product_manager.get_all()
    product = next((p for p in products if p["id"] == product_id), None)
    
    return templates.TemplateResponse(
        request=request,
        name="edit_product.html",
        context={"product": product}
    )

@app.post("/update_product/{product_id}")
def update_product(
    product_id: int,
    name: str = Form(...),
    article_number: str = Form(...),
    price: float = Form(...)
):
    product_manager.update(product_id, name, article_number, price)
    return RedirectResponse(url="/", status_code=303)

@app.get("/transactions", response_class=HTMLResponse)
def transactions_page(request: Request):
    products = product_manager.get_all()
    warehouses = warehouse_manager.get_all()
    
    return templates.TemplateResponse(
        request=request,
        name="transactions.html",
        context={"products": products, "warehouses": warehouses}
    )

@app.post("/receive_product")
def receive_product(
    product_id: int = Form(...),
    warehouse_id: int = Form(...),
    quantity: int = Form(...)
):
    transaction_manager.receive_product(product_id, warehouse_id, quantity)
    return RedirectResponse(url="/transactions", status_code=303)

@app.post("/sell_product")
def sell_product(
    product_id: int = Form(...),
    warehouse_id: int = Form(...),
    quantity: int = Form(...)
):
    transaction_manager.sell_product(product_id, warehouse_id, quantity)
    return RedirectResponse(url="/transactions", status_code=303)

@app.post("/move_product")
def move_product(
    product_id: int = Form(...),
    from_warehouse_id: int = Form(...),
    to_warehouse_id: int = Form(...),
    quantity: int = Form(...)
):
    transaction_manager.move_product(product_id, from_warehouse_id, to_warehouse_id, quantity)
    return RedirectResponse(url="/transactions", status_code=303)

@app.get("/warehouses", response_class=HTMLResponse)
def warehouses_page(request: Request):
    warehouses = warehouse_manager.get_all()
    return templates.TemplateResponse(
        request=request,
        name="warehouses.html",
        context={"warehouses": warehouses}
    )

@app.post("/add_warehouse")
def add_warehouse(
    name: str = Form(...),
    address: str = Form(...)
):
    warehouse_manager.create_warehouse(name, address)
    return RedirectResponse(url="/warehouses", status_code=303)

@app.get("/delete_warehouse/{warehouse_id}")
def delete_warehouse(warehouse_id: int):
    warehouse_manager.delete_warehouse(warehouse_id)
    return RedirectResponse(url="/warehouses", status_code=303)

@app.get("/edit_warehouse/{warehouse_id}", response_class=HTMLResponse)
def edit_warehouse_page(request: Request, warehouse_id: int):
    # Шукаємо конкретний склад для форми
    warehouses = warehouse_manager.get_all()
    warehouse = next((w for w in warehouses if w["id"] == warehouse_id), None)
    
    return templates.TemplateResponse(
        request=request,
        name="edit_warehouse.html",
        context={"warehouse": warehouse}
    )

@app.post("/update_warehouse/{warehouse_id}")
def update_warehouse(
    warehouse_id: int,
    name: str = Form(...),
    address: str = Form(...)
):
    warehouse_manager.update_warehouse(warehouse_id, name, address)
    return RedirectResponse(url="/warehouses", status_code=303)

@app.get("/balances", response_class=HTMLResponse)
def balances_page(request: Request):
    balances = inventory_manager.get_all_balances()
    return templates.TemplateResponse(
        request=request,
        name="balances.html",
        context={"balances": balances}
    )


# 🍰 Sweet Crumbs Bakery — Full-Stack Learning Project

> **"Freshly Baked Happiness, Every Day."**

A complete, beginner-friendly full-stack web application for a bakery shop.  
Built to teach **frontend development, backend APIs, database operations, and deployment** — all in one project.

---

## 📚 What You Will Learn

| Topic | Covered In |
|-------|-----------|
| HTML structure & semantics | All `.html` files |
| CSS — responsive design, flexbox, grid | `frontend/css/style.css` |
| JavaScript DOM manipulation | `frontend/js/main.js`, `products.js`, `cart.js` |
| Fetch API & async/await | `frontend/js/api.js` |
| localStorage | `frontend/js/cart.js`, `auth.js` |
| Flask REST API | `backend/routes/` |
| Python data models | `backend/models/` |
| SQLAlchemy ORM | `backend/models/`, `database/db.py` |
| SQLite database | `backend/database/` |
| Password hashing | `backend/routes/auth.py` |
| CORS configuration | `backend/app.py` |
| Environment variables | `backend/.env.example` |

---

## 🏗️ Architecture

```
Browser (HTML / CSS / JS)
         ↓
  Fetch API  (frontend/js/api.js)
         ↓
  HTTP Request
         ↓
  Flask REST API  (backend/app.py + routes/)
         ↓
  SQLAlchemy ORM  (backend/models/)
         ↓
  SQLite Database  (backend/bakery.db)
         ↓
  JSON Response
         ↓
  JavaScript updates the DOM
```

---

## 📁 Folder Structure

```
sweet-crumbs-bakery/
│
├── frontend/                  ← Everything the browser sees
│   ├── index.html             ← Homepage
│   ├── products.html          ← Product listing with filters
│   ├── product.html           ← Single product detail page
│   ├── cart.html              ← Shopping cart + checkout
│   ├── contact.html           ← Contact form
│   ├── login.html             ← Login form
│   ├── register.html          ← Registration form
│   ├── admin.html             ← Admin dashboard
│   │
│   ├── css/
│   │   └── style.css          ← All styles (warm bakery theme)
│   │
│   └── js/
│       ├── api.js             ← ⭐ ALL fetch() calls live here
│       ├── main.js            ← Homepage & shared utilities
│       ├── products.js        ← Products page logic
│       ├── cart.js            ← Cart & checkout logic
│       ├── auth.js            ← Login/register & token storage
│       └── admin.js           ← Admin dashboard logic
│
└── backend/                   ← Flask server
    ├── app.py                 ← ⭐ Main entry point — run this!
    ├── requirements.txt       ← Python packages to install
    ├── .env.example           ← Copy to .env and fill in values
    │
    ├── routes/                ← URL endpoints
    │   ├── products.py        ← GET/POST/PUT/DELETE /api/products
    │   ├── auth.py            ← POST /api/auth/register & login
    │   ├── orders.py          ← POST/GET /api/orders
    │   └── contact.py         ← POST/GET /api/contact
    │
    ├── models/                ← Database table definitions
    │   ├── product.py         ← products table
    │   ├── order.py           ← orders + order_items tables
    │   ├── user.py            ← users table
    │   └── contact.py         ← contact_messages table
    │
    └── database/
        └── db.py              ← SQLAlchemy instance (shared)
```

---

## 🚀 Local Setup Guide

### Step 1 — Clone / Download the Project

```bash
git clone <your-repo-url>
cd sweet-crumbs-bakery
```

### Step 2 — Set Up the Backend

```bash
cd backend
```

Create a Python virtual environment (keeps packages isolated):

```bash
python -m venv venv
```

Activate it:

- **Windows (PowerShell):**
  ```powershell
  venv\Scripts\Activate.ps1
  ```
- **Windows (Command Prompt):**
  ```cmd
  venv\Scripts\activate.bat
  ```
- **macOS / Linux:**
  ```bash
  source venv/bin/activate
  ```

You should see `(venv)` at the start of your terminal prompt.

Install the required Python packages:

```bash
pip install -r requirements.txt
```

Copy the environment file and fill in your values:

```bash
copy .env.example .env     # Windows
# OR
cp .env.example .env       # macOS / Linux
```

Open `.env` and change `SECRET_KEY` to any long random string.

Start the Flask backend server:

```bash
python app.py
```

You should see:

```
✅ Seeded 10 starter products into the database.
✅ Created default admin: admin@sweetcrumbs.com / admin123
 * Running on http://127.0.0.1:5000
```

Test that it works — open your browser and visit:
```
http://127.0.0.1:5000/api/products
```
You should see a JSON response with 10 products.

### Step 3 — Start the Frontend

> **Important:** Do NOT open `.html` files directly by double-clicking them.  
> The browser will block Fetch API requests due to CORS/security policies.  
> You must use a local web server.

**Option A — VS Code Live Server (recommended)**

1. Install the [Live Server extension](https://marketplace.visualstudio.com/items?itemName=ritwickdey.LiveServer) in VS Code
2. Open the `frontend/` folder in VS Code
3. Right-click `index.html` → **Open with Live Server**
4. It opens at `http://127.0.0.1:5500`

**Option B — Python's built-in server**

```bash
cd frontend
python -m http.server 5500
```

Then open `http://127.0.0.1:5500` in your browser.

### Step 4 — Test the Full Flow

1. Open `http://127.0.0.1:5500` — you should see the homepage
2. Products load automatically from the backend
3. Click a product → view details
4. Add to cart → check the cart page
5. Login with `admin@sweetcrumbs.com` / `admin123`
6. Visit `admin.html` to manage products and orders

---

## 🔑 Default Credentials

| Role | Email | Password |
|------|-------|----------|
| Admin | `admin@sweetcrumbs.com` | `admin123` |

Register any other account to test as a regular user.

---

## 🌐 REST API Reference

### Products

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/products` | List all products |
| `GET` | `/api/products?category=Cakes` | Filter by category |
| `GET` | `/api/products?search=chocolate` | Search products |
| `GET` | `/api/products/<id>` | Get one product |
| `POST` | `/api/products` | Add product (admin) |
| `PUT` | `/api/products/<id>` | Update product (admin) |
| `DELETE` | `/api/products/<id>` | Delete product (admin) |

### Authentication

| Method | Endpoint | Body | Description |
|--------|----------|------|-------------|
| `POST` | `/api/auth/register` | `{name, email, password}` | Register |
| `POST` | `/api/auth/login` | `{email, password}` | Login |

### Orders

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/orders` | Place new order |
| `GET` | `/api/orders` | List all orders (admin) |
| `GET` | `/api/orders/<id>` | Get one order |
| `PUT` | `/api/orders/<id>/status` | Update status (admin) |

### Contact

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/contact` | Submit contact form |
| `GET` | `/api/contact` | List all messages (admin) |

---

## 🔍 How the Frontend Talks to the Backend

Here is an exact step-by-step walkthrough of what happens when you open the **Products page**:

```
1. User opens products.html in the browser
         ↓
2. Browser loads products.js
         ↓
3. products.js calls loadProducts()
         ↓
4. loadProducts() calls getProducts() from api.js
         ↓
5. api.js runs:
   fetch("http://127.0.0.1:5000/api/products")
         ↓
6. HTTP GET request travels across localhost to Flask
         ↓
7. Flask's router matches the URL to get_products() in routes/products.py
         ↓
8. get_products() runs:
   Product.query.all()   ← SQLAlchemy queries SQLite
         ↓
9. SQLite returns rows from the 'products' table
         ↓
10. Flask converts rows to JSON:
    { "success": true, "products": [...] }
         ↓
11. HTTP response travels back to the browser
         ↓
12. api.js receives the JSON object
         ↓
13. products.js receives the products array
         ↓
14. renderProducts() builds HTML for each product card
         ↓
15. The product cards appear in the browser
```

### Files Involved

| Step | File |
|------|------|
| Page structure | `frontend/products.html` |
| Trigger + rendering | `frontend/js/products.js` |
| API call | `frontend/js/api.js` |
| URL routing | `backend/routes/products.py` |
| Database model | `backend/models/product.py` |
| DB connection | `backend/database/db.py` |
| DB file | `backend/bakery.db` (auto-created) |

---

## 🗂️ Database Tables

| Table | Purpose |
|-------|---------|
| `users` | Registered customers and admins |
| `products` | Bakery items available for purchase |
| `orders` | Customer orders |
| `order_items` | Individual items within each order |
| `contact_messages` | Messages from the contact form |

---

## 🛡️ Security Notes (for learning)

1. **Passwords are never stored in plain text.**  
   Werkzeug's `generate_password_hash()` is used on registration.  
   `check_password_hash()` is used on login.

2. **The `.env` file must never be committed to Git.**  
   It contains your `SECRET_KEY`. The `.gitignore` already excludes it.

3. **Admin routes check the Authorization header.**  
   The token is a simple HMAC-signed string — sufficient for learning purposes.  
   In production, use a proper JWT library like `PyJWT`.

---

## 🚢 How to Deploy Frontend and Backend Separately

When you're ready to put this online, you deploy the frontend and backend to **different services**.

### Architecture

```
Frontend (static files)          Backend (Python server)
  Netlify / Vercel / GitHub         Render / Railway /
         Pages               →      Fly.io / Heroku
         ↓                                  ↓
  Serves HTML, CSS, JS           Runs Flask + connects to DB
```

### Step-by-Step Deployment

**1. Push your project to GitHub**

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin <your-github-url>
git push -u origin main
```

**2. Deploy the backend (example: Render.com)**

- Sign up at [render.com](https://render.com)
- Create a new **Web Service**
- Connect your GitHub repo
- Set Root Directory to `backend`
- Build Command: `pip install -r requirements.txt`
- Start Command: `python app.py`
- Add environment variables:
  - `SECRET_KEY` = a long random string
  - `FRONTEND_ORIGIN` = your frontend URL (from step 4)
- Deploy → get your backend URL, e.g., `https://sweet-crumbs-api.onrender.com`

**3. Update the frontend API URL**

Open `frontend/js/api.js` and change line 1:

```javascript
// Before (local development)
const API_URL = "http://127.0.0.1:5000/api";

// After (production)
const API_URL = "https://sweet-crumbs-api.onrender.com/api";
```

**4. Deploy the frontend (example: Netlify)**

- Sign up at [netlify.com](https://netlify.com)
- Drag and drop the `frontend/` folder
- OR connect GitHub and set Publish Directory to `frontend`
- Get your frontend URL, e.g., `https://sweet-crumbs.netlify.app`

**5. Update CORS on the backend**

In your backend's environment variables, set:
```
FRONTEND_ORIGIN=https://sweet-crumbs.netlify.app
```

**6. Test the live site**

- Open your frontend URL
- Products should load from the live backend
- Register a user, place an order, check the admin dashboard

### Production Checklist

- [ ] `SECRET_KEY` is a real random secret, not "dev-secret"
- [ ] `debug=False` is set in `app.py` (or use a production WSGI server like `gunicorn`)
- [ ] `FRONTEND_ORIGIN` is set to the exact frontend URL
- [ ] `.env` is NOT committed to Git
- [ ] Test register, login, order placement, and admin CRUD

---

## 📦 Tech Stack Summary

| Layer | Technology |
|-------|-----------|
| Frontend | HTML5, CSS3, Vanilla JavaScript |
| HTTP Requests | Fetch API + async/await |
| Backend | Python 3, Flask 3 |
| ORM | Flask-SQLAlchemy |
| Database | SQLite (development) |
| CORS | Flask-CORS |
| Auth | Werkzeug password hashing + HMAC tokens |
| Config | python-dotenv |

---

## 📝 License

MIT — free for learning and personal projects.

---

*Built for educational purposes. Happy coding! 🎓🍰*

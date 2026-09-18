/**
 * api.js — Centralised API Communication Layer
 * ============================================
 *
 * ALL fetch requests to the Flask backend should go through
 * the functions defined in this file.
 *
 * FLOW:
 *   User action (click/submit)
 *       ↓
 *   JavaScript function in this file
 *       ↓
 *   fetch() sends HTTP request
 *       ↓
 *   Flask route receives request
 *       ↓
 *   Database is queried via SQLAlchemy
 *       ↓
 *   Flask returns JSON response
 *       ↓
 *   JavaScript receives JSON
 *       ↓
 *   DOM is updated (page changes)
 *
 * TO DEPLOY: Change API_URL to your deployed backend URL.
 * Example: const API_URL = "https://your-backend.onrender.com/api";
 */

const API_URL = "http://127.0.0.1:5000/api";

// ── Helper: build auth headers ──────────────────────────────
/**
 * Reads the token stored in localStorage after login and
 * adds it to the request headers so the backend can verify
 * who is making the request.
 */
function getAuthHeaders() {
  const token = localStorage.getItem("authToken");
  const headers = { "Content-Type": "application/json" };
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }
  return headers;
}

// ── Helper: handle API errors ───────────────────────────────
/**
 * Tries to read a JSON error body from the response.
 * If the backend is down, throws a user-friendly message.
 */
async function handleResponse(response) {
  const data = await response.json();
  if (!response.ok) {
    // Backend returned an error (4xx or 5xx status code)
    throw new Error(data.message || "Something went wrong. Please try again.");
  }
  return data;
}

// ═══════════════════════════════════════════════════════════
//  PRODUCT API FUNCTIONS
// ═══════════════════════════════════════════════════════════

/**
 * Fetch all products from the backend.
 * Optionally filter by category or search term.
 *
 * GET /api/products
 * GET /api/products?category=Cakes
 * GET /api/products?search=chocolate
 */
async function getProducts({ category = "", search = "" } = {}) {
  const params = new URLSearchParams();
  if (category && category !== "All") params.append("category", category);
  if (search) params.append("search", search);

  const queryString = params.toString();
  const url = queryString
    ? `${API_URL}/products?${queryString}`
    : `${API_URL}/products`;

  // Send a GET request to the Flask backend
  // The backend returns product data as JSON
  const response = await fetch(url);
  return handleResponse(response);
}

/**
 * Fetch a single product by ID.
 * The product ID comes from the URL: product.html?id=3
 *
 * GET /api/products/<id>
 */
async function getProduct(id) {
  const response = await fetch(`${API_URL}/products/${id}`);
  return handleResponse(response);
}

/**
 * Add a new product (admin only).
 * The Authorization header carries the admin token.
 *
 * POST /api/products
 */
async function addProduct(productData) {
  const response = await fetch(`${API_URL}/products`, {
    method: "POST",
    headers: getAuthHeaders(),
    body: JSON.stringify(productData),
  });
  return handleResponse(response);
}

/**
 * Update an existing product (admin only).
 *
 * PUT /api/products/<id>
 */
async function updateProduct(id, productData) {
  const response = await fetch(`${API_URL}/products/${id}`, {
    method: "PUT",
    headers: getAuthHeaders(),
    body: JSON.stringify(productData),
  });
  return handleResponse(response);
}

/**
 * Delete a product (admin only).
 *
 * DELETE /api/products/<id>
 */
async function deleteProduct(id) {
  const response = await fetch(`${API_URL}/products/${id}`, {
    method: "DELETE",
    headers: getAuthHeaders(),
  });
  return handleResponse(response);
}

// ═══════════════════════════════════════════════════════════
//  AUTH API FUNCTIONS
// ═══════════════════════════════════════════════════════════

/**
 * Register a new user.
 *
 * POST /api/auth/register
 * Body: { name, email, password }
 */
async function registerUser(name, email, password) {
  const response = await fetch(`${API_URL}/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, email, password }),
  });
  return handleResponse(response);
}

/**
 * Log in an existing user.
 *
 * POST /api/auth/login
 * Body: { email, password }
 */
async function loginUser(email, password) {
  const response = await fetch(`${API_URL}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  return handleResponse(response);
}

// ═══════════════════════════════════════════════════════════
//  ORDER API FUNCTIONS
// ═══════════════════════════════════════════════════════════

/**
 * Place a new order.
 *
 * POST /api/orders
 * Body: { customer_name, email, phone, address, items, total }
 */
async function placeOrder(orderData) {
  const response = await fetch(`${API_URL}/orders`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(orderData),
  });
  return handleResponse(response);
}

/**
 * Get all orders (admin only).
 *
 * GET /api/orders
 */
async function getOrders() {
  const response = await fetch(`${API_URL}/orders`, {
    headers: getAuthHeaders(),
  });
  return handleResponse(response);
}

/**
 * Get a single order by ID.
 *
 * GET /api/orders/<id>
 */
async function getOrder(id) {
  const response = await fetch(`${API_URL}/orders/${id}`, {
    headers: getAuthHeaders(),
  });
  return handleResponse(response);
}

/**
 * Update the status of an order (admin only).
 *
 * PUT /api/orders/<id>/status
 * Body: { status: "Confirmed" }
 */
async function updateOrderStatus(id, status) {
  const response = await fetch(`${API_URL}/orders/${id}/status`, {
    method: "PUT",
    headers: getAuthHeaders(),
    body: JSON.stringify({ status }),
  });
  return handleResponse(response);
}

// ═══════════════════════════════════════════════════════════
//  CONTACT API FUNCTIONS
// ═══════════════════════════════════════════════════════════

/**
 * Submit a contact form message.
 *
 * POST /api/contact
 * Body: { name, email, subject, message }
 */
async function submitContact(name, email, subject, message) {
  const response = await fetch(`${API_URL}/contact`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, email, subject, message }),
  });
  return handleResponse(response);
}

/**
 * Get all contact messages (admin only).
 *
 * GET /api/contact
 */
async function getContactMessages() {
  const response = await fetch(`${API_URL}/contact`, {
    headers: getAuthHeaders(),
  });
  return handleResponse(response);
}

/**
 * admin.js — Admin Dashboard Logic
 * ==================================
 *
 * The admin dashboard demonstrates CRUD operations:
 *  - View / Add / Edit / Delete products
 *  - View orders and update their status
 *  - View contact messages
 *
 * All API calls use the admin token from localStorage.
 * The backend verifies this token before allowing changes.
 */

// ── Check admin access ────────────────────────────────────────
const adminUser = JSON.parse(localStorage.getItem("authUser") || "null");
if (!adminUser || !adminUser.is_admin) {
  // Redirect non-admins to the login page
  document.getElementById("admin-access-denied").style.display = "block";
  document.getElementById("admin-layout").style.display = "none";
}

// ── Sidebar navigation ────────────────────────────────────────
const navItems = document.querySelectorAll(".admin-nav a");
const sections = document.querySelectorAll(".admin-section");

navItems.forEach(link => {
  link.addEventListener("click", (e) => {
    e.preventDefault();
    const target = link.dataset.section;

    navItems.forEach(l => l.classList.remove("active"));
    sections.forEach(s => s.classList.remove("active"));

    link.classList.add("active");
    document.getElementById(`section-${target}`).classList.add("active");

    // Load data when switching sections
    if (target === "products")  loadAdminProducts();
    if (target === "orders")    loadAdminOrders();
    if (target === "messages")  loadAdminMessages();
    if (target === "dashboard") loadDashboardStats();
  });
});

// ── Dashboard stats ───────────────────────────────────────────
async function loadDashboardStats() {
  try {
    const [productsData, ordersData, messagesData] = await Promise.all([
      getProducts(),
      getOrders(),
      getContactMessages(),
    ]);

    document.getElementById("stat-products").textContent = productsData.products.length;
    document.getElementById("stat-orders").textContent   = ordersData.orders.length;
    document.getElementById("stat-messages").textContent = messagesData.messages.length;

    const revenue = ordersData.orders
      .filter(o => o.status !== "Cancelled")
      .reduce((sum, o) => sum + o.total, 0);
    document.getElementById("stat-revenue").textContent = `₹${revenue.toFixed(0)}`;
  } catch (err) {
    console.error("Stats load error:", err.message);
  }
}

// ── PRODUCTS section ──────────────────────────────────────────
async function loadAdminProducts() {
  const tbody = document.getElementById("products-tbody");
  if (!tbody) return;
  tbody.innerHTML = `<tr><td colspan="6" style="text-align:center; padding:2rem;"><div class="spinner" style="margin:0 auto;"></div></td></tr>`;

  try {
    const data = await getProducts();
    const products = data.products;

    if (products.length === 0) {
      tbody.innerHTML = `<tr><td colspan="6" style="text-align:center;">No products found.</td></tr>`;
      return;
    }

    tbody.innerHTML = products.map(p => `
      <tr>
        <td>${p.id}</td>
        <td>
          ${p.image ? `<img src="${p.image}" style="width:50px;height:40px;object-fit:cover;border-radius:6px;" onerror="this.style.display='none'">` : '🎂'}
          ${p.name}
        </td>
        <td>${p.category}</td>
        <td>₹${p.price.toFixed(0)}</td>
        <td>
          <span class="availability-badge ${p.available ? 'badge-available' : 'badge-unavailable'}">
            ${p.available ? 'Yes' : 'No'}
          </span>
        </td>
        <td>
          <button class="btn btn-outline btn-sm" onclick="openEditModal(${p.id}, '${escHtml(p.name)}', '${escHtml(p.description)}', ${p.price}, '${p.category}', '${escHtml(p.image || '')}', ${p.available})">Edit</button>
          <button class="btn btn-danger btn-sm" onclick="confirmDeleteProduct(${p.id}, '${escHtml(p.name)}')">Delete</button>
        </td>
      </tr>
    `).join("");
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="6" style="color:red;">${err.message}</td></tr>`;
  }
}

// ── Add Product ───────────────────────────────────────────────
function openAddModal() {
  document.getElementById("modal-title").textContent = "Add New Product";
  document.getElementById("product-form").reset();
  document.getElementById("edit-product-id").value = "";
  document.getElementById("product-modal").classList.remove("hidden");
}

// ── Edit Product ──────────────────────────────────────────────
function openEditModal(id, name, desc, price, category, image, available) {
  document.getElementById("modal-title").textContent = "Edit Product";
  document.getElementById("edit-product-id").value = id;
  document.getElementById("p-name").value = name;
  document.getElementById("p-description").value = desc;
  document.getElementById("p-price").value = price;
  document.getElementById("p-category").value = category;
  document.getElementById("p-image").value = image;
  document.getElementById("p-available").checked = available;
  document.getElementById("product-modal").classList.remove("hidden");
}

function closeProductModal() {
  document.getElementById("product-modal").classList.add("hidden");
}

const productForm = document.getElementById("product-form");
if (productForm) {
  productForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const alertEl = document.getElementById("modal-alert");
    const id = document.getElementById("edit-product-id").value;

    const productData = {
      name: document.getElementById("p-name").value.trim(),
      description: document.getElementById("p-description").value.trim(),
      price: parseFloat(document.getElementById("p-price").value),
      category: document.getElementById("p-category").value,
      image: document.getElementById("p-image").value.trim(),
      available: document.getElementById("p-available").checked,
    };

    try {
      if (id) {
        // Update existing product
        await updateProduct(parseInt(id), productData);
        showModalAlert("Product updated successfully!", "success");
      } else {
        // Add new product
        await addProduct(productData);
        showModalAlert("Product added successfully!", "success");
      }
      setTimeout(() => {
        closeProductModal();
        loadAdminProducts();
        loadDashboardStats();
      }, 800);
    } catch (err) {
      showModalAlert(err.message, "error");
    }
  });
}

async function confirmDeleteProduct(id, name) {
  if (!confirm(`Delete "${name}"? This cannot be undone.`)) return;
  try {
    await deleteProduct(id);
    loadAdminProducts();
    loadDashboardStats();
  } catch (err) {
    alert("Error deleting product: " + err.message);
  }
}

// ── ORDERS section ────────────────────────────────────────────
async function loadAdminOrders() {
  const tbody = document.getElementById("orders-tbody");
  if (!tbody) return;
  tbody.innerHTML = `<tr><td colspan="7" style="text-align:center; padding:2rem;"><div class="spinner" style="margin:0 auto;"></div></td></tr>`;

  try {
    const data = await getOrders();
    const orders = data.orders;

    if (orders.length === 0) {
      tbody.innerHTML = `<tr><td colspan="7" style="text-align:center;">No orders yet.</td></tr>`;
      return;
    }

    tbody.innerHTML = orders.map(o => `
      <tr>
        <td>#${o.id}</td>
        <td>${o.customer_name}</td>
        <td>${o.email}</td>
        <td>₹${o.total.toFixed(0)}</td>
        <td>${new Date(o.created_at).toLocaleDateString()}</td>
        <td><span class="status-badge ${getStatusClass(o.status)}">${o.status}</span></td>
        <td>
          <select class="status-select" onchange="handleStatusChange(${o.id}, this.value)" style="font-size:0.82rem; padding:0.3rem; border-radius:6px; border:1px solid #ddd;">
            ${["Pending","Confirmed","Preparing","Out for Delivery","Delivered","Cancelled"]
              .map(s => `<option value="${s}" ${s === o.status ? 'selected' : ''}>${s}</option>`)
              .join("")}
          </select>
        </td>
      </tr>
    `).join("");
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="7" style="color:red;">${err.message}</td></tr>`;
  }
}

async function handleStatusChange(orderId, newStatus) {
  try {
    await updateOrderStatus(orderId, newStatus);
    // Subtle feedback — reload the table
    loadAdminOrders();
    loadDashboardStats();
  } catch (err) {
    alert("Error updating status: " + err.message);
  }
}

function getStatusClass(status) {
  const map = {
    "Pending":          "status-pending",
    "Confirmed":        "status-confirmed",
    "Preparing":        "status-preparing",
    "Out for Delivery": "status-out",
    "Delivered":        "status-delivered",
    "Cancelled":        "status-cancelled",
  };
  return map[status] || "status-pending";
}

// ── MESSAGES section ──────────────────────────────────────────
async function loadAdminMessages() {
  const tbody = document.getElementById("messages-tbody");
  if (!tbody) return;
  tbody.innerHTML = `<tr><td colspan="5" style="text-align:center; padding:2rem;"><div class="spinner" style="margin:0 auto;"></div></td></tr>`;

  try {
    const data = await getContactMessages();
    const messages = data.messages;

    if (messages.length === 0) {
      tbody.innerHTML = `<tr><td colspan="5" style="text-align:center;">No messages yet.</td></tr>`;
      return;
    }

    tbody.innerHTML = messages.map(m => `
      <tr>
        <td>${m.name}</td>
        <td>${m.email}</td>
        <td>${m.subject}</td>
        <td style="max-width:280px; word-break:break-word;">${m.message}</td>
        <td>${new Date(m.created_at).toLocaleDateString()}</td>
      </tr>
    `).join("");
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="5" style="color:red;">${err.message}</td></tr>`;
  }
}

// ── Utilities ─────────────────────────────────────────────────
function escHtml(str) {
  return String(str).replace(/'/g, "\\'");
}

function showModalAlert(msg, type) {
  const el = document.getElementById("modal-alert");
  if (el) { el.textContent = msg; el.className = `alert alert-${type}`; }
}

// ── Init ──────────────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", () => {
  loadDashboardStats();
  loadAdminProducts();

  // Mobile nav
  const navToggle = document.getElementById("nav-toggle");
  const navLinks  = document.getElementById("nav-links");
  if (navToggle && navLinks) {
    navToggle.addEventListener("click", () => navLinks.classList.toggle("open"));
  }
});

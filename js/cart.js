/**
 * cart.js — Shopping Cart & Checkout
 * =====================================
 *
 * Cart storage: localStorage (no backend needed for cart state)
 * Checkout: sends POST /api/orders to Flask backend
 *
 * This file demonstrates:
 *  - Reading/writing localStorage
 *  - DOM manipulation (rendering a list)
 *  - Sending form data to the backend via fetch
 */

// ── Read the cart from localStorage ──────────────────────────
function getCart() {
  return JSON.parse(localStorage.getItem("cart") || "[]");
}

/** Save updated cart back to localStorage */
function saveCart(cart) {
  localStorage.setItem("cart", JSON.stringify(cart));
  updateCartCount();
}

/** Update cart item count badge in navbar */
function updateCartCount() {
  const cart = getCart();
  const totalItems = cart.reduce((sum, item) => sum + item.quantity, 0);
  const badge = document.getElementById("cart-count");
  if (badge) {
    badge.textContent = totalItems;
    badge.style.display = totalItems > 0 ? "flex" : "none";
  }
}

// ── Add product to cart (called from other pages too) ─────────
function addToCart(product) {
  let cart = getCart();
  const existing = cart.find(item => item.id === product.id);
  if (existing) {
    existing.quantity += 1;
  } else {
    cart.push({ ...product, quantity: 1 });
  }
  saveCart(cart);
}

// ── Render the cart items list ────────────────────────────────
const cartItemsList = document.getElementById("cart-items-list");
const cartSummaryEl = document.getElementById("cart-summary-section");
const emptyCartEl   = document.getElementById("empty-cart");
const checkoutEl    = document.getElementById("checkout-section");

function renderCart() {
  const cart = getCart();

  if (cart.length === 0) {
    if (emptyCartEl)   emptyCartEl.style.display = "block";
    if (cartSummaryEl) cartSummaryEl.style.display = "none";
    if (checkoutEl)    checkoutEl.style.display = "none";
    if (cartItemsList) cartItemsList.innerHTML = "";
    return;
  }

  if (emptyCartEl)   emptyCartEl.style.display = "none";
  if (cartSummaryEl) cartSummaryEl.style.display = "block";
  if (checkoutEl)    checkoutEl.style.display = "block";

  // Build cart item cards
  cartItemsList.innerHTML = cart.map(item => `
    <div class="cart-item" data-id="${item.id}">
      <img
        class="cart-item-image"
        src="${item.image || ''}"
        alt="${item.name}"
        onerror="this.src='';this.style.display='none'"
      >
      <div class="cart-item-info">
        <h4>${item.name}</h4>
        <div class="price">₹${item.price.toFixed(0)} each</div>
      </div>
      <div class="cart-item-controls">
        <button class="qty-btn" onclick="changeQty(${item.id}, -1)">−</button>
        <span class="qty-display">${item.quantity}</span>
        <button class="qty-btn" onclick="changeQty(${item.id}, 1)">+</button>
        <span style="margin-left:0.5rem; font-weight:700; color:var(--brown);">
          ₹${(item.price * item.quantity).toFixed(0)}
        </span>
      </div>
      <button class="btn btn-danger btn-sm" onclick="removeFromCart(${item.id})">✕</button>
    </div>
  `).join("");

  renderSummary(cart);
}

/** Render the totals in the order summary panel */
function renderSummary(cart) {
  const subtotal = cart.reduce((sum, item) => sum + item.price * item.quantity, 0);
  const delivery = 50; // flat delivery fee
  const total    = subtotal + delivery;

  const subtotalEl = document.getElementById("summary-subtotal");
  const deliveryEl = document.getElementById("summary-delivery");
  const totalEl    = document.getElementById("summary-total");

  if (subtotalEl) subtotalEl.textContent = `₹${subtotal.toFixed(0)}`;
  if (deliveryEl) deliveryEl.textContent = `₹${delivery.toFixed(0)}`;
  if (totalEl)    totalEl.textContent    = `₹${total.toFixed(0)}`;
}

/** Increase or decrease quantity of a cart item */
function changeQty(productId, delta) {
  let cart = getCart();
  const item = cart.find(i => i.id === productId);
  if (!item) return;

  item.quantity += delta;
  if (item.quantity <= 0) {
    // Remove the item if quantity drops to zero
    cart = cart.filter(i => i.id !== productId);
  }

  saveCart(cart);
  renderCart();
}

/** Remove a product from the cart entirely */
function removeFromCart(productId) {
  let cart = getCart().filter(i => i.id !== productId);
  saveCart(cart);
  renderCart();
}

/** Clear all items from the cart */
function clearCart() {
  localStorage.removeItem("cart");
  updateCartCount();
  renderCart();
}

// ── Clear cart button ─────────────────────────────────────────
const clearBtn = document.getElementById("clear-cart-btn");
if (clearBtn) {
  clearBtn.addEventListener("click", () => {
    if (confirm("Clear all items from the cart?")) {
      clearCart();
    }
  });
}

// ── Checkout Form Submission ──────────────────────────────────
const checkoutForm = document.getElementById("checkout-form");
if (checkoutForm) {
  checkoutForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const cart = getCart();
    if (cart.length === 0) {
      showAlert(document.getElementById("checkout-alert"), "Your cart is empty!", "error");
      return;
    }

    const name    = document.getElementById("co-name").value.trim();
    const email   = document.getElementById("co-email").value.trim();
    const phone   = document.getElementById("co-phone").value.trim();
    const address = document.getElementById("co-address").value.trim();
    const alertEl = document.getElementById("checkout-alert");

    if (!name || !email || !phone || !address) {
      showAlert(alertEl, "Please fill in all delivery details.", "error");
      return;
    }

    const subtotal = cart.reduce((sum, i) => sum + i.price * i.quantity, 0);
    const total    = subtotal + 50; // add delivery fee

    // Build the order payload to send to the backend
    const orderPayload = {
      customer_name: name,
      email: email,
      phone: phone,
      address: address,
      items: cart.map(item => ({
        product_id: item.id,
        quantity: item.quantity,
      })),
      total: total,
    };

    const submitBtn = checkoutForm.querySelector("button[type=submit]");
    submitBtn.disabled = true;
    submitBtn.textContent = "Placing Order...";

    try {
      // Send the order to Flask backend → saved to database
      const data = await placeOrder(orderPayload);

      // Order was successful! Clear the cart and show success screen
      clearCart();
      showOrderSuccess(data.order_id);

    } catch (err) {
      showAlert(alertEl, err.message, "error");
    } finally {
      submitBtn.disabled = false;
      submitBtn.textContent = "Place Order 🎉";
    }
  });
}

/** Show the order success screen */
function showOrderSuccess(orderId) {
  const cartSection = document.getElementById("cart-main-section");
  const successEl   = document.getElementById("order-success");

  if (cartSection) cartSection.style.display = "none";
  if (successEl) {
    successEl.style.display = "block";
    const orderIdEl = document.getElementById("order-id-display");
    if (orderIdEl) orderIdEl.textContent = `Order #${orderId}`;
  }
}

/** Show an alert message */
function showAlert(el, message, type) {
  if (!el) return;
  el.textContent = message;
  el.className = `alert alert-${type}`;
}

// ── Initialise on page load ───────────────────────────────────
document.addEventListener("DOMContentLoaded", () => {
  renderCart();
  updateCartCount();

  // Mobile nav toggle (shared with main.js but safe to repeat)
  const navToggle = document.getElementById("nav-toggle");
  const navLinks  = document.getElementById("nav-links");
  if (navToggle && navLinks) {
    navToggle.addEventListener("click", () => navLinks.classList.toggle("open"));
  }
});

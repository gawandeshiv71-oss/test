/**
 * main.js — Homepage Logic
 * ========================
 *
 * This file handles:
 *  1. Loading featured products from the backend API on the homepage
 *  2. Updating the cart count badge in the navbar
 *  3. Mobile navigation toggle
 */

// ── Update cart count in navbar ──────────────────────────────
/**
 * Reads the cart from localStorage and updates the badge
 * showing the number of items in the cart.
 */
function updateCartCount() {
  const cart = JSON.parse(localStorage.getItem("cart") || "[]");
  const totalItems = cart.reduce((sum, item) => sum + item.quantity, 0);
  const badge = document.getElementById("cart-count");
  if (badge) {
    badge.textContent = totalItems;
    badge.style.display = totalItems > 0 ? "flex" : "none";
  }
}

// ── Mobile navbar toggle ─────────────────────────────────────
const navToggle = document.getElementById("nav-toggle");
const navLinks = document.getElementById("nav-links");
if (navToggle && navLinks) {
  navToggle.addEventListener("click", () => {
    navLinks.classList.toggle("open");
  });
}

// ── Load featured products on homepage ──────────────────────
const featuredGrid = document.getElementById("featured-products");
if (featuredGrid) {
  loadFeaturedProducts();
}

async function loadFeaturedProducts() {
  // Show loading spinner while we wait for the API response
  featuredGrid.innerHTML = `
    <div class="loading-state" style="grid-column:1/-1">
      <div class="spinner"></div>
      <p>Loading fresh products...</p>
    </div>`;

  try {
    // Send a GET request to the Flask backend
    // The backend queries the database and returns products as JSON
    const data = await getProducts();
    const products = data.products;

    if (!products || products.length === 0) {
      featuredGrid.innerHTML = `
        <div class="empty-state" style="grid-column:1/-1">
          <div class="emoji">🎂</div>
          <p>No products found. Check back soon!</p>
        </div>`;
      return;
    }

    // Display only the first 6 products on the homepage
    const featured = products.slice(0, 6);

    // Build HTML for each product card and insert into the DOM
    featuredGrid.innerHTML = featured.map(product => renderProductCard(product)).join("");

    // Add "Add to Cart" click listeners
    attachAddToCartListeners();

  } catch (err) {
    // Show a friendly message if the backend is unreachable
    featuredGrid.innerHTML = `
      <div class="error-state" style="grid-column:1/-1">
        <p>⚠️ Unable to connect to the server. Please make sure the backend is running.</p>
        <p style="font-size:0.85rem; margin-top:0.5rem; color:#888;">${err.message}</p>
      </div>`;
  }
}

/**
 * Builds the HTML for a single product card.
 * This is used on both the homepage and the products page.
 */
function renderProductCard(product) {
  const imageHtml = product.image
    ? `<img class="product-card-image" src="${product.image}" alt="${product.name}" loading="lazy" onerror="this.style.display='none';this.nextElementSibling.style.display='flex'">`
    : "";
  const placeholderHtml = `<div class="product-card-image-placeholder" style="${product.image ? 'display:none' : ''}">🎂</div>`;

  const availabilityBadge = product.available
    ? `<span class="availability-badge badge-available">Available</span>`
    : `<span class="availability-badge badge-unavailable">Unavailable</span>`;

  return `
    <div class="product-card" data-id="${product.id}">
      ${imageHtml}
      ${placeholderHtml}
      <div class="product-card-body">
        <div class="product-category">${product.category}</div>
        <h3>${product.name}</h3>
        <p>${product.description}</p>
        <div class="product-footer">
          <div class="product-price">₹${product.price.toFixed(0)}</div>
          ${availabilityBadge}
        </div>
        <div style="display:flex; gap:0.5rem; margin-top:0.8rem;">
          <button
            class="btn btn-primary btn-sm add-to-cart-btn"
            data-id="${product.id}"
            data-name="${product.name}"
            data-price="${product.price}"
            data-image="${product.image || ''}"
            ${!product.available ? "disabled" : ""}
            style="${!product.available ? 'opacity:0.5; cursor:not-allowed' : ''}"
          >
            🛒 Add to Cart
          </button>
          <a href="product.html?id=${product.id}" class="btn btn-outline btn-sm">View</a>
        </div>
      </div>
    </div>`;
}

/**
 * Attach click event listeners to all "Add to Cart" buttons.
 * When clicked, the product is added to the localStorage cart.
 */
function attachAddToCartListeners() {
  document.querySelectorAll(".add-to-cart-btn").forEach(btn => {
    btn.addEventListener("click", (e) => {
      const b = e.currentTarget;
      addToCart({
        id: parseInt(b.dataset.id),
        name: b.dataset.name,
        price: parseFloat(b.dataset.price),
        image: b.dataset.image,
      });

      // Visual feedback
      b.textContent = "✓ Added!";
      b.classList.add("btn-success");
      b.classList.remove("btn-primary");
      setTimeout(() => {
        b.innerHTML = "🛒 Add to Cart";
        b.classList.remove("btn-success");
        b.classList.add("btn-primary");
      }, 1500);
    });
  });
}

// ── Cart helpers (used across pages) ────────────────────────

/** Add a product to the cart stored in localStorage */
function addToCart(product) {
  let cart = JSON.parse(localStorage.getItem("cart") || "[]");

  // Check if the product is already in the cart
  const existing = cart.find(item => item.id === product.id);
  if (existing) {
    existing.quantity += 1;
  } else {
    cart.push({ ...product, quantity: 1 });
  }

  localStorage.setItem("cart", JSON.stringify(cart));
  updateCartCount();
}

// Initialise on page load
updateCartCount();

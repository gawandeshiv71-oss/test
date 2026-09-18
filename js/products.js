/**
 * products.js — Products Listing Page
 * ====================================
 *
 * This file handles:
 *  1. Fetching all products from GET /api/products
 *  2. Rendering product cards in the grid
 *  3. Category filter buttons
 *  4. Real-time search
 *  5. Add to Cart functionality
 */

// Current filter state
let currentCategory = "All";
let currentSearch = "";

// ── DOM references ───────────────────────────────────────────
const productGrid  = document.getElementById("products-grid");
const searchInput  = document.getElementById("search-input");
const filterBtns   = document.querySelectorAll(".filter-btn");

// ── Load products when the page loads ───────────────────────
document.addEventListener("DOMContentLoaded", () => {
  loadProducts();
  updateCartCount();
});

/**
 * Fetch products from the backend API and render them.
 * This is the key function that demonstrates frontend-backend communication.
 *
 * Step-by-step:
 *  1. Show loading state in the grid
 *  2. Call getProducts() from api.js → sends fetch() to Flask
 *  3. Flask queries the database
 *  4. Flask returns JSON with product list
 *  5. We render HTML cards for each product
 */
async function loadProducts() {
  if (!productGrid) return;

  // Step 1: Show loading spinner
  showLoadingState();

  try {
    // Step 2-4: Fetch from backend (defined in api.js)
    const data = await getProducts({ category: currentCategory, search: currentSearch });
    const products = data.products;

    // Step 5: Render the results
    if (!products || products.length === 0) {
      showEmptyState();
    } else {
      renderProducts(products);
    }
  } catch (err) {
    showErrorState(err.message);
  }
}

function showLoadingState() {
  productGrid.innerHTML = `
    <div class="loading-state" style="grid-column:1/-1">
      <div class="spinner"></div>
      <p>Fetching products from the server...</p>
    </div>`;
}

function showEmptyState() {
  productGrid.innerHTML = `
    <div class="empty-state" style="grid-column:1/-1">
      <div class="emoji">🔍</div>
      <p>No products found for your search.</p>
    </div>`;
}

function showErrorState(message) {
  productGrid.innerHTML = `
    <div class="error-state" style="grid-column:1/-1">
      <p>⚠️ Unable to connect to the server. Please try again.</p>
      <p style="font-size:0.82rem; margin-top:0.5rem; color:#888;">${message}</p>
    </div>`;
}

/** Render product cards into the grid */
function renderProducts(products) {
  productGrid.innerHTML = products.map(renderProductCard).join("");
  attachAddToCartListeners();
}

// ── Category filter buttons ──────────────────────────────────
filterBtns.forEach(btn => {
  btn.addEventListener("click", () => {
    // Update active state visually
    filterBtns.forEach(b => b.classList.remove("active"));
    btn.classList.add("active");

    // Update filter state and reload
    currentCategory = btn.dataset.category;
    loadProducts();
  });
});

// ── Search input ─────────────────────────────────────────────
if (searchInput) {
  // Debounce: wait 400ms after user stops typing before searching
  let debounceTimer;
  searchInput.addEventListener("input", () => {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => {
      currentSearch = searchInput.value.trim();
      loadProducts();
    }, 400);
  });
}

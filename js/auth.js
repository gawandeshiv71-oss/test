/**
 * auth.js — Login, Registration & Auth State Management
 * ======================================================
 *
 * This file handles:
 *  - Login form submission → POST /api/auth/login
 *  - Register form submission → POST /api/auth/register
 *  - Storing auth info in localStorage
 *  - Updating the navbar to show the logged-in user's name
 *  - Logout functionality
 */

// ── Auth helpers ─────────────────────────────────────────────

/** Save user info and token to localStorage after login/register */
function saveAuthInfo(user, token) {
  localStorage.setItem("authToken", token);
  localStorage.setItem("authUser", JSON.stringify(user));
}

/** Remove auth info from localStorage on logout */
function clearAuthInfo() {
  localStorage.removeItem("authToken");
  localStorage.removeItem("authUser");
}

/** Read the currently logged-in user object from localStorage */
function getCurrentUser() {
  const raw = localStorage.getItem("authUser");
  return raw ? JSON.parse(raw) : null;
}

/** Check if the current user is an admin */
function isAdmin() {
  const user = getCurrentUser();
  return user && user.is_admin;
}

// ── Update navbar based on login state ──────────────────────
/**
 * Called on every page load.
 * If a user is logged in, show their name instead of "Login".
 */
function updateNavbarAuth() {
  const user = getCurrentUser();
  const loginLink = document.getElementById("nav-login-link");
  const userDisplay = document.getElementById("nav-user-display");
  const logoutBtn = document.getElementById("nav-logout-btn");

  if (user) {
    if (loginLink) loginLink.style.display = "none";
    if (userDisplay) {
      userDisplay.textContent = `👤 ${user.name}`;
      userDisplay.style.display = "inline-block";
    }
    if (logoutBtn) {
      logoutBtn.style.display = "inline-block";
      logoutBtn.addEventListener("click", handleLogout);
    }
  } else {
    if (loginLink) loginLink.style.display = "inline-block";
    if (userDisplay) userDisplay.style.display = "none";
    if (logoutBtn) logoutBtn.style.display = "none";
  }
}

/** Log the user out and reload the page */
function handleLogout() {
  clearAuthInfo();
  window.location.href = "index.html";
}

// ── Login Form ───────────────────────────────────────────────
const loginForm = document.getElementById("login-form");
if (loginForm) {
  loginForm.addEventListener("submit", async (e) => {
    e.preventDefault(); // Prevent default browser form submission

    const email = document.getElementById("login-email").value.trim();
    const password = document.getElementById("login-password").value;
    const alertEl = document.getElementById("login-alert");
    const submitBtn = loginForm.querySelector("button[type=submit]");

    // Clear any previous alerts
    alertEl.className = "alert hidden";
    alertEl.textContent = "";

    if (!email || !password) {
      showAlert(alertEl, "Please enter your email and password.", "error");
      return;
    }

    submitBtn.disabled = true;
    submitBtn.textContent = "Logging in...";

    try {
      // Send email + password to Flask backend
      // Flask checks the hash in the database and returns a token
      const data = await loginUser(email, password);

      // Save the returned user info and token to localStorage
      saveAuthInfo(data.user, data.token);

      showAlert(alertEl, "Login successful! Redirecting...", "success");

      // Redirect after a short delay
      setTimeout(() => {
        const redirect = new URLSearchParams(window.location.search).get("redirect");
        window.location.href = redirect || "index.html";
      }, 1000);
    } catch (err) {
      showAlert(alertEl, err.message, "error");
    } finally {
      submitBtn.disabled = false;
      submitBtn.textContent = "Login";
    }
  });
}

// ── Register Form ────────────────────────────────────────────
const registerForm = document.getElementById("register-form");
if (registerForm) {
  registerForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const name = document.getElementById("reg-name").value.trim();
    const email = document.getElementById("reg-email").value.trim();
    const password = document.getElementById("reg-password").value;
    const confirm = document.getElementById("reg-confirm").value;
    const alertEl = document.getElementById("register-alert");
    const submitBtn = registerForm.querySelector("button[type=submit]");

    alertEl.className = "alert hidden";
    alertEl.textContent = "";

    // Client-side validation before sending to the server
    if (!name || !email || !password) {
      showAlert(alertEl, "All fields are required.", "error");
      return;
    }
    if (password.length < 6) {
      showAlert(alertEl, "Password must be at least 6 characters.", "error");
      return;
    }
    if (password !== confirm) {
      showAlert(alertEl, "Passwords do not match.", "error");
      return;
    }

    submitBtn.disabled = true;
    submitBtn.textContent = "Creating account...";

    try {
      // Send name, email, password to Flask backend
      // Flask hashes the password and stores it in the database
      const data = await registerUser(name, email, password);

      saveAuthInfo(data.user, data.token);

      showAlert(alertEl, "Account created! Redirecting...", "success");

      setTimeout(() => {
        window.location.href = "index.html";
      }, 1000);
    } catch (err) {
      showAlert(alertEl, err.message, "error");
    } finally {
      submitBtn.disabled = false;
      submitBtn.textContent = "Create Account";
    }
  });
}

// ── Helper: show an alert message ────────────────────────────
function showAlert(el, message, type) {
  if (!el) return;
  el.textContent = message;
  el.className = `alert alert-${type}`;
}

// Run on every page to keep navbar up to date
updateNavbarAuth();

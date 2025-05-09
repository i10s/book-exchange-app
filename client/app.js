// client/app.js

// Base URL for all API calls
const API_BASE = location.origin;

// In-memory JWT
let token = null;

// DOM refs
const registerSec   = document.getElementById("register-section");
const registerForm  = document.getElementById("register-form");
const registerError = document.getElementById("register-error");

const loginSec      = document.getElementById("login-section");
const loginForm     = document.getElementById("login-form");
const loginError    = document.getElementById("login-error");

const booksSec      = document.getElementById("books-section");
const booksList     = document.getElementById("books-list");
const refreshBtn    = document.getElementById("refresh-books");

const addBookForm   = document.getElementById("add-book-form");
const addBookError  = document.getElementById("add-book-error");

// ─────────────────────────────────────────────────────────────────────────────
// 1) Sign-Up handler
registerForm.addEventListener("submit", async e => {
  e.preventDefault();
  registerError.textContent = "";

  // collect form data
  const formData = new FormData(registerForm);
  const payload = {
    username: formData.get("username"),
    email:    formData.get("email"),
    password: formData.get("password"),
  };

  try {
    // call register endpoint
    const res = await fetch(`${API_BASE}/auth/register`, {
      method:  "POST",
      headers: { "Content-Type": "application/json" },
      body:    JSON.stringify(payload),
    });
    if (!res.ok) {
      const err = await res.json().catch(()=>({}));
      throw new Error(err.detail || `Failed to register (${res.status})`);
    }

    // on successful sign-up, auto-login
    const loginParams = new URLSearchParams();
    loginParams.append("username", payload.username);
    loginParams.append("password", payload.password);

    const loginRes = await fetch(`${API_BASE}/auth/token`, {
      method:  "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body:    loginParams,
    });
    if (!loginRes.ok) throw new Error("Registered but login failed");

    const { access_token } = await loginRes.json();
    token = access_token;

    // hide auth forms, show books
    registerSec.style.display = "none";
    loginSec.style.display    = "none";
    booksSec.style.display    = "block";

    // load books
    await loadBooks();

  } catch (err) {
    registerError.textContent = err.message;
  }
});

// ─────────────────────────────────────────────────────────────────────────────
// 2) Login handler
loginForm.addEventListener("submit", async e => {
  e.preventDefault();
  loginError.textContent = "";

  const form = new URLSearchParams(new FormData(loginForm));
  try {
    const res = await fetch(`${API_BASE}/auth/token`, {
      method:  "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body:    form,
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || "Invalid credentials");
    }

    const data = await res.json();
    token = data.access_token;

    // hide auth forms, show books
    registerSec.style.display = "none";
    loginSec.style.display    = "none";
    booksSec.style.display    = "block";

    // initial fetch
    await loadBooks();

  } catch (err) {
    loginError.textContent = err.message;
  }
});

// ─────────────────────────────────────────────────────────────────────────────
// 3) Fetch & render books
async function loadBooks() {
  booksList.innerHTML = "";
  try {
    const res = await fetch(`${API_BASE}/books`, {
      headers: { "Authorization": `Bearer ${token}` },
    });
    if (!res.ok) {
      throw new Error(`Error ${res.status}: ${res.statusText}`);
    }
    const books = await res.json();
    if (books.length === 0) {
      booksList.innerHTML = `<li>No books found.</li>`;
      return;
    }
    books.forEach(b => {
      const li = document.createElement("li");
      li.textContent = `${b.title} by ${b.author} (Grade ${b.grade ?? "—"})`;
      booksList.appendChild(li);
    });

  } catch (err) {
    booksList.innerHTML = `<li class="error">${err.message}</li>`;
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// 4) Refresh button
refreshBtn.addEventListener("click", () => {
  if (!token) return;
  loadBooks();
});

// ─────────────────────────────────────────────────────────────────────────────
// 5) Add-book form handler
addBookForm.addEventListener("submit", async e => {
  e.preventDefault();
  addBookError.textContent = "";

  const data = {};
  new FormData(addBookForm).forEach((value, key) => {
    if (["grade","owner_id"].includes(key) && value !== "") {
      data[key] = Number(value);
    } else if (value !== "") {
      data[key] = value;
    }
  });

  try {
    const res = await fetch(`${API_BASE}/books`, {
      method:  "POST",
      headers: {
        "Content-Type":  "application/json",
        "Authorization": `Bearer ${token}`,
      },
      body: JSON.stringify(data),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || `Failed to add book (${res.status})`);
    }

    addBookForm.reset();
    await loadBooks();

  } catch (err) {
    addBookError.textContent = err.message;
  }
});

// client/app.js

// Base URL for all API calls
const API_BASE = location.origin;

// State
let token = null;

// DOM refs
const loginSec      = document.getElementById("login-section");
const loginForm     = document.getElementById("login-form");
const loginError    = document.getElementById("login-error");

const booksSec      = document.getElementById("books-section");
const booksList     = document.getElementById("books-list");
const refreshBtn    = document.getElementById("refresh-books");

const addBookForm   = document.getElementById("add-book-form");
const addBookError  = document.getElementById("add-book-error");

// ─────────────────────────────────────────────────────────────────────────────
// 1) Login handler
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

    const { access_token } = await res.json();
    token = access_token;

    // Toggle views
    loginSec.style.display = "none";
    booksSec.style.display = "block";

    // Initial load
    await loadBooks();

  } catch (err) {
    loginError.textContent = err.message;
  }
});

// ─────────────────────────────────────────────────────────────────────────────
// 2) Fetch & render books
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
// 3) Refresh button
refreshBtn.addEventListener("click", () => {
  if (!token) return;
  loadBooks();
});

// ─────────────────────────────────────────────────────────────────────────────
// 4) Add-book form handler
addBookForm.addEventListener("submit", async e => {
  e.preventDefault();
  addBookError.textContent = "";

  // Build payload
  const data = {};
  new FormData(addBookForm).forEach((value, key) => {
    // Convert numeric fields to numbers
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

    // Success! Clear form and refresh list
    addBookForm.reset();
    await loadBooks();

  } catch (err) {
    addBookError.textContent = err.message;
  }
});

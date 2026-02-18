const signInButton = document.getElementById('signInButton');
const Signindiv = document.getElementById('Signin');
const signUpdiv = document.getElementById('signUp');
const mobileSigninForm = document.getElementById("loginForm");
const LapSigninForm = document.getElementById("LapSignIn");


// ------------- Modal popup for success -------------
function showSuccessModal(message, redirectUrl = null, delay = 0) {
    // Overlay
    const overlay = document.createElement("div");
    overlay.className = "modal-overlay";

    // Modal
    const modal = document.createElement("div");
    modal.className = "modal-card";

    modal.innerHTML = `
        <div class="modal-icon">
            <svg viewBox="0 0 24 24" fill="none">
                <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
                <path d="M8 12.5l2.5 2.5L16 9" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
        </div>

        <h2>Success</h2>
        <p>${message}</p>

        <button class="modal-btn">Continue</button>
    `;

    overlay.appendChild(modal);
    document.body.appendChild(overlay);

    // Trigger animation
    requestAnimationFrame(() => overlay.classList.add("show"));

    const closeModal = () => {
        overlay.classList.remove("show");
        setTimeout(() => overlay.remove(), 250);
    };

    // Button click
    modal.querySelector(".modal-btn").onclick = () => {
        closeModal();
        if (redirectUrl) window.location.href = redirectUrl;
    };

    // Click outside to close
    overlay.onclick = (e) => {
        if (e.target === overlay) closeModal();
    };

    // Escape key
    document.addEventListener("keydown", function escClose(e) {
        if (e.key === "Escape") {
            closeModal();
            document.removeEventListener("keydown", escClose);
        }
    });

    // Auto redirect
    if (redirectUrl && delay > 0) {
        setTimeout(() => {
            closeModal();
            window.location.href = redirectUrl;
        }, delay);
    }
}

function showErrorModal(message) {
    const overlay = document.createElement("div");
    overlay.className = "modal-overlay";

    const modal = document.createElement("div");
    modal.className = "modal-card error";

    modal.innerHTML = `
        <div class="modal-icon error-icon">
            <svg viewBox="0 0 24 24" fill="none">
                <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
                <path d="M15 9l-6 6M9 9l6 6"
                      stroke="currentColor"
                      stroke-width="2"
                      stroke-linecap="round"/>
            </svg>
        </div>

        <h2>Error</h2>
        <p>${message}</p>

        <button class="modal-btn error-btn">Close</button>
    `;

    overlay.appendChild(modal);
    document.body.appendChild(overlay);

    requestAnimationFrame(() => overlay.classList.add("show"));

    const close = () => {
        overlay.classList.remove("show");
        setTimeout(() => overlay.remove(), 250);
    };

    modal.querySelector(".error-btn").onclick = close;

    overlay.onclick = (e) => {
        if (e.target === overlay) close();
    };

    document.addEventListener("keydown", function esc(e) {
        if (e.key === "Escape") {
            close();
            document.removeEventListener("keydown", esc);
        }
    });
}

// -------------------------
// Loading Spinner Helpers
// -------------------------

function setLoading(button, text = "Loading...") {
    button.dataset.originalText = button.innerHTML;
    button.disabled = true;

    // Add spinner HTML (simple rolling dots)
    button.innerHTML = `
        <span class="spinner"></span> ${text}
    `;
}

function clearLoading(button) {
    button.innerHTML = button.dataset.originalText || "Submit";
    button.disabled = false;
}

// ------------- Spinner CSS dynamically (optional) -------------
const style = document.createElement("style");
style.innerHTML = `
.spinner {
    border: 3px solid rgba(255,255,255,0.3);
    border-top: 3px solid #fff;
    border-radius: 50%;
    width: 18px;
    height: 18px;
    display: inline-block;
    margin-right: 8px;
    animation: spin 0.8s linear infinite;
}
@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}
`;
document.head.appendChild(style);



signInButton.addEventListener('click', function () {
    signUpdiv.style.display = 'none';
    Signindiv.style.display = 'block'
});

mobileSigninForm.addEventListener("submit", async function (e) {
    e.preventDefault();

    const loginbtn = document.getElementById("mobilelbtn");
    const d_data = {
        username : document.getElementById("username"),
        password : document.getElementById("password")
    };

    setLoading(loginbtn);
    try {
        const response = await fetch("/loginp", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(d_data)
        });

        const data = await response.json();

        clearLoading(loginbtn);

        if (data.status === "success") {
            window.location.href = "/verify1";
            
        } else {
            showErrorModal(data.message || "Login failed");
        }

    } catch (error) {
        clearLoading(loginbtn);
        console.error("Error:", error);
        showErrorModal("An error occurred during Login");
    }
});


LapSigninForm.addEventListener("submit", async function (e) {
    e.preventDefault();

    const loginbtn = document.getElementById("Lapbtn");

    const d_data = {
        username : document.getElementById("Tabusername").value,
        password : document.getElementById("1password").value
    };


    setLoading(loginbtn);
    try {
        const response = await fetch("/loginp", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(d_data)
        });

        const data = await response.json();

        clearLoading(loginbtn);

        if (data.status === "success") {
            window.location.href = "/verify1";
            
        } else {
            showErrorModal(data.message || "Login failed");
        }

    } catch (error) {
        clearLoading(loginbtn);
        console.error("Error:", error);
        showErrorModal("An error occurred during Login");
    }
});


//This will hold the login and registration logic
// Keys are generated and stored by the backend

// GLOBAL KEY STORAGE — ater by chat.js after login
window.userPrivateKey = null;     // decrypted private key (CryptoKey)
window.userPublicKeyPem = null;   // public key PEM
window.currentUserId = null;
//REGISTER USER
// Backend generates RSA keys, so frontend only sends username and password
async function registerUser() {
    // Get values from registration form inputs
    const username = document.getElementById("regUsername").value;
    const password = document.getElementById("regPassword").value;
  try {
        // Send registration request to backend
        const res = await fetch("https://secure-chat-project.onrender.com/register", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username, password })
        });

        // Parse backend response
        const data = await res.json();

        // res.ok = true for 200–299 status codes (ex: 201 Created)
        if (res.ok) {
            alert("Registration successful!");
        } else {
            // Show backend error message (ex: "Username already exists")
            alert("Registration failed: " + (data.error || data.message));
        }

    } catch (err) {
        // Handles network issues (backend offline, wrong URL, etc.)
        console.error("Network error:", err);
        alert("Network error — backend might be offline.");
    }
}



//LOGIN USER
// Backend returns a success flag and the user's public/private key PEMs

async function loginUser() {
    const username = document.getElementById("loginUsername").value;
    const password = document.getElementById("loginPassword").value;

 // Send login request to backend
    const res = await fetch("https://secure-chat-project.onrender.com/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password })
    });

    // Parse backend response
    const data = await res.json();

    // Backend returns { success: false } for invalid login
    if (!data.success) {
        alert("Login failed: " + data.message);
        return;
    }
    // store user id
    window.currentUserId = data.user_id;

    // Auto-fill "My User ID" field
    document.getElementById("myId").value = data.user_id;

    // store public key
    window.userPublicKeyPem = data.publicKey;

    // decrypt private key
    window.userPrivateKey = await decryptPrivateKey(data.encryptedPrivateKey, password);
 
    // Show login status
    document.getElementById("loginStatus").textContent =
        `Login successful! Your User ID is ${data.user_id}`;

    // Hide login/register panel
    document.getElementById("authPanel").classList.add("hidden");

    // Highlight logged-in user in the user list
    setTimeout(() => highlightCurrentUser(), 300);

    // Notify chat.js that login is complete
    document.dispatchEvent(new Event("loginSuccess")); 
       
}


//BUTTON LISTEN EVENTS

// Trigger registration when the Register button is clicked
document.getElementById("registerBtn").addEventListener("click", registerUser);
// Trigger login when the Login button is clicked
document.getElementById("loginBtn").addEventListener("click", loginUser);
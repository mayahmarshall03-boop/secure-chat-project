//This is for sending, reciving, and decrypting messages

window.sentMessages = {};

// GLOBAL CHAT CONTEXT
// These MUST exist so all scripts can access them
window.currentUserId = window.currentUserId || null; 
window.currentChatUserId = null; 
window.currentChatUserPublicKeyPem = null;



// Set active chat context
function setChatContext(myId, otherUserId, otherUserPublicKeyPem) {
    window.currentUserId = myId;
    window.currentChatUserId = otherUserId //the person i chose
    window.currentChatUserPublicKeyPem = otherUserPublicKeyPem 

    fetchMessages();

    // Auto‑fetch every 2 seconds
    if (window.messageInterval) clearInterval(window.messageInterval);
    window.messageInterval = setInterval(fetchMessages, 2000);
}


//SEND MESSAGE (HYBRID ENCRYPTION - AES and RSA)
async function sendMessage() {
    console.log("currentChatUserId =", window.currentChatUserId);

    const input = document.getElementById("messageInput");
    const message = input.value.trim(); //gets value and removes leading and trailing whitespace
    if (!message) return; // dont send any empty messages

    // Save your plaintext before encrypting
   const timestamp = Date.now();
    window.sentMessages[timestamp] = message;
 

    //ensures user is logged in and chat partner is selected
    if (!window.currentChatUserId || !window.currentChatUserPublicKeyPem) {
        alert ("Please select a user to chat with before sending a message.");
        return;
    }

    if (!window.userPrivateKey) {
        alert("You must log in before sending messages.");
        return;
    }

    try {
        // Generates a fresh AES key for this message because its fast and handles large messages 
        const aesKey = await generateAesKey();

        //encrypt the plaintext message using AES-GCM
        const aesEncrypted = await encryptWithAes(message, aesKey);

        // export the AES key into raw bytes (base64)
        const aesKeyBase64 = await exportAesKeyToBase64(aesKey);

        // encrypt the AES key using the recipient's RSA public key (simple Base64)
        const encryptedKeyReceiver = await encryptAesKeyWithRsa(
        window.currentChatUserPublicKeyPem,
        aesKeyBase64
        );

        // Encrypt AES key for sender (NEW)
        const encryptedKeySender = await encryptAesKeyWithRsa(
            window.userPublicKeyPem,   // YOUR OWN PUBLIC KEY
            aesKeyBase64
        );
        //package the AES-encrypted  message into a JSON string
        const encryptedMessagePayload = {
            iv: aesEncrypted.iv,
            ciphertext: aesEncrypted.ciphertext
        };

        //send everything to the backend
        const res = await fetch("https://secure-chat-project.onrender.com/messages/send", {
        method: "POST",
        headers: {"Content-Type": "application/json" },
        body: JSON.stringify({
            sender_id: window.currentUserId,
            receiver_id: window.currentChatUserId,
            encrypted_message: encryptedMessagePayload,
            encrypted_key_receiver: encryptedKeyReceiver, // NEW
            encrypted_key_sender: encryptedKeySender,     // NEW
            client_timestamp: timestamp
        })
    });

        // Try to read the backend's JSON response.
        // If it fails, use an empty object instead of crashing.
        const data = await res.json().catch(() => ({}));

        // Element where we show "Message sent" or errors
        const statusEl = document.getElementById("messageStatus");

        // Check if the request succeeded
        if (res.ok && (data.success === undefined || data.success === true)) {

            
            // Show success message
            statusEl.textContent = "Message sent!";
            statusEl.style.color = "green";

            // Clear the input box
            input.value = "";

            // Immediately show your own message in the chat
            displayMessage(message, true);

            // Reload messages so the new one appears
            fetchMessages();

        } else {
            // Show backend error message
            const msg = data.error || data.message || "Failed to send message.";
            statusEl.textContent = msg;
            statusEl.style.color = "red";
        }

    } catch (err) {
        // Handles network or unexpected errors
        console.error("Error sending message:", err);
        const statusEl = document.getElementById("messageStatus");
        statusEl.textContent = "Error sending message.";
        statusEl.style.color = "red";
    }

    
}


//FETCH MESSAGES
async function fetchMessages(){
    //stop if user isnt logged in
    if (!window.currentUserId) {
        console.error("currentUserId is missing");
        return;
    }

    // ask backend for all the messages where you are the receiver
    const res = await fetch(
    `https://secure-chat-project.onrender.com/messages/conversation?user1=${window.currentUserId}&user2=${window.currentChatUserId}`);
    const data = await res.json();

    console.log("RAW messages from backend:", data);

    const container = document.getElementById("messagesContainer");
    container.innerHTML = "";

    //checks if the backend catually returned messages
    if (!data.messages || !Array.isArray(data.messages)) return;

    //loops through each messaage and decrypts it
    for (const msg of data.messages) {
        const isMe = msg.sender_id === window.currentUserId;

        if (isMe) {
           // You sent this message → decrypt using your sender key
            try {
                const decryptedText = await decryptHybridMessage({
                    encrypted_message: msg.encrypted_message,
                    encrypted_key: msg.encrypted_key_sender   // NEW
                });
                displayMessage(decryptedText, true);
            } catch (e) {
                console.error("decryptHybridMessage error:", e);
                displayMessage("(failed to decrypt)", true);
            }
            continue;
        }

        // You received this message → decrypt using receiver key
        try {
            const decryptedText = await decryptHybridMessage({
                encrypted_message: msg.encrypted_message,
                encrypted_key: msg.encrypted_key_receiver    // NEW
            });
            displayMessage(decryptedText, false);
        } catch (e) {
            console.error("decryptHybridMessage error:", e);
            displayMessage("(failed to decrypt)", false);
        }
    }
}

//DISPLAY MESSAGES
function displayMessage(text, isMe) {
    const container = document.getElementById("messagesContainer");

    const div = document.createElement("div");
    div.className = isMe ? "message me" : "message them";
    div.textContent = text;

    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
}



//DECRYPT ONE HYBRID-ENCRYPTED MESSAGE
async function decryptHybridMessage(msg) {
    // RSA-decrypt AES key
    const aesKey = await decryptAesKey(
        msg.encrypted_key,
        window.userPrivateKey
    );

    // Parse AES-encrypted chat payload
    const payload = JSON.parse(msg.encrypted_message);
    const { iv, ciphertext } = payload;

    // AES-decrypt the chat message
    return await decryptWithAes(ciphertext, iv, aesKey);
}

// Highlights the logged‑in user in the user list
function highlightCurrentUser() {
    const items = document.querySelectorAll(".user-item");
    items.forEach(item => {
        if (parseInt(item.dataset.userId) === window.currentUserId) {
            item.classList.add("active-user");
        } else {
            item.classList.remove("active-user");
        }
    });
}

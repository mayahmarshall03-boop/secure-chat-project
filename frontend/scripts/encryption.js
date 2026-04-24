//This file handles all client‑side encryption for the secure messaging app

//Convert PEM Key to CryptoKey
async function importRSAPublicKey(pem) {
    const pemHeader = "-----BEGIN PUBLIC KEY-----";
    const pemFooter = "-----END PUBLIC KEY-----";
    const pemContents = pem.replace(pemHeader, "").replace(pemFooter, "").replace(/\s/g, "");
    const binaryDer = Uint8Array.from(atob(pemContents), c => c.charCodeAt(0));

    return window.crypto.subtle.importKey(
        "spki",
        binaryDer,
        {
            name: "RSA-OAEP",
            hash: "SHA-256"
        },
        true,
        ["encrypt"]
    );
}

//Convert ArrayBuffer to Base64
function arrayBufferToBase64(buffer) {
    let binary = "";
    const bytes = new Uint8Array(buffer);
    bytes.forEach(b => binary += String.fromCharCode(b));
    return btoa(binary);
}

//Encrypt a message for a recipient
async function encryptMessage(recipientPublicKeyPem, plaintext) {
    // Import the recipient's RSA public key
    const publicKey = await importRSAPublicKey(recipientPublicKeyPem);

    // Generate a random AES-GCM key
    const aesKey = await window.crypto.subtle.generateKey(
        {
            name: "AES-GCM",
            length: 256
        },
        true,
        ["encrypt", "decrypt"]
    );

    // Encrypt the plaintext using AES-GCM
    const encoder = new TextEncoder();
    const iv = window.crypto.getRandomValues(new Uint8Array(12)); // 96-bit IV
    const encryptedMessageBuffer = await window.crypto.subtle.encrypt(
        {
            name: "AES-GCM",
            iv: iv
        },
        aesKey,
        encoder.encode(plaintext)
    );

    // Export AES key to raw bytes
    const rawAesKey = await window.crypto.subtle.exportKey("raw", aesKey);

    // Encrypt AES key using RSA-OAEP
    const encryptedAesKeyBuffer = await window.crypto.subtle.encrypt(
        {
            name: "RSA-OAEP"
        },
        publicKey,
        rawAesKey
    );

    // Convert everything to base64 for sending to backend
    return {
        encryptedMessage: arrayBufferToBase64(encryptedMessageBuffer),
        encryptedKey: arrayBufferToBase64(encryptedAesKeyBuffer),
        iv: arrayBufferToBase64(iv)
    };
}



async function encryptAesKeyWithRsa(publicKeyPem, aesKeyBase64) {
    const publicKey = await importRSAPublicKey(publicKeyPem);

    const rawAesKey = base64ToArrayBuffer(aesKeyBase64);

    const encrypted = await window.crypto.subtle.encrypt(
        { name: "RSA-OAEP" },
        publicKey,
        rawAesKey
    );

    return arrayBufferToBase64(encrypted); // plain Base64 string
}
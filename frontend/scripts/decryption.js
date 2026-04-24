//This file handles all client‑side decryption for the secure messaging app

// Convert Base64 to ArrayBuffer
function base64ToArrayBuffer(base64) {
    const binary = atob(base64);
    const bytes = new Uint8Array(binary.length);
    for (let i = 0; i < binary.length; i++) {
        bytes[i] = binary.charCodeAt(i);
    }
    return bytes.buffer;
}

// Import RSA Private Key (PKCS8 DER)
async function importRSAPrivateKey(derBuffer) {
    return window.crypto.subtle.importKey(
        "pkcs8",
        derBuffer,
        {
            name: "RSA-OAEP",
            hash: "SHA-256"
        },
        true,
        ["decrypt"]
    );
}

// Derive AES key from password (PBKDF2)
async function deriveKeyFromPassword(password, salt) {
    const encoder = new TextEncoder();

    const keyMaterial = await window.crypto.subtle.importKey(
        "raw",
        encoder.encode(password),
        "PBKDF2",
        false,
        ["deriveKey"]
    );

    return window.crypto.subtle.deriveKey(
        {
            name: "PBKDF2",
            salt: salt,
            iterations: 250000,
            hash: "SHA-256"
        },
        keyMaterial,
        {
            name: "AES-GCM",
            length: 256
        },
        true,
        ["decrypt"]
    );
}

// Decrypt the user's encrypted private key
// Convert PEM (PKCS8) to ArrayBuffer
function pemToArrayBuffer(pem) {
    const base64 = pem
        .replace("-----BEGIN PRIVATE KEY-----", "")
        .replace("-----END PRIVATE KEY-----", "")
        .replace(/\s+/g, ""); // remove all whitespace/newlines

    const binary = atob(base64);
    const bytes = new Uint8Array(binary.length);
    for (let i = 0; i < binary.length; i++) {
        bytes[i] = binary.charCodeAt(i);
    }
    return bytes.buffer;
}

// Import the user's private key (backend sends plain PEM)
async function decryptPrivateKey(privateKeyPem, password) {
    const derBuffer = pemToArrayBuffer(privateKeyPem);
    return importRSAPrivateKey(derBuffer);
}

// Decrypt a message using RSA private key and AES key
async function decryptMessage(encryptedMessageBase64, encryptedKeyBase64, ivBase64, privateKey) {
    // 1. Convert Base64 to ArrayBuffer
    const encryptedMessage = base64ToArrayBuffer(encryptedMessageBase64);
    const encryptedAesKey = base64ToArrayBuffer(encryptedKeyBase64);
    const iv = new Uint8Array(base64ToArrayBuffer(ivBase64));

    // 2. Decrypt AES key using RSA private key
    const rawAesKey = await window.crypto.subtle.decrypt(
        {
            name: "RSA-OAEP"
        },
        privateKey,
        encryptedAesKey
    );

    // 3. Import AES key
    const aesKey = await window.crypto.subtle.importKey(
        "raw",
        rawAesKey,
        {
            name: "AES-GCM"
        },
        false,
        ["decrypt"]
    );

    // 4. Decrypt message
    const decryptedBuffer = await window.crypto.subtle.decrypt(
        {
            name: "AES-GCM",
            iv: iv
        },
        aesKey,
        encryptedMessage
    );

    // 5. Convert bytes to text
    const decoder = new TextDecoder();
    return decoder.decode(decryptedBuffer);
}

// Decrypt AES key using RSA private key, return CryptoKey
async function decryptAesKey(encryptedKeyBase64, privateKey) {
    const encryptedAesKey = base64ToArrayBuffer(encryptedKeyBase64);

    const rawAesKey = await window.crypto.subtle.decrypt(
        { name: "RSA-OAEP" },
        privateKey,
        encryptedAesKey
    );

    return window.crypto.subtle.importKey(
        "raw",
        rawAesKey,
        { name: "AES-GCM" },
        true,
        ["decrypt"]
    );
}
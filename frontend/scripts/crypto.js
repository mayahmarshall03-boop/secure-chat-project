// this is for encryption, decryption, and key storage

//converts binary to base64
function arrayBufferToBase64(buffer) {
    const bytes = new Uint8Array(buffer);
    let binary = "";
    for (let i = 0; i < bytes.length; i++) {
        //converts raw bytes into a binary string
        binary += String.fromCharCode(bytes[i]);
    }
    return btoa(binary);
}

//converts base64 to binary
function base64ToArrayBuffer(base64) {
    const binary = atob(base64);
    const bytes = new Uint8Array(binary.length);
    for (let i = 0; i < binary.length; i++) {
        bytes[i] = binary.charCodeAt(i);
    }
    return bytes.buffer;
}

async function encryptPrivateKeyWithPassword(privateKeyPem, password){
    const enc = new TextEncoder();
    //converts password bytes into key material
    const keyMaterial = await crypto.subtle.importKey(
        "raw",
        enc.encode(password),
        "PBKDF2",
        false,
        ["deriveKey"]
    );
    //generate random salt
    const salt = crypto.getRandomValues(new Uint8Array(16));
    //derive a stong AES key from the password 
    const aesKey = await crypto.subtle.deriveKey(
        {
            name: "PBKDF2",
            salt: salt,
            iterations: 100000,
            hash: "SHA-256",
        },
        keyMaterial,
        { name: "AES-GCM", length: 256 },
        true,
        ["encrypt"]
    );
    //iv is the initialization vector
    const iv = crypto.getRandomValues(new Uint8Array(12));

    const ciphertext = await crypto.subtle.encrypt(
        {name: "AES-GCM", iv: iv },
        aesKey,
        enc.encode(privateKeyPem)
    );
    return{
        salt: arrayBufferToBase64(salt.buffer),
        iv: arrayBufferToBase64(iv.buffer),
        ciphertext: arrayBufferToBase64(ciphertext)
    };
}

async function decryptPrivateKeyWithPassword(encryptedData, password){
    const enc = new TextEncoder();
    
    const keyMaterial = await crypto.subtle.importKey(
        "raw",
        enc.encode(password),
        "PBKDF2",
        false,
        ["deriveKey"]
    );

    const salt = base64ToArrayBuffer(encryptedData.salt);
    const iv = base64ToArrayBuffer(encryptedData.iv);
    const ciphertext = base64ToArrayBuffer(encryptedData.ciphertext);

    const aesKey = await crypto.subtle.deriveKey(
        {
            name: "PBKDF2",
            salt: new Uint8Array(salt),
            iterations: 100000,
            hash: "SHA-256",
        },
        keyMaterial,
        { name: "AES-GCM", length: 256 },
        true,
        ["decrypt"]
    );

    const decrypted = await crypto.subtle.decrypt(
        { name: "AES-GCM", iv: new Uint8Array(iv) },
        aesKey,
        ciphertext
    );
    return new TextDecoder().decode(decrypted);
}

async function importKey(pem, type = "public"){
    // Remove PEM header/footer and newlines
    const pemBody = pem
        .replace(/-----BEGIN PUBLIC KEY-----/, "")
        .replace(/-----END PUBLIC KEY-----/, "")
        .replace(/-----BEGIN PRIVATE KEY-----/, "")
        .replace(/-----END PRIVATE KEY-----/, "")
        .replace(/\s+/g, "");

    // Convert Base64 to ArrayBuffer
    const binaryDer = base64ToArrayBuffer(pemBody);

    // Import based on key type
    if (type === "public") {
        return crypto.subtle.importKey(
            "spki", //public key format
            binaryDer,
            { name: "RSA-OAEP", hash: "SHA-256" },
            true,
            ["encrypt"] //allows to encrypt
        );
    } else {
        return crypto.subtle.importKey(
            "pkcs8", //private key format
            binaryDer,
            { name: "RSA-OAEP", hash: "SHA-256" },
            true,
            ["decrypt"] //allows to decrypt
        );
    }

}

async function encryptMessage(message, recipientPublicKeyPem){
    //Import the recipient's public key
    const publicKey = await importKey(recipientPublicKeyPem, "public");

    //Convert message text to bytes
    const enc = new TextEncoder();
    const encodedMessage = enc.encode(message);

    //Encrypt using RSA-OAEP
    const ciphertext = await crypto.subtle.encrypt(
        { name: "RSA-OAEP" },
        publicKey,
        encodedMessage
    );

    //Convert ciphertext to Base64 for storage/transmission
    return arrayBufferToBase64(ciphertext);
}

async function decryptMessage(ciphertextBase64, privateKeyPem){
    // Import your private key
    const privateKey = await importKey(privateKeyPem, "private");

    // Convert Base64 to ArrayBuffer
    const ciphertext = base64ToArrayBuffer(ciphertextBase64);

    // Decrypt using RSA-OAEP
    const decrypted = await crypto.subtle.decrypt(
        { name: "RSA-OAEP" },
        privateKey,
        ciphertext
    );

    // Convert decrypted bytes to text
    return new TextDecoder().decode(decrypted);
}


async function exportKey(key, type = "public"){
    //Export the key to DER format
    const exported = await crypto.subtle.exportKey(
        type === "public" ? "spki" : "pkcs8",
        key
    );

    //Convert ArrayBuffer to Base64
    const base64 = arrayBufferToBase64(exported);

    // Wrap in PEM formatting
    const pemHeader = type === "public"
        ? "-----BEGIN PUBLIC KEY-----"
        : "-----BEGIN PRIVATE KEY-----";

    const pemFooter = type === "public"
        ? "-----END PUBLIC KEY-----"
        : "-----END PRIVATE KEY-----";

    // Insert line breaks every 64 chars (PEM standard)
    const formatted = base64.match(/.{1,64}/g).join("\n");

    return `${pemHeader}\n${formatted}\n${pemFooter}`;
}




//AES ENCRYPTION FOR MESSAGES

// Generate random AES key
async function generateAesKey() {
    return crypto.subtle.generateKey(
        { name: "AES-GCM", length: 256 },
        true,
        ["encrypt", "decrypt"]
    );
}

// AES encrypt message
async function encryptWithAes(plaintext, aesKey) {
    const enc = new TextEncoder();
    const iv = crypto.getRandomValues(new Uint8Array(12));

    const ciphertext = await crypto.subtle.encrypt(
        { name: "AES-GCM", iv },
        aesKey,
        enc.encode(plaintext)
    );

    return {
        iv: arrayBufferToBase64(iv.buffer),
        ciphertext: arrayBufferToBase64(ciphertext)
    };
}

// AES decrypt message
async function decryptWithAes(ciphertextBase64, ivBase64, aesKey) {
    const ciphertext = base64ToArrayBuffer(ciphertextBase64);
    const iv = new Uint8Array(base64ToArrayBuffer(ivBase64));

    const decrypted = await crypto.subtle.decrypt(
        { name: "AES-GCM", iv },
        aesKey,
        ciphertext
    );

    return new TextDecoder().decode(decrypted);  
}  

async function exportAesKeyToBase64(aesKey) {
    const raw = await crypto.subtle.exportKey("raw", aesKey);
    return arrayBufferToBase64(raw);
}

async function importAesKeyFromBase64(base64Key) {
    const rawKey = base64ToArrayBuffer(base64Key);
    return crypto.subtle.importKey(
        "raw",
        rawKey,
        { name: "AES-GCM" },
        true,
        ["encrypt", "decrypt"]
    );
}
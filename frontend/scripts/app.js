// This file handles loading the list of users from the backend and updating the chat context

//LOAD USERS
async function loadUsers() {
    const res = await fetch("https://secure-chat-project.onrender.com/users");
    const data = await res.json();

    const list = document.getElementById("usersList");
    list.innerHTML = "";

    data.users.forEach(user => {
        const div = document.createElement("div");
        div.className = "user-item";
        div.textContent = `${user.user_id}: ${user.username}`;

        // CLICK TO START CHAT
        div.onclick = () => {
            console.log("Selected user public key:", user.public_key);

            // Set chat partner info
            setChatContext(window.currentUserId, user.user_id, user.public_key);
            // keeps hidden fields updated
            document.getElementById("otherId").value = user.user_id;
            document.getElementById("otherPubKey").value = user.public_key;

            // Load messages for this conversation
            fetchMessages();
        };

        list.appendChild(div);
    });
}
// Run loadUsers after the user logs in
document.addEventListener("loginSuccess", loadUsers);










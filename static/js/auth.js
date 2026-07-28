// ================================
// AUTHENTICATION MODULE
// ================================


// ================================
// LOGIN
// ================================
async function login() {

    const emailInput = document.getElementById('emailInput');
    const passwordInput = document.getElementById('passwordInput');

    const loginBtn = document.getElementById('loginBtn');
    const errorDiv = document.getElementById('loginError');


    const email = emailInput.value.trim();
    const password = passwordInput.value.trim();


    errorDiv.textContent = "";


    if (!email || !email.includes("@")) {
        errorDiv.textContent = "⚠️ Please enter a valid email";
        return;
    }


    if (!password) {
        errorDiv.textContent = "⚠️ Password required";
        return;
    }


    loginBtn.disabled = true;
    loginBtn.textContent = "Signing in...";


    try {

        const res = await fetch("/login", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                email: email,
                password: password
            })

        });


        const data = await res.json();


        if (res.ok) {

            localStorage.setItem(
                "user_id",
                data.user_id
            );

            localStorage.setItem(
                "email",
                data.email
            );


            currentUser = data.user_id;


            document.getElementById(
                "userEmailDisplay"
            ).textContent = data.email;


            showDashboard();

            loadHistory();


        } else {

            errorDiv.textContent =
                "❌ " + (data.error || "Login failed");

        }


    } catch(err) {

        errorDiv.textContent =
            "❌ Network error. Please try again.";

    }


    loginBtn.disabled = false;
    loginBtn.textContent = "Continue";

}


// ================================
// REGISTER
// ================================

async function register() {

    const errorDiv = document.getElementById("registerError");

    const fullName = document.getElementById("regFullNameInput").value.trim();
    const company = document.getElementById("regCompanyInput").value.trim();
    const email = document.getElementById("regEmailInput").value.trim();
    const password = document.getElementById("regPasswordInput").value;
    const confirm = document.getElementById("regConfirmPasswordInput").value;
    const agree = document.getElementById("agreeTerms").checked;

    errorDiv.textContent = "";

    if (!fullName) {
        errorDiv.textContent = "❌ Enter your full name";
        return;
    }

    if (!company) {
        errorDiv.textContent = "❌ Enter company name";
        return;
    }

    if (password !== confirm) {
        errorDiv.textContent = "❌ Passwords do not match";
        return;
    }

    if (!agree) {
        errorDiv.textContent = "❌ Please accept Terms";
        return;
    }

    try {

        const res = await fetch("/register", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                full_name: fullName,
                company_name: company,
                email: email,
                password: password
            })

        });

        const data = await res.json();

        if (res.ok) {

            alert("🎉 Account created. Please login.");

            showLogin();

        } else {

            errorDiv.textContent = "❌ " + data.error;

        }

    } catch (err) {

        errorDiv.textContent = "❌ Network error. Please try again.";

    }

}


// ================================
// LOGOUT
// ================================

function logout() {

    localStorage.removeItem("user_id");
    localStorage.removeItem("email");

    currentUser = null;
    historyData = [];

    showLogin();

    document.getElementById("emailInput").value = "";
    document.getElementById("passwordInput").value = "";

}



// ================================
// AUTO LOGIN
// ================================

window.onload = function () {

    const userId = localStorage.getItem("user_id");
    const email = localStorage.getItem("email");


    if (userId && email) {

        currentUser = Number(userId);

        document.getElementById('userEmailDisplay').textContent = email;

        showDashboard(false);

        loadHistory();

    } else {

        showLogin(false);

    }

};
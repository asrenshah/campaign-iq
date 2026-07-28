// ========================================
// UI FUNCTIONS + BROWSER HISTORY
// ========================================


function showLogin(push = false) {

    const loginScreen = document.getElementById('loginScreen');
    const registerScreen = document.getElementById('registerScreen');
    const dashboard = document.getElementById('dashboard');


    if (loginScreen) {
        loginScreen.classList.add('active');
    }

    if (registerScreen) {
        registerScreen.classList.remove('active');
    }

    if (dashboard) {
        dashboard.classList.remove('visible');
    }


    if (push) {
        history.pushState(
            {page: "login"},
            "",
            "#login"
        );
    }
}


function showRegister(push = true) {

    const loginScreen = document.getElementById('loginScreen');
    const registerScreen = document.getElementById('registerScreen');
    const dashboard = document.getElementById('dashboard');


    if (loginScreen) {
        loginScreen.classList.remove('active');
    }

    if (registerScreen) {
        registerScreen.classList.add('active');
    }

    if (dashboard) {
        dashboard.classList.remove('visible');
    }


    if (push) {
        history.pushState(
            {page: "register"},
            "",
            "#register"
        );
    }
}


function showDashboard(push = true) {

    const loginScreen = document.getElementById('loginScreen');
    const registerScreen = document.getElementById('registerScreen');
    const dashboard = document.getElementById('dashboard');


    if (loginScreen) {
        loginScreen.classList.remove('active');
    }

    if (registerScreen) {
        registerScreen.classList.remove('active');
    }

    if (dashboard) {
        dashboard.classList.add('visible');
    }


    if (push) {
        history.pushState(
            {page: "dashboard"},
            "",
            "#dashboard"
        );
    }
}


// ========================================
// BROWSER BACK BUTTON
// ========================================

window.onpopstate = function(event) {

    if (event.state && event.state.page === "register") {
        showRegister(false);
    } else {
        showLogin(false);
    }

};
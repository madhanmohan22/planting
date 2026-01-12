// Check auth
const token = localStorage.getItem('token');
if (!token && !window.location.href.includes('index.html')) {
    window.location.href = '/static/index.html';
}

function logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('role');
    localStorage.removeItem('user_id');
    window.location.href = '/static/index.html';
}

async function apiCall(url, method = 'GET', body = null) {
    const headers = {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
    };

    const config = {
        method,
        headers
    };

    if (body) {
        config.body = JSON.stringify(body);
    }

    const response = await fetch(url, config);
    if (response.status === 401) {
        logout();
        return null;
    }
    return response;
}

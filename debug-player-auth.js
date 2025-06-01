// Debug script for Player UI authentication issues
// Run this in the browser console when on the Player UI page

console.log("=== Player UI Authentication Debug ===");

// Check localStorage
console.log("\n1. Checking localStorage:");
const accessToken = localStorage.getItem('accessToken');
const refreshToken = localStorage.getItem('refreshToken');
const userId = localStorage.getItem('userId');

console.log("- Access Token exists:", !!accessToken);
console.log("- Access Token (first 20 chars):", accessToken ? accessToken.substring(0, 20) + "..." : "null");
console.log("- Refresh Token exists:", !!refreshToken);
console.log("- User ID:", userId);

// Check axios defaults
console.log("\n2. Checking axios defaults:");
if (window.axios) {
    console.log("- Authorization header:", window.axios.defaults.headers.common['Authorization'] || "Not set");
} else {
    console.log("- axios not available on window");
}

// Test API connectivity
console.log("\n3. Testing API connectivity:");
const apiUrl = window.location.origin.includes('.app.github.dev') 
    ? window.location.origin.replace('-3000.app.github.dev', '-8080.app.github.dev')
    : 'http://localhost:8080';

console.log("- API URL:", apiUrl);

// Test status endpoint (no auth required)
fetch(`${apiUrl}/api/v1/status`)
    .then(res => {
        console.log("- Status endpoint:", res.status, res.statusText);
        return res.json();
    })
    .then(data => console.log("- Status response:", data))
    .catch(err => console.error("- Status endpoint error:", err));

// Test auth endpoint with token
if (accessToken) {
    console.log("\n4. Testing authenticated endpoint:");
    fetch(`${apiUrl}/api/v1/auth/me`, {
        headers: {
            'Authorization': `Bearer ${accessToken}`,
            'Content-Type': 'application/json'
        }
    })
    .then(res => {
        console.log("- Auth endpoint:", res.status, res.statusText);
        if (!res.ok) {
            return res.json().then(err => Promise.reject(err));
        }
        return res.json();
    })
    .then(data => {
        console.log("- User data:", data);
        console.log("- User ID:", data.id);
        console.log("- Username:", data.username);
    })
    .catch(err => console.error("- Auth endpoint error:", err));

    // Test first login status
    console.log("\n5. Testing first login status:");
    fetch(`${apiUrl}/api/v1/first-login/status`, {
        headers: {
            'Authorization': `Bearer ${accessToken}`,
            'Content-Type': 'application/json'
        }
    })
    .then(res => {
        console.log("- First login endpoint:", res.status, res.statusText);
        return res.json();
    })
    .then(data => {
        console.log("- First login required:", data.requires_first_login);
        console.log("- Full response:", data);
    })
    .catch(err => console.error("- First login endpoint error:", err));

    // Test player state
    console.log("\n6. Testing player state:");
    fetch(`${apiUrl}/api/v1/player/state`, {
        headers: {
            'Authorization': `Bearer ${accessToken}`,
            'Content-Type': 'application/json'
        }
    })
    .then(res => {
        console.log("- Player state endpoint:", res.status, res.statusText);
        if (!res.ok) {
            return res.json().then(err => Promise.reject(err));
        }
        return res.json();
    })
    .then(data => {
        console.log("- Player credits:", data.credits);
        console.log("- Player turns:", data.turns);
        console.log("- Current sector:", data.current_sector_id);
        console.log("- Full player state:", data);
    })
    .catch(err => console.error("- Player state error:", err));
} else {
    console.log("\n4. Skipping authenticated endpoints - no access token found");
}

console.log("\n=== End Debug ===");
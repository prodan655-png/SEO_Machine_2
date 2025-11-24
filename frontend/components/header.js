// Shared Header Component
(function () {
    const headerHTML = `
    <header class="header">
        <div class="container">
            <div class="header-content">
                <div class="logo">
                    <a href="index.html" style="text-decoration: none; color: inherit; display: flex; align-items: center; gap: 0.5rem;">
                        <span style="font-size: 1.5rem;">🔍</span>
                        <div>
                            <h1 style="margin: 0; font-size: 1.25rem;">SEO Machine</h1>
                            <p class="tagline" style="margin: 0; font-size: 0.75rem; opacity: 0.8;">Professional Content Optimizer</p>
                        </div>
                    </a>
                </div>
                
                <nav class="main-nav">
                    <a href="index.html" class="nav-link" id="nav-dashboard">Dashboard</a>
                    <a href="editor.html" class="nav-link" id="nav-editor">Editor</a>
                    <a href="competitors.html" class="nav-link" id="nav-competitors">Competitors</a>
                </nav>

                <div class="api-status">
                    <span class="status-dot" id="apiStatus"></span>
                    <span class="status-text" id="apiStatusText">Checking...</span>
                </div>
            </div>
        </div>
    </header>
    `;

    // Insert header at the beginning of body
    document.body.insertAdjacentHTML('afterbegin', headerHTML);

    // Highlight active link
    const path = window.location.pathname;
    if (path.includes('editor.html')) {
        document.getElementById('nav-editor')?.classList.add('active');
    } else if (path.includes('competitors.html')) {
        document.getElementById('nav-competitors')?.classList.add('active');
    } else {
        document.getElementById('nav-dashboard')?.classList.add('active');
    }

    // Check API Status
    if (window.API) {
        window.API.checkHealth().then(isOk => {
            const dot = document.getElementById('apiStatus');
            const text = document.getElementById('apiStatusText');
            if (dot && text) {
                dot.style.background = isOk ? '#10b981' : '#ef4444';
                text.textContent = isOk ? 'Online' : 'Offline';
            }
        });
    }

    // Add styles for nav if not present
    const style = document.createElement('style');
    style.textContent = `
        .main-nav {
            display: flex;
            gap: 1.5rem;
            margin: 0 2rem;
        }
        .nav-link {
            color: var(--text-secondary);
            text-decoration: none;
            font-weight: 500;
            transition: color 0.2s;
            padding: 0.5rem 0;
            border-bottom: 2px solid transparent;
        }
        .nav-link:hover, .nav-link.active {
            color: var(--primary);
            border-bottom-color: var(--primary);
        }
    `;
    document.head.appendChild(style);
})();

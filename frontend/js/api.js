// API Client Module
const API_BASE = 'http://localhost:8000';

const API = {
    // Health Check
    checkHealth: async () => {
        try {
            const response = await fetch(`${API_BASE}/health`);
            return response.ok;
        } catch (e) {
            console.error('API Health Check Failed:', e);
            return false;
        }
    },

    // Analysis
    createAnalysis: async (keyword, language = 'uk', location = 'Ukraine') => {
        const response = await fetch(`${API_BASE}/api/analysis/create`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                keyword,
                language,
                location
            })
        });
        if (!response.ok) throw new Error('Failed to create analysis');
        return await response.json();
    },

    getAnalysis: async (id) => {
        const response = await fetch(`${API_BASE}/api/analysis/${id}`);
        if (!response.ok) throw new Error('Failed to get analysis');
        return await response.json();
    },

    scoreContent: async (analysisId, content) => {
        const response = await fetch(`${API_BASE}/api/analysis/${analysisId}/score`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ content })
        });
        if (!response.ok) throw new Error('Failed to score content');
        return await response.json();
    },

    // AI Tools
    generateBrief: async (analysisId) => {
        // Mock implementation for now as endpoint might not exist yet
        return {
            title: "Generated Brief",
            structure: ["Introduction", "Main Point 1", "Main Point 2", "Conclusion"]
        };
    },

    generateImages: async (analysisId, html, numImages = 3) => {
        const response = await fetch(`${API_BASE}/api/ai/generate-images`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                analysis_id: analysisId,
                article_html: html,
                num_images: numImages
            })
        });
        if (!response.ok) throw new Error('Failed to generate images');
        return await response.json();
    }
};

// Export globally
window.API = API;

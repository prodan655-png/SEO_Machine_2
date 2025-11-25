// SEO Machine - Central State Management
// Uses Alpine.js for reactivity

document.addEventListener('alpine:init', () => {
    Alpine.store('app', {
        // --- State ---
        currentAnalysisId: null,
        currentKeyword: '',

        // Content
        content: '',
        wordCount: 0,
        charCount: 0,

        // Scoring
        score: 0,
        scoreBreakdown: {
            terms: { score: 0, max: 60 },
            structure: { score: 0, max: 20 },
            headings: { score: 0, max: 20 }
        },

        // Guidelines
        terms: [], // Array of { term, count, min, max, status }
        structure: {}, // { word_count: { current, min, max }, ... }

        // UI State
        isLoading: false,
        activeTab: 'write', // 'write' | 'review'

        // --- Actions ---

        init() {
            console.log('🚀 AppState Initialized');
        },

        setAnalysis(id, keyword) {
            this.currentAnalysisId = id;
            this.currentKeyword = keyword;
        },

        updateContent(newContent) {
            this.content = newContent;
            // Simple word count (can be improved)
            const text = newContent.replace(/<[^>]*>/g, ' ');
            this.wordCount = text.trim().split(/\s+/).filter(w => w.length > 0).length;
            this.charCount = text.length;
        },

        updateScore(scoreData) {
            this.score = scoreData.total_score;
            this.scoreBreakdown = scoreData.breakdown;

            // Update terms list
            if (scoreData.term_details) {
                this.terms = scoreData.term_details.map(t => ({
                    term: t.term,
                    count: t.current,
                    min: t.recommended_min,
                    max: t.recommended_max,
                    status: t.status // 'low', 'good', 'high'
                }));
            }

            // Update structure metrics
            if (scoreData.structure_details) {
                this.structure = scoreData.structure_details;
            }
        },

        setLoading(state) {
            this.isLoading = state;
        }
    });
});

# Phase 6: AI Integration - Detailed Specification

## Overview
This phase adds 5 AI-powered modules that sit on top of the existing SEO analyzer, leveraging LLM capabilities to generate briefs, enhance content, create meta tags, provide coaching, and analyze competitors.

## Configuration

### config.yaml additions:
```yaml
ai:
  enabled: true
  provider: "gemini"  # gemini | openai | anthropic | ollama
  model: "gemini-1.5-pro"
  temperature: 0.7
  max_tokens: 4000
  features_enabled:
    - brief
    - enhance
    - meta
    - coach
    - intent
  rate_limits:
    brief: 10  # per hour per user
    enhance: 20
    meta: 15
    coach: 10
    intent: 5
```

### .env additions:
```bash
# AI Configuration
AI_PROVIDER=gemini
GEMINI_API_KEY=your_api_key_here
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
AI_MODEL=gemini-1.5-pro
AI_ENABLED=true
```

## Module 1: Brief & Outline Generator

**File**: `backend/modules/ai/ai_brief_generator.py`

**Purpose**: Generate SEO-optimized content brief with H1, H2/H3 structure, talking points, and FAQs

**API Endpoint**: `POST /api/analysis/{id}/ai/brief`

**Request**:
```json
{
  "content_type": "blog | category | landing",
  "tone": "neutral | friendly | expert"
}
```

**Response**:
```json
{
  "h1": "Кето дієта: повний гід для початківців у 2025 році",
  "sections": [
    {
      "h2": "Що таке кето дієта",
      "h3": ["Основні принципи кето дієти", "Як працює кетоз"],
      "talking_points": [
        "Пояснити механізм кетозу простою мовою",
        "Описати макронутрієнти: 70% жирів, 25% білків, 5% вуглеводів"
      ]
    }
  ],
  "faqs": [
    "Скільки кілограмів можна скинути на кето дієті?",
    "Чи можна їсти фрукти на кето?"
  ],
  "meta": {
    "estimated_word_count": 1850,
    "sections_count": 6,
    "tokens_used": 1876
  }
}
```

## Module 2: Content Enhancer

**File**: `backend/modules/ai/ai_content_enhancer.py`

**Purpose**: Rewrite/expand text fragments to naturally integrate missing terms

**API Endpoint**: `POST /api/analysis/{id}/ai/enhance`

**Request**:
```json
{
  "fragment_text": "Original text...",
  "target_terms": ["кето дієта", "схуднення"],
  "max_words": 200,
  "style": "friendly"
}
```

**Response**:
```json
{
  "original_length": 150,
  "enhanced_text": "Кето дієта - це низьковуглеводний раціон...",
  "new_length": 185,
  "terms_added": [
    {"term": "кето дієта", "count": 2, "positions": [0, 95]},
    {"term": "схуднення", "count": 1, "positions": [142]}
  ],
  "tokens_used": 456
}
```

## Module 3: Title & Meta Generator

**File**: `backend/modules/ai/ai_meta_generator.py`

**Purpose**: Generate multiple variants of SEO titles, meta descriptions, H1s, and intro paragraphs

**API Endpoint**: `POST /api/analysis/{id}/ai/meta`

**Response**:
```json
{
  "titles": [
    {"text": "Кето дієта: повний гід 2025 | Меню, результати, поради", "length": 52, "keyword_included": true}
  ],
  "descriptions": [
    {"text": "Кето дієта для схуднення ✓ Докладне меню ✓ Список продуктів...", "length": 157}
  ],
  "h1_variants": [
    "Кето дієта: повний гід для початківців у 2025 році"
  ],
  "intro_paragraphs": [
    "Кето дієта - один з найефективніших способів схуднення..."
  ],
  "tokens_used": 892
}
```

## Module 4: Score Coach / Explainer

**File**: `backend/modules/ai/ai_score_explainer.py`

**Purpose**: Provide actionable advice to improve Content Score

**API Endpoint**: `POST /api/analysis/{id}/ai/coach`

**Request**:
```json
{
  "target_score": 75
}
```

**Response**:
```json
{
  "current_score": 54,
  "target_score": 75,
  "gap": 21,
  "improvement_steps": [
    {
      "priority": "high",
      "action": "Додайте терміни 'кетоз' (4-6 разів) та 'низьковуглеводна дієта' (3-5 разів) у текст",
      "expected_gain": 8,
      "category": "terms",
      "difficulty": "easy"
    }
  ],
  "summary": "Фокус на термінах дасть найбільший приріст (+8)...",
  "tokens_used": 1234
}
```

## Module 5: Competitor & Intent Analyzer

**File**: `backend/modules/ai/ai_competitor_analyzer.py`

**Purpose**: Classify search intent and identify content gaps

**API Endpoint**: `POST /api/analysis/{id}/ai/intent`

**Response**:
```json
{
  "intent": {
    "primary": "informational",
    "secondary": "commercial",
    "confidence": 0.85
  },
  "competitor_summaries": [
    {
      "position": 1,
      "url": "example.com/keto",
      "summary": "Докладний гід про кето дієту з науковими дослідженнями..."
    }
  ],
  "common_topics": [
    {"topic": "Принципи кето дієти", "coverage": "9/10"}
  ],
  "content_gaps": [
    "Калькулятор макронутрієнтів для кето",
    "Порівняння кето з іншими дієтами"
  ],
  "recommendations": [
    "Додайте практичний калькулятор або таблицю"
  ],
  "tokens_used": 3456
}
```

## Frontend Integration

### New UI Elements:

1. **В блоці Guidelines**:
   - Button: "🤖 Згенерувати бриф"
   - Modal with content type/tone selection
   - Display generated structure in expandable panel

2. **В редакторі контенту**:
   - Context menu on text selection: "✨ Покращити фрагмент"
   - Sidebar with missing terms checkboxes
   - Slider for max_words

3. **В блоці Guidelines (новапанель)**:
   - Button: "📝 AI Title & Meta"
   - Display variants in cards with copy buttons

4. **В блоці Content Score**:
   - Button: "💡 AI-план покращень"
   - Prioritized checklist with checkboxes
   - Progress bar showing expected score

5. **В блоці SERP & Competitors**:
   - Button: "🎯 Аналіз інтенту"
   - Intent badge
   - Expandable competitor summaries

## Implementation Notes

### Rate Limiting
```python
@app.middleware("http")
async def ai_rate_limiter(request, call_next):
    # Check user's AI feature usage against config limits
    # Store usage in database or Redis
    # Return 429 if limit exceeded
```

### Token Cost Estimation
- Brief generation: ~2000 tokens
- Content enhancement: ~1500 tokens  
- Meta generation: ~1000 tokens
- Score coaching: ~1500 tokens
- Competitor analysis: ~3000-5000 tokens

### Prompt Engineering Best Practices
1. Always specify output format (JSON)
2. Provide concrete examples
3. Set character/word limits
4. Specify language explicitly
5. Include anti-spam instructions

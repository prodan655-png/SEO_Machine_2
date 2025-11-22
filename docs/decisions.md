# Architecture Decisions

This document records important architectural decisions made during the development of SEO Analyzer.

## ADR-001: Use SQLite for Initial Version

**Date**: 2025-11-22

**Status**: Accepted

**Context**: Need to choose a database for storing analyses, competitors, terms, and guidelines.

**Decision**: Use SQLite for initial version with SQLAlchemy ORM, allowing easy migration to PostgreSQL later.

**Rationale**:
- No external dependencies for development
- Easy to back up (single file)
- SQLAlchemy provides database-agnostic code
- Sufficient for single-user deployment
- Can migrate to PostgreSQL when multi-user support is needed

**Consequences**:
- Limited concurrent write performance
- No built-in replication
- File-based storage

---

## ADR-002: Async Background Processing for Analysis Creation

**Date**: 2025-11-22

**Status**: Accepted

**Context**: Analysis creation involves SERP fetching, scraping 10+ pages, NLP processing, which can take 30-60 seconds.

**Decision**: Use FastAPI background tasks with polling-based status checks.

**Rationale**:
- Better UX (no long HTTP request timeouts)
- Frontend can show progress indicator
- Allows cancellation of long-running tasks
- Simpler than implementing full job queue initially

**Consequences**:
- Frontend must implement polling logic
- No persistence of background tasks (lost on server restart)
- May need to migrate to Celery for production scale

---

## ADR-003: Mock APIs in Development Mode

**Date**: 2025-11-22

**Status**: Accepted

**Context**: SERP API and LLM API calls cost money and have rate limits.

**Decision**: Implement mock versions of SERP and AI modules, controlled by environment variables.

**Rationale**:
- Avoid API costs during development
- Faster development cycle (no network calls)
- Easier testing with predictable data
- Can develop without API keys

**Consequences**:
- Must maintain mock implementations
- Need to ensure mocks match real API behavior
- Testing against real APIs still required before production

---

## ADR-004: Gemini 1.5 Pro as Default LLM

**Date**: 2025-11-22

**Status**: Accepted

**Context**: Need to choose LLM provider for AI features (brief generation, content enhancement, etc.)

**Decision**: Use Google Gemini 1.5 Pro as default, with pluggable architecture for other providers.

**Rationale**:
- Good Ukrainian language support
- Competitive pricing (~$0.005 per 1K tokens)
- Large context window (1M tokens)
- Easy to integrate via official SDK
- User can switch to OpenAI/Claude if preferred

**Consequences**:
- Google dependency
- Must implement provider abstraction layer
- Different providers may have different prompt requirements

---

## ADR-005: TF-IDF + spaCy for Term Extraction

**Date**: 2025-11-22

**Status**: Accepted

**Context**: Need to extract important terms from competitor content.

**Decision**: Combine TF-IDF (statistical) with spaCy NLP (entity recognition).

**Rationale**:
- TF-IDF finds statistically important phrases
- spaCy adds semantic entities (people, organizations, products)
- Both are language-agnostic (support Ukrainian and English)
- Local processing (no API costs)
- Good balance of accuracy and speed

**Consequences**:
- Must download spaCy models (~50MB each)
- Processing time increases with more competitors
- May miss domain-specific terms without context

---

## ADR-006: Ukrainian as Primary UI Language

**Date**: 2025-11-22

**Status**: Accepted

**Context**: Tool will be used primarily by Ukrainian content creators.

**Decision**: Build UI in Ukrainian with i18n infrastructure for future localization.

**Rationale**:
- Target audience is Ukrainian speakers
- Better UX with native language
- Shows differentiation from international tools
- i18n structure allows adding English later

**Consequences**:
- All UI strings must be in Ukrainian
- Need translation file structure
- May limit international adoption initially

---

## Future Decisions to Make

- **Database Migration Strategy**: When to migrate from SQLite to PostgreSQL?
- **Hosting Platform**: AWS, Google Cloud, DigitalOcean, or self-hosted?
- **Authentication Method**: Token-based, OAuth, or custom SSO?
- **Rate Limiting Storage**: In-memory, Redis, or database?
- **File Storage**: Local filesystem or cloud storage (S3, GCS)?

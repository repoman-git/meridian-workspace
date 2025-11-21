# 2025-11-20 - Database Technology Analysis for Workspace Tracking

**Date:** 2025-11-20  
**Purpose:** Comprehensive analysis of database options for workspace tracking system  
**Question:** SQLite, SQLAlchemy, PostgreSQL, VectorDB, or a blend?

---

## Executive Summary

**Recommendation:** **SQLAlchemy with SQLite (single database)** + **Future: VectorDB for semantic search**

**Rationale:**
1. ✅ **SQLAlchemy + SQLite** - Matches existing infrastructure, proven patterns, simple setup
2. ✅ **Single workspace.db** - All tracking in one place, relationships, queries
3. ⏳ **Future enhancement** - VectorDB for semantic search of architecture docs

---

## Requirements Analysis

### What We Need to Store

1. **Structured Data** (Relational)
   - Tasks → Issues (many-to-many)
   - Sessions → Decisions (one-to-many)
   - Architecture states → Components (one-to-many)
   - Drift detections → Files (one-to-many)
   - **Requires:** Relational database, foreign keys, joins

2. **Semi-Structured Data** (JSON fields)
   - Task metadata (JSON)
   - Architecture rules (JSON)
   - Configuration snapshots (JSON)
   - **Requires:** JSON column support

3. **Text Search** (Future)
   - Semantic search of architecture docs
   - Semantic search of decisions/notes
   - **Requires:** Vector embeddings, similarity search

### Access Patterns

1. **Frequent:**
   - Query tasks by status, repo, context
   - Filter issues by severity, type
   - List sessions for a date range
   - **Requires:** Fast queries, indexes

2. **Occasional:**
   - Full-text search of architecture docs
   - Semantic similarity search
   - **Requires:** Vector search (future enhancement)

3. **Concurrent:**
   - Multiple AI agents working simultaneously
   - Pre-commit hooks checking drift
   - CI/CD pipelines
   - **Requires:** Thread-safe, connection pooling

---

## Option Comparison

### Option 1: SQLite Only (Raw)

**Pros:**
- ✅ Simple - no dependencies
- ✅ Built into Python
- ✅ File-based (portable)
- ✅ Zero configuration

**Cons:**
- ❌ Manual SQL queries
- ❌ No ORM (more verbose)
- ❌ Manual connection management
- ❌ More error-prone

**Verdict:** ❌ Too low-level, doesn't match existing patterns

---

### Option 2: SQLAlchemy + SQLite (Recommended)

**Pros:**
- ✅ **Matches existing infrastructure** (meridian-core uses this)
- ✅ **Proven patterns** - reuse connection pooling, WAL mode
- ✅ **ORM** - Type-safe, less verbose
- ✅ **Thread-safe** - Connection pooling already implemented
- ✅ **Relationships** - Foreign keys, joins
- ✅ **JSON support** - JSON columns for metadata
- ✅ **Simple setup** - Single file database
- ✅ **Portable** - File-based, easy to backup
- ✅ **Migration support** - Alembic for schema changes

**Cons:**
- ⚠️ File-based (shared access needs WAL mode) - but already solved
- ⚠️ No full-text semantic search - but we can add VectorDB later

**Verdict:** ✅ **BEST FIT** - Matches existing patterns, proven infrastructure

---

### Option 3: PostgreSQL

**Pros:**
- ✅ More powerful queries
- ✅ Better concurrency (multi-writer)
- ✅ Full-text search (pg_trgm)
- ✅ JSONB columns (faster JSON queries)
- ✅ Better for production scale

**Cons:**
- ❌ **Requires external server** - Setup overhead
- ❌ **Different from existing infrastructure** - meridian-core uses SQLite
- ❌ **Less portable** - Requires PostgreSQL installation
- ❌ **Overkill** - Workspace tracking doesn't need production-scale DB
- ❌ **More complexity** - Connection strings, server management

**Verdict:** ❌ Overkill for workspace tracking, doesn't match existing patterns

---

### Option 4: VectorDB Only (Chroma, Pinecone, etc.)

**Pros:**
- ✅ Great for semantic search
- ✅ Embeddings for architecture docs

**Cons:**
- ❌ **No relational data** - Can't do foreign keys, joins
- ❌ **No SQL queries** - Can't filter tasks by status, etc.
- ❌ **Different paradigm** - Designed for similarity search, not structured data
- ❌ **Overkill** - Most data is structured, not semantic

**Verdict:** ❌ Wrong tool for structured data

---

### Option 5: Hybrid: SQLAlchemy + SQLite + VectorDB (Future Enhancement)

**Pros:**
- ✅ **SQLAlchemy + SQLite** for structured data (tasks, issues, sessions)
- ✅ **VectorDB** for semantic search (architecture docs, decisions)
- ✅ **Best of both worlds** - Relational + semantic search
- ✅ **Incremental** - Start with SQLite, add VectorDB later

**Cons:**
- ⚠️ Two systems to maintain (but can add VectorDB incrementally)

**Verdict:** ✅ **RECOMMENDED APPROACH** - Start with SQLite, add VectorDB later

---

## Detailed Analysis

### SQLAlchemy + SQLite (Primary Recommendation)

#### Why SQLAlchemy?

1. **Matches Existing Infrastructure**
   ```
   meridian-core already uses:
   - SQLAlchemy ORM
   - Connection pooling
   - WAL mode
   - Thread-safe patterns
   ```

2. **Proven Patterns**
   ```python
   # From meridian-core/src/meridian_core/db/models.py
   # We can reuse these patterns:
   - Base declarative model
   - Connection pooling
   - WAL mode setup
   - Session management
   ```

3. **ORM Benefits**
   - Type-safe queries
   - Relationship handling (foreign keys)
   - Migration support (Alembic)
   - Less boilerplate

#### Why SQLite?

1. **Single File Database**
   ```
   workspace.db - All tracking in one place
   ├── Tasks
   ├── Sessions
   ├── Issues
   ├── Architecture states
   └── Drift detections
   ```

2. **Portable**
   - Easy to backup (copy file)
   - Easy to share
   - No server needed

3. **Sufficient for Workspace Scale**
   - Workspace tracking: ~thousands of records
   - SQLite handles millions easily
   - Fast queries with indexes

4. **Thread-Safe with WAL Mode**
   - Write-Ahead Logging enables concurrent reads
   - Multiple readers, single writer (sufficient for workspace)
   - Already proven in meridian-core

---

## Recommended Architecture

### Phase 1: SQLAlchemy + SQLite (Now)

```
workspace.db (SQLite)
├── Structured Tables (SQLAlchemy ORM)
│   ├── workspace_tasks
│   ├── workspace_sessions
│   ├── cross_repo_issues
│   ├── architecture_decisions
│   ├── architecture_states
│   ├── component_placements
│   ├── drift_detections
│   └── ... (all relational data)
│
└── JSON Columns (for flexible metadata)
    ├── task.metadata (JSON)
    ├── issue.details (JSON)
    └── decision.rationale (JSON)
```

**Benefits:**
- ✅ All workspace tracking in one place
- ✅ Relationships (foreign keys)
- ✅ Fast queries with indexes
- ✅ Thread-safe with connection pooling
- ✅ Matches existing infrastructure

### Phase 2: VectorDB for Semantic Search (Future)

```
ChromaDB / Qdrant (VectorDB)
├── Architecture Documents (embeddings)
│   ├── architecture diagrams
│   ├── ADR documents
│   └── roadmap documents
│
└── Decision/Issue Notes (embeddings)
    ├── Decision rationales
    ├── Issue descriptions
    └── Context notes
```

**Benefits:**
- ✅ Semantic search: "find architecture docs about learning"
- ✅ Similarity search: "find similar decisions"
- ✅ Natural language queries

**When to add:**
- When you need semantic search
- When you have many architecture docs
- When searching by meaning (not just keywords)

---

## Implementation Strategy

### Step 1: Core Database (SQLAlchemy + SQLite)

**Create:**
- `workspace/db/models.py` - SQLAlchemy models
- `workspace/db/workspace_db.py` - Database manager
- `workspace.db` - SQLite database file

**Models:**
```python
# workspace/db/models.py
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, JSON, Integer, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class WorkspaceTask(Base):
    __tablename__ = 'workspace_tasks'
    
    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    status = Column(String, nullable=False)  # pending, in_progress, completed
    repo = Column(String)  # meridian-core, etc.
    metadata = Column(JSON)  # Flexible metadata
    # ... relationships ...
```

**Database Manager:**
```python
# workspace/db/workspace_db.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base

class WorkspaceDB:
    def __init__(self, db_path: str = "workspace.db"):
        # Reuse meridian-core patterns
        self.engine = create_engine(
            f'sqlite:///{db_path}',
            pool_pre_ping=True,
            connect_args={'check_same_thread': False}
        )
        # Enable WAL mode (like meridian-core)
        # ... connection pooling ...
```

### Step 2: JSON Export/Import (Hybrid Approach)

**Keep JSON files as human-readable exports:**

```python
class WorkspaceDB:
    def export_to_json(self) -> Dict[str, Any]:
        """Export to JSON for human readability."""
        return {
            "tasks": [task.to_dict() for task in self.get_all_tasks()],
            "sessions": [session.to_dict() for session in self.get_all_sessions()],
            # ...
        }
    
    def import_from_json(self, data: Dict[str, Any]):
        """Import from JSON (for migration or manual edits)."""
        # ...
```

**Benefits:**
- Database for queries and concurrency
- JSON export for human review
- Best of both worlds

### Step 3: VectorDB Integration (Future)

**When needed, add semantic search:**

```python
# workspace/db/vector_db.py (future)
from chromadb import Client

class WorkspaceVectorDB:
    """Semantic search for architecture docs and decisions."""
    
    def index_architecture_doc(self, doc_path: str, content: str):
        """Index architecture document for semantic search."""
        embedding = self.embed(content)
        self.collection.add(
            embeddings=[embedding],
            documents=[content],
            metadatas=[{"path": doc_path}]
        )
    
    def search_similar(self, query: str) -> List[Dict]:
        """Semantic search for similar content."""
        # ...
```

---

## Comparison Summary

| Feature | SQLite Only | SQLAlchemy+SQLite | PostgreSQL | VectorDB | Hybrid |
|---------|-------------|-------------------|------------|----------|--------|
| **Setup Complexity** | ⭐ Simple | ⭐⭐ Easy | ⭐⭐⭐ Complex | ⭐⭐ Easy | ⭐⭐ Easy |
| **Matches Existing** | ❌ | ✅ Yes | ❌ | ❌ | ✅ Yes |
| **Relational Data** | ✅ Yes | ✅ Yes | ✅ Yes | ❌ | ✅ Yes |
| **ORM Support** | ❌ | ✅ Yes | ✅ Yes | ❌ | ✅ Yes |
| **Semantic Search** | ❌ | ❌ | ⚠️ Limited | ✅ Yes | ✅ Yes |
| **Portability** | ✅ Yes | ✅ Yes | ❌ | ⚠️ | ✅ Yes |
| **Thread-Safe** | ⚠️ Manual | ✅ Yes | ✅ Yes | ⚠️ | ✅ Yes |
| **Production Ready** | ⚠️ | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |

---

## Final Recommendation

### **Primary: SQLAlchemy + SQLite**

**Why:**
1. ✅ **Matches existing infrastructure** - meridian-core already uses this
2. ✅ **Proven patterns** - Reuse connection pooling, WAL mode
3. ✅ **Simple setup** - Single file database
4. ✅ **Sufficient for workspace scale** - Handles thousands of records easily
5. ✅ **Thread-safe** - Connection pooling already implemented
6. ✅ **Relationships** - Foreign keys for complex queries
7. ✅ **JSON support** - Flexible metadata in JSON columns

### **Future Enhancement: VectorDB for Semantic Search**

**When to add:**
- When you have many architecture documents
- When you need semantic search: "find docs about learning"
- When searching by meaning, not just keywords

**Implementation:**
- Keep SQLAlchemy + SQLite for structured data
- Add ChromaDB or Qdrant for semantic search
- Index architecture docs and decisions
- Hybrid query: SQL for structured data, vector for semantic search

---

## Implementation Plan

### Phase 1: SQLAlchemy + SQLite (Now)

1. **Create database module**
   - `workspace/db/models.py` - SQLAlchemy models
   - `workspace/db/workspace_db.py` - Database manager
   - Reuse meridian-core patterns (connection pooling, WAL mode)

2. **Create database schema**
   - All workspace tracking tables
   - Relationships (foreign keys)
   - Indexes for performance

3. **Migrate JSON data**
   - Import existing JSON files
   - Verify data integrity

4. **Add JSON export**
   - Periodic export for human readability
   - Manual export for backup

### Phase 2: VectorDB (Future)

1. **Evaluate VectorDB options**
   - ChromaDB (local, simple)
   - Qdrant (local or cloud)
   - Pinecone (cloud)

2. **Add semantic search**
   - Index architecture documents
   - Index decision rationales
   - Semantic search API

3. **Hybrid queries**
   - SQL for structured data
   - Vector for semantic search
   - Combine results

---

## Summary

**Answer:** **SQLAlchemy + SQLite** (now), with **VectorDB** as a future enhancement.

**Rationale:**
- ✅ Matches existing meridian-core infrastructure
- ✅ Proven patterns (connection pooling, WAL mode)
- ✅ Sufficient for workspace tracking scale
- ✅ Simple setup, portable
- ✅ Future-ready (can add VectorDB later)

**Start with SQLAlchemy + SQLite, add VectorDB when needed for semantic search.**

---

**Last Updated:** 2025-11-20  
**Status:** Recommendation Complete - SQLAlchemy + SQLite Recommended


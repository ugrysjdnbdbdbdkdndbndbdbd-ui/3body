"""简单迁移：为已有表添加 PRD 新增列（SQLite 兼容）."""
import sqlite3


def run_sqlite_migrations(db_path: str) -> None:
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        # chronicle_events: summary, event_type
        for col, typ in [("summary", "TEXT"), ("event_type", "VARCHAR(32) DEFAULT 'pgc'")]:
            try:
                cur.execute(f"ALTER TABLE chronicle_events ADD COLUMN {col} {typ}")
            except sqlite3.OperationalError as e:
                if "duplicate column" not in str(e).lower():
                    raise
        # 零点计划 Phase 2：因果律时间轴
        for col, typ in [
            ("causality_status", "VARCHAR(32) DEFAULT 'collapsed'"),
            ("interaction_count", "INTEGER DEFAULT 0"),
            ("collapse_threshold", "INTEGER DEFAULT 5"),
            ("parent_node_id", "INTEGER NULL"),
            ("variant_source", "TEXT NULL"),
        ]:
            try:
                cur.execute(f"ALTER TABLE chronicle_events ADD COLUMN {col} {typ}")
            except sqlite3.OperationalError as e:
                if "duplicate column" not in str(e).lower():
                    raise
        # gallery_items: prompt_text, status, logic_score
        try:
            cur.execute("ALTER TABLE gallery_items ADD COLUMN prompt_text TEXT")
        except sqlite3.OperationalError as e:
            if "duplicate column" not in str(e).lower():
                raise
        for col, typ in [("status", "VARCHAR(32) DEFAULT 'normal'"), ("logic_score", "FLOAT DEFAULT 1.0")]:
            try:
                cur.execute(f"ALTER TABLE gallery_items ADD COLUMN {col} {typ}")
            except sqlite3.OperationalError as e:
                if "duplicate column" not in str(e).lower():
                    raise
        # universe_state
        try:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS universe_state (
                    id INTEGER PRIMARY KEY,
                    dark_forest_deterrence FLOAT DEFAULT 0.5,
                    resonance_state VARCHAR(32) DEFAULT '3d',
                    broadcast_enabled BOOLEAN DEFAULT 0,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            # Ensure singleton row exists
            cur.execute("INSERT OR IGNORE INTO universe_state (id, dark_forest_deterrence, resonance_state) VALUES (1, 0.5, '3d')")
        except Exception:
            pass
            
        # figures
        try:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS figures (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(64),
                    en_name VARCHAR(64),
                    role VARCHAR(64),
                    era VARCHAR(64),
                    status VARCHAR(32) DEFAULT 'active',
                    description TEXT,
                    image_url VARCHAR(512),
                    quotes TEXT,
                    logic_score FLOAT DEFAULT 1.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
        except Exception:
            pass
        
        # figures updates
        try:
            for col, typ in [
                ("metrics", "TEXT"),
                ("key_events", "TEXT"),
                ("key_decisions", "TEXT"),
                ("relationships", "TEXT"),
                ("key_quotes", "TEXT"),
            ]:
                try:
                    cur.execute(f"ALTER TABLE figures ADD COLUMN {col} {typ}")
                except sqlite3.OperationalError as e:
                    if "duplicate column" not in str(e).lower():
                        raise
        except Exception:
            pass
        
        # mini_universes
        try:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS mini_universes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id VARCHAR(64) UNIQUE,
                    mass FLOAT DEFAULT 5.0,
                    items TEXT,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
        except Exception:
            pass
        
        # mental_seal_sessions
        try:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS mental_seal_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id VARCHAR(64),
                    plan_title VARCHAR(256),
                    plan_content TEXT,
                    status VARCHAR(32) DEFAULT 'active',
                    history TEXT DEFAULT '[]',
                    round_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
        except Exception:
            pass
        
        # red_coast_signals
        try:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS red_coast_signals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_type VARCHAR(32),
                    frequency FLOAT DEFAULT 1420.0,
                    content_encrypted TEXT,
                    content_decrypted TEXT,
                    power_level VARCHAR(32) DEFAULT 'low',
                    integrity FLOAT DEFAULT 1.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
        except Exception:
            pass
        
        # forest_stars
        try:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS forest_stars (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    author_id VARCHAR(64),
                    content TEXT,
                    mass FLOAT DEFAULT 10.0,
                    brightness FLOAT DEFAULT 1.0,
                    status VARCHAR(32) DEFAULT 'active',
                    x FLOAT DEFAULT 0.0,
                    y FLOAT DEFAULT 0.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
        except Exception:
            pass
        
        # user_seals
        try:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS user_seals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id VARCHAR(64) UNIQUE,
                    seal_type VARCHAR(32),
                    imprinted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    strength INTEGER DEFAULT 100
                )
            """)
        except Exception:
            pass
        
        # chronicle_extra
        try:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS chronicle_archives (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title VARCHAR(256),
                    classification VARCHAR(32) DEFAULT 'CONFIDENTIAL',
                    content_markdown TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS chronicle_wiki (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    term VARCHAR(64),
                    category VARCHAR(32),
                    summary VARCHAR(512),
                    content_markdown TEXT,
                    visual_effect VARCHAR(32),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
        except Exception:
            pass
        
        conn.commit()
        conn.close()
    except FileNotFoundError:
        pass  # DB 文件尚未创建（create_all 会创建）
    except sqlite3.OperationalError as e:
        if "no such table" not in str(e).lower():
            raise  # 表不存在时跳过，其余 SQL 错误抛出


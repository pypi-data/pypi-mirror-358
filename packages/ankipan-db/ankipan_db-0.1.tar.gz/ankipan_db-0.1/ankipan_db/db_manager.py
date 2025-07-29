from psycopg2 import pool, sql
import psycopg2
import hashlib
import random
from collections import Counter
import logging
from functools import partial, wraps
from collections import defaultdict
import time

from typing import Dict, Optional, Iterable, Dict, List

import ankipan_db

logger = logging.getLogger(__name__)

random.seed(42)

# ------------------------------------------------------------------ #
class ConnWrapper(psycopg2.extensions.connection):
    def __init__(self, *args, lang: str, **kw):
        self.lang = lang
        super().__init__(*args, **kw)
        with self.cursor() as cur:
            cur.execute(sql.SQL("SET search_path TO {}").format(sql.Identifier(self.lang)))

def with_pool_cursor(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        conn = self.db_pool.getconn()
        try:
            with conn.cursor() as cur:
                cur.execute(sql.SQL("SET LOCAL search_path TO {},public").format(sql.Identifier(self.lang)))
                return func(self, cur, *args, **kwargs)
        finally:
            self.db_pool.putconn(conn)
    return wrapper

def with_conditional_pool_cursor(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if kwargs.get("cur") is not None:
            return func(self, *args, **kwargs)
        conn = self.db_pool.getconn()
        try:
            with conn.cursor() as cur:
                cur.execute(sql.SQL("SET LOCAL search_path TO {},public").format(sql.Identifier(self.lang)))
                kwargs["cur"] = cur
                return func(self, *args, **kwargs)
        finally:
            self.db_pool.putconn(conn)
    return wrapper

def with_conditional_pool_conn(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if kwargs.get("conn") is not None:
            return func(self, *args, **kwargs)
        conn = self.db_pool.getconn()
        try:
            kwargs["conn"] = conn
            return func(self, *args, **kwargs)
        finally:
            self.db_pool.putconn(conn)
    return wrapper

class DBManager:
    def __init__(self, lang):
        logger.info("DBManager initializing...")
        self.db_pool = pool.ThreadedConnectionPool(
            minconn=1,
            maxconn=20,
            connection_factory=partial(ConnWrapper, lang=lang)  ,
            **ankipan_db.db_config,
        )
        self.lang = lang

    @with_pool_cursor
    def get_lemma_counts(self, cur, source_paths: list[str] = None, limit=10000):
        if not source_paths:
            cur.execute("SELECT name FROM sources WHERE nesting_level=0")
            source_paths = [path[0] for path in cur.fetchall()]
        res = {}
        for source_path in source_paths:
            path_parts = source_path.split('/')
            cur.execute(f"SELECT source_id_from_path(VARIADIC %s)", (path_parts,))
            root_id = cur.fetchone()[0]
            cur.execute( "SELECT lemma, cnt FROM lemmas_with_counts(%s)", (root_id,))
            res[source_path] = dict(cur.fetchall())
        return res

    @with_pool_cursor
    def get_segments_for_lemmas(self,
                                cur,
                                paths: list[str],
                                lemmas: list[str],
                                source_category_name: str,
                                native_lang,
                                n_sentences: int = 8,
                                k_root: int = 5,
                                stride: int = 1) -> dict:
        """Return sentence-context for lemmas with ≈50 / 50 inside/outside mix."""

        cur.execute("SELECT id FROM sources WHERE name=%s AND nesting_level=0", (source_category_name,))
        source_category_id_unary_list = cur.fetchone()

        if not source_category_id_unary_list:
            raise RuntimeError(f'Source Category "{source_category_name}" not defined in db')
        source_category_id = source_category_id_unary_list[0]

        lemmas = list(set(lemmas))
        path_ids: list[int] = []
        for p in paths:
            parts = [source_category_name] + p.strip("/").split("/")
            cur.execute(f"SELECT source_id_from_path(VARIADIC %s)", (parts,))
            path_ids.append(cur.fetchone()[0])

        sql = f"""
        WITH roots AS (
            SELECT * FROM UNNEST(%s::int[]) AS r(root_id)
        ),
        target_sources AS (
            SELECT sd.id
            FROM   roots
            CROSS  JOIN LATERAL source_descendants(roots.root_id) sd
        ),
        raw AS (                                             -- all matches
            SELECT
                l.lemma,
                (ts.source_id = ANY(SELECT id FROM target_sources)) AS in_target,
                r.root_name,
                src.name AS source_name,
                ts.id          AS ts_id,
                w.word,
                ts.index       AS ts_index,
                ts.source_id   AS match_source_id,
                ROW_NUMBER() OVER (
                    PARTITION BY l.lemma,
                                (ts.source_id = ANY (SELECT id FROM target_sources)),
                                r.root_name
                    ORDER BY random()
                ) AS rn_root
            FROM   lemmas l
            JOIN   words  w   ON w.lemma_id = l.id
            JOIN   words_in_text_segments wits ON wits.word_id = w.id
            JOIN   text_segments ts ON ts.id = wits.text_segment_id
            JOIN   source_root_lookup r ON r.id = ts.source_id
            JOIN   sources src ON src.id = ts.source_id
            WHERE  l.lemma = ANY(%s) AND src.id = ANY(SELECT id FROM source_descendants(%s))
        ),
        raw_limited AS (               -- cap per root for diversity
            SELECT * FROM raw
            WHERE  rn_root <= %s
        ),
        counts AS (                    -- rows per lemma inside/outside
            SELECT lemma,
                COUNT(*) FILTER (WHERE in_target)     AS inside_total,
                COUNT(*) FILTER (WHERE NOT in_target) AS outside_total
            FROM   raw_limited
            GROUP  BY lemma
        ),
        quota AS (
            SELECT lemma,
                LEAST(%s / 2, inside_total)                        AS q_in,
                LEAST(%s - LEAST(%s / 2, inside_total),
                        outside_total)                               AS q_out
            FROM   counts
        ),
        matches AS (                   -- enforce ≈50/50 quota
            SELECT *
            FROM (
                SELECT rl.*,
                    ROW_NUMBER() OVER (
                        PARTITION BY rl.lemma, rl.in_target
                        ORDER BY random()
                    ) AS rn_side
                FROM   raw_limited rl
            ) rl
            JOIN quota q USING (lemma)
            WHERE (rl.in_target AND rn_side <= q.q_in)
            OR (NOT rl.in_target AND rn_side <= q.q_out)
        )
        SELECT
            m.lemma,
            lvl1.name   AS lvl1_name,
            m.source_name,
            m.word,
            m.in_target,
            ctx.text,
            ctx.start_s,
            ctx.end_s,
            ctx.index - m.ts_index AS rel_index
        FROM matches m
        JOIN LATERAL (
                WITH RECURSIVE up AS (
                    SELECT s.id, s.parent_id, s.name, s.nesting_level
                    FROM   sources s
                    WHERE  s.id = m.match_source_id        -- start at the match
                UNION ALL
                    SELECT p.id, p.parent_id, p.name, p.nesting_level
                    FROM   sources p
                    JOIN   up u ON p.id = u.parent_id
                )
                SELECT name
                FROM   up
                WHERE  nesting_level = 1                   -- first child of root
                LIMIT  1
            ) lvl1 ON TRUE
        CROSS  JOIN LATERAL (
            SELECT *
            FROM   text_segments ctx
            WHERE  ctx.source_id = m.match_source_id
            AND  ctx.index BETWEEN m.ts_index - %s AND m.ts_index + %s
            ORDER  BY ctx.index
        ) ctx
        ORDER  BY m.lemma, m.root_name, m.ts_id, ctx.index;
        """

        cur.execute(
            sql,(path_ids,
                lemmas,
                source_category_id,
                k_root,
                n_sentences, n_sentences, n_sentences,
                stride, stride))
        rows = cur.fetchall()

        result = {}
        for (lemma, source_root_name, source_name, word,
            in_target, text, start_s, end_s, rel_index) in rows:
            entry_type = "entries_from_known_sources" if in_target else "entries_from_unknown_sources"

            if not result.get(lemma, {}).get(entry_type, {}).get(source_root_name, {}).get(source_name):
                result.setdefault(lemma, {}).setdefault(entry_type, {}).setdefault(source_root_name, {}).setdefault(source_name, []).append({
                    "word": word,
                    'entries': [text],
                    'main_text_segment_index': 0 if rel_index==0 else None,
                    "start_s": start_s,
                    "end_s": end_s,
                })
            else:
                result[lemma][entry_type][source_root_name][source_name]['entries'].append(text)
                if rel_index==0:
                    result[lemma][entry_type][source_root_name][source_name]['main_text_segment_index'] = len(result[lemma][entry_type][source_root_name][source_name][-1]['entries'])-1
                result[lemma][entry_type][source_root_name][source_name]['end_s'] = end_s

        # fetch cached translations (new loop because we need all text segments to fetch cached entry)
        for lemma, entries in result.items():
            for entry_type, source_data in entries.items():
                for source_root_name, sources in source_data.items():
                    for source_name, source_results in sources.items():
                        for i, source_result in enumerate(source_results):
                            cur.execute("SELECT translation from translations WHERE hash=%s AND lang = %s",
                                        (hashlib.sha256((' '.join(source_result['entries'])).encode("utf-8")).hexdigest(),native_lang))
                            translation_raw = cur.fetchone()
                            if translation_raw:
                                result[lemma][entry_type][source_root_name][source_name][i]['translation'] = translation_raw[0]
        return result

    def cache_translations(self, text_segments_data, translations, native_lang):
        text_segments = [' '.join(entries) for _, _, entries in text_segments_data]
        assert len(text_segments) == len(translations)
        rows = [(hashlib.sha256(o.encode("utf-8")).hexdigest(), t, native_lang) for o, t in zip(text_segments, translations)]
        conn = self.db_pool.getconn()
        with conn.cursor() as cur:
            cur.execute(sql.SQL("SET LOCAL search_path TO {},public").format(sql.Identifier(self.lang)))
            cur.executemany(
                """
                INSERT INTO translations (hash, translation, lang)
                VALUES (%s, %s, %s)
                ON CONFLICT (hash) DO NOTHING
                """, rows)
        conn.commit()
        self.db_pool.putconn(conn)

    @with_pool_cursor
    def get_available_sources(self, cur, source_category_names: list[str] | None = None) -> dict[str, dict]:
        if source_category_names:
            cur.execute("SELECT id from sources WHERE name=%s AND nesting_level=0", (source_category_names,))
            root_ids = [id[0] for id in cur.fetchall()]
            if not root_ids:
                raise RuntimeError(
                    f'Source category name(s) not found: {source_category_names}')
        else:
            root_ids = []
        sql_roots = """
            SELECT so.id, so.name
            FROM   sources so
            WHERE parent_id IS NULL
        """
        params = []
        if root_ids:
            sql_roots += f"""
            AND so.id = ANY (
                    SELECT sd.id
                    FROM   UNNEST(%s::int[]) AS r(root_id)
                    CROSS  JOIN LATERAL source_descendants(r.root_id) sd
            )
            """
            params.append(root_ids)
        cur.execute(sql_roots, tuple(params))

        result: dict[str, dict] = {}
        root_id_by_name: dict[int, str] = {}
        for root_id, root_name in cur.fetchall():
            result[root_name] = {}
            root_id_by_name[root_id] = root_name
        if not root_id_by_name:
            return result

        cur.execute(
            """
            SELECT parent_id, name
            FROM   sources
            WHERE  parent_id = ANY(%s)
            """,
            (list(root_id_by_name.keys()),)
        )
        for parent_id, child_name in cur.fetchall():
            root_name = root_id_by_name[parent_id]
            result[root_name].setdefault(child_name, {})
        return result

    @with_pool_cursor
    def get_source_list(self, cur, source_path: str):
        path_parts = source_path.split('/')
        cur.execute(f"SELECT source_id_from_path(VARIADIC %s)", (path_parts,))
        root_id = cur.fetchone()[0]
        cur.execute(
            "SELECT metadata FROM sources WHERE id = %s",
            (root_id,)
        )
        root_meta = cur.fetchone()[0]
        root_meta = root_meta or {}
        lemma_counts = self.get_lemma_counts([source_path])[source_path]
        root_meta["lemma_counts"] = lemma_counts
        cur.execute(
            """
            SELECT name, metadata
            FROM   sources
            WHERE  parent_id = %s
            ORDER  BY name
            """, (root_id,))
        children = []
        for name, meta in cur.fetchall():
            meta = meta or {}
            meta["lemma_counts"] = self.get_lemma_counts([source_path + f'/{name}'])
            children.append((name, meta))
        return root_meta, children

    def get_source_tree_for_id(self, cur, root_id: int) -> dict[int, tuple[int | None, str]]:
        """
        Returns {id: (parent_id, name)} for all nodes under `root_id`
        (including the root itself).  One SQL round-trip.
        """
        cur.execute(
            """
            WITH RECURSIVE tree AS (
                SELECT id, parent_id, name
                FROM sources
                WHERE id = %s
                UNION ALL
                SELECT s.id, s.parent_id, s.name
                FROM sources s
                JOIN tree t ON s.parent_id = t.id
            )
            SELECT id, parent_id, name
            FROM tree;
            """,
            (root_id,),
        )
        return {row_id: (parent_id, name) for row_id, parent_id, name in cur.fetchall()}

    @with_pool_cursor
    def print_all(self, cur):
        cur.execute("""
            SELECT table_schema, table_name, column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_schema = '%s'
            ORDER BY table_schema, table_name, ordinal_position;
        """, (self.lang,))
        return cur.fetchall()

    def render_conditions(self, conditions):
        condition_clauses = []
        values = []
        for key, value in conditions.items():
            if value:
                if isinstance(value, list):
                    placeholders = sql.SQL(", ").join([sql.Placeholder() for _ in value])
                    clause = sql.SQL("{} IN ({})").format(sql.Identifier(key), placeholders)
                    values.extend(value)
                else:
                    clause = sql.SQL("{} = {}").format(sql.Identifier(key), sql.Placeholder())
                    values.append(value)
                condition_clauses.append(clause)
        if condition_clauses:
            return sql.SQL(" WHERE ") + sql.SQL(" AND ").join(condition_clauses), values
        else:
            return sql.SQL(""), []

    @with_conditional_pool_cursor
    def list_table_entries(
            self,
            table_name: str,
            col_name: str | Iterable[str],
            conditions: Optional[Dict[str, str]] = None,
            cur=None):
        if isinstance(col_name, str):
            cols_sql = sql.Identifier(col_name)
        else:
            cols_sql = sql.SQL(", ").join(map(sql.Identifier, col_name))
        query = sql.SQL("SELECT {cols} FROM {tbl}").format(
            cols=cols_sql,
            tbl=sql.Identifier(table_name))
        vals: list[str] = []
        if conditions:
            cond_sql, vals = self.render_conditions(conditions)
            query += cond_sql
        cur.execute(query, vals)
        if isinstance(col_name, str):
            return [row[0] for row in cur.fetchall()]
        else:
            return list(cur.fetchall())

    @with_conditional_pool_conn
    def add_table_entries(
        self,
        table_name: str,
        entries: list[dict],
        *,
        ignore_duplicates: bool = False,
        return_ids: bool = True,
        conn=None):

        with conn.cursor() as cur:
            if not entries:
                return [] if return_ids else None
            cols = list(entries[0])
            values_tpl = f'({",".join(["%s"] * len(cols))})'
            values_sql = ", ".join(
                cur.mogrify(values_tpl, tuple(e[c] for c in cols)).decode()
                for e in entries)
            query = sql.SQL("""
                INSERT INTO {tbl} ({cols})
                VALUES {vals}
            """).format(
                tbl  = sql.Identifier(table_name),
                cols = sql.SQL(", ").join(map(sql.Identifier, cols)),
                vals = sql.SQL(values_sql))

            if ignore_duplicates:
                query += sql.SQL(" ON CONFLICT DO NOTHING")
            if return_ids:
                query += sql.SQL(" RETURNING id")
            cur.execute(query)
            if return_ids:
                return [row[0] for row in cur.fetchall()]

    @with_conditional_pool_conn
    def update_wordcounts(self, conn=None, limit = 100000):
        with conn.cursor() as cur:
            cur.execute("SELECT name from sources WHERE nesting_level=0")
            root_source_names = [name[0] for name in cur.fetchall()]
            for root_source_name in root_source_names:
                view_name = f"mv_lemma_counts_{root_source_name.replace(' ', '_').lower()}"
                logger.info("Refreshing materialised view %s", view_name)
                cur.execute(f"DROP MATERIALIZED VIEW IF EXISTS {view_name}")
                cur.execute(f"""
                    CREATE MATERIALIZED VIEW {view_name} AS
                    WITH root AS (                                   -- level-0 node
                        SELECT id
                        FROM   sources
                        WHERE  parent_id IS NULL
                            AND  name = %s
                    ),
                    target_sources AS (
                        SELECT sd.id
                        FROM   root r
                        CROSS  JOIN LATERAL source_descendants(r.id) sd
                    ),
                    segments AS (
                        SELECT ts.id
                        FROM   text_segments        ts
                        JOIN   target_sources       t  ON t.id = ts.source_id
                    ),
                    words_for_segments AS (
                        SELECT w.lemma_id
                        FROM   segments seg
                        JOIN   words_in_text_segments wits ON wits.text_segment_id = seg.id
                        JOIN   words w ON w.id = wits.word_id
                    )
                    SELECT  l.lemma,
                            COUNT(*) AS lemma_count,
                            %s::text AS source_text
                    FROM    words_for_segments wf
                    JOIN    lemmas l ON l.id = wf.lemma_id
                    GROUP BY l.lemma
                    ORDER BY lemma_count DESC
                    LIMIT   %s;
                """,(root_source_name, root_source_name, limit))
                conn.commit()

    def delete_source(self, cur, root_id: int) -> dict[str, list[int] | None]:
        """
        Delete *root_id* and all descendants from `sources`
        (plus dependent rows in other tables) and return the deleted IDs.

        Returns
        -------
        {
            'sources':             [ids…] | None,
            'text_segments':       [ids…] | None,
            'words_in_text_segments': [ids…] | None
        }
        """
        sql = """
        WITH RECURSIVE tree AS (
            SELECT id FROM sources WHERE id = %(root)s
            UNION ALL
            SELECT s.id FROM sources s JOIN tree t ON s.parent_id = t.id
        ),
        ts_delete AS (
            DELETE FROM text_segments
            WHERE  source_id IN (SELECT id FROM tree)
            RETURNING id
        ),
        wits_delete AS (
            DELETE FROM words_in_text_segments
            WHERE  text_segment_id IN (SELECT id FROM ts_delete)
            RETURNING id
        ),
        src_delete AS (
            DELETE FROM sources
            WHERE  id IN (SELECT id FROM tree)
            RETURNING id
        )
        SELECT
            (SELECT array_agg(id) FROM src_delete)  AS sources,
            (SELECT array_agg(id) FROM ts_delete)   AS text_segments,
            (SELECT array_agg(id) FROM wits_delete) AS words_in_text_segments;
        """
        cur.execute(sql, {"root": root_id})
        result = cur.fetchone()
        return result

    @with_conditional_pool_conn
    def make_schema(self, conn=None):
        commands = [
            "CREATE SCHEMA IF NOT EXISTS {};".format(self.lang),
            'CREATE EXTENSION IF NOT EXISTS pgcrypto;',
            """
            CREATE TABLE translations (
                hash bytea PRIMARY KEY,
                translation TEXT NOT NULL,
                lang VARCHAR(2) NOT NULL
            );
            """,
            """
            CREATE TABLE lemmas (
                id SERIAL PRIMARY KEY,
                lemma TEXT NOT NULL UNIQUE
            );
            """,
            """
            CREATE TABLE words (
                id SERIAL PRIMARY KEY,
                word TEXT NOT NULL,
                pos VARCHAR(20),
                xpos VARCHAR(20),
                lemma_id INTEGER NOT NULL,
                FOREIGN KEY (lemma_id) REFERENCES lemmas(id),
                UNIQUE(word, pos)
            );
            """,
            """
            CREATE TABLE sources (
                id SERIAL PRIMARY KEY,
                parent_id int REFERENCES sources(id),
                name TEXT NOT NULL,
                metadata jsonb,
                nesting_level INT NOT NULL,
                UNIQUE (parent_id, name)
            );
            """,
            """
            CREATE TABLE text_segments (
                id SERIAL PRIMARY KEY,
                index INTEGER NOT NULL,
                text TEXT NOT NULL,
                start_s INTEGER,
                end_s INTEGER,
                source_id INTEGER REFERENCES sources(id)
            );
            """,
            """
            CREATE TABLE words_in_text_segments (
                id SERIAL PRIMARY KEY,
                word_id INTEGER NOT NULL,
                text_segment_id INTEGER NOT NULL,
                FOREIGN KEY (word_id) REFERENCES words(id),
                FOREIGN KEY (text_segment_id) REFERENCES text_segments(id)
            );
            """,
            # TODO
            # """
            # CREATE EXTENSION IF NOT EXISTS pg_cron;
            # SELECT cron.schedule(
            # 'nightly_word_cleanup',
            # '30 2 * * *',  -- every night at 2:30 AM
            # $$
            # DELETE FROM words WHERE NOT EXISTS (
            #     SELECT 1 FROM words_in_text_segments WHERE word_id = words.id
            # );
            # DELETE FROM lemmas WHERE NOT EXISTS (
            #     SELECT 1 FROM words WHERE lemma_id = lemmas.id
            # );
            # $$
            # );
            # """,
            """
            CREATE OR REPLACE FUNCTION {schema}.source_descendants(root_id int)
            RETURNS TABLE(id int)
            LANGUAGE sql
            SET search_path = {schema},public         -- pin search_path for the fn
            AS $$
                WITH RECURSIVE d(id) AS (
                    SELECT id FROM sources WHERE id = $1
                    UNION ALL
                    SELECT s.id FROM sources s JOIN d ON s.parent_id = d.id
                )
                SELECT id FROM d;
            $$;

            -- helper to resolve path → source_id
            CREATE OR REPLACE FUNCTION {schema}.source_id_from_path(VARIADIC p_names text[])
            RETURNS int
            LANGUAGE plpgsql
            SET search_path = {schema},public
            AS $$
            DECLARE
                part text;
                pid  int := NULL;
            BEGIN
                FOREACH part IN ARRAY p_names LOOP
                    SELECT id INTO pid
                    FROM   sources
                    WHERE  parent_id IS NOT DISTINCT FROM pid
                    AND  name = part
                    LIMIT 1;
                    IF pid IS NULL THEN
                        RAISE EXCEPTION 'Path element "%" not found', part;
                    END IF;
                END LOOP;
                RETURN pid;
            END;
            $$;
            -- ---------- helper to aggregate lemma counts in a subtree --------------
            CREATE OR REPLACE FUNCTION {schema}.lemmas_with_counts(root_id int)
            RETURNS TABLE(lemma text, cnt bigint)
            LANGUAGE sql
            SET search_path = {schema},public
            AS $$
                SELECT l.lemma,
                    COUNT(*) AS cnt
                FROM   source_descendants(root_id) d
                JOIN   text_segments        ts   ON ts.source_id = d.id
                JOIN   words_in_text_segments wits ON wits.text_segment_id = ts.id
                JOIN   words                w    ON w.id = wits.word_id
                JOIN   lemmas               l    ON l.id = w.lemma_id
                GROUP  BY l.lemma
                ORDER  BY cnt DESC;
            $$;
            -- ---------- helper to get root id for source --------------
            CREATE OR REPLACE VIEW source_root_lookup AS
            WITH RECURSIVE link(id, root_id, root_name) AS (
                SELECT id, id       AS root_id, name AS root_name
                FROM   sources
                WHERE  parent_id IS NULL              -- the roots
                UNION ALL
                SELECT s.id, l.root_id, l.root_name
                FROM   sources s
                JOIN   link    l ON s.parent_id = l.id
            )
            SELECT * FROM link;
            """.format(schema=self.lang),
            """
            CREATE INDEX idx_lemmas_lemma ON lemmas (lemma);
            CREATE INDEX idx_words_lemma_id ON words (lemma_id);
            CREATE INDEX idx_text_segments_source_id ON text_segments (source_id);
            CREATE INDEX idx_words_in_text_segments_text_segment_id ON words_in_text_segments (text_segment_id);
            CREATE INDEX idx_words_in_text_segments_text_word_id ON words_in_text_segments (word_id);
            """
        ]
        with conn.cursor() as cur:
            for command in commands:
                cur.execute(command)
        conn.commit()

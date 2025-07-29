from pathlib import Path
import psycopg2
from psycopg2.extras import execute_values
import concurrent.futures
from typing import Iterable
import time
import logging
import json
from ankipan import Reader

from ankipan_db import DBManager, db_config, PROJECT_ROOT

logger = logging.getLogger(__name__)

class Parser:
    def __init__(self, lang, db = None):
        if not db:
            db = DBManager(lang)
        self.db = db
        self.reader = Reader(lang)
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=2)

    def add_source_category(self, source_category_name, metadata = None):
        conn = self.db.db_pool.getconn()
        source_id = self.db.add_table_entries('sources', [{'name': source_category_name,
                                                           'metadata': metadata,
                                                           'nesting_level': 0}], conn=conn)[0]
        conn.commit()
        self.db.db_pool.putconn(conn)
        return source_id

    def add_source(self,
                   path,
                   source_category_name: str,
                   overwrite=False,
                   source_root_name=None,
                   n_threads=None,
                   index_separators: Iterable[str] = None,
                   replace_chars: Iterable[str] = None,
                   link = None,
                   chunk_size: int = None,
                   file_match_pattern = None,
                   dir_match_pattern = None,
                   conn_ = None):
        if not conn_:
            conn = self.db.db_pool.getconn()
        else:
            conn = conn_
        path = Path(path)

        with conn.cursor() as cur:
            cur.execute("SELECT id FROM sources WHERE name = %s AND nesting_level = 0", (source_category_name,))
            source_category_id_unary_list = cur.fetchone()

            if not source_category_id_unary_list:
                raise RuntimeError(f'Source Category "{source_category_name}" not defined in db')
            source_category_id = source_category_id_unary_list[0]

            if source_root_name is None:
                source_root_name = Path(path).stem

            cur.execute("SELECT id FROM sources WHERE parent_id = %s", (source_category_id,))
            existing_root_sources = [source for source in cur.fetchall()]

            print("existing_root_sources",existing_root_sources)
            print("source_root_name",source_root_name)
            if not source_root_name in existing_root_sources:
                cur.execute("""INSERT INTO sources (parent_id, name, metadata, nesting_level)
                               VALUES (%s, %s, %s, %s)
                               RETURNING id""", (source_category_id, source_root_name, None, 1))
            else:
                cur.execute("SELECT id FROM sources WHERE name = %s AND parent_id = %s", (source_root_name,source_category_id))
            source_root_id = cur.fetchone()[0]
            if overwrite:
                self.db.delete_source(cur, source_root_id)

            source_tree = self.db.get_source_tree_for_id(cur, source_category_id)
        cache = {}
        imported_files = set()
        for node_id in source_tree.keys():
            parts: list[str] = []
            current_id = node_id
            while current_id is not None:
                parent_id, name = source_tree[current_id]
                parts.append(name)
                current_id = parent_id
            p = path.joinpath(*reversed(parts))
            cache[node_id] = p
            imported_files.add(p.resolve())

        file_paths = list(self.reader.collect_file_paths(path,
                                                         file_match_pattern = file_match_pattern,
                                                         exclude_paths = imported_files,
                                                         dir_match_pattern = dir_match_pattern))
        logger.info("Files to import: %d (already in DB: %d)",
                    len(file_paths), len(imported_files))
        if not file_paths:
            logger.info(f'Source {source_root_name} filtered out or already fully imported.')
            return
        logger.info(f'Adding source "{source_root_name}"')
        if imported_files:
            logger.info('Skipping {len(existing_source_names} already existing files')
        chunk_size = chunk_size if chunk_size else 10
        file_paths_chunks = [file_paths[i:i + chunk_size] for i in range(0, len(file_paths), chunk_size)]
        logger.info(f"Processing {len(file_paths_chunks)} chunks")
        for file_paths_chunk in file_paths_chunks:
            files = self.reader.open_files(file_paths_chunk,
                                           index_separators=index_separators,
                                           replace_chars=replace_chars,
                                           source_name = source_root_name,
                                           assert_coherence=True)
            self.reader.process_files(files, get_indices=True, n_threads=n_threads)
            self.add_files_to_db(files, source_root_id, Path(path).resolve(), conn)
            conn.commit()
        if not conn_:
            self.db.db_pool.putconn(conn)
        logger.info(f"Finished adding source {source_root_name}")

    def add_files_to_db(self, files, source_root_id, disk_root, conn):
        disk_root = Path(disk_root).resolve()
        cache: dict[tuple[int, str], int] = {}
        with conn.cursor() as cur:
            def ensure_dir(cur, parent_id: int, name: str, level: int) -> int:
                """
                Return the id for (parent_id, name), inserting it at `level`
                if it doesn't exist yet. Results are cached in-memory.
                """
                key = (parent_id, name)
                if key in cache:
                    return cache[key]

                cur.execute(
                    """
                    INSERT INTO sources (parent_id, name, metadata, nesting_level)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (parent_id, name) DO NOTHING
                    RETURNING id
                    """,
                    (parent_id, name, json.dumps({}), level),
                )
                row = cur.fetchone()
                if row:
                    new_id = row[0]
                else:
                    cur.execute(
                        "SELECT id FROM sources WHERE parent_id = %s AND name = %s",
                        (parent_id, name),
                    )
                    new_id = cur.fetchone()[0]
                cache[key] = new_id
                return new_id

            for file in files:
                path = Path(file.path).resolve()
                parent_id = source_root_id
                rel_parts = path.parent.relative_to(disk_root).parts
                for level, part in enumerate(rel_parts, start=2):
                    parent_id = ensure_dir(cur, parent_id, part, level)
                leaf_level = len(rel_parts) + 2
                cur.execute(
                    """
                    INSERT INTO sources (parent_id, name, metadata, nesting_level)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (parent_id, name) DO NOTHING
                    RETURNING id
                    """,
                    (parent_id, path.name, json.dumps({'transcript': file.content}), leaf_level)
                )
                row = cur.fetchone()
                if row:
                    leaf_source_id = row[0]
                    text_segments = []
                    lemmas = []
                    words = []
                    poss = []
                    xposs = []
                    indices = []
                    for index, (text_segment_indices, metadata) in enumerate(file.text_segment_components.items()):
                        text_segment = file.content[text_segment_indices[0]:text_segment_indices[1]]
                        start_s, end_s = file.sub_indices[index] if file.sub_indices else (None, None)
                        text_segments.append((start_s, end_s, text_segment, index, leaf_source_id))
                        words.extend([i['word'] for i in metadata])
                        poss.extend([i['pos'] for i in metadata])
                        xposs.extend([i['xpos'] for i in metadata])
                        lemmas.extend([i['lemma'] for i in metadata])
                        indices.extend([index for i in metadata])
                    logger.debug(f"add_table_entries text_segnents")

                    cur.executemany("INSERT INTO text_segments (start_s, end_s, text, index, source_id) VALUES (%s, %s, %s, %s, %s)", text_segments)
                    if lemmas:
                        cur.executemany("INSERT INTO lemmas (lemma) VALUES (%s)  ON CONFLICT DO NOTHING", [(lemma,) for lemma in set(lemmas)])
                        cur.execute("SELECT lemma, id FROM lemmas WHERE lemma = ANY (%s)", (list(set(lemmas)),))
                        ids_by_lemmas = {lemma: id for lemma, id in cur.fetchall()}

                        cur.executemany("INSERT INTO words (word, pos, xpos, lemma_id) VALUES (%s, %s, %s, %s) ON CONFLICT DO NOTHING",
                                        [(word, pos, xpos, ids_by_lemmas[lemma]) for word, pos, xpos, lemma in zip(words, poss, xposs, lemmas)])

                        cur.execute("SELECT word, id FROM words WHERE word = ANY (%s)", (list(set(words)),))
                        ids_by_words = {lemma: id for lemma, id in cur.fetchall()}

                        cur.execute("SELECT index, id FROM text_segments WHERE source_id = (%s)", (leaf_source_id,))
                        text_segment_id_by_index = {index: id for index, id in cur.fetchall()}

                        cur.executemany("INSERT INTO words_in_text_segments (word_id, text_segment_id) VALUES (%s, %s)",
                                        [(ids_by_words[word], text_segment_id_by_index[index]) for word, index in zip(words, indices)])
                else:
                    logger.warning("File %s already present; skipped.", f.path)
        logger.info("add_files_to_db finished – %d folders, %d files", len(cache))

    def sync_dir(self,
                 sources_path: str,
                 source_category: str,
                 overwrite = False,
                 n_threads = None,
                 index_separators: Iterable[str] = None,
                 replace_chars=None,
                 start_at: str = None):
        """
        Parse lemmas from path with text data using the ankimelon.Reader.collect_file_paths() method

        Parameters
        ----------
        sources_path: '/' separated Path to a file or directory with textfiles
        source_category: name of subcategory
        overwrite (optional): overwrite existing data
        n_threads (optional): number of threads to parse with
        index_separators (optional): custom separates for source (see help(ankimelon.Reader.open_files))
        replace_chars (optional): List of characters to be removed when processing
        start_at (optional): If parsing was previously interrupted, specify name of file to start with

        """
        conn = self.db.db_pool.getconn()
        starting = False
        for path in Path(sources_path).iterdir():
            if start_at:
                if start_at == path.stem:
                    starting = True
                if not starting:
                    logger.info(f'Skipping source "{path.stem}" because start_at "{start_at}" hat not yet been reached')
                    continue
            while True:
                try:
                    self.add_source(path, source_category, overwrite = overwrite, n_threads = n_threads, index_separators=index_separators, replace_chars=replace_chars, conn_ = conn)
                    break
                except psycopg2.OperationalError as e:
                    logger.error(f"Operational error for {path}:\n\n{e}")
                    time.sleep(300)
                    try:
                        conn.rollback()
                    except Exception as e:
                        logger.error("rollback exception:", e)
                        for i in range(100):
                            try:
                                self.db = DBManager(self.lang)
                                break
                            except Exception as e:
                                logger.error("reconnecting...", e)
                            time.sleep(3)
        self.db.db_pool.putconn(conn)

    def __del__(self):
        self.executor.shutdown(wait=True)

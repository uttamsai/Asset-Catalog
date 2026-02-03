from db import get_connection
import os
import hashlib

# assets
def get_file_size(path):
    return os.path.getsize(path)
def compute_sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

file_extensions = {
    "image": {
        ".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff", ".gif"
    },
    "video": {
        ".mp4", ".mkv", ".avi", ".mov", ".webm"
    },
    "audio": {
        ".mp3", ".wav", ".flac", ".aac", ".ogg"
    },
    "archive": {
        ".zip", ".rar", ".7z", ".tar", ".gz"
    },
    "document": {
        ".pdf", ".txt", ".md", ".docx", ".xlsx"
    },
    "data": {
        ".json", ".csv", ".xml", ".db"
    }
}
def asset_type(path):
    ext = os.path.splitext(path)[1].lower()

    for asset_type, exts in file_extensions.items():
        if ext in exts:
            return asset_type

    return "unknown"

def add_asset(file_path, title=None):
    file_path = os.path.abspath(file_path)

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    if title is None:
        title = os.path.splitext(os.path.basename(file_path))[0]

    size = get_file_size(file_path)
    sha256 = compute_sha256(file_path)
    asset_type_str = asset_type(file_path)

    with get_connection() as conn:
        conn.execute(
            """
            INSERT OR IGNORE INTO assets
              (title, asset_type, file_path, file_size, sha256)
            VALUES (?, ?, ?, ?, ?)
            """,
            (title, asset_type_str, file_path, size, sha256)
        )

def get_asset(asset_id):
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM assets WHERE ID = ?", (asset_id, )).fetchone()
        return row

def list_assets():
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM assets").fetchall()
        return rows

def delete_asset(asset_id):
    with get_connection() as conn:
        conn.execute(
            "DELETE FROM assets WHERE id = ?", (asset_id,))


# creators 

def add_creator(display_name, notes=None):
    with get_connection() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO creators (display_name, notes) values (?, ?)", (display_name, notes)
        )

def delete_creator(creator_id):
    with get_connection() as conn:
        conn.execute(
            "DELETE FROM creators WHERE id = ?", (creator_id,)
        )

def edit_creator(creator_id, display_name=None, notes=None):
    with get_connection() as conn:
        if display_name is not None:
            conn.execute(
                "UPDATE creators SET display_name = ? WHERE id = ?", (display_name, creator_id)
            )
        if notes is not None:
            conn.execute(
                "UPDATE creators SET notes = ? WHERE id = ?", (notes, creator_id)
            )

def link_creator(asset_id, creator_id, role="Author"):
    with get_connection() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO asset_creators (asset_id, creator_id, role) VALUES (?, ?, ?)", (asset_id, creator_id, role)
        )

def unlink_creator(asset_id, creator_id):
   with get_connection() as conn:
       conn.execute(
           "DELETE FROM asset_creators WHERE asset_id = ? AND creator_id = ?", (asset_id, creator_id)
       )


# tags 

def add_tag(name):
    with get_connection() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO tags (name) VALUES (?)", (name,)
        )

def tag_asset(asset_id, tag_name):
    tag_name = tag_name.strip().lower()

    with get_connection() as conn:
        tag_row = conn.execute(
            "SELECT id FROM tags WHERE name = ?", (tag_name,)
        ).fetchone()
        if tag_row is None:
            raise ValueError(f"Tag not found: {tag_name}")
        tag_id = tag_row[0]
        conn.execute(
            "INSERT OR IGNORE INTO asset_tags (asset_id, tag_id) VALUES (?, ?)", (asset_id, tag_id)
        )

def untag_asset(asset_id, tag_name):
    tag_name = tag_name.strip().lower()

    with get_connection() as conn:
        tag_row = conn.execute(
            "SELECT id FROM tags WHERE name = ?",
            (tag_name,)
        ).fetchone()

        if tag_row is None:
            return

        conn.execute(
            "DELETE FROM asset_tags WHERE asset_id = ? AND tag_id = ?",
            (asset_id, tag_row[0])
        )

# sources

def add_source(name, category=None, url=None, notes=None):
    with get_connection() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO sources (name, category, url, notes) VALUES (?, ?, ?, ?)", (name, category, url, notes)
        )

def link_source(asset_id, source_id):
    with get_connection() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO asset_source (asset_id, source_id) VALUES (?, ?)", (asset_id, source_id)
        )

def unlink_source(asset_id, source_id):
    with get_connection() as conn:
        conn.execute(
            "DELETE FROM asset_source WHERE asset_id = ? and source_id = ?", (asset_id, source_id)
        )

# search 

def search_by_tag(tag_name):
    tag_name = tag_name.strip().lower()
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT assets.* FROM assets 
            JOIN asset_tags ON assets.id = asset_tags.asset_id
            JOIN tags ON asset_tags.tag_id = tags.id
            WHERE tags.name = ?
            """, (tag_name,)
        )
        return rows.fetchall()

def search_by_creator(creator_name):
    creator_name = creator_name.strip()

    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT assets.*
            FROM assets
            JOIN asset_creators ON assets.id = asset_creators.asset_id
            JOIN creators ON asset_creators.creator_id = creators.id
            WHERE creators.display_name = ?
            """,
            (creator_name,)
        ).fetchall()

        return rows

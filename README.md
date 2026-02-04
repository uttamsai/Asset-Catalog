# Asset Catalog

A lightweight **Python + SQLite** backend for organizing and searching local assets  
(images, videos, archives, documents, etc.) using **tags, creators, and sources**.

This project focuses on **clean relational design** and practical SQL usage
(JOINs, foreign keys, many-to-many relationships).

---

## Features

- Add and track local files as assets
- Automatic file hashing (SHA-256) and size detection
- Tag assets and search by tag
- Link creators to assets (many-to-many)
- Link a source/origin to each asset
- Search assets by creator
- SQLite with foreign key enforcement
- Clean separation between database and logic layers

---

## Schema Overview

- `assets` – core asset records
- `creators` + `asset_creators` – creator relationships
- `tags` + `asset_tags` – flexible tagging system
- `sources` + `asset_source` – asset origin tracking

All relationships are enforced using **foreign keys**.

---

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/uttamsai/Asset-Catalog.git
cd Asset-Catalog

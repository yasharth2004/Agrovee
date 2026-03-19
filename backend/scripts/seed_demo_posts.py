"""Populate the community tables with curated demo posts and media.

Run: python scripts/seed_demo_posts.py
"""

from __future__ import annotations

import sqlite3
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Tuple

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DB_PATH = PROJECT_ROOT / "agrovee.db"
UPLOAD_PREFIX = Path("uploads/community")
MEDIA_URL_PREFIX = "/uploads/community"
USER_ID = 1  # default demo user

PostMedia = List[Tuple[str, str]]  # (original_filename, stored_filename)

POSTS: List[dict] = [
    {
        "title": "Fall Armyworm Alert: Scouting Notes",
        "category": "pest_control",
        "views": 64,
        "content": (
            "Spotted early signs of armyworm pressure along the maize perimeter. "
            "Sharing pheromone trap counts (7 moths over 48h) and neem spray mix "
            "that kept last season under control. Remember to scout underside of leaves "
            "just after sunrise before larvae hide in the whorl."
        ),
        "media": [
            ("scouting-maize-block.jpg", "demo-armyworm-field.jpg"),
        ],
    },
    {
        "title": "DIY Solar-Powered Drip Controller",
        "category": "irrigation",
        "views": 51,
        "content": (
            "Finished wiring a low-cost controller using a 10W panel, 12V battery, and "
            "ESP32 to automate pulse irrigation for the nursery beds. Posting the manifold "
            "layout plus the moisture thresholds we used (18-24% volumetric water content). "
            "Works great for keeping transplants stress-free during heatwaves."
        ),
        "media": [
            ("drip-manifold-layout.jpg", "demo-irrigation-layout.jpg"),
        ],
    },
    {
        "title": "Building Carbon-Rich Beds with Cover Crops",
        "category": "soil_health",
        "views": 73,
        "content": (
            "Trial plot update after rolling down a rye-vetch mix. Soil respiration up "
            "12% and earthworm counts doubled in four weeks. Posting before/after shots "
            "plus the seed rate recipe (20kg rye + 8kg vetch per acre) if anyone wants to "
            "copy the system for the winter lean period."
        ),
        "media": [
            ("cover-crop-ridge.jpg", "demo-cover-crop.jpg"),
            ("nursery-bed-prep.jpg", "demo-greenhouse.jpg"),
        ],
    },
    {
        "title": "Storm Tracker: Prepping for Incoming Monsoon",
        "category": "weather",
        "views": 88,
        "content": (
            "Sharing radar snapshots + checklist we circulate with growers when the "
            "monsoon trough shifts south. Key steps: open drainage furrows, stake young "
            "fruit trees, and pre-mix foliar nutrition for post-storm recovery. Stay safe "
            "and keep sensors above flood line!"
        ),
        "media": [
            ("radar-loop-june.jpg", "demo-weather-radar.jpg"),
        ],
    },
]


def seed_posts() -> None:
    if not DB_PATH.exists():
        raise FileNotFoundError(f"Database not found at {DB_PATH}")

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    print("Clearing existing community data...")
    cur.execute("DELETE FROM community_post_media")
    cur.execute("DELETE FROM community_posts")

    base_time = datetime.utcnow()

    for index, post in enumerate(POSTS):
        post_id = str(uuid.uuid4())
        created = base_time - timedelta(hours=index * 6)
        cur.execute(
            """
            INSERT INTO community_posts (id, user_id, title, content, category, views, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                post_id,
                USER_ID,
                post["title"],
                post["content"],
                post["category"],
                post["views"],
                created,
                created,
            ),
        )
        print(f" • Inserted post: {post['title']}")

        for original_name, stored_file in post.get("media", []):
            media_id = str(uuid.uuid4())
            file_path = UPLOAD_PREFIX / stored_file
            file_url = f"{MEDIA_URL_PREFIX}/{stored_file}"
            cur.execute(
                """
                INSERT INTO community_post_media (id, post_id, file_name, file_path, file_url, mime_type, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    media_id,
                    post_id,
                    original_name,
                    str(file_path),
                    file_url,
                    "image/jpeg",
                    created,
                ),
            )
            print(f"   ↳ attached media: {original_name} -> {stored_file}")

    conn.commit()
    conn.close()
    print(f"Seeded {len(POSTS)} posts successfully.")


if __name__ == "__main__":
    seed_posts()

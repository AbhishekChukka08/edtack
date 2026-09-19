import os
import json
from datetime import datetime

STATE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'state')
QUEUE_FILE = os.path.join(STATE_DIR, 'queue.json')
HISTORY_FILE = os.path.join(STATE_DIR, 'history.json')

DEFAULT_TOPICS = [
    {
        "id": "redis-cache-aside",
        "topic": "Redis Cache-Aside Pattern",
        "category": "Caching & Performance",
        "difficulty": "Intermediate",
        "summary": "How applications safely fetch data from cache and fall back to database without stale reads."
    },
    {
        "id": "db-sharding-vs-partitioning",
        "topic": "Database Sharding vs Horizontal Partitioning",
        "category": "Database Architecture",
        "difficulty": "Advanced",
        "summary": "Distributing relational data across multiple physical database nodes to overcome single-server limits."
    },
    {
        "id": "kafka-vs-rabbitmq",
        "topic": "Kafka vs RabbitMQ",
        "category": "Messaging & Streaming",
        "difficulty": "Intermediate",
        "summary": "Log-based distributed streaming versus smart broker push messaging queues."
    },
    {
        "id": "rate-limiting-algorithms",
        "topic": "Token Bucket vs Leaky Bucket Rate Limiting",
        "category": "API Gateway Patterns",
        "difficulty": "Intermediate",
        "summary": "Protecting backend microservices against traffic spikes and DDoS attacks."
    },
    {
        "id": "consistent-hashing",
        "topic": "Consistent Hashing in Distributed Caches",
        "category": "Distributed Systems",
        "difficulty": "Advanced",
        "summary": "Minimizing cache re-mapping when nodes join or leave a cluster."
    },
    {
        "id": "single-point-of-failure-ha",
        "topic": "Eliminating Single Points of Failure (SPOF)",
        "category": "High Availability",
        "difficulty": "Intermediate",
        "summary": "Building fault-tolerant systems using active-passive failover and load balancer pairs."
    },
    {
        "id": "database-indexing-b-trees",
        "topic": "How Database B-Tree Indexes Work",
        "category": "Database Internals",
        "difficulty": "Intermediate",
        "summary": "Why B-Trees accelerate O(log N) lookups and how composite indexes optimize queries."
    }
]

def init_state():
    """Ensures state directory and JSON files exist."""
    os.makedirs(STATE_DIR, exist_ok=True)
    if not os.path.exists(QUEUE_FILE):
        topics_json_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'topics.json')
        if os.path.exists(topics_json_path):
            with open(topics_json_path, 'r', encoding='utf-8') as f:
                topics_source = json.load(f)
        else:
            topics_source = DEFAULT_TOPICS
        with open(QUEUE_FILE, 'w', encoding='utf-8') as f:
            json.dump(topics_source, f, indent=2)
    if not os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f, indent=2)

def get_next_topic() -> dict:
    """Fetches the next uncompleted topic from queue."""
    init_state()
    with open(QUEUE_FILE, 'r', encoding='utf-8') as f:
        queue = json.load(f)
    with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
        history = json.load(f)

    completed_ids = {item['id'] for item in history}
    
    for topic in queue:
        if topic['id'] not in completed_ids:
            return topic

    # Fallback if queue exhausted
    return queue[0] if queue else DEFAULT_TOPICS[0]

def mark_topic_completed(topic_id: str):
    """Logs topic as completed with timestamp."""
    init_state()
    with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
        history = json.load(f)

    if not any(item['id'] == topic_id for item in history):
        history.append({
            "id": topic_id,
            "completed_at": datetime.utcnow().isoformat() + "Z"
        })

    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, indent=2)

def get_curriculum_status(page: int = 1, page_size: int = 5) -> tuple[list[dict], int, int, int]:
    """Returns paginated curriculum items with completion flags.
    Returns: (items_for_page, total_items, total_pages, current_page)
    """
    init_state()
    with open(QUEUE_FILE, 'r', encoding='utf-8') as f:
        queue = json.load(f)
    with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
        history = json.load(f)

    completed_ids = {item['id'] for item in history}
    
    annotated = []
    for idx, t in enumerate(queue, start=1):
        is_done = t['id'] in completed_ids
        annotated.append({
            "index": idx,
            "id": t['id'],
            "topic": t['topic'],
            "category": t.get('category', 'Generative AI'),
            "completed": is_done
        })
        
    total_items = len(annotated)
    total_pages = max(1, (total_items + page_size - 1) // page_size)
    page = max(1, min(page, total_pages))
    
    start = (page - 1) * page_size
    end = start + page_size
    items_for_page = annotated[start:end]
    
    return items_for_page, total_items, total_pages, page


def get_upcoming_topics(count: int = 4, offset: int = 0) -> list[dict]:
    """Returns the next 'count' uncompleted topics from queue starting at offset."""
    init_state()
    with open(QUEUE_FILE, 'r', encoding='utf-8') as f:
        queue = json.load(f)
    with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
        history = json.load(f)

    completed_ids = {item['id'] for item in history}
    remaining = [t for t in queue if t['id'] not in completed_ids]
    
    if not remaining:
        return queue[:count]
        
    start_idx = offset % len(remaining)
    selected = remaining[start_idx:start_idx + count]
    if len(selected) < count:
        selected.extend(remaining[:count - len(selected)])
    return selected

def get_topic_by_id(topic_id: str) -> dict | None:
    """Finds a topic in queue by ID."""
    init_state()
    with open(QUEUE_FILE, 'r', encoding='utf-8') as f:
        queue = json.load(f)
    for topic in queue:
        if topic['id'] == topic_id:
            return topic
    return None

def create_custom_topic(topic_name: str) -> dict:
    """Creates a custom topic entry from user prompt."""
    import re
    slug = re.sub(r'[^a-zA-Z0-9]+', '-', topic_name.strip().lower()).strip('-')[:50]
    return {
        "id": f"custom-{slug}",
        "topic": topic_name.strip(),
        "category": "System Design & Architecture",
        "difficulty": "Intermediate",
        "summary": f"User-requested topic: {topic_name}"
    }


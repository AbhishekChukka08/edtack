import os
import sys
import json
import argparse
from dotenv import load_dotenv

load_dotenv()

from src.state_manager import get_next_topic, mark_topic_completed
from src.ai_scriptwriter import generate_carousel_content
from src.renderer import generate_carousel_images
from src.telegram_bot import send_to_telegram

def main():
    parser = argparse.ArgumentParser(description="Automated IG Carousel Generator")
    parser.add_argument("--dry-run", action="store_true", help="Generate HTML and PNG slides without sending to Telegram")
    parser.add_argument("--theme", default="theme-notebook", choices=["theme-notebook", "white-infographic", "dark-slate"], help="Visual style theme")
    parser.add_argument("--output-dir", default="./output", help="Directory to save output files")
    parser.add_argument("--serve", action="store_true", help="Start 24/7 interactive Telegram bot listener for button clicks & custom topics")
    args = parser.parse_args()

    if args.serve:
        from src.bot_listener import start_bot
        start_bot()
        return

    print("[*] Starting Daily Technical Carousel Generator ('edtack')...")
    
    topic_info = get_next_topic()
    print(f"[*] Selected Topic: '{topic_info['topic']}' ({topic_info['category']})")

    # Step 1: AI Content Generation or Fallback Mock
    try:
        print("[*] Generating digital engineering notebook script with Gemini 3.1 Flash Lite...")
        carousel_data = generate_carousel_content(topic_info)
    except Exception as e:
        print(f"[!] Gemini API failed or key missing ({e}). Using structured engineering notebook template...")
        carousel_data = {
            "topic_id": topic_info.get("id", "db-sharding"),
            "category": topic_info.get("category", "Database Architecture"),
            "handle": "edtack_tech",
            "caption": {
                "hook": "Why horizontal database scaling breaks traditional foreign keys in production.",
                "body": "When your API hits 100K QPS, querying a single SQL primary exhausts connection pools in seconds. Here is the handwritten breakdown of Database Sharding.",
                "key_takeaways": [
                    "💡 Mental Model: Like library bookshelves split across separate rooms",
                    "⚖️ Core Trade-off: Infinite write capacity vs no cross-shard joins",
                    "🎯 Interview Rule: Always choose shard keys with uniform cardinality"
                ],
                "call_to_action": "What's your answer to the Slide 5 interview dilemma? Drop A or B below! 👇",
                "hashtags": ["systemdesign", "backend", "database", "cloudarchitecture", "devcommunity"]
            },
            "slides": [
                {
                    "slide_number": 1,
                    "title_html": "Database Sharding <span class='highlight-yellow'>Explained Simply</span>",
                    "subtitle": "The bottleneck every scaling backend encounters",
                    "mental_model": {
                        "title": "The 5-Second Real-World Analogy",
                        "body": "Imagine a library with 1 million books. Instead of cramming them into one giant bookshelf that collapses under its own weight, you build 5 separate shelves (A-E, F-J, K-O, P-T, U-Z) in different rooms!",
                        "style": "sticky-yellow"
                    },
                    "footer_hint": "Swipe for Step-by-Step Flow ➡️"
                },
                {
                    "slide_number": 2,
                    "title_html": "Step-by-Step <span class='highlight-mint'>Partition Routing</span>",
                    "subtitle": "How queries find the right physical server in O(1) time",
                    "diagram_nodes": [
                        {"icon": "📱", "label": "Client API", "sub": "GET /user/42", "step": "STEP 1"},
                        {"icon": "⚡", "label": "Shard Router", "sub": "hash(42) % 4 = Shard 2", "step": "STEP 2", "status": "Sub-1ms", "highlight": True},
                        {"icon": "🗄️", "label": "Shard Node 2", "sub": "Isolated IOPS", "step": "STEP 3"}
                    ],
                    "footer_hint": "Real-World Case Study ➡️"
                },
                {
                    "slide_number": 3,
                    "title_html": "Real-World Case Study: <span class='highlight-blue'>Notion / Pinterest</span>",
                    "subtitle": "How high-scale platforms scaled from 1 DB to dozens",
                    "cards": [
                        {
                            "title": "Notion's 480 Postgres Shards",
                            "icon": "🏗️",
                            "body": "Notion partitioned its Postgres database into 480 physical logical shards based on Workspace UUID, eliminating single-node storage ceilings."
                        },
                        {
                            "title": "The Trade-off",
                            "icon": "⚠️",
                            "body": "Cross-workspace joins became impossible at the DB level, requiring fast application-layer aggregation."
                        }
                    ],
                    "footer_hint": "Interview Cheat Sheet ➡️"
                },
                {
                    "slide_number": 4,
                    "title_html": "The 'Never Forget' <span class='highlight-yellow'>Cheat Sheet</span>",
                    "subtitle": "Trade-offs you must know for technical interviews",
                    "cheat_sheet": {
                        "when_to_use": "• Dataset exceeds single-server NVMe capacity (>10TB)<br>• Write throughput saturates single primary IOPS<br>• Need clear blast radius isolation between tenants",
                        "when_it_fails": "• Premature optimization on <100GB databases<br>• Complex multi-table joins are frequent<br>• Re-sharding when key distribution becomes skewed"
                    },
                    "cards": [
                        {
                            "title": "Staff Engineer Rule of Thumb",
                            "icon": "📌",
                            "body": "Never shard until you have exhausted vertical scaling, read-replicas, and Redis caching. Sharding introduces massive operational complexity."
                        }
                    ],
                    "footer_hint": "Pop Quiz ➡️"
                },
                {
                    "slide_number": 5,
                    "title_html": "Senior Engineer <span class='highlight-coral'>Pop Quiz</span>",
                    "subtitle": "Test your distributed database judgment",
                    "quiz": {
                        "title": "System Design Interview Dilemma",
                        "question": "When user orders and user profiles live on different physical database shards, how do you query both without crashing the system?",
                        "option_a": "Application-level aggregation (parallel async fetch)",
                        "option_b": "Distributed 2-Phase Commit SQL JOIN across shards"
                    },
                    "footer_hint": "Save & Comment Below 👇"
                }
            ]
        }

    # Step 2: Render Slides HTML & PNG with Selected Theme (Default: Digital Engineering Notebook)
    out_dir = os.path.abspath(args.output_dir)
    print(f"[*] Rendering 5x 1080x1350 PNG slides with theme '{args.theme}' to '{out_dir}'...")
    png_paths = generate_carousel_images(carousel_data, out_dir, theme=args.theme)
    print(f"[+] Rendered {len(png_paths)} slides successfully!")

    # Step 3: Telegram Notification
    if not args.dry_run:
        try:
            print("[*] Sending engineering notebook carousel & interactive controls to Telegram...")
            send_to_telegram(png_paths, carousel_data['caption'], topic_info['topic'])
            print("[+] Telegram message delivered successfully!")
            mark_topic_completed(topic_info['id'])
        except Exception as e:
            print(f"[!] Telegram delivery failed ({e}).")
    else:
        print("[i] Dry-run mode enabled: skipped Telegram delivery.")

if __name__ == "__main__":
    main()

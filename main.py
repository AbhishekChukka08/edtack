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

    out_dir = os.path.abspath(args.output_dir)
    png_paths = []
    caption = ""

    # Primary: 5-Slide Infographic Image Generation (gemini-3.1-flash-lite-image)
    try:
        from src.infographic_generator import generate_infographic_carousel
        print(f"[*] Generating 5-slide visual infographic carousel with gemini-3.1-flash-lite-image...")
        png_paths, caption = generate_infographic_carousel(topic_info, output_dir=out_dir)
    except Exception as img_err:
        print(f"[!] Infographic image model skipped or hit limit ({img_err}). Falling back to HTML/CSS/Mermaid Playwright engine...")
        try:
            print("[*] Generating digital engineering notebook script with Gemini...")
            carousel_data = generate_carousel_content(topic_info)
        except Exception as e:
            print(f"[!] Gemini text API failed ({e}). Using structured notebook template...")
            carousel_data = {
                "topic_id": topic_info.get("id", "db-sharding"),
                "category": topic_info.get("category", "Database Architecture"),
                "handle": "edtack_edu",
                "caption": {
                    "hook": f"How {topic_info['topic']} works in high-scale production systems.",
                    "body": topic_info.get('summary', 'Engineering notebook cheat sheet breakdown.'),
                    "key_takeaways": [
                        "💡 Mental Model: High-scale architectural trade-offs",
                        "⚖️ Core Trade-off: Latency vs consistency vs memory",
                        "🎯 Interview Rule: Optimize for the primary production bottleneck"
                    ],
                    "call_to_action": "What's your answer to the Slide 5 interview dilemma? Drop A or B below! 👇",
                    "hashtags": ["systemdesign", "backend", "genai", "softwareengineering", "edtack_edu"]
                },
                "slides": [
                    {
                        "slide_number": 1,
                        "title_html": f"{topic_info['topic']} <span class='highlight-yellow'>Explained Simply</span>",
                        "subtitle": "The bottleneck every scaling backend encounters",
                        "mental_model": {
                            "title": "The 5-Second Real-World Analogy",
                            "body": topic_info.get("summary", "Mental model breakdown."),
                            "style": "sticky-yellow"
                        },
                        "footer_hint": "Swipe for Step-by-Step Flow ➡️"
                    },
                    {
                        "slide_number": 2,
                        "title_html": "Step-by-Step <span class='highlight-mint'>Architectural Flow</span>",
                        "subtitle": "How the pipeline executes step-by-step",
                        "diagram_nodes": [
                            {"icon": "📱", "label": "Client API", "sub": "Initiates Request", "step": "STEP 1"},
                            {"icon": "⚡", "label": "Processor", "sub": "High-throughput node", "step": "STEP 2", "highlight": True},
                            {"icon": "🗄️", "label": "Storage", "sub": "Distributed State", "step": "STEP 3"}
                        ],
                        "footer_hint": "Real-World Case Study ➡️"
                    },
                    {
                        "slide_number": 3,
                        "title_html": "Real-World Case Study: <span class='highlight-blue'>Production Scale</span>",
                        "subtitle": "How top engineering teams deploy it",
                        "cards": [
                            {"title": "Production Deployment", "icon": "🏗️", "body": "Deployed across high-availability clusters to guarantee 99.99% uptime."},
                            {"title": "The Trade-off", "icon": "⚠️", "body": "Balancing resource footprint with throughput and response latency."}
                        ],
                        "footer_hint": "Interview Cheat Sheet ➡️"
                    },
                    {
                        "slide_number": 4,
                        "title_html": "The 'Never Forget' <span class='highlight-yellow'>Cheat Sheet</span>",
                        "subtitle": "Trade-offs you must know for technical interviews",
                        "cheat_sheet": {
                            "when_to_use": "• High traffic throughput requirement<br>• Scalable distributed workloads<br>• Need clear fault isolation",
                            "when_it_fails": "• Small trivial datasets<br>• Over-engineering before measuring<br>• High network latency hops"
                        },
                        "footer_hint": "Senior Engineer Pop Quiz ➡️"
                    },
                    {
                        "slide_number": 5,
                        "title_html": "Senior Engineer <span class='highlight-coral'>Pop Quiz</span>",
                        "subtitle": "Test your system design judgment",
                        "quiz": {
                            "title": "System Design Interview Dilemma",
                            "question": f"When deploying {topic_info['topic']} in high-throughput production, which architecture do you prioritize?",
                            "option_a": "Option A: Maximum throughput with asynchronous batching",
                            "option_b": "Option B: Strict low latency with isolated compute instances"
                        },
                        "footer_hint": "Save & Comment Below 👇"
                    }
                ]
            }

        print(f"[*] Rendering 5x 1080x1350 PNG slides with theme '{args.theme}' to '{out_dir}'...")
        png_paths = generate_carousel_images(carousel_data, out_dir, theme=args.theme)
        caption = carousel_data.get('caption', {})
        print(f"[+] Rendered {len(png_paths)} slides successfully!")

    # Step 2: Telegram Notification
    if not args.dry_run and png_paths:
        try:
            print("[*] Sending engineering carousel & interactive controls to Telegram...")
            send_to_telegram(png_paths, caption, topic_info['topic'])
            print("[+] Telegram message delivered successfully!")
            mark_topic_completed(topic_info['id'])
        except Exception as e:
            print(f"[!] Telegram delivery failed ({e}).")
    else:
        print("[i] Dry-run mode enabled or no slides rendered: skipped Telegram delivery.")

if __name__ == "__main__":
    main()

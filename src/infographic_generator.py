import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

HANDLE = "edtack_edu"
IMAGE_MODEL = "gemini-3.1-flash-lite-image"

def get_client() -> genai.Client:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not set in environment.")
    return genai.Client(api_key=api_key)


def build_slide_prompts(topic_info: dict) -> list[dict]:
    """Builds tailored, high-yield infographic prompts for the 5-slide carousel."""
    title = topic_info.get("topic", "System Architecture")
    category = topic_info.get("category", "Generative AI & LLM Systems")
    summary = topic_info.get("summary", "")

    return [
        {
            "num": 1,
            "filename": "slide_1.png",
            "prompt": f"""A masterclass infographic cheat sheet on a crisp white background titled '{title.upper()} (PART 1: THE INTUITION)', in the exact visual style of Brij Kishore Pandey's famous engineering cheat sheets.

Visual Style:
- Clean white background, minimalist, beautiful, and highly structured.
- Pastel color-coded rounded cards (sky blue, soft green, pale yellow).
- Cute vector illustrations: friendly icons, magnifying glass, sentence connection arcs.
- Ultra-crisp typography, completely legible and easy to read.
- Footer mark: '@{HANDLE}'

Content & Simplicity (Explain like I am 15 with ZERO unnecessary jargon):
- Header: Slide 1 of 5 • The Intuition & Mental Model
- The Problem: Explain the core bottleneck or limitation before this concept existed. ({summary})
- The Core Analogy: Relatable 5-second real-world everyday analogy that makes the concept click instantly.
- The 3 Simple Roles Explained: Break down the 3 main parts/roles with friendly icons.
- Bottom Hint: Swipe for the Step-by-Step Flow ➡️
"""
        },
        {
            "num": 2,
            "filename": "slide_2.png",
            "prompt": f"""A masterclass infographic cheat sheet on a crisp white background titled '{title.upper()}: STEP-BY-STEP DATA FLOW', in the exact visual style of Brij Kishore Pandey's famous engineering cheat sheets.

Visual Style:
- Clean white background, minimalist and highly structured.
- Horizontal step-by-step pipeline layout with arrows and pastel numbered cards.
- Clean vector icons (data blocks, matrix grid, processing nodes, lightbulb).
- Ultra-crisp, legible labels.
- Footer mark: '@{HANDLE}'

Content:
- Header: Slide 2 of 5 • The Architectural Flow
- Clear 5-step numbered flow showing inputs transforming into the final output.
- Step 1: Input preparation & representation
- Step 2: Intermediate transformation / feature extraction
- Step 3: Core matching / mathematical scoring mechanism
- Step 4: Normalization / filtering / ranking
- Step 5: Final output generation / weighted context assembly
- Clean highlighted formula or system guarantee callout box at the bottom.
- Bottom Hint: Real-World Case Study ➡️
"""
        },
        {
            "num": 3,
            "filename": "slide_3.png",
            "prompt": f"""A masterclass infographic cheat sheet on a crisp white background titled '{title.upper()}: REAL-WORLD PRODUCTION ARCHITECTURE', in the exact visual style of Brij Kishore Pandey's famous engineering cheat sheets.

Visual Style:
- Clean white background, minimalist and highly structured.
- Pastel color-coded rounded cards (lavender, mint, coral).
- Diagram showing multi-path or parallel processing components.
- Ultra-crisp, legible typography.
- Footer mark: '@{HANDLE}'

Content:
- Header: Slide 3 of 5 • Real-World Production Architecture
- Everyday Analogy: Why simple single-worker setups fail at scale.
- How Modern Production Systems (e.g. OpenAI, Google, Anthropic, Netflix) Implement It:
  * Component 1: Dedicated specialized processing path (e.g. syntax / grammar / caching).
  * Component 2: Cross-referencing & relational mapping path.
  * Component 3: Semantic & contextual aggregation path.
- Production Numbers: Scale metrics and parallel concurrency in high-throughput production clusters.
- Bottom Hint: Interview Cheat Sheet ➡️
"""
        },
        {
            "num": 4,
            "filename": "slide_4.png",
            "prompt": f"""A masterclass infographic cheat sheet on a crisp white background titled '{title.upper()} CHEAT SHEET: TRADE-OFFS & LIMITS', in the exact visual style of Brij Kishore Pandey's famous engineering cheat sheets.

Visual Style:
- Clean white background, 2-column comparative cheat sheet layout.
- Green card on left (When It Dominates 🟢), Red card on right (The Critical Bottleneck 🔴).
- Micro-table and clear bullet points.
- Ultra-crisp typography.
- Footer mark: '@{HANDLE}'

Content:
- Header: Slide 4 of 5 • Trade-Offs & Limits
- Left Column (🟢 Why It Dominates):
  * Massive throughput & parallel scalability advantages
  * Direct retrieval / speed benefits over traditional alternatives
- Right Column (🔴 The Critical Failure Modes & Bottlenecks):
  * Computational or memory scaling walls (e.g. quadratic memory, network saturation)
  * Latency or cost implications at high scale
- The Modern Solutions: 2 key engineering tricks or optimizations used to overcome these bottlenecks.
- Bottom Hint: Pop Quiz Dilemma ➡️
"""
        },
        {
            "num": 5,
            "filename": "slide_5.png",
            "prompt": f"""A masterclass infographic cheat sheet on a crisp white background titled 'SYSTEM DESIGN POP QUIZ: {title.upper()}', in the exact visual style of Brij Kishore Pandey's famous engineering cheat sheets.

Visual Style:
- Clean white background with a prominent, warm amber/yellow dilemma card.
- High-contrast Option A vs Option B comparison boxes.
- Call to action with comment bubbles and debate icons.
- Ultra-crisp, inviting typography.
- Footer mark: '@{HANDLE}'

Content:
- Header: Slide 5 of 5 • Senior Engineer Interview Dilemma
- Concrete Scenario: A high-scale production situation requiring an architectural choice.
- Option A: First viable architectural approach with its pros and minor trade-off.
- Option B: Second viable architectural approach with its alternative benefits.
- The Core Question: Which architecture would you deploy to production?
- Call to Action: Drop 'A' or 'B' with your reasoning in the comments! 👇
"""
        }
    ]


def _generate_single_slide(client: genai.Client, slide_info: dict, output_dir: str) -> str:
    """Generates a single slide image via Gemini Image API."""
    out_path = os.path.join(output_dir, slide_info["filename"])
    t0 = time.time()
    
    response = client.models.generate_content(
        model=IMAGE_MODEL,
        contents=slide_info["prompt"],
        config=types.GenerateContentConfig(
            image_config=types.ImageConfig(
                aspect_ratio="3:4",
                image_size="1K"
            )
        )
    )
    
    for part in response.candidates[0].content.parts:
        if hasattr(part, "inline_data") and part.inline_data:
            with open(out_path, "wb") as f:
                f.write(part.inline_data.data)
            duration = time.time() - t0
            print(f"[+] Slide {slide_info['num']}/5 generated in {duration:.1f}s -> {out_path}")
            return out_path
            
    raise RuntimeError(f"No image data returned for Slide {slide_info['num']}")


def generate_infographic_carousel(topic_info: dict, output_dir: str = "./output") -> tuple[list[str], str]:
    """
    Generates a 5-slide visual infographic carousel for Instagram using gemini-3.1-flash-lite-image.
    Executes in parallel for ultra-fast generation (~5-10 seconds total).
    Returns (list_of_png_paths, caption_text).
    """
    client = get_client()
    os.makedirs(output_dir, exist_ok=True)
    
    slide_prompts = build_slide_prompts(topic_info)
    png_paths = [None] * len(slide_prompts)
    
    print(f"[*] Concurrently generating 5 infographic slides for '{topic_info.get('topic')}'...")
    start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_idx = {
            executor.submit(_generate_single_slide, client, s_info, output_dir): idx
            for idx, s_info in enumerate(slide_prompts)
        }
        for future in as_completed(future_to_idx):
            idx = future_to_idx[future]
            png_paths[idx] = future.result()
            
    total_time = time.time() - start_time
    print(f"[✓] All 5 slides generated in parallel in {total_time:.1f} seconds!")
    
    # Generate engaging Instagram caption
    title = topic_info.get("topic", "System Design")
    category = topic_info.get("category", "LLM Systems")
    
    caption = (
        f"🔥 {title} Explained Simply (5-Slide Visual Cheat Sheet) 📓\n\n"
        f"Swipe through the visual guide below! ➡️\n"
        f"• Slide 1: The 5-second intuition & real-world analogy\n"
        f"• Slide 2: Step-by-step architectural data flow\n"
        f"• Slide 3: Real-world production architecture\n"
        f"• Slide 4: Trade-offs & scaling limits cheat sheet\n"
        f"• Slide 5: Senior engineer interview dilemma\n\n"
        f"💡 Drop your answer to the Slide 5 pop quiz (A or B) in the comments! 👇\n\n"
        f"Follow @{HANDLE} for daily hand-crafted visual cheat sheets on Generative AI & System Design.\n\n"
        f"#{title.lower().replace(' ', '').replace('-', '')} #systemdesign #machinelearning #genai #llm "
        f"#deeplearning #softwareengineering #coding #developers #{HANDLE}"
    )
    
    return png_paths, caption

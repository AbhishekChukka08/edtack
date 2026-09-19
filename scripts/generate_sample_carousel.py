import os
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY is not set.")

client = genai.Client(api_key=api_key)
out_dir = os.path.join(os.getcwd(), "output", "sample_carousel")
os.makedirs(out_dir, exist_ok=True)

slides_prompts = [
    {
        "num": 1,
        "name": "slide_1_intuition.png",
        "prompt": """A masterclass infographic cheat sheet on a crisp white background titled 'TRANSFORMER ATTENTION (PART 1: THE INTUITION)', in the exact visual style of Brij Kishore Pandey's famous engineering cheat sheets.

Visual Style:
- Clean white background, minimalist, beautiful and highly structured.
- Pastel color-coded rounded cards (sky blue, soft green, pale yellow).
- Cute vector illustrations: brain, magnifying glass, sentence connection arcs.
- Ultra-crisp typography, completely legible.

Content:
- Header: Slide 1 of 5 • The Intuition & Analogy
- The Problem: Traditional models read word-by-word and forgot the beginning of long paragraphs.
- The Core Analogy: When reading 'The trophy didn't fit in the suitcase because it was too big', what is 'it'? Attention scores connect 'it' to 'trophy'!
- The 3 Simple Roles Explained:
  * 🔍 Query (Q): 'What am I searching for?'
  * 🏷️ Key (K): 'What is my identity / label?'
  * 📦 Value (V): 'The actual information content'
- Bottom Hint: Swipe for the Step-by-Step Flow ➡️
"""
    },
    {
        "num": 2,
        "name": "slide_2_flow.png",
        "prompt": """A masterclass infographic cheat sheet on a crisp white background titled 'SELF-ATTENTION: STEP-BY-STEP DATA FLOW', in the exact visual style of Brij Kishore Pandey's famous engineering cheat sheets.

Visual Style:
- Clean white background, minimalist and highly structured.
- Horizontal step-by-step pipeline layout with arrows and pastel numbered cards.
- Clean vector icons (word blocks, matrix grid, scale, lightbulb).
- Ultra-crisp, legible labels.

Content:
- Header: Slide 2 of 5 • The Architectural Flow
- Step 1: Input Words converted to numerical Embeddings
- Step 2: Multiply by Weights to create Q, K, and V vectors
- Step 3: Dot Product (Q · K) to calculate Attention Raw Scores (Who is relevant to whom?)
- Step 4: Scale & Softmax (Convert scores into clean probabilities between 0% and 100%)
- Step 5: Weighted Sum (Multiply Softmax probabilities by Value V to create the enriched Context Vector!)
- Formula Callout in a clean box: Attention(Q, K, V) = softmax(Q · K^T / √d_k) · V
"""
    },
    {
        "num": 3,
        "name": "slide_3_real_world.png",
        "prompt": """A masterclass infographic cheat sheet on a crisp white background titled 'MULTI-HEAD ATTENTION: REAL-WORLD EXAMPLE', in the exact visual style of Brij Kishore Pandey's famous engineering cheat sheets.

Visual Style:
- Clean white background, minimalist and highly structured.
- Pastel color-coded rounded cards (lavender, mint, coral).
- Diagram showing parallel processing heads splitting and concatenating.
- Ultra-crisp, legible typography.

Content:
- Header: Slide 3 of 5 • Real-World Production Architecture
- Analogy: One detective looks for clues, but a team of specialized detectives spots everything at once!
- How Modern LLMs (GPT-4, Claude) Process:
  * Head 1 (Syntax): Tracks grammar and subject-verb pairs ('cat' -> 'sat').
  * Head 2 (Coreference): Tracks pronouns ('it' -> 'trophy').
  * Head 3 (Semantic Context): Tracks emotion and topic.
- Production Architecture: In GPT-style models, 32 to 128 attention heads run in parallel, then concatenate back together!
"""
    },
    {
        "num": 4,
        "name": "slide_4_cheat_sheet.png",
        "prompt": """A masterclass infographic cheat sheet on a crisp white background titled 'ATTENTION CHEAT SHEET: TRADE-OFFS & LIMITS', in the exact visual style of Brij Kishore Pandey's famous engineering cheat sheets.

Visual Style:
- Clean white background, 2-column comparative cheat sheet layout.
- Green card on left (When Attention Dominates 🟢), Red card on right (The Critical Bottleneck 🔴).
- Micro-table and clear pros/cons list.
- Ultra-crisp typography.

Content:
- Header: Slide 4 of 5 • Trade-Offs & Limits
- Left Side (🟢 Why Transformers Won):
  * 100% Parallel Training (GPUs run at maximum throughput)
  * Direct connections between any 2 words regardless of distance
- Right Side (🔴 The O(N²) Quadratic Memory Wall):
  * Doubling context length quadruples memory and compute!
  * 100k tokens = 10,000,000,000 attention calculations!
- The Modern Solutions: FlashAttention (SRAM tiling) & KV Caching.
"""
    },
    {
        "num": 5,
        "name": "slide_5_interview_dilemma.png",
        "prompt": """A masterclass infographic cheat sheet on a crisp white background titled 'SYSTEM DESIGN POP QUIZ: THE KV CACHE CRISIS', in the exact visual style of Brij Kishore Pandey's famous engineering cheat sheets.

Visual Style:
- Clean white background with a prominent, warm amber/yellow dilemma card.
- High-contrast Option A vs Option B comparison boxes.
- Call to action with comment bubbles and debate icons.
- Ultra-crisp, inviting typography.

Content:
- Header: Slide 5 of 5 • Senior Engineer Interview Dilemma
- Scenario: Your AI chatbot handles 100k-token conversations. Your GPU VRAM is overflowing due to storing Key-Value caches for thousands of users.
- Option A: Multi-Query Attention (MQA / GQA) - Share Key and Value heads across all query heads. Saves 8x VRAM with ~1% quality loss.
- Option B: Sliding Window Attention - Keep KV cache only for the last 4,096 tokens, discarding older history.
- The Question: Which architecture would you deploy to production?
- Call to Action: Drop 'A' or 'B' with your reasoning in the comments! 👇
"""
    }
]

print("Starting generation of 5 focused infographic carousel slides...")
for s in slides_prompts:
    out_file = os.path.join(out_dir, s["name"])
    print(f"[*] Generating Slide {s['num']}/5: {s['name']}...")
    t0 = time.time()
    resp = client.models.generate_content(
        model="gemini-3.1-flash-lite-image",
        contents=s["prompt"],
        config=types.GenerateContentConfig(
            image_config=types.ImageConfig(
                aspect_ratio="3:4",
                image_size="1K"
            )
        )
    )
    for part in resp.candidates[0].content.parts:
        if hasattr(part, "inline_data") and part.inline_data:
            with open(out_file, "wb") as f:
                f.write(part.inline_data.data)
            print(f"[+] Completed Slide {s['num']} in {time.time()-t0:.1f}s -> {out_file} ({len(part.inline_data.data)} bytes)")

print("\n[✓] All 5 focused infographic slides generated successfully!")

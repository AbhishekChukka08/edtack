import os
import asyncio
from jinja2 import Environment, FileSystemLoader
from playwright.async_api import async_playwright
from src.svg_diagram_generator import (
    generate_client_server_db_svg,
    generate_horizontal_flow_svg,
    generate_comparison_table_svg
)
from src.mermaid_generator import clean_mermaid_code, get_mermaid_for_slide

TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates')

def render_html_files(carousel_data: dict, output_dir: str, theme: str = "theme-notebook") -> list[str]:
    """Renders Jinja2 HTML templates with inlined CSS, Mermaid infographics & sketched notebook SVGs."""
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    template = env.get_template('slide.html')
    
    css_path = os.path.join(TEMPLATE_DIR, 'style.css')
    css_content = ""
    if os.path.exists(css_path):
        with open(css_path, 'r', encoding='utf-8') as f:
            css_content = f.read()

    os.makedirs(output_dir, exist_ok=True)
    rendered_html_paths = []
    topic_id = carousel_data.get('topic_id', '')

    for slide in carousel_data['slides']:
        s_num = slide.get("slide_number", 1)
        diagram_svg = ""
        mermaid_code = clean_mermaid_code(slide.get("mermaid_code", ""))
        micro_infographic = slide.get("micro_infographic")

        # 1. Topic-Specific Mermaid Diagram Selection
        if not mermaid_code and s_num in [1, 2]:
            fallback_diag = get_mermaid_for_slide(topic_id, s_num)
            if fallback_diag.get("mermaid"):
                mermaid_code = clean_mermaid_code(fallback_diag["mermaid"])
            if not micro_infographic and fallback_diag.get("micro_infographic"):
                micro_infographic = fallback_diag["micro_infographic"]

        # 2. Secondary SVG Fallback (if no Mermaid code)
        if not mermaid_code:
            if "diagram_nodes" in slide and slide["diagram_nodes"]:
                diagram_svg = generate_horizontal_flow_svg(slide["diagram_nodes"])
            elif s_num == 1:
                diagram_svg = generate_client_server_db_svg()
            elif s_num == 2:
                default_nodes = [
                    {"icon": "📱", "label": "Client App", "sub": "Sends Request", "step": "STEP 1"},
                    {"icon": "⚡", "label": "Memory Cache", "sub": "RAM Hit (0.5ms)", "step": "STEP 2", "status": "Sub-1ms", "highlight": True},
                    {"icon": "🗄️", "label": "Database", "sub": "Async Sync", "step": "STEP 3"}
                ]
                diagram_svg = generate_horizontal_flow_svg(default_nodes)
            elif s_num == 3 and not slide.get("cards"):
                diagram_svg = generate_comparison_table_svg()

        # 3. Ensure cards / cheat sheet / quiz are populated
        cards = slide.get("cards", [])
        cheat_sheet = slide.get("cheat_sheet")
        quiz = slide.get("quiz")
        mental_model = slide.get("mental_model")

        # Fallback for Slide 4 cheat sheet if not specified
        if s_num == 4 and not cheat_sheet and not cards:
            cheat_sheet = {
                "when_to_use": "• Read-heavy workloads (>80% reads)<br>• Tolerant of eventual consistency<br>• Predictable access keys",
                "when_it_fails": "• Write-heavy hot rows (cache churn)<br>• Strict ACID financial transactions<br>• High cache invalidation cost"
            }

        # Fallback for Slide 5 quiz if not specified
        if s_num == 5 and not quiz and not cards:
            quiz = {
                "title": "Senior System Design Interview Dilemma",
                "question": "When your primary cache crashes under peak traffic, how do you prevent all backend queries from swamping and taking down the database simultaneously?",
                "option_a": "Circuit Breaker + Mutual Exclusion (Mutex Lock)",
                "option_b": "Directly double database connection pool limit"
            }

        slide_ctx = {
            **slide,
            "theme_class": theme,
            "cards": cards,
            "cheat_sheet": cheat_sheet,
            "quiz": quiz,
            "mental_model": mental_model,
            "css_content": css_content,
            "diagram_svg": diagram_svg,
            "mermaid_code": mermaid_code,
            "micro_infographic": micro_infographic,
            "category": carousel_data.get('category', 'SYSTEM DESIGN CHEAT SHEET'),
            "handle": carousel_data.get('handle', 'edtack_tech')
        }
        
        html_content = template.render(**slide_ctx)
        file_path = os.path.join(output_dir, f"slide_{s_num}.html")
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
            
        rendered_html_paths.append(file_path)

    return rendered_html_paths


async def convert_html_to_png_async(html_paths: list[str], output_dir: str) -> list[str]:
    """Uses Playwright headless browser to render 1080x1350 screenshots of each slide."""
    png_paths = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1080, "height": 1350}, device_scale_factor=2)

        for idx, html_path in enumerate(html_paths, start=1):
            file_url = f"file:///{os.path.abspath(html_path).replace('\\', '/')}"
            await page.goto(file_url, wait_until="networkidle")
            
            # If slide has a Mermaid diagram, wait for vector rendering
            try:
                mermaid_elem = await page.query_selector('.mermaid')
                if mermaid_elem:
                    await page.wait_for_selector('.mermaid svg', timeout=8000)
            except Exception as err:
                print(f"[*] Note on Slide {idx} Mermaid rendering: {err}")

            await page.wait_for_timeout(350)
            
            png_path = os.path.join(output_dir, f"slide_{idx}.png")
            await page.screenshot(path=png_path, full_page=True, type="png")
            png_paths.append(png_path)

        await browser.close()
        
    return png_paths


async def generate_carousel_images_async(carousel_data: dict, output_dir: str, theme: str = "theme-notebook") -> list[str]:
    """Asynchronous pipeline for generating carousel PNG slides."""
    html_paths = render_html_files(carousel_data, output_dir, theme=theme)
    return await convert_html_to_png_async(html_paths, output_dir)


def generate_carousel_images(carousel_data: dict, output_dir: str, theme: str = "theme-notebook") -> list[str]:
    """Synchronous wrapper for generating carousel PNG slides."""
    return asyncio.run(generate_carousel_images_async(carousel_data, output_dir, theme=theme))

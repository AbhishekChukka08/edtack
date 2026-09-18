import os
import json
import pytest
from src.renderer import render_html_files
from src.telegram_bot import format_caption_text

@pytest.fixture
def mock_carousel_data():
    return {
        "topic_id": "redis-cache-aside",
        "category": "Caching & Performance",
        "handle": "tech_architecture_daily",
        "caption": {
            "hook": "Master Redis Cache-Aside Pattern",
            "body": "How to scale backend database reads.",
            "key_takeaways": ["Sub-ms latency", "DB protection"],
            "call_to_action": "Comment your choice below!",
            "hashtags": ["#systemdesign", "#backend"]
        },
        "slides": [
            {
                "slide_number": 1,
                "title_html": "Redis <span class='highlight'>Cache-Aside</span>",
                "subtitle": "High-scale backend caching architecture",
                "cards": [
                    {
                        "title": "The DB Bottleneck",
                        "icon": "⚠️",
                        "body": "Direct DB queries fail under high QPS."
                    }
                ],
                "footer_hint": "Swipe to Solve ➡️"
            }
        ]
    }

def test_html_rendering(tmp_path, mock_carousel_data):
    output_dir = str(tmp_path)
    rendered_files = render_html_files(mock_carousel_data, output_dir)
    
    assert len(rendered_files) == 1
    assert os.path.exists(rendered_files[0])
    
    with open(rendered_files[0], 'r', encoding='utf-8') as f:
        html = f.read()
        assert "ENGINEERING CHEAT SHEET" in html
        assert "Redis <span class='highlight'>Cache-Aside</span>" in html

def test_caption_formatting(mock_carousel_data):
    caption_text = format_caption_text(mock_carousel_data['caption'], "Redis Cache-Aside")
    
    assert "🚀 Master Redis Cache-Aside Pattern" in caption_text
    assert "• Sub-ms latency" in caption_text
    assert "#systemdesign #backend" in caption_text

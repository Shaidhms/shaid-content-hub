#!/usr/bin/env python3
"""Capture screenshots of real articles for carousel reference images."""

from playwright.sync_api import sync_playwright
import os

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "reference_screenshots")

URLS = [
    {
        "name": "claude-code-satisfaction",
        "url": "https://newsletter.pragmaticengineer.com/p/ai-tooling-2026",
        "desc": "Pragmatic Engineer - AI Tooling 2026 survey (Claude Code 46% satisfaction)",
    },
    {
        "name": "copilot-market-share",
        "url": "https://www.getpanto.ai/blog/ai-coding-assistant-statistics",
        "desc": "AI Coding Assistant Statistics 2026 (Copilot market share, adoption stats)",
    },
    {
        "name": "cursor-vs-claude-code",
        "url": "https://www.builder.io/blog/cursor-vs-claude-code",
        "desc": "Builder.io - Cursor vs Claude Code 2026 (token efficiency comparison)",
    },
    {
        "name": "windsurf-ranked-1",
        "url": "https://www.taskade.com/blog/windsurf-review",
        "desc": "Windsurf Review 2026 (ranked #1 by LogRocket)",
    },
    {
        "name": "ai-coding-landscape",
        "url": "https://toolshelf.dev/blog/ai-coding-landscape-2026",
        "desc": "AI Coding Landscape 2026 overview",
    },
    {
        "name": "copilot-agent-mode",
        "url": "https://github.com/features/copilot",
        "desc": "GitHub Copilot features page",
    },
]


def capture_screenshots():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(
            viewport={"width": 1280, "height": 900},
            device_scale_factor=2,
        )

        for item in URLS:
            page = context.new_page()
            print(f"Capturing: {item['name']} - {item['url']}")
            try:
                page.goto(item["url"], timeout=30000, wait_until="networkidle")
                # Wait a bit for lazy-loaded content
                page.wait_for_timeout(2000)
                # Dismiss cookie banners if any
                for selector in [
                    "button:has-text('Accept')",
                    "button:has-text('Got it')",
                    "button:has-text('Close')",
                    "[class*='cookie'] button",
                    "[class*='consent'] button",
                ]:
                    try:
                        btn = page.locator(selector).first
                        if btn.is_visible(timeout=1000):
                            btn.click()
                            page.wait_for_timeout(500)
                    except:
                        pass

                output_path = os.path.join(OUTPUT_DIR, f"{item['name']}.png")
                page.screenshot(path=output_path, full_page=False)
                print(f"  Saved: {output_path}")
            except Exception as e:
                print(f"  ERROR: {e}")
            finally:
                page.close()

        browser.close()


if __name__ == "__main__":
    capture_screenshots()

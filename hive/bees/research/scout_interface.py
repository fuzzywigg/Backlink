from abc import ABC, abstractmethod

from playwright.sync_api import sync_playwright


class ScoutInterface(ABC):
    """
    Abstract Interface for the Scout Bee's Web Capabilities.
    Standardizes interaction whether using Playwright, or MCP-like bridges.
    """

    @abstractmethod
    def navigate(self, url: str) -> bool:
        """Navigates to a URL."""
        pass

    @abstractmethod
    def extract_text(self, selector: str = "body") -> str:
        """Extracts text from the current page."""
        pass

    @abstractmethod
    def screenshot(self, path: str) -> str:
        """Takes a screenshot for visual analysis."""
        pass

    @abstractmethod
    def click(self, selector: str) -> bool:
        """Interacts with an element."""
        pass


class SovereignScout(ScoutInterface):
    """
    Implementation of ScoutInterface using Sovereign tools (Playwright, local).
    """

    def __init__(self, headless: bool = True):
        self.headless = headless
        self.playwright = None
        self.browser = None
        self.page = None
        self._setup()

    def _setup(self):
        """Initializes the browser session."""
        try:
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.launch(headless=self.headless)
            self.page = self.browser.new_page()
            # Set a standard user agent to avoid basic blocks
            self.page.set_extra_http_headers({
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            })
        except Exception as e:
            print(f"[Scout] Setup Error: {e}")

    def navigate(self, url: str) -> bool:
        if not self.page:
            return False
        try:
            print(f"[Scout] Navigating to {url}...")
            self.page.goto(url, wait_until="domcontentloaded", timeout=30000)
            return True
        except Exception as e:
            print(f"[Scout] Navigation Error: {e}")
            return False

    def extract_text(self, selector: str = "body") -> str:
        if not self.page:
            return ""
        try:
            # Prefer inner_text for readable content
            return self.page.inner_text(selector)
        except Exception as e:
            print(f"[Scout] Extraction Error: {e}")
            return ""

    def screenshot(self, path: str) -> str:
        if not self.page:
            return ""
        try:
            self.page.screenshot(path=path)
            print(f"[Scout] Saved screenshot to {path}")
            return path
        except Exception as e:
            print(f"[Scout] Screenshot Error: {e}")
            return ""

    def click(self, selector: str) -> bool:
        if not self.page:
            return False
        try:
            self.page.click(selector)
            return True
        except Exception as e:
            print(f"[Scout] Interaction Error: {e}")
            return False

    def close(self):
        """Clean shutdown."""
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()

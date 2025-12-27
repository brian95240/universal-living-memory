"""
Web Browser Integration for Ghost Mode
Vertex Genesis v1.4.0

Provides autonomous web browsing capabilities for Ghost Mode:
- Voice-commanded web searches
- Autonomous page navigation
- Content extraction and summarization
- Form filling and submission
- Integration with Vaultwarden for credentials
"""

import logging
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
import asyncio

logger = logging.getLogger(__name__)


class BrowserAction(Enum):
    """Browser action types."""
    SEARCH = "search"
    NAVIGATE = "navigate"
    READ = "read"
    FILL_FORM = "fill_form"
    CLICK = "click"
    EXTRACT = "extract"
    SCREENSHOT = "screenshot"


@dataclass
class BrowserCommand:
    """Browser command representation."""
    action: BrowserAction
    target: str
    parameters: Dict[str, Any]
    requires_consent: bool = False


class WebBrowserController:
    """
    Web browser controller for autonomous browsing.
    Integrates with Ghost Mode for voice-commanded web operations.
    """
    
    def __init__(self):
        self.browser = None
        self.page = None
        self.history: List[Dict[str, Any]] = []
        self.current_url: Optional[str] = None
        
        logger.info("🌐 Web Browser Controller initialized")
    
    async def init_browser(self):
        """Initialize browser (lazy loading)."""
        if self.browser:
            return
        
        try:
            from playwright.async_api import async_playwright
            
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(headless=True)
            self.page = await self.browser.new_page()
            
            logger.info("✅ Browser initialized (headless Chromium)")
        except Exception as e:
            logger.error(f"Browser init error: {e}")
            raise
    
    async def close_browser(self):
        """Close browser and cleanup."""
        if self.browser:
            await self.browser.close()
            await self.playwright.stop()
            self.browser = None
            self.page = None
            logger.info("🔒 Browser closed")
    
    def parse_voice_command(self, voice_input: str) -> Optional[BrowserCommand]:
        """
        Parse voice input into browser command.
        
        Args:
            voice_input: Natural language voice input
            
        Returns:
            BrowserCommand or None
        """
        voice_lower = voice_input.lower()
        
        # Search patterns
        search_patterns = [
            r"search (?:for |about )?(.+)",
            r"google (.+)",
            r"find (?:information about |info on )?(.+)",
            r"look up (.+)"
        ]
        
        for pattern in search_patterns:
            match = re.search(pattern, voice_lower)
            if match:
                query = match.group(1)
                return BrowserCommand(
                    action=BrowserAction.SEARCH,
                    target=query,
                    parameters={"engine": "google"},
                    requires_consent=False
                )
        
        # Navigate patterns
        navigate_patterns = [
            r"go to (.+)",
            r"open (?:website |site )?(.+)",
            r"navigate to (.+)",
            r"visit (.+)"
        ]
        
        for pattern in navigate_patterns:
            match = re.search(pattern, voice_lower)
            if match:
                url = match.group(1)
                # Add https:// if missing
                if not url.startswith(("http://", "https://")):
                    url = f"https://{url}"
                return BrowserCommand(
                    action=BrowserAction.NAVIGATE,
                    target=url,
                    parameters={},
                    requires_consent=False
                )
        
        # Read patterns
        read_patterns = [
            r"read (?:this |the )?page",
            r"summarize (?:this |the )?page",
            r"what does (?:this |the )?page say",
            r"extract (?:text|content) from (?:this |the )?page"
        ]
        
        for pattern in read_patterns:
            if re.search(pattern, voice_lower):
                return BrowserCommand(
                    action=BrowserAction.READ,
                    target="current_page",
                    parameters={"summarize": True},
                    requires_consent=False
                )
        
        # Form filling patterns (requires consent)
        form_patterns = [
            r"fill (?:out |in )?(?:the )?form",
            r"complete (?:the )?form",
            r"submit (?:the )?form"
        ]
        
        for pattern in form_patterns:
            if re.search(pattern, voice_lower):
                return BrowserCommand(
                    action=BrowserAction.FILL_FORM,
                    target="current_page",
                    parameters={},
                    requires_consent=True  # Requires user consent
                )
        
        # Click patterns (requires consent for sensitive actions)
        click_patterns = [
            r"click (?:on )?(.+)",
            r"press (?:the )?(.+) button",
            r"select (.+)"
        ]
        
        for pattern in click_patterns:
            match = re.search(pattern, voice_lower)
            if match:
                target = match.group(1)
                # Check if sensitive action
                sensitive_keywords = ["buy", "purchase", "pay", "submit", "confirm", "delete"]
                requires_consent = any(kw in target.lower() for kw in sensitive_keywords)
                
                return BrowserCommand(
                    action=BrowserAction.CLICK,
                    target=target,
                    parameters={},
                    requires_consent=requires_consent
                )
        
        # Screenshot patterns
        screenshot_patterns = [
            r"take (?:a )?screenshot",
            r"capture (?:the )?page",
            r"save (?:this |the )?page"
        ]
        
        for pattern in screenshot_patterns:
            if re.search(pattern, voice_lower):
                return BrowserCommand(
                    action=BrowserAction.SCREENSHOT,
                    target="current_page",
                    parameters={},
                    requires_consent=False
                )
        
        return None
    
    async def execute_command(self, command: BrowserCommand, consent_given: bool = False) -> Dict[str, Any]:
        """
        Execute browser command.
        
        Args:
            command: BrowserCommand to execute
            consent_given: Whether user has given consent
            
        Returns:
            Result dictionary
        """
        # Check consent for sensitive actions
        if command.requires_consent and not consent_given:
            return {
                "status": "consent_required",
                "message": "This action requires your consent. Say 'yes' to proceed or 'no' to cancel.",
                "command": command.action.value,
                "target": command.target
            }
        
        # Initialize browser if needed
        await self.init_browser()
        
        try:
            if command.action == BrowserAction.SEARCH:
                result = await self._search(command.target, command.parameters.get("engine", "google"))
            elif command.action == BrowserAction.NAVIGATE:
                result = await self._navigate(command.target)
            elif command.action == BrowserAction.READ:
                result = await self._read_page(command.parameters.get("summarize", False))
            elif command.action == BrowserAction.FILL_FORM:
                result = await self._fill_form()
            elif command.action == BrowserAction.CLICK:
                result = await self._click(command.target)
            elif command.action == BrowserAction.SCREENSHOT:
                result = await self._screenshot()
            else:
                result = {"status": "error", "message": f"Unknown action: {command.action}"}
            
            # Add to history
            self.history.append({
                "command": command.action.value,
                "target": command.target,
                "result": result,
                "url": self.current_url
            })
            
            return result
        
        except Exception as e:
            logger.error(f"Command execution error: {e}")
            return {"status": "error", "message": str(e)}
    
    async def _search(self, query: str, engine: str = "google") -> Dict[str, Any]:
        """Perform web search."""
        search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        await self.page.goto(search_url)
        self.current_url = search_url
        
        # Wait for results
        await self.page.wait_for_selector("div#search", timeout=5000)
        
        # Extract top results
        results = await self.page.query_selector_all("div.g")
        top_results = []
        
        for result in results[:5]:  # Top 5 results
            try:
                title_elem = await result.query_selector("h3")
                link_elem = await result.query_selector("a")
                snippet_elem = await result.query_selector("div.VwiC3b")
                
                if title_elem and link_elem:
                    title = await title_elem.inner_text()
                    link = await link_elem.get_attribute("href")
                    snippet = await snippet_elem.inner_text() if snippet_elem else ""
                    
                    top_results.append({
                        "title": title,
                        "link": link,
                        "snippet": snippet
                    })
            except Exception as e:
                logger.warning(f"Result extraction error: {e}")
                continue
        
        return {
            "status": "success",
            "action": "search",
            "query": query,
            "results_count": len(top_results),
            "results": top_results,
            "url": search_url
        }
    
    async def _navigate(self, url: str) -> Dict[str, Any]:
        """Navigate to URL."""
        await self.page.goto(url)
        self.current_url = url
        
        # Wait for page load
        await self.page.wait_for_load_state("networkidle")
        
        title = await self.page.title()
        
        return {
            "status": "success",
            "action": "navigate",
            "url": url,
            "title": title
        }
    
    async def _read_page(self, summarize: bool = False) -> Dict[str, Any]:
        """Read and extract page content."""
        if not self.current_url:
            return {"status": "error", "message": "No page loaded"}
        
        # Extract text content
        content = await self.page.inner_text("body")
        
        # Extract title
        title = await self.page.title()
        
        # Basic summarization (first 500 chars)
        summary = content[:500] + "..." if len(content) > 500 else content
        
        return {
            "status": "success",
            "action": "read",
            "url": self.current_url,
            "title": title,
            "content_length": len(content),
            "summary": summary if summarize else None,
            "full_content": content if not summarize else None
        }
    
    async def _fill_form(self) -> Dict[str, Any]:
        """Fill form with data from Vaultwarden."""
        # This would integrate with vault_manager to retrieve credentials
        # For now, return placeholder
        return {
            "status": "not_implemented",
            "message": "Form filling requires Vaultwarden integration",
            "action": "fill_form"
        }
    
    async def _click(self, target: str) -> Dict[str, Any]:
        """Click element on page."""
        # Try to find element by text
        try:
            await self.page.click(f"text={target}")
            return {
                "status": "success",
                "action": "click",
                "target": target
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Could not find element: {target}",
                "error": str(e)
            }
    
    async def _screenshot(self) -> Dict[str, Any]:
        """Take screenshot of current page."""
        if not self.current_url:
            return {"status": "error", "message": "No page loaded"}
        
        screenshot_path = f"/tmp/screenshot_{int(asyncio.get_event_loop().time())}.png"
        await self.page.screenshot(path=screenshot_path)
        
        return {
            "status": "success",
            "action": "screenshot",
            "path": screenshot_path,
            "url": self.current_url
        }
    
    def get_history(self) -> List[Dict[str, Any]]:
        """Get browsing history."""
        return self.history
    
    def clear_history(self):
        """Clear browsing history."""
        self.history = []
        logger.info("🗑️ Browser history cleared")


# Singleton instance
_browser_controller = None


def get_browser_controller() -> WebBrowserController:
    """Get singleton browser controller instance."""
    global _browser_controller
    if not _browser_controller:
        _browser_controller = WebBrowserController()
    return _browser_controller


async def process_browser_command(voice_input: str, consent_given: bool = False) -> Dict[str, Any]:
    """
    Process browser command from voice input.
    
    Args:
        voice_input: Natural language voice input
        consent_given: Whether user has given consent
        
    Returns:
        Result dictionary
    """
    controller = get_browser_controller()
    
    # Parse command
    command = controller.parse_voice_command(voice_input)
    
    if not command:
        return {
            "status": "error",
            "message": "Could not understand browser command",
            "voice_input": voice_input
        }
    
    # Execute command
    result = await controller.execute_command(command, consent_given)
    
    return result

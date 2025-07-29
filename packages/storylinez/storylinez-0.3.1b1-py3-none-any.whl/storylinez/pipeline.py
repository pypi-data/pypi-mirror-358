import time
from typing import Dict, Any
# from .utils import UtilsClient
# from .tools import ToolsClient

class PipelineClient:
    """
    Client for managing pipelines that combine multiple operations like web scraping and brand extraction.
    """

    def __init__(self, client):
        """
        Initialize the PipelineClient.

        Args:
            client: The main API client, which must provide `.utils` and `.tools` attributes.
        """
        self.client = client

    def run_web_scraping_and_brand_extraction(
        self,
        website_url: str,
        timeout: int = 60,
        depth: int = 1,
        enable_js: bool = False,
        include_palette: bool = True,
        dynamic_extraction: bool = False,
        deepthink: bool = False,
        overdrive: bool = False,
        web_search: bool = False,
        eco: bool = False,
        polling_interval: int = 10
    ) -> Dict[str, Any]:
        """
        Perform web scraping and brand extraction in a single pipeline.
        This function ensures both steps are fully completed before returning.

        Args:
            website_url: The URL of the website to scrape.
            timeout: Maximum time (in seconds) to wait for each job (default: 60).
            depth: How deep to crawl links during web scraping (default: 1).
            enable_js: Enable JavaScript rendering for web scraping (default: False).
            include_palette: Include color palette in brand extraction (default: True).
            dynamic_extraction: Enable dynamic extraction for brand settings (default: False).
            deepthink: Enable advanced AI reasoning (default: False).
            overdrive: Enable maximum quality and detail (default: False).
            web_search: Enable web search for up-to-date information (default: False).
            eco: Enable eco mode for faster processing (default: False).
            polling_interval: Time (in seconds) between job status checks (default: 10).

        Returns:
            A dictionary containing the completed outputs for "web_scraping" and "brand_extraction".

        Raises:
            Exception: If any step in the pipeline fails.
        """
        errors = {}
        web_scraping_result = None
        brand_extraction_result = None

        # Step 1: Web scraping (waits for completion)
        try:
            # Step 1: Start web scraping and get tool ID
            web_scraping_job = self.client.tools.create_web_scraper_advanced(
                name="WebScrapingJob",
                website_url=website_url,
                depth=depth,
                enable_js=enable_js,
                deepthink=deepthink,
                overdrive=overdrive,
                web_search=web_search,
                eco=eco,
                timeout=timeout
            )
            tool_id = web_scraping_job.get("tool", {}).get("tool_id")
            if not tool_id:
                raise Exception("Web scraping did not return a tool ID in response['tool']['tool_id'].")
            web_scraping_result = self.client.tools.wait_for_tool_completion(
                tool_id,
                polling_interval=polling_interval
            )
        except Exception as e:
            errors["web_scraping"] = str(e)
            web_scraping_result = None

        # Step 2: Brand extraction (waits for completion, only if scraping succeeded)
        if web_scraping_result:
            try:
                brand_extraction_job = self.client.utils.extract_brand_settings(
                    website_url=website_url,
                    deepthink=deepthink,
                    overdrive=overdrive,
                    eco=eco,
                    timeout=timeout,
                    include_palette=include_palette,
                    dynamic_extraction=dynamic_extraction,
                    web_search=web_search
                )
                job_id = brand_extraction_job.get("job_id") or brand_extraction_job.get("id")
                if not job_id:
                    raise Exception("Brand extraction did not return a job ID.")
                brand_extraction_result = self.client.utils.wait_for_job_completion(
                    job_id,
                    polling_interval=polling_interval
                )
            except Exception as e:
                errors["brand_extraction"] = str(e)
                brand_extraction_result = None
        elif "web_scraping" not in errors:
            errors["web_scraping"] = "Web scraping did not return expected result."
            brand_extraction_result = None

        # Ensure both results are fully obtained before returning
        result = {
            "web_scraping": web_scraping_result,
            "brand_extraction": brand_extraction_result
        }
        if errors:
            result["errors"] = errors
        return result
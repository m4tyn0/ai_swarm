import asyncio
import csv
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy


async def fetch_product_data(url):
    async with AsyncWebCrawler() as crawler:        
        # Define extraction rules for crawl4ai
        schema = {
            "name": "topg product",
            "baseSelector": "div", 
            "fields" :[
                {
                "name": "product_name",
                "selector": "h1",         # select the <h1> tag for product name
                "type": "text",        # extract its text content
                "multiple": False
                },
                {
                "name" : "main_description", 
                "selector": "div.description-columns",  # select the description container
                "type": "text",                      # extract the primary text content
                "multiple": False,
                "strip": True
                },
                {
                "name":"features", 
                "selector": "div.description-columns ul li",  # select list items for features
                "attritypebute": "text",                           # extract their text content
                "multiple": True,
                "strip": True
                }]
        }
        extraction_strategy = JsonCssExtractionStrategy(schema, verbose=True)

        config = CrawlerRunConfig(
            cache_mode = CacheMode.BYPASS, 
            extraction_strategy = extraction_strategy,
        )
        # Execute the crawler with extraction_rules
        result = await crawler.arun(url=url, config=config)
        print(result.extracted_content)
        if not result.success:
            print(f"Crawl failed: {result.error_message}")
            print(f"Status code: {result.status_code}")
        return result


async def main():
    # List of product URLs to scrape (add more URLs as needed)
    product_urls = [
        "https://www.topgrily.cz/elektricky-gril-weber-lumin-se-stojanem.html"
    ]
    
    # Prepare CSV file to store product data
    with open("grill_products.csv", mode="w", newline='', encoding="utf-8") as file:
        writer = csv.writer(file, quoting=csv.QUOTE_ALL)
        writer.writerow(["Name", "Main Description", "Features"])
  
        for url in product_urls:
            product_data = await fetch_product_data(url)
            if product_data:
                writer.writerow([
                    product_data.extracted_content("name", "No name found"),
                    product_data.extracted_content("main_description", "No main description found"),
                    "\n".join(product_data.get("features", []))
                ])
            else:
                print(f"Failed to retrieve product page: {url}")

if __name__ == "__main__":
    asyncio.run(main())

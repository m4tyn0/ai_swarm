import asyncio
import csv
import json
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy

async def fetch_product_data(url):
    # Define a schema for extracting the product details
    schema = {
        "name": "ProductDetails",
        "baseSelector": "body",  # Start extraction from the full page
        "fields": [
            {
                "name": "name",
                "selector": "h1",
                "type": "text"
            },
            {
                "name" : "description", 
                "selector" : ".description-columns",
                "type" : "text",
                "fields" : [
                    {"name" : "description-article", "selector": ".p", "type":"text"},             
                    {"name": "features", "selector": ".description-columns.ul", "type": "text"}
                ]

            },
            # ,
            # {
            #     "name": "main_description",
            #     "selector": "div.description-columns",
            #     "type": "text"
            # },
            {
                "name": "features",
                "selector": ".description-columns.ul",
                "type": "text"
            }
        ]
    }

    schema_2 = {
                "name": "ProductDetails",
                "baseSelector": "body",
                "fields": [
                    {
                        "name": "name",
                        "selector": "h1",
                        "type": "text",
                        "transform": "strip()"
                    },
                    {
                        "name": "description",
                        "selector": "div.description-columns",
                        "type": "nested",
                        "fields": [
                            {
                                "name": "article",
                                "selector": "p",
                                "type": "list",
                                "fields": [{
                                    "name": "paragraph", 
                                    "type": "text"
                                }]
                            },
                            {
                                "name": "highlights",
                                "selector": "ul:first-of-type li",
                                "type": "list",
                                "fields": [{
                                    "name": "feature", 
                                    "type": "text"
                                }]
                            }
                        ]
                    },
                    {
                        "name": "specifications",
                        "selector": "h2.ul li",
                        "type": "list",
                        "fields": [{
                            "name": "spec", 
                            "type": "text"
                        }]
                    }
                ]
            }
    
    # Initialize extraction strategy using the defined schema
    extraction_strategy = JsonCssExtractionStrategy(schema = schema_2, verbose = True)
    
    # Create the crawler configuration using our extraction strategy
    config = CrawlerRunConfig(
        cache_mode = CacheMode.BYPASS,
        extraction_strategy=extraction_strategy,
        only_text = True
    )
    
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=url, config=config)
        if result.success:
            print(result)
            return result
        else:
            print(f"Error for URL {url}: {result.error_message}")
            return None

async def main():
    # List of product URLs to scrape
    product_urls = [
        "https://www.topgrily.cz/elektricky-gril-weber-lumin-se-stojanem.html"
    ]
    
    with open("grill_products.csv", mode="w", newline='', encoding="utf-8") as file:
        writer = csv.writer(file, quoting=csv.QUOTE_ALL)
        writer.writerow(["Name", "Description", "Key Features", "Specifications"])
        
        for url in product_urls:
            result = await fetch_product_data(url)
            if result and result.extracted_content:
                data = json.loads(result.extracted_content)[0]
                description = " ".join([p["paragraph"] for p in data["description"]["article"]])
                features = "\n".join([f["feature"] for f in data["description"]["highlights"]])
                specs = "\n".join([s["spec"] for s in data["specifications"]])
                
                writer.writerow([
                    data.get("name", "N/A"),
                    description,
                    features,
                    specs
                ])

        else:
            print(f"Failed to retrieve data from: {url}")

if __name__ == "__main__":
    asyncio.run(main())

import asyncio
import csv
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode

async def fetch_html(url):
    """Retrieve HTML content of a webpage asynchronously."""
    async with AsyncWebCrawler() as crawler:
        config = CrawlerRunConfig(cache_mode=CacheMode.BYPASS)  # Bypass cache for fresh data
        result = await crawler.arun(url=url, config=config)
        return result.html if result.success else None

def extract_category_links(main_page_html, base_url):
    """Extract category links from the main page."""
    soup = BeautifulSoup(main_page_html, "html.parser")
    category_links = []
    list_recipes = soup.find("ul", class_="list-recipes")
    if list_recipes:
        for link in list_recipes.find_all("a", href=True):
            full_link = urljoin(base_url, link['href'])
            category_links.append(full_link)
    return category_links

def extract_recipe_links(category_html, base_url):
    """Extract all recipe links within a category, including pagination."""
    soup = BeautifulSoup(category_html, "html.parser")
    recipe_links = []

    # Extract links from the "news_list" section
    news_list = soup.find("div", class_="news_list")
    if news_list:
        for link in news_list.find_all("a", href=True):
            full_link = urljoin(base_url, link['href'])
            recipe_links.append(full_link)

    # Handle pagination within this category
    pagination = soup.find("ul", class_="pagination")
    if pagination:
        for page_link in pagination.find_all("a", href=True):
            next_page_url = urljoin(base_url, page_link['href'])
            next_page_html = fetch_html(next_page_url)
            if next_page_html:
                recipe_links.extend(extract_recipe_links(next_page_html, base_url))
    
    return recipe_links

def extract_recipe_details(recipe_html):
    """Extract details from a recipe page."""
    soup = BeautifulSoup(recipe_html, "html.parser")
    details = {}

    # Get the recipe title
    title_tag = soup.find("h1")
    details['title'] = title_tag.get_text(strip=True) if title_tag else "No title found"

    # Extract "about-recipe" information
    about_recipe = soup.find("div", class_="about-recipe")
    if about_recipe:
        for item in about_recipe.find_all("div", recursive=False):
            title_elem = item.find("div", class_="title")
            info_elem = item.find("div", class_="info")
            if title_elem and info_elem:
                details[title_elem.get_text(strip=True)] = info_elem.get_text(strip=True)

    # Extract annotations and textual information
    for section_name in ["annotation", "ingredients", "content", "process", "recipe"]:
        section_div = soup.find("div", class_=section_name)
        details[section_name] = section_div.get_text(strip=True) if section_div else "Not available"

    return details

async def main():
    base_url = "https://www.topgrily.cz"
    start_url = f"{base_url}/grilovaci-recepty/"
    main_page_html = await fetch_html(start_url)

    # Ensure main page was retrieved successfully
    if not main_page_html:
        print("Failed to retrieve the main page.")
        return

    # Extract category links from the main page
    category_links = extract_category_links(main_page_html, base_url)

    # Prepare CSV file to store recipe data
    with open("grill_recipes.csv", mode="w", newline='', encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Title", "Preparation Time", "Complexity", "Method", "Annotation", "Ingredients", "Content", "Process", "Recipe"])

        # Iterate through each category
        for category_link in category_links:
            category_html = await fetch_html(category_link)
            if not category_html:
                print(f"Failed to retrieve category page: {category_link}")
                continue

            # Extract all recipe links within the category
            recipe_links = extract_recipe_links(category_html, base_url)

            # Iterate through each recipe link and extract details
            for recipe_link in recipe_links:
                recipe_html = await fetch_html(recipe_link)
                if recipe_html:
                    details = extract_recipe_details(recipe_html)
                    writer.writerow([
                        details.get("title"),
                        details.get("Doba přípravy", "Not specified"),
                        details.get("Složitost", "Not specified"),
                        details.get("Postup", "Not specified"),
                        details.get("annotation"),
                        details.get("ingredients"),
                        details.get("content"),
                        details.get("process"),
                        details.get("recipe")
                    ])
                else:
                    print(f"Failed to retrieve recipe page: {recipe_link}")

# Run the main function
if __name__ == "__main__":
    asyncio.run(main())
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time


def fetch_rendered_html(url):
    """
    Uses Selenium to get the fully rendered HTML of a page.
    """
    print(f"🚀 Fetching rendered HTML from: {url}")
    # Setup Chrome options
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run in headless mode (no browser window)
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    # Initialize driver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    try:
        driver.get(url)
        # Give the page some time to load dynamic content
        time.sleep(5)  
        html = driver.page_source
        print("✅ HTML fetched successfully.")
        return html
    finally:
        driver.quit()


def clone_page(url, page_html, output_dir="cloned_site"):
    """
    Parses HTML, downloads assets, and rewrites the HTML to use local paths.
    """
    soup = BeautifulSoup(page_html, 'html.parser')
    # Create a directory to store the site
    project_folder = output_dir
    os.makedirs(project_folder, exist_ok=True)

    # Dictionary to hold tags and their attributes to check (e.g., 'link' tag, 'href' attribute)
    asset_tags = {
        'link': 'href',
        'script': 'src',
        'img': 'src',
    }

    allowed_domain = "upgrad.com"

    for tag, attr in asset_tags.items():
        for res in soup.find_all(tag):
            if res.has_attr(attr):
                asset_url = res.get(attr)
                if not asset_url or asset_url.startswith('data:'):
                    continue

                # Create the full, absolute URL for the asset
                full_asset_url = urljoin(url, asset_url)
                parsed_asset_url = urlparse(full_asset_url)

                # Only download assets from upgrad.com
                if allowed_domain not in parsed_asset_url.netloc:
                    continue

                # Use path to create a sane folder structure
                local_asset_path = os.path.join(project_folder, parsed_asset_url.netloc, parsed_asset_url.path.lstrip('/'))

                # For root paths, name them something like index.css
                if local_asset_path.endswith(os.sep) or local_asset_path.endswith('/'):
                    local_asset_path = local_asset_path.rstrip(os.sep).rstrip('/')
                    local_asset_path += f"/index.{tag}"

                # Create local directories if they don't exist
                os.makedirs(os.path.dirname(local_asset_path), exist_ok=True)

                try:
                    print(f"📥 Downloading asset: {full_asset_url}")
                    response = requests.get(full_asset_url, stream=True)
                    response.raise_for_status()
                    with open(local_asset_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    relative_path = os.path.relpath(local_asset_path, project_folder)
                    res[attr] = relative_path
                    print(f"🔄 Rewrote path to: {relative_path}")
                except requests.exceptions.RequestException as e:
                    print(f"❌ Failed to download {full_asset_url}: {e}")

    # Save the modified HTML file
    final_html_path = os.path.join(project_folder, "index.html")
    with open(final_html_path, "w", encoding="utf-8") as f:
        f.write(str(soup.prettify()))
    print(f"\n🎉 Cloning complete! View the site at: {final_html_path}")


# Depth-limited crawl for upgrad.com only
def run_clone(url, output_dir="cloned_site", depth=1, max_depth=2, visited=None):
    if visited is None:
        visited = set()
    if depth > max_depth or url in visited:
        return
    visited.add(url)
    html = fetch_rendered_html(url)
    if html:
        clone_page(url, html, output_dir)
        # Find internal links and crawl them up to max_depth
        soup = BeautifulSoup(html, 'html.parser')
        for a in soup.find_all('a', href=True):
            link = urljoin(url, a['href'])
            parsed_link = urlparse(link)
            if "upgrad.com" in parsed_link.netloc:
                run_clone(link, output_dir, depth+1, max_depth, visited)


# In clone_ui.py


# Ensure this block is at the root level, not inside any function
if __name__ == "__main__":
    target_url = "https://www.upgrad.com/" # Change this to the website you want to clone
    output_dir = "cloned_site" # You can change this to any folder name you want
    run_clone(target_url, output_dir, depth=0, max_depth=0)
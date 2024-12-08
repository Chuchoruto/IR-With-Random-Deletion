import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

# Function to extract data from an individual article
def scrape_article(article_url):
    try:
        response = requests.get(article_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract the title
        title = soup.find('h1').text.strip() if soup.find('h1') else "No title"

        # Extract the publication date
        date = soup.find('time').text.strip() if soup.find('time') else "No date"

        # Extract the main content
        paragraphs = soup.find_all('p')
        article_content = " ".join([p.text.strip() for p in paragraphs if p.text.strip()])

        return {
            "title": title,
            "url": article_url,
            "date": date,
            "content": article_content if article_content else "No content"
        }

    except Exception as e:
        print(f"Error scraping {article_url}: {e}")
        return {
            "title": "Error",
            "url": article_url,
            "date": "Error",
            "content": str(e)
        }

# Function to scrape the main page and gather all article links
def scrape_yahoo_finance_main_page(main_url):
    try:
        response = requests.get(main_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract all article links (ensure unique links)
        article_links = set(
            a['href'] for a in soup.find_all('a', href=True)
            if '/news/' in a['href']
        )

        # Ensure full URLs
        article_links = [
            link if link.startswith('http') else f"https://finance.yahoo.com{link}"
            for link in article_links
        ]

        return list(article_links)

    except Exception as e:
        print(f"Error scraping main page {main_url}: {e}")
        return []

# Main function to crawl and gather article data
def scrape_data(main_url):
    
    print(f"Scraping main page: {main_url}")

    # Get all article links
    article_links = scrape_yahoo_finance_main_page(main_url)
    print(f"Found {len(article_links)} article links.")

    # Scrape data from each article
    articles_data = []
    for idx, link in enumerate(article_links):
        print(f"Scraping article {idx + 1}/{len(article_links)}: {link}")
        article_data = scrape_article(link)
        articles_data.append(article_data)

        # Add delay to avoid being flagged as a bot
        time.sleep(2)

    df = pd.DataFrame(articles_data)

    return df
    


def combine_and_deduplicate_dataframes(dataframes):
    """
    Combine multiple dataframes and remove duplicate URLs.

    Parameters:
        dataframes (list): A list of pandas DataFrames.

    Returns:
        pd.DataFrame: A combined DataFrame with duplicate URLs removed.
    """
    # Combine all dataframes
    combined_df = pd.concat(dataframes, ignore_index=True)
    
    # Remove duplicate URLs (keeping the first occurrence)
    deduplicated_df = combined_df.drop_duplicates(subset="url", keep="first")
    
    return deduplicated_df


def filter_urls_with_html(df):
    """
    Filter rows in a DataFrame where the 'url' column ends with '.html'.

    Parameters:
        df (pd.DataFrame): The input DataFrame with a 'url' column.

    Returns:
        pd.DataFrame: A filtered DataFrame containing only rows where 'url' ends with '.html'.
    """
    # Filter rows where 'url' ends with '.html'
    filtered_df = df[df['url'].str.endswith('.html', na=False)].reset_index(drop=True)
    return filtered_df


def main():
    main_url = "https://finance.yahoo.com/topic/latest-news/"
    df = scrape_data(main_url)

    
    df.to_csv("yahoo_finance_articles_with_content.csv", index=False)
    print("Scraped data saved to 'yahoo_finance_articles_with_content.csv'.")

if __name__ == "__main__":
    main()

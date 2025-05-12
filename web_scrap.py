from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
import time
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize the Chrome WebDriver with automatic chromedriver management
driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))

try:
    # Open the website
    logging.info("Opening NDEM website...")
    driver.get("https://ndem.nrsc.gov.in/#/")

    # Wait for the "Explore" button to be present and clickable with better error handling
    wait = WebDriverWait(driver, 30)
    try:
        explore_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//mat-icon[contains(@class, 'mat-icon')]")
        ))
        logging.info("Explore button found. Clicking...")
        explore_button.click()
    except TimeoutException:
        logging.error("Explore button not found within timeout period")
        raise
    except Exception as e:
        logging.error(f"Error clicking explore button: {e}")
        raise

    # Wait for the Disaster News section to appear with better error handling
    try:
        disaster_news_section_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//*[contains(@class, 'mat-mdc-tooltip-trigger') and contains(@class, 'disaster-news')]"))
        )
        logging.info("Disaster News section found. Clicking...")
        disaster_news_section_button.click()
    except TimeoutException:
        logging.error("Disaster News section not found within timeout period")
        raise
    except Exception as e:
        logging.error(f"Error clicking Disaster News section: {e}")
        raise

    # Wait for content to load with dynamic wait
    try:
        # Wait for the panel to be present
        disaster_news_panel = wait.until(
            EC.presence_of_element_located((By.XPATH, "//ndem-disaster-news-panel"))
        )
        logging.info("Disaster news panel located. Waiting for content...")

        # Scroll to load dynamic content
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        
        # Wait for cards to be present
        wait.until(
            EC.presence_of_all_elements_located((By.XPATH, "//ndem-disaster-news-panel/mat-card"))
        )
        logging.info("Content loaded successfully")
    except TimeoutException:
        logging.error("Content failed to load within timeout period")
        raise
    except Exception as e:
        logging.error(f"Error loading content: {e}")
        raise

    # Find all cards inside the section with better error handling
    try:
        news_cards = wait.until(
            EC.presence_of_all_elements_located((By.XPATH, "//ndem-disaster-news-panel/mat-card[@class='mat-mdc-card mdc-card example-card ng-star-inserted']/mat-card/mat-card-content/div"))
        )
        logging.info(f"Found {len(news_cards)} news cards")

        # Prepare a list to store the news data
        news_data = []
        max_retries = 3

        # Extract details from each card with retry mechanism
        for idx, card in enumerate(news_cards):
            if idx >= 5:  # Limit to 5 cards
                break

            for retry in range(max_retries):
                try:
                    # Extract source with wait condition
                    source_element = WebDriverWait(card, 10).until(
                        EC.presence_of_element_located((By.XPATH, ".//div[contains(text(), 'Source')]"))
                    )
                    source = source_element.text

                    # Extract date with wait condition
                    date_element = WebDriverWait(card, 10).until(
                        EC.presence_of_element_located((By.XPATH, ".//div[@style[contains(., 'min-width')]]"))
                    )
                    date = date_element.text

                    # Extract news content with wait condition
                    news_content_element = WebDriverWait(card, 10).until(
                        EC.presence_of_element_located((By.XPATH, ".//a[contains(@class, 'news-link')]"))
                    )
                    news_content = news_content_element.text
                    news_link = news_content_element.get_attribute('href')

                    # Store in the news_data list
                    news_data.append({
                        'source': source or "N/A",
                        'date': date or "N/A",
                        'content': news_content or "N/A",
                        'link': news_link or "N/A"
                    })
                    logging.info(f"Successfully processed card {idx + 1}")
                    break  # Break retry loop if successful

                except (StaleElementReferenceException, TimeoutException) as e:
                    if retry == max_retries - 1:  # Last retry
                        logging.error(f"Failed to process card {idx + 1} after {max_retries} retries: {e}")
                    else:
                        logging.warning(f"Retry {retry + 1} for card {idx + 1}: {e}")
                        time.sleep(1)  # Wait before retry
                except Exception as e:
                    logging.error(f"Unexpected error processing card {idx + 1}: {e}")
                    break  # Break retry loop for unexpected errors

        # Save results
        logging.info(f"Extracted {len(news_data)} news items")
        
        if news_data:
            with open("top_disaster_news.json", "w") as json_file:
                json.dump(news_data, json_file, indent=4)
            logging.info("Data successfully saved to top_disaster_news.json")
        else:
            logging.warning("No news data was extracted")

    except Exception as e:
        logging.error(f"Error finding or processing news cards: {e}")
        raise

except Exception as e:
    print(f"Error encountered: {e}")

finally:
    # Close the browser
    driver.quit()
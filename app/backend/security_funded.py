from curl_cffi import requests
import time
import re
from bs4 import BeautifulSoup
import urllib.parse
from datetime import datetime
import logging
from app.backend.database import db_manager
from app.backend.models import CompanyData, Investor
from app.shared.config import Config

logger = logging.getLogger(__name__)

headers = {
    'sec-ch-ua-platform': '"macOS"',
    'Referer': 'https://www.returnonsecurity.com/',
    'User-Agent': Config.USER_AGENT,
    'sec-ch-ua': '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
}

def get_links():
    """Get all security funded post links"""
    post_links = {"links": []}
    
    try:
        for i in range(1, 2):  # Currently processing only first page
            logger.info(f"Processing page {i}")
            time.sleep(1)
            
            params = {
                'page': str(i),
                '_data': 'routes/__loaders/posts',
            }
            
            response = requests.get(Config.SCRAPE_URL, params=params, headers=headers)
            response.raise_for_status()
            
            resp_json = response.json()
            for post in resp_json['posts']:
                post_url = f"https://www.returnonsecurity.com/p/{post['slug']}"
                if post_url not in post_links['links']:
                    if "security-funded-" in post_url:
                        post_links['links'].append(post_url)
            
            logger.info(f"Total posts found: {len(post_links['links'])}")
            
    except Exception as e:
        logger.error(f"Error getting links: {str(e)}")
        
    return post_links

def parse_investment_data(soup, date, company_type):
    """Parse investment data from HTML soup"""
    results = []
    exit_flag = False
    
    for li in soup.find_all('li'):
        item = {}
        p = li.find('p')
        if not p:
            continue
        
        # Get description
        item['description'] = li.get_text(' ', strip=True).split('. (')[0].strip()
        
        # Get company name and URL
        company_link = p.find('a', class_='link')
        if company_link:
            item['company_name'] = company_link.text.strip()
            item['company_url'] = company_link.get('href', '').split('?')[0]
        
        text = p.get_text(' ', strip=True)
        parsed_round_text = None

        # Parse funding amount and round
        funding_match = re.search(r'\$(\d+\.?\d*)([KMB]) ([^\.]+)', text)
        if funding_match:
            value = float(funding_match.group(1))
            multiplier = {'K': 1000, 'M': 1000000, 'B': 1000000000}
            item['amount'] = int(value * multiplier.get(funding_match.group(2), 1))
            raw_round_info = funding_match.group(3)
            parsed_round_text = raw_round_info.split('from')[0].strip()
        else:
            undisclosed_round_match = re.search(r'raised an undisclosed\s+([a-zA-Z\s]+?Round)', text, re.IGNORECASE)
            if undisclosed_round_match:
                parsed_round_text = undisclosed_round_match.group(1).strip()
                item['amount'] = 0
        
        # Clean and format round text
        if parsed_round_text:
            parsed_round_text = parsed_round_text.lower().strip()
            parsed_round_text = parsed_round_text.replace('round', '')
            if 'and' in parsed_round_text:
                parsed_round_text = parsed_round_text.split('and')[0]
            if '(' in parsed_round_text:
                parsed_round_text = parsed_round_text.split('(')[0]
            parsed_round_text = parsed_round_text.replace('from', '')
            parsed_round_text = parsed_round_text.replace('in ', '')
            if 'with' in parsed_round_text:
                parsed_round_text = parsed_round_text.split('with')[0]
            if 'but' in parsed_round_text:
                parsed_round_text = parsed_round_text.split('but')[0]
            parsed_round_text = parsed_round_text.strip()
            split_round = parsed_round_text.split()
            item['round'] = ' '.join(word.capitalize() for word in split_round)
            
        # Parse investors
        links = p.find_all('a', class_='link')
        investors = []
        for i in range(1, len(links)):
            link_href = links[i].get('href', '')
            if 'utm_campaign' in link_href and 'more' not in links[i].text.lower():
                investor = Investor(
                    name=links[i].text.strip(),
                    url=link_href.split('?')[0]
                )
                investors.append(investor)
        
        investors = [inv for inv in investors if inv.name]
        item['investors'] = investors
        
        # Find story link
        for link in reversed(links):
            if link.text.strip().lower() == 'more':
                item['story_link'] = link.get('href', '').split('?')[0]
                break
        if 'story_link' not in item and len(links) > 1:
            item['story_link'] = links[-1].get('href', '').split('?')[0]
        
        # Extract source from story link
        if 'story_link' in item:
            parsed_url = urllib.parse.urlparse(item['story_link'])
            domain = parsed_url.netloc
            if domain.startswith('www.'):
                domain = domain[4:]
            item['source'] = domain.split('.')[0].upper()

        item['date'] = date
        item['company_type'] = company_type
        
        # Validate data
        if not item.get('amount') and item.get('amount') != 0: 
            if 'raised' in item.get('description', '').lower() and 'undisclosed' in item.get('description', '').lower():
                item['amount'] = 0
            else:
                exit_flag = True
                break 
        
        if item.get('amount') is not None and item.get('amount') >= 0 and item.get('company_name'):
            results.append(item)
            
    return results, exit_flag

def find_and_parse_funding_sections(article_div, date, article_link):
    """Find and parse all funding sections in the article"""
    all_funding_data = []
    
    funding_heading_tag = article_div.find(['h2', 'h3'], 
                                         string=lambda text: text and 'Funding By Company' in text.strip())
    
    if not funding_heading_tag:
        return all_funding_data
    
    heading_container_div = funding_heading_tag.find_parent('div')
    if not heading_container_div:
        return _parse_fallback_structure(funding_heading_tag, date, all_funding_data)
    
    all_funding_data.extend(_parse_structured_sections(heading_container_div, date, article_link))
    
    if not all_funding_data:
        all_funding_data.extend(_parse_simple_case(heading_container_div, date))
    
    return all_funding_data

def _parse_structured_sections(heading_container_div, date, article_link):
    """Parse structured funding sections"""
    data = []
    sub_headings_map = {
        "Products:": "Product", 
        "Services:": "Service",
        "Product Companies:": "Product", 
        "Service Companies:": "Service"
    }
    
    current_div = heading_container_div.find_next_sibling('div')
    while current_div:
        p_tag = current_div.find('p')
        if p_tag and (bold_tag := p_tag.find('b')):
            sub_text = bold_tag.get_text(strip=True)
            if sub_text in sub_headings_map:
                ul_div = current_div.find_next_sibling('div')
                if ul_div and (ul_tag := ul_div.find('ul')):
                    parsed_data, exit_flag = parse_investment_data(ul_tag, date, sub_headings_map[sub_text])
                    data.extend([{**d, 'reference': article_link} for d in parsed_data])
                    if exit_flag:
                        return data
                current_div = ul_div.find_next_sibling('div') if ul_div else None
                continue
        current_div = current_div.find_next_sibling('div') if current_div else None
    
    return data

def _parse_simple_case(heading_container_div, date):
    """Parse simple case funding sections"""
    ul_div = heading_container_div.find_next_sibling('div')
    if not ul_div:
        return []
    
    ul_tag = ul_div.find('ul') or (ul_div.find_next_sibling('div') and ul_div.find_next_sibling('div').find('ul'))
    if ul_tag:
        data, _ = parse_investment_data(ul_tag, date, "Product")
        return data
    return []

def _parse_fallback_structure(funding_heading_tag, date, all_funding_data):
    """Parse fallback structure for funding sections"""
    h_parent = funding_heading_tag.find_parent()
    if h_parent and (ul_div := h_parent.find_next_sibling('div')) and (ul_tag := ul_div.find('ul')):
        data, _ = parse_investment_data(ul_tag, date, "Product")
        all_funding_data.extend(data)
    return all_funding_data

def parse_article(link):
    """Parse a single article for funding data"""
    try:
        response = requests.get(link, headers=headers)
        if not response.status_code == 200:
            logger.error(f"Failed to fetch {link}: {response.status_code}")
            return None
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract date
        date_tag = soup.find('span', class_='text-wt-text-on-background')
        date_tag = date_tag.text.strip() if date_tag else None
        if not date_tag:
            logger.warning(f"Date not found for {link}")
            return None
            
        date = datetime.strptime(date_tag.split('•')[0].strip(), "%B %d, %Y").date().isoformat()
        
        # Find and parse funding sections
        article_div = soup.find('div', class_='rendered-post')
        all_funding_data = find_and_parse_funding_sections(article_div, date, link)
        
        return all_funding_data
        
    except Exception as e:
        logger.error(f"Error parsing article {link}: {str(e)}")
        return None

def get_data():
    """Main function to collect and store funding data"""
    logger.info("Starting data collection...")
    
    try:
        # Connect to database
        if not db_manager.connect():
            raise Exception("Failed to connect to database")
        
        # Get article links
        links = get_links()
        logger.info(f"Found {len(links['links'])} articles to process")
        
        processed_count = 0
        skipped_count = 0
        error_count = 0
        
        for link in links['links']: 
            logger.info(f"Processing {link}")
            
            # Check if article already exists
            existing_article = db_manager.find_one({"reference": link})
            if existing_article:
                logger.info(f"Article already exists in database, skipping: {link}")
                skipped_count += 1
                continue
            
            # Parse article
            data = parse_article(link)
            if data and len(data) > 0:
                # Convert to CompanyData objects and then to dicts
                company_data_objects = []
                for entry in data:
                    # Convert investors to Investor objects if needed
                    investors = []
                    for inv in entry.get('investors', []):
                        if isinstance(inv, Investor):
                            investors.append(inv)
                        elif isinstance(inv, dict):
                            investors.append(Investor(name=inv.get('name', ''), url=inv.get('url', '')))
                        else:
                            investors.append(Investor(name=str(inv)))
                    
                    company_data = CompanyData(
                        description=entry.get('description', ''),
                        company_name=entry.get('company_name', ''),
                        company_url=entry.get('company_url', ''),
                        amount=entry.get('amount', 0),
                        round=entry.get('round', ''),
                        investors=investors,
                        story_link=entry.get('story_link', ''),
                        source=entry.get('source', ''),
                        date=entry.get('date', ''),
                        company_type=entry.get('company_type', ''),
                        reference=link
                    )
                    company_data_objects.append(company_data.to_dict())
                
                # Insert into database
                result = db_manager.insert_many(company_data_objects)
                logger.info(f"Successfully inserted {len(result.inserted_ids)} funding entries from {link}")
                processed_count += 1
            else:
                logger.warning(f"No funding data found for {link}")
                error_count += 1
        
        logger.info(f"Processing complete:")
        logger.info(f"- Articles processed: {processed_count}")
        logger.info(f"- Articles skipped (already exist): {skipped_count}")
        logger.info(f"- Errors encountered: {error_count}")
        
        return {
            'processed': processed_count,
            'skipped': skipped_count,
            'errors': error_count
        }
        
    except Exception as e:
        logger.error(f"Error in data collection: {str(e)}")
        raise
    finally:
        db_manager.close()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    get_data()
    print("Data collection complete.")
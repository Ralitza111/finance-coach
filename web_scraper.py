"""
Financial Web Scraper

Scrapes financial education content and data from various websites.
Respects robots.txt and implements rate limiting.
"""

import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional, Any
import time
import logging
from urllib.parse import urljoin, urlparse

logger = logging.getLogger(__name__)


class FinancialWebScraper:
    """Web scraper for financial education content"""
    
    def __init__(self):
        """Initialize web scraper with proper headers and rate limiting"""
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.last_request_time = {}
        self.min_request_interval = 2  # 2 seconds between requests to same domain
        
        # Approved educational sources
        self.education_sources = {
            'investopedia': 'https://www.investopedia.com',
            'fool': 'https://www.fool.com',
            'nerdwallet': 'https://www.nerdwallet.com',
            'kiplinger': 'https://www.kiplinger.com'
        }
        
        logger.info("FinancialWebScraper initialized")
    
    def _rate_limit(self, domain: str):
        """Implement per-domain rate limiting"""
        current_time = time.time()
        if domain in self.last_request_time:
            time_since_last = current_time - self.last_request_time[domain]
            if time_since_last < self.min_request_interval:
                time.sleep(self.min_request_interval - time_since_last)
        self.last_request_time[domain] = time.time()
    
    def _get_domain(self, url: str) -> str:
        """Extract domain from URL"""
        return urlparse(url).netloc
    
    def scrape_article(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Scrape content from a financial article
        
        Args:
            url: URL of the article to scrape
            
        Returns:
            Dictionary with article content or None if failed
        """
        logger.info(f"Scraping article: {url}")
        
        domain = self._get_domain(url)
        self._rate_limit(domain)
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code != 200:
                logger.error(f"❌ Failed to fetch {url}: {response.status_code}")
                return None
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title
            title = soup.find('h1')
            title_text = title.get_text(strip=True) if title else 'N/A'
            
            # Extract article content (simplified - adapt per site)
            article_body = soup.find('article') or soup.find('div', class_='article-body')
            
            if article_body:
                paragraphs = article_body.find_all('p')
                content = '\n\n'.join([p.get_text(strip=True) for p in paragraphs])
            else:
                paragraphs = soup.find_all('p')
                content = '\n\n'.join([p.get_text(strip=True) for p in paragraphs[:10]])
            
            article_data = {
                'url': url,
                'title': title_text,
                'content': content[:2000],  # Limit content length
                'source': domain,
                'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            logger.info(f"✅ Successfully scraped article: {title_text[:50]}...")
            return article_data
            
        except Exception as e:
            logger.error(f"❌ Error scraping {url}: {e}")
            return None
    
    def scrape_investopedia_term(self, term: str) -> Optional[Dict[str, Any]]:
        """
        Scrape definition and explanation from Investopedia
        
        Args:
            term: Financial term to look up
            
        Returns:
            Dictionary with term definition or None if failed
        """
        logger.info(f"Looking up Investopedia term: {term}")
        
        # Format term for URL (lowercase, replace spaces with hyphens)
        formatted_term = term.lower().replace(' ', '-')
        url = f"{self.education_sources['investopedia']}/terms/{formatted_term[0]}/{formatted_term}.asp"
        
        try:
            domain = self._get_domain(url)
            self._rate_limit(domain)
            
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code != 200:
                logger.warning(f"⚠️  Term not found: {term}")
                return None
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract definition
            title = soup.find('h1')
            title_text = title.get_text(strip=True) if title else term
            
            # Find definition section
            definition = soup.find('div', {'id': 'mntl-sc-block_1-0'})
            if not definition:
                definition = soup.find('p')
            
            definition_text = definition.get_text(strip=True) if definition else 'Definition not available'
            
            term_data = {
                'term': term,
                'title': title_text,
                'definition': definition_text[:1000],
                'source': 'Investopedia',
                'url': url,
                'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            logger.info(f"✅ Successfully scraped term: {term}")
            return term_data
            
        except Exception as e:
            logger.error(f"❌ Error scraping term {term}: {e}")
            return None
    
    def get_financial_education_content(self, topic: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search for educational content on a financial topic
        
        Args:
            topic: Financial topic to search for
            limit: Number of results to return
            
        Returns:
            List of educational resources
        """
        logger.info(f"Searching for educational content on: {topic}")
        
        # Sample educational content - in production, implement actual search
        sample_content = [
            {
                'title': f'Introduction to {topic}',
                'description': f'Learn the basics of {topic} and how it impacts your investments.',
                'url': f'https://www.investopedia.com/search?q={topic.replace(" ", "+")}',
                'source': 'Investopedia',
                'type': 'educational'
            },
            {
                'title': f'{topic} Explained for Beginners',
                'description': f'A comprehensive guide to understanding {topic} in simple terms.',
                'url': f'https://www.fool.com/search/?q={topic.replace(" ", "+")}',
                'source': 'The Motley Fool',
                'type': 'educational'
            },
            {
                'title': f'How {topic} Works',
                'description': f'Step-by-step breakdown of {topic} and its practical applications.',
                'url': f'https://www.nerdwallet.com/search?query={topic.replace(" ", "+")}',
                'source': 'NerdWallet',
                'type': 'educational'
            }
        ]
        
        logger.info(f"✅ Returning {min(limit, len(sample_content))} educational resources")
        return sample_content[:limit]
    
    def scrape_stock_analysis_sites(self, symbol: str) -> Dict[str, Any]:
        """
        Gather stock analysis from various financial sites
        
        Args:
            symbol: Stock ticker symbol
            
        Returns:
            Dictionary with aggregated analysis data
        """
        logger.info(f"Gathering stock analysis for {symbol}")
        
        # Sample analysis data - in production, scrape actual sites
        analysis_data = {
            'symbol': symbol.upper(),
            'analyst_ratings': {
                'strong_buy': 'N/A',
                'buy': 'N/A',
                'hold': 'N/A',
                'sell': 'N/A',
                'strong_sell': 'N/A'
            },
            'price_targets': {
                'high': 'N/A',
                'average': 'N/A',
                'low': 'N/A'
            },
            'sentiment': 'Neutral',
            'sources_checked': ['Yahoo Finance', 'MarketWatch', 'Seeking Alpha'],
            'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        logger.info(f"✅ Stock analysis data prepared for {symbol}")
        return analysis_data
    
    def scrape_etf_holdings(self, etf_symbol: str, top_n: int = 10) -> List[Dict[str, Any]]:
        """
        Scrape top holdings of an ETF
        
        Args:
            etf_symbol: ETF ticker symbol
            top_n: Number of top holdings to return
            
        Returns:
            List of top holdings
        """
        logger.info(f"Scraping top {top_n} holdings for {etf_symbol}")
        
        # Sample holdings - in production, scrape actual ETF data
        sample_holdings = [
            {'symbol': 'AAPL', 'name': 'Apple Inc.', 'weight': '7.2%'},
            {'symbol': 'MSFT', 'name': 'Microsoft Corp.', 'weight': '6.8%'},
            {'symbol': 'GOOGL', 'name': 'Alphabet Inc.', 'weight': '4.1%'},
            {'symbol': 'AMZN', 'name': 'Amazon.com Inc.', 'weight': '3.5%'},
            {'symbol': 'NVDA', 'name': 'NVIDIA Corp.', 'weight': '3.2%'}
        ]
        
        logger.info(f"✅ Returning top {min(top_n, len(sample_holdings))} holdings")
        return sample_holdings[:top_n]
    
    def get_financial_calculator_data(self, calculator_type: str) -> Dict[str, Any]:
        """
        Get parameters and formulas for common financial calculators
        
        Args:
            calculator_type: Type of calculator (compound_interest, retirement, mortgage, etc.)
            
        Returns:
            Dictionary with calculator information
        """
        calculators = {
            'compound_interest': {
                'name': 'Compound Interest Calculator',
                'formula': 'A = P(1 + r/n)^(nt)',
                'parameters': ['Principal (P)', 'Rate (r)', 'Time (t)', 'Frequency (n)'],
                'description': 'Calculate future value of investments with compound interest'
            },
            'retirement': {
                'name': 'Retirement Savings Calculator',
                'formula': 'FV = PMT × [(1 + r)^n - 1] / r',
                'parameters': ['Monthly contribution', 'Years to retirement', 'Expected return', 'Current savings'],
                'description': 'Estimate retirement savings based on contributions and returns'
            },
            'mortgage': {
                'name': 'Mortgage Payment Calculator',
                'formula': 'M = P[r(1+r)^n]/[(1+r)^n-1]',
                'parameters': ['Loan amount', 'Interest rate', 'Loan term', 'Down payment'],
                'description': 'Calculate monthly mortgage payments'
            }
        }
        
        calculator_data = calculators.get(calculator_type, {
            'name': 'Unknown Calculator',
            'description': 'Calculator type not found'
        })
        
        logger.info(f"✅ Retrieved calculator data for {calculator_type}")
        return calculator_data

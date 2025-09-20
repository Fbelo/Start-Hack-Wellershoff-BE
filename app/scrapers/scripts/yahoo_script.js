/**
 * Yahoo Finance News Scraper Script
 * This script extracts financial news from Yahoo Finance
 */

// Helper function to get text content and handle missing elements
function getTextContent(element) {
  if (!element) return '';
  return element.textContent.trim();
}

// Main function to extract articles from news listings
function extractNewsArticles() {
  const results = [];
  
  // Try different selectors for article containers based on page type
  let articleElements = [];
  
  // Homepage news stream
  const streamArticles = document.querySelectorAll('li.js-stream-content');
  // News page articles
  const newsPageArticles = document.querySelectorAll('div.Ov\\(h\\).Pend\\(44px\\).Pstart\\(25px\\)');
  // Latest news section
  const latestNewsArticles = document.querySelectorAll('div.article');
  
  if (streamArticles.length > 0) {
    articleElements = streamArticles;
  } else if (newsPageArticles.length > 0) {
    articleElements = newsPageArticles;
  } else if (latestNewsArticles.length > 0) {
    articleElements = latestNewsArticles;
  }
  
  // Process each article
  articleElements.forEach((article, index) => {
    if (index >= 20) return; // Limit to 20 articles
    
    try {
      // Extract title and URL
      let title = '';
      let url = '';
      
      // Try different title selectors
      const headingElement = 
        article.querySelector('h3, h4, .js-content-viewer') || 
        article.querySelector('a[data-test="mega"]') ||
        article.querySelector('.StretchedBox');
      
      if (headingElement) {
        title = getTextContent(headingElement);
        
        // Get the URL - it might be on the heading or a parent element
        const linkElement = headingElement.closest('a') || headingElement.querySelector('a');
        if (linkElement) {
          url = linkElement.href;
        }
      }
      
      if (!title || !url) {
        return; // Skip this article if no title or URL
      }
      
      // Extract summary if available
      let summary = '';
      const summaryElement = 
        article.querySelector('p, .Fz\\(14px\\)') || 
        article.querySelector('[data-test="description"]');
      
      if (summaryElement) {
        summary = getTextContent(summaryElement);
      }
      
      // Extract publish time
      let publishTime = '';
      const timeElement = article.querySelector('time, span.C\\(\\#959595\\)');
      if (timeElement) {
        publishTime = timeElement.getAttribute('datetime') || getTextContent(timeElement);
      }
      
      // Extract image URL
      let imageUrl = null;
      const imageElement = article.querySelector('img');
      if (imageElement) {
        imageUrl = imageElement.src;
      }
      
      // Extract provider/source
      let provider = 'Yahoo Finance';
      const providerElement = article.querySelector('.C\\(\\#959595\\) span:not(.Mstart\\(3px\\)), .provider-name');
      if (providerElement) {
        const providerText = getTextContent(providerElement);
        if (providerText) {
          provider = providerText;
        }
      }
      
      // Extract stock tickers mentioned in article
      const tickers = [];
      const tickerElements = article.querySelectorAll('.Fw\\(b\\)');
      tickerElements.forEach(el => {
        const ticker = getTextContent(el);
        if (ticker && ticker.match(/^[A-Z]+$/)) {
          tickers.push(ticker);
        }
      });
      
      results.push({
        title,
        url,
        summary,
        publishTime,
        imageUrl,
        provider,
        tickers,
        source: 'Yahoo Finance'
      });
    } catch (error) {
      console.error(`Error extracting Yahoo Finance article: ${error.message}`);
    }
  });
  
  return results;
}

// Function to extract article content from a single article page
function extractArticleContent() {
  // Get the article container
  const articleContainer = document.querySelector('.caas-body, .canvas-body');
  if (!articleContainer) return '';
  
  // Get article metadata
  const metadata = {};
  
  // Get title
  const titleElement = document.querySelector('h1.caas-title, .canvas-header');
  if (titleElement) {
    metadata.title = getTextContent(titleElement);
  }
  
  // Get author
  const authorElement = document.querySelector('.caas-author-byline-collapse span, .provider-link');
  if (authorElement) {
    metadata.author = getTextContent(authorElement);
  }
  
  // Get publish time
  const timeElement = document.querySelector('time.caas-attr-meta-time, .date');
  if (timeElement) {
    metadata.publishTime = timeElement.getAttribute('datetime') || getTextContent(timeElement);
  }
  
  // Get source
  const sourceElement = document.querySelector('.caas-attr-source, .provider');
  if (sourceElement) {
    metadata.source = getTextContent(sourceElement);
  }
  
  // Get all paragraphs in the article body
  const paragraphs = articleContainer.querySelectorAll('p, h2, blockquote');
  
  // Extract content with formatting
  let content = '';
  paragraphs.forEach(element => {
    const text = getTextContent(element);
    if (!text) return;
    
    if (element.tagName === 'H2') {
      content += `## ${text}\n\n`;
    } else if (element.tagName === 'BLOCKQUOTE') {
      content += `> ${text}\n\n`;
    } else {
      content += `${text}\n\n`;
    }
  });
  
  // Extract related stock tickers if available
  const tickers = [];
  const tickerElements = document.querySelectorAll('.caas-sidebar a[data-test="quoteLink"]');
  tickerElements.forEach(el => {
    const ticker = getTextContent(el);
    if (ticker) {
      tickers.push(ticker);
    }
  });
  
  if (tickers.length > 0) {
    metadata.tickers = tickers;
  }
  
  return {
    content: content.trim(),
    metadata
  };
}

// Get related news for a specific ticker if on a stock page
function extractTickerNews() {
  const tickerNewsElements = document.querySelectorAll('#quoteNewsStream-0-Stream li, .Pos\\(r\\)');
  const results = [];
  
  // Get ticker symbol from URL or page
  let ticker = '';
  const urlMatch = window.location.pathname.match(/quote\/([A-Z]+)/);
  if (urlMatch && urlMatch[1]) {
    ticker = urlMatch[1];
  } else {
    const tickerElement = document.querySelector('h1[data-reactid*="quote-header"]');
    if (tickerElement) {
      const tickerText = getTextContent(tickerElement);
      const match = tickerText.match(/\(([A-Z]+)\)/);
      if (match && match[1]) {
        ticker = match[1];
      }
    }
  }
  
  tickerNewsElements.forEach((element, index) => {
    if (index >= 10) return; // Limit to 10 articles
    
    try {
      // Extract title and link
      const titleElement = element.querySelector('a, h3');
      if (!titleElement) return;
      
      const title = getTextContent(titleElement);
      const url = titleElement.href;
      
      // Extract time
      const timeElement = element.querySelector('span.C\\(\\#959595\\)');
      const publishTime = timeElement ? getTextContent(timeElement) : '';
      
      // Extract source
      const sourceElement = element.querySelector('.C\\(\\#959595\\) span:not(.Mstart\\(3px\\))');
      const source = sourceElement ? getTextContent(sourceElement) : 'Yahoo Finance';
      
      results.push({
        title,
        url,
        publishTime,
        source,
        ticker,
        type: 'ticker-specific'
      });
    } catch (error) {
      console.error(`Error extracting ticker news: ${error.message}`);
    }
  });
  
  return results;
}

// Determine what type of page we're on and run the appropriate function
if (window.location.pathname.includes('/news/')) {
  // Single article page
  return JSON.stringify(extractArticleContent());
} else if (window.location.pathname.includes('/quote/')) {
  // Stock quote page - get ticker-specific news
  return JSON.stringify(extractTickerNews());
} else {
  // News listing page
  return JSON.stringify(extractNewsArticles());
}

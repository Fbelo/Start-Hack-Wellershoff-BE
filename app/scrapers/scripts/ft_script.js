/**
 * Financial Times Scraper Script
 * This script extracts news articles from FT.com
 */

// Main extraction function for article lists
function scrapeArticleList() {
  // Configuration for different FT page types
  const config = {
    newsFeed: {
      articleSelector: 'div.o-teaser',
      titleSelector: 'a.js-teaser-heading-link',
      summarySelector: 'div.o-teaser__standfirst',
      timeSelector: 'time.o-date',
    },
    markets: {
      articleSelector: 'div.o-teaser--article',
      titleSelector: 'div.o-teaser__heading a',
      summarySelector: 'p.o-teaser__standfirst',
      timeSelector: 'time.o-date',
    }
  };
  
  // Determine page type
  let pageType = 'newsFeed';
  if (window.location.href.includes('/markets')) {
    pageType = 'markets';
  }
  
  const pageConfig = config[pageType];
  const articles = document.querySelectorAll(pageConfig.articleSelector);
  const results = [];
  
  // Process each article
  articles.forEach((article, index) => {
    if (index >= 12) return; // Limit to 12 articles
    
    try {
      // Get article title and URL
      const titleElement = article.querySelector(pageConfig.titleSelector);
      if (!titleElement) return;
      
      const title = titleElement.textContent.trim();
      const url = titleElement.href;
      
      // Get summary if available
      const summaryElement = article.querySelector(pageConfig.summarySelector);
      const summary = summaryElement ? summaryElement.textContent.trim() : '';
      
      // Get publication time
      const timeElement = article.querySelector(pageConfig.timeSelector);
      const publishedTime = timeElement ? timeElement.getAttribute('datetime') : '';
      
      // Get premium status
      const isPremium = !!article.querySelector('.o-teaser__tag--premium');
      
      // Get image if available
      const imageElement = article.querySelector('img');
      const imageUrl = imageElement ? imageElement.src : null;
      
      // Get theme/category
      const themeElement = article.querySelector('.o-teaser__tag');
      const theme = themeElement ? themeElement.textContent.trim() : '';
      
      results.push({
        title,
        url,
        summary,
        publishedTime,
        isPremium,
        imageUrl,
        theme,
        source: 'Financial Times'
      });
    } catch (error) {
      console.error(`Error extracting FT article: ${error.message}`);
    }
  });
  
  return results;
}

// Extract full article content
function extractArticleContent() {
  // Article container
  const articleContainer = document.querySelector('article.article');
  if (!articleContainer) return '';
  
  // Article body
  const articleBody = document.querySelector('div.article__content-body');
  if (!articleBody) return '';
  
  // Extract all paragraphs
  const paragraphs = articleBody.querySelectorAll('p, h2, h3, blockquote');
  
  // Build content with proper formatting
  let content = '';
  paragraphs.forEach(element => {
    const text = element.textContent.trim();
    if (!text) return;
    
    // Format based on element type
    if (element.tagName === 'H2' || element.tagName === 'H3') {
      content += `## ${text}\n\n`;
    } else if (element.tagName === 'BLOCKQUOTE') {
      content += `> ${text}\n\n`;
    } else {
      content += `${text}\n\n`;
    }
  });
  
  // Extract metadata
  const metaData = {};
  
  // Get author info
  const authorElement = document.querySelector('a.n-content-tag--author');
  if (authorElement) {
    metaData.author = authorElement.textContent.trim();
  }
  
  // Get publication date
  const dateElement = document.querySelector('time.article-info__time-stamp');
  if (dateElement) {
    metaData.publishedAt = dateElement.getAttribute('datetime');
  }
  
  // Return combined results
  return {
    content: content.trim(),
    metadata: metaData
  };
}

// Execute based on page type
if (window.location.pathname.startsWith('/content/') || 
    window.location.pathname.match(/\/\d{4}\/\d{2}\/\d{2}\//)) {
  // On an article page
  return JSON.stringify(extractArticleContent());
} else {
  // On a listing page
  return JSON.stringify(scrapeArticleList());
}

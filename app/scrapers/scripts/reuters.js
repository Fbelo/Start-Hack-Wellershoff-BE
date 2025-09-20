/**
 * Reuters News Scraper Script
 * This script extracts business and finance news from Reuters
 */

// Utility function to clean text
function cleanText(text) {
  if (!text) return '';
  return text.replace(/\s+/g, ' ').trim();
}

// Extract articles from Reuters business/finance pages
function extractBusinessArticles() {
  // Get all article containers
  let articleContainers = [];
  
  // Try different selectors based on page structure
  const mediaStoryCards = document.querySelectorAll('div[data-testid="media-story-card"]');
  const storyCards = document.querySelectorAll('div.story-card');
  const mediaItems = document.querySelectorAll('li[data-testid="media-item"]');
  
  if (mediaStoryCards.length > 0) {
    articleContainers = mediaStoryCards;
  } else if (storyCards.length > 0) {
    articleContainers = storyCards;
  } else if (mediaItems.length > 0) {
    articleContainers = mediaItems;
  }
  
  const results = [];
  
  // Process each article
  articleContainers.forEach((container, index) => {
    if (index >= 15) return; // Limit to 15 articles
    
    try {
      // Extract headline
      const headlineElement = container.querySelector('h3[data-testid="heading"], h3.story-card-heading');
      if (!headlineElement) return;
      
      const headline = cleanText(headlineElement.textContent);
      
      // Extract URL
      const linkElement = container.querySelector('a[data-testid="heading-link"], a.heading-link');
      const url = linkElement ? linkElement.href : '';
      
      // Extract timestamp
      let timestamp = '';
      const timeElement = container.querySelector('time[data-testid="timestamp"], time.story-card-timestamp');
      if (timeElement) {
        timestamp = timeElement.getAttribute('datetime') || timeElement.textContent.trim();
      }
      
      // Extract image
      let imageUrl = null;
      const imageElement = container.querySelector('img[data-testid="image"], img.story-card-image');
      if (imageElement) {
        imageUrl = imageElement.src;
      }
      
      // Extract description/summary
      let summary = '';
      const descriptionElement = container.querySelector('p[data-testid="description"], p.story-card-description');
      if (descriptionElement) {
        summary = cleanText(descriptionElement.textContent);
      }
      
      // Extract section/category
      let category = '';
      const sectionElement = container.querySelector('span[data-testid="section-name"], span.story-card-section');
      if (sectionElement) {
        category = cleanText(sectionElement.textContent);
      }
      
      // Extract author information
      let author = '';
      const authorElement = container.querySelector('span[data-testid="byline"], span.story-card-byline');
      if (authorElement) {
        author = cleanText(authorElement.textContent);
      }
      
      results.push({
        title: headline,
        url,
        summary,
        publishedAt: timestamp,
        imageUrl,
        category,
        author,
        source: 'Reuters'
      });
    } catch (error) {
      console.error(`Error extracting Reuters article: ${error.message}`);
    }
  });
  
  return results;
}

// Extract content from an article page
function extractArticleContent() {
  // Get article body
  const articleBodyElement = document.querySelector('div[data-testid="article-body"], div.article-body');
  if (!articleBodyElement) return '';
  
  // Get all paragraphs
  const paragraphs = articleBodyElement.querySelectorAll('p[data-testid="paragraph"], p.paragraph');
  
  // Combine paragraphs into full content
  const content = Array.from(paragraphs)
    .map(p => cleanText(p.textContent))
    .filter(text => text.length > 0)
    .join('\n\n');
  
  // Get additional metadata
  const metadata = {};
  
  // Get article headline (for verification)
  const headlineElement = document.querySelector('h1[data-testid="article-header"], h1.article-header');
  if (headlineElement) {
    metadata.title = cleanText(headlineElement.textContent);
  }
  
  // Get publication date
  const dateElement = document.querySelector('time[data-testid="published-timestamp"], time.published-timestamp');
  if (dateElement) {
    metadata.publishedAt = dateElement.getAttribute('datetime') || dateElement.textContent.trim();
  }
  
  // Get authors
  const authorElements = document.querySelectorAll('div[data-testid="byline"], div.byline a');
  if (authorElements.length > 0) {
    metadata.authors = Array.from(authorElements).map(el => cleanText(el.textContent));
  }
  
  return {
    content,
    metadata
  };
}

// Determine page type and run appropriate function
if (window.location.pathname.includes('/article/')) {
  // On an article page
  return JSON.stringify(extractArticleContent());
} else {
  // On a listing page (business, finance, markets, etc.)
  return JSON.stringify(extractBusinessArticles());
}

/**
 * Bloomberg News Scraper Script
 * This script extracts market news articles from Bloomberg
 */

// Function to extract articles from Bloomberg markets page
function extractArticles() {
  // Article container - main story list
  const articles = document.querySelectorAll('article.story-package-module__story, div.story-list-story');
  
  const results = [];
  
  articles.forEach((article, index) => {
    if (index >= 15) return; // Limit to 15 articles
    
    try {
      // Extract headline
      const headlineElement = article.querySelector('h3.story-package-module__headline, h3.story-list-story__headline');
      if (!headlineElement) return;
      
      const title = headlineElement.textContent.trim();
      
      // Extract URL
      const linkElement = article.querySelector('a.story-package-module__headline-link, a.story-list-story__headline-link');
      const url = linkElement ? linkElement.href : '';
      
      // Extract summary
      const summaryElement = article.querySelector('div.story-package-module__summary, p.story-list-story__summary');
      const summary = summaryElement ? summaryElement.textContent.trim() : '';
      
      // Extract author
      const authorElement = article.querySelector('div.byline-details__wrapper span');
      const author = authorElement ? authorElement.textContent.trim() : '';
      
      // Extract time
      const timeElement = article.querySelector('time.timestamp');
      const publishedTime = timeElement ? timeElement.getAttribute('datetime') : '';
      
      // Extract image
      const imageElement = article.querySelector('img');
      const imageUrl = imageElement ? imageElement.src : null;
      
      // Extract category/topic
      const topicElement = article.querySelector('div.story-package-module__story__eyebrow, span.story-list-story__eyebrow');
      const topic = topicElement ? topicElement.textContent.trim() : '';
      
      results.push({
        title,
        url,
        summary,
        author,
        publishedTime,
        imageUrl,
        topic,
        source: 'Bloomberg'
      });
    } catch (error) {
      console.error(`Error extracting article: ${error.message}`);
    }
  });
  
  return results;
}

// Function to extract content from a specific article page
function extractArticleContent() {
  // Article body container
  const articleBody = document.querySelector('div.body-content, div.body-copy-v2');
  if (!articleBody) return '';
  
  // Get all paragraphs
  const paragraphs = articleBody.querySelectorAll('p');
  
  // Combine paragraphs into full content
  const content = Array.from(paragraphs)
    .map(p => p.textContent.trim())
    .filter(text => text.length > 0)
    .join('\n\n');
  
  return content;
}

// Main execution - execute different functions based on the URL
if (window.location.href.includes('/markets') || window.location.href.includes('/latest')) {
  return JSON.stringify(extractArticles());
} else if (window.location.href.includes('/news/')) {
  return extractArticleContent();
} else {
  console.error('Unknown page type, cannot extract content');
  return JSON.stringify([]);
}

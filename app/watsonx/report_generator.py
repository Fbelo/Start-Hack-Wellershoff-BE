"""
Watson AI Report Generator

This module provides functionality for generating AI-powered reports based on news data.
"""
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime, date, timedelta
from app.api.schemas.report import (
    WeeklyAIReport, 
    WeeklyReportNewsItem, 
    MarketImpactSummary, 
    CategoryInsight
)
from app.api.schemas.news import NewsModel
from app.common.enums import ImpactType
from app.watsonx.client import WatsonAgentClient
from sqlalchemy.orm import Session

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ReportGenerator:
    """
    Generates AI-powered reports based on news data
    """
    def __init__(self):
        self.watson_client = WatsonAgentClient()
    
    async def generate_weekly_report(
        self, 
        news_items: List[NewsModel],
        start_date: date,
        end_date: date,
        max_news_items: int = 10,
        categories_of_interest: Optional[List[str]] = None
    ) -> WeeklyAIReport:
        """
        Generate a weekly AI report based on news data
        
        Args:
            news_items (List[NewsModel]): The news items to include in the report
            start_date (date): The start date of the report period
            end_date (date): The end date of the report period
            max_news_items (int): The maximum number of news items to include in the report
            categories_of_interest (Optional[List[str]]): Categories to focus on
            
        Returns:
            WeeklyAIReport: The generated report
        """
        logger.info(f"Generating weekly report for period {start_date} to {end_date}")
        
        # Filter news by date range
        filtered_news = [
            news for news in news_items 
            if start_date <= news.published_at.date() <= end_date
        ]
        
        # Filter by categories if specified
        if categories_of_interest:
            filtered_news = [
                news for news in filtered_news
                if any(cat.name.lower() in [c.lower() for c in categories_of_interest] 
                       for cat in news.categories)
            ]
        
        logger.info(f"Found {len(filtered_news)} news items for the report period")
        
        # Calculate impact statistics
        impact_stats = self._calculate_impact_statistics(filtered_news)
        
        # Get the top news items based on importance
        top_news = self._select_top_news(filtered_news, max_news_items)
        
        # Generate category insights
        category_insights = self._generate_category_insights(filtered_news)
        
        # Determine key trends and outlook using Watson AI
        trends_and_outlook = await self._generate_trends_and_outlook(filtered_news)
        
        # Generate executive summary
        executive_summary = await self._generate_executive_summary(
            filtered_news, 
            impact_stats, 
            category_insights,
            trends_and_outlook
        )
        
        # Create the report title
        report_title = f"Weekly Market Intelligence Report: {start_date.strftime('%b %d')} - {end_date.strftime('%b %d, %Y')}"
        
        # Build the complete report
        report = WeeklyAIReport(
            report_date=datetime.now().date(),
            week_start=start_date,
            week_end=end_date,
            report_title=report_title,
            executive_summary=executive_summary,
            market_impact=impact_stats,
            top_news=top_news,
            category_insights=category_insights,
            key_trends=trends_and_outlook.get("key_trends", []),
            outlook=trends_and_outlook.get("outlook", "")
        )
        
        return report
    
    def _calculate_impact_statistics(self, news_items: List[NewsModel]) -> MarketImpactSummary:
        """
        Calculate statistics about the market impact of news items
        """
        # Count news items by impact type
        positive_count = sum(1 for news in news_items if news.impact_prediction in [ImpactType.POSITIVE, ImpactType.VERY_POSITIVE])
        negative_count = sum(1 for news in news_items if news.impact_prediction in [ImpactType.NEGATIVE, ImpactType.VERY_NEGATIVE])
        neutral_count = sum(1 for news in news_items if news.impact_prediction == ImpactType.UNSURE)
        
        # Determine overall sentiment
        total = positive_count + negative_count + neutral_count
        if total == 0:
            overall_sentiment = "neutral"
        else:
            positive_ratio = positive_count / total
            negative_ratio = negative_count / total
            
            if positive_ratio > 0.6:
                overall_sentiment = "strongly positive"
            elif positive_ratio > 0.4:
                overall_sentiment = "positive"
            elif negative_ratio > 0.6:
                overall_sentiment = "strongly negative"
            elif negative_ratio > 0.4:
                overall_sentiment = "negative"
            else:
                overall_sentiment = "neutral"
        
        # Extract key factors (simplistic approach - could be enhanced with AI)
        key_factors = []
        # Extract key categories that appear frequently
        category_counts = {}
        for news in news_items:
            for cat in news.categories:
                if cat.name in category_counts:
                    category_counts[cat.name] += 1
                else:
                    category_counts[cat.name] = 1
        
        # Get top categories
        key_factors = [cat for cat, count in sorted(
            category_counts.items(), key=lambda x: x[1], reverse=True
        )[:5]]
        
        return MarketImpactSummary(
            positive_count=positive_count,
            negative_count=negative_count,
            neutral_count=neutral_count,
            overall_sentiment=overall_sentiment,
            key_factors=key_factors
        )
    
    def _select_top_news(self, news_items: List[NewsModel], max_items: int) -> List[WeeklyReportNewsItem]:
        """
        Select the top news items for the report
        """
        # Sort news by importance (prioritize very positive/negative impact)
        def news_importance_score(news):
            # Prioritize news with strong impact predictions
            impact_score = {
                ImpactType.VERY_POSITIVE: 5,
                ImpactType.POSITIVE: 4,
                ImpactType.UNSURE: 3,
                ImpactType.NEGATIVE: 4,
                ImpactType.VERY_NEGATIVE: 5
            }.get(news.impact_prediction, 3)
            
            # Recent news is more important
            days_old = (datetime.now().date() - news.published_at.date()).days
            recency_score = max(0, 7 - days_old) / 7  # 1.0 for today, decreasing to 0 for a week old
            
            return impact_score * 0.7 + recency_score * 0.3
        
        sorted_news = sorted(news_items, key=news_importance_score, reverse=True)
        
        # Convert to report format
        top_news = []
        for news in sorted_news[:max_items]:
            top_news.append(
                WeeklyReportNewsItem(
                    id=news.id,
                    title=news.title,
                    summary=news.summary,
                    url=news.url,
                    published_at=news.published_at,
                    impact_prediction=news.impact_prediction,
                    categories=[cat.name for cat in news.categories]
                )
            )
        
        return top_news
    
    def _generate_category_insights(self, news_items: List[NewsModel]) -> List[CategoryInsight]:
        """
        Generate insights for each significant category
        """
        # Group news by category
        category_news = {}
        for news in news_items:
            for cat in news.categories:
                if cat.name not in category_news:
                    category_news[cat.name] = []
                category_news[cat.name].append(news)
        
        # Generate insights for categories with at least 3 news items
        insights = []
        for category, news_list in category_news.items():
            if len(news_list) < 3:
                continue
            
            # Count impact types
            pos_count = sum(1 for n in news_list if n.impact_prediction in [ImpactType.POSITIVE, ImpactType.VERY_POSITIVE])
            neg_count = sum(1 for n in news_list if n.impact_prediction in [ImpactType.NEGATIVE, ImpactType.VERY_NEGATIVE])
            
            # Generate simple impact summary
            if pos_count > neg_count * 2:
                impact_summary = f"Strongly positive outlook for {category} based on recent news."
            elif pos_count > neg_count:
                impact_summary = f"Generally positive sentiment around {category} with some mixed signals."
            elif neg_count > pos_count * 2:
                impact_summary = f"Significant concerns regarding {category} based on recent developments."
            elif neg_count > pos_count:
                impact_summary = f"Cautious outlook for {category} with some negative indicators."
            else:
                impact_summary = f"Mixed signals regarding {category} with no clear trend."
            
            insights.append(
                CategoryInsight(
                    category=category,
                    news_count=len(news_list),
                    impact_summary=impact_summary
                )
            )
        
        # Sort by news count
        insights.sort(key=lambda x: x.news_count, reverse=True)
        
        return insights[:5]  # Return top 5 categories
    
    async def _generate_trends_and_outlook(self, news_items: List[NewsModel]) -> Dict[str, Any]:
        """
        Use Watson AI to generate key trends and outlook based on news data
        """
        # For simplicity, this is mocked - in a real implementation, this would call Watson
        # with news data to generate insights
        
        # TODO: Implement actual Watson API call for trends and outlook
        
        # Mock data for now
        return {
            "key_trends": [
                "Increasing focus on AI and automation across industries",
                "Growing concerns about inflation and interest rates",
                "Continued supply chain challenges affecting multiple sectors"
            ],
            "outlook": "Markets are expected to remain cautious in the coming week, with particular attention to upcoming economic data releases and central bank communications. Volatility may increase as earnings season approaches."
        }
    
    async def _generate_executive_summary(
        self, 
        news_items: List[NewsModel],
        impact_stats: MarketImpactSummary,
        category_insights: List[CategoryInsight],
        trends_and_outlook: Dict[str, Any]
    ) -> str:
        """
        Generate an executive summary for the report
        """
        # For simplicity, this is mocked - in a real implementation, this would call Watson
        # to generate a natural language summary
        
        # TODO: Implement actual Watson API call for executive summary
        
        # Generate a basic summary based on the available data
        total_news = len(news_items)
        sentiment = impact_stats.overall_sentiment
        
        summary = f"This week's analysis of {total_news} news items reveals a {sentiment} market sentiment. "
        
        if impact_stats.key_factors:
            factors = ", ".join(impact_stats.key_factors[:3])
            summary += f"Key factors influencing markets include {factors}. "
        
        if category_insights:
            top_category = category_insights[0]
            summary += f"{top_category.category.capitalize()} was particularly active with {top_category.news_count} significant developments. "
        
        if "outlook" in trends_and_outlook:
            summary += trends_and_outlook["outlook"]
        
        return summary
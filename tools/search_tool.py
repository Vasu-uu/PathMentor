import requests
from typing import Dict, List, Any
import json
from datetime import datetime

class WebSearchTool:
    """
    Keyless web search tool using DuckDuckGo's instant answer API
    and Wikipedia API for educational content.
    No API keys required.
    """
    
    def __init__(self):
        self.name = "web_search"
        self.description = "Searches the web for information without requiring API keys"
        self.ddg_api = "https://api.duckduckgo.com/"
        self.wikipedia_api = "https://en.wikipedia.org/api/rest_v1/page/summary/"
    
    def execute(self, query: str, source: str = "auto") -> Dict[str, Any]:
        """
        Execute a web search query.
        
        Args:
            query: Search query string
            source: Search source ('duckduckgo', 'wikipedia', or 'auto')
        
        Returns:
            Search results with relevant information
        """
        
        if source == "wikipedia" or (source == "auto" and self._is_factual_query(query)):
            return self._search_wikipedia(query)
        else:
            return self._search_duckduckgo(query)
    
    def _search_duckduckgo(self, query: str) -> Dict[str, Any]:
        """Search using DuckDuckGo Instant Answer API."""
        
        try:
            params = {
                'q': query,
                'format': 'json',
                'no_html': 1,
                'skip_disambig': 1
            }
            
            response = requests.get(self.ddg_api, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            abstract = data.get('Abstract', '')
            heading = data.get('Heading', '')
            abstract_url = data.get('AbstractURL', '')
            related_topics = data.get('RelatedTopics', [])
            
            topics_text = []
            for topic in related_topics[:5]:
                if isinstance(topic, dict) and 'Text' in topic:
                    topics_text.append(topic['Text'])
            
            result = {
                "success": True,
                "query": query,
                "source": "DuckDuckGo",
                "heading": heading,
                "summary": abstract if abstract else "No direct answer found",
                "url": abstract_url,
                "related_topics": topics_text,
                "timestamp": datetime.now().isoformat()
            }
            
            if not abstract and topics_text:
                result["summary"] = topics_text[0]
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "query": query,
                "source": "DuckDuckGo",
                "error": str(e),
                "summary": "Search failed",
                "timestamp": datetime.now().isoformat()
            }
    
    def _search_wikipedia(self, query: str) -> Dict[str, Any]:
        """Search using Wikipedia API."""
        
        try:
            search_term = query.replace(' ', '_')
            url = f"{self.wikipedia_api}{search_term}"
            
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            return {
                "success": True,
                "query": query,
                "source": "Wikipedia",
                "heading": data.get('title', ''),
                "summary": data.get('extract', ''),
                "url": data.get('content_urls', {}).get('desktop', {}).get('page', ''),
                "thumbnail": data.get('thumbnail', {}).get('source', ''),
                "timestamp": datetime.now().isoformat()
            }
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                return self._search_duckduckgo(query)
            
            return {
                "success": False,
                "query": query,
                "source": "Wikipedia",
                "error": str(e),
                "summary": "Search failed",
                "timestamp": datetime.now().isoformat()
            }
        
        except Exception as e:
            return {
                "success": False,
                "query": query,
                "source": "Wikipedia",
                "error": str(e),
                "summary": "Search failed",
                "timestamp": datetime.now().isoformat()
            }
    
    def _is_factual_query(self, query: str) -> bool:
        """Determine if query is likely factual (better for Wikipedia)."""
        
        factual_keywords = [
            'what is', 'who is', 'when was', 'where is', 'define',
            'history of', 'explain', 'meaning of', 'biography'
        ]
        
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in factual_keywords)
    
    def search_educational_content(self, topic: str) -> Dict[str, Any]:
        """
        Search for educational content on a specific topic.
        
        Args:
            topic: Educational topic to search for
        
        Returns:
            Educational resources and summary
        """
        
        result = self.execute(topic, source="wikipedia")
        
        result["educational"] = True
        result["topic"] = topic
        
        if result["success"] and result.get("summary"):
            result["study_notes"] = self._extract_key_points(result["summary"])
        
        return result
    
    def _extract_key_points(self, text: str, max_points: int = 5) -> List[str]:
        """Extract key points from text."""
        
        sentences = text.split('. ')
        
        key_points = []
        for sentence in sentences[:max_points]:
            if len(sentence) > 20:
                clean_sentence = sentence.strip()
                if not clean_sentence.endswith('.'):
                    clean_sentence += '.'
                key_points.append(clean_sentence)
        
        return key_points

web_search_tool = WebSearchTool()

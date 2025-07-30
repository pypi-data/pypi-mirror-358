"""
Module for searching through conference data.
"""
import re
from typing import Dict, List, Any


def search_conference(conference_data: Dict[str, Any], query: str) -> List[Dict[str, Any]]:
    """
    Search through conference data for sessions/talks matching the query.
    
    Args:
        conference_data: The conference data dictionary
        query: The search query string
        
    Returns:
        A list of dictionaries containing the matching talk information
    """
    results = []
    query = query.lower()
    
    for session in conference_data.get("sessions", []):
        # Check if query matches session title
        if query in session.get("title", "").lower():
            results.append({
                "title": session.get("title", ""),
                "session": session.get("code", ""),
                "time": session.get("time", ""),
                "location": session.get("location", ""),
                "type": "session"
            })
        
        # Check talks within the session
        for talk in session.get("talks", []):
            # Check if query matches talk title, authors, or abstract
            title = talk.get("title", "").lower()
            authors = talk.get("authors", "").lower()
            abstract = talk.get("abstract", "").lower()
            
            if query in title or query in authors or query in abstract:
                results.append({
                    "title": talk.get("title", ""),
                    "session": session.get("code", ""),
                    "time": session.get("time", ""),
                    "location": session.get("location", ""),
                    "authors": talk.get("authors", ""),
                    "type": "talk"
                })
    
    return results 
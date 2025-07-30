"""
Module for handling conference data fetching and parsing.
"""
import requests
from bs4 import BeautifulSoup
import re
from typing import Dict, List, Any
from conventions.cache import cache
from conventions.config import CONFERENCES


def get_conference(conference_id: str) -> Dict[str, Any]:
    """
    Fetch and parse conference data from the specified conference.
    
    Args:
        conference_id: The identifier of the conference to fetch
        
    Returns:
        A dictionary containing the parsed conference data
    
    Raises:
        ValueError: If the conference_id is not supported
    """
    if conference_id not in CONFERENCES:
        raise ValueError(f"Conference '{conference_id}' is not supported")
    
    # Try to get from cache first
    cached_data = cache.get(conference_id)
    if cached_data:
        return cached_data
    
    # Fetch and parse
    url = CONFERENCES[conference_id]["url"]
    conference_data = fetch_and_parse_conference(url, conference_id)
    
    # Add additional metadata from config
    conference_data.update({
        "name": CONFERENCES[conference_id]["name"],
        "dates": CONFERENCES[conference_id]["dates"],
        "location": CONFERENCES[conference_id]["location"]
    })
    
    # Save to cache
    cache.set(conference_id, conference_data)
    
    return conference_data


def fetch_and_parse_conference(url: str, conference_id: str) -> Dict[str, Any]:
    """
    Fetch the conference webpage and parse its content.
    
    Args:
        url: The URL of the conference program
        conference_id: The identifier of the conference
        
    Returns:
        A dictionary containing the parsed conference data
    """
    try:
        # Fetch the webpage
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        # Parse the HTML content
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Extract conference title and dates
        conference_info = None
        for strong in soup.find_all('strong'):
            if 'conference' in strong.text.lower():
                conference_info = strong.text.strip()
                break
        
        if not conference_info:
            conference_info = f"Conference {conference_id}"
        
        # Parse based on the conference type
        if conference_id == "ICRA25":
            sessions = parse_icra25(soup)
        elif conference_id == "IROS25":
            sessions = parse_iros25(soup)
        elif conference_id == "HUMANOIDS25":
            sessions = parse_humanoids25(soup)
        else:
            sessions = []
            
    except requests.exceptions.RequestException as e:
        # Handle network errors, 404s, etc.
        print(f"Warning: Could not fetch {conference_id} program page ({url}): {e}")
        conference_info = f"Conference {conference_id}"
        
        # Return basic conference info when webpage is not available
        if conference_id == "IROS25":
            sessions = [{
                "code": "iros25_placeholder",
                "title": "IROS 2025 - Program will be available closer to the conference date",
                "time": "Oct 19-25, 2025",
                "location": "Hangzhou, China",
                "talks": [],
                "url": url
            }]
        elif conference_id == "HUMANOIDS25":
            sessions = [{
                "code": "humanoids25_placeholder",
                "title": "Humanoids 2025 - Program will be available closer to the conference date",
                "time": "Sep 30 - Oct 2, 2025",
                "location": "Seoul, Korea (South)",
                "talks": [],
                "url": url
            }]
        else:
            sessions = []
    
    return {
        "id": conference_id,
        "title": conference_info,
        "url": url,
        "sessions": sessions
    }


def parse_icra25(soup: BeautifulSoup) -> List[Dict[str, Any]]:
    """
    Parse ICRA 2025 specific conference data.
    
    Args:
        soup: BeautifulSoup object of the parsed HTML content
        
    Returns:
        A list of session dictionaries with talk information
    """
    sessions = []
    
    # Find all session links that have content
    session_links = []
    for a_tag in soup.find_all('a'):
        if a_tag.get('href') and a_tag.get('href').startswith('ICRA25_ContentListWeb') and a_tag.text.strip():
            session_links.append(a_tag)
    
    # Parse each track (column in the table)
    tracks = {}
    for track_header in soup.select('tr:first-child td'):
        track_name = track_header.text.strip()
        if track_name.startswith('Track'):
            tracks[track_name] = []
    
    # Find all session cells in the table
    for td in soup.select('td'):
        # Look for links to session content
        links = td.select('a[href*="ContentListWeb"]')
        if not links:
            continue
            
        for link in links:
            session_title = link.text.strip()
            if not session_title:
                continue
                
            # Get session code from the href (format: ICRA25_ContentListWeb_1.html#tuat1)
            href = link.get('href', '')
            session_code = href.split('#')[-1] if '#' in href else ''
            
            # Get time and location from preceding elements
            parent_row = td.find_parent('tr')
            if parent_row:
                # Try to find time from the row
                time_match = re.search(r'(\d{2}:\d{2}-\d{2}:\d{2})', parent_row.text)
                time = time_match.group(1) if time_match else ""
                
                # Location is usually in the first cell
                location_cells = parent_row.select('td:first-child')
                location = location_cells[0].text.strip() if location_cells else ""
            else:
                time = ""
                location = ""
            
            # Clean up the title (often contains session type)
            title_parts = session_title.split('_', 1)
            clean_title = title_parts[1].strip() if len(title_parts) > 1 else session_title
            
            sessions.append({
                "code": session_code,
                "title": clean_title,
                "time": time,
                "location": location,
                "talks": [],  # Would need to parse the detail page to get individual talks
                "url": f"https://ras.papercept.net/conferences/conferences/ICRA25/program/{href}"
            })
    
    return sessions


def parse_iros25(soup: BeautifulSoup) -> List[Dict[str, Any]]:
    """
    Parse IROS 2025 specific conference data.
    
    Args:
        soup: BeautifulSoup object of the parsed HTML content
        
    Returns:
        A list of session dictionaries with talk information
    """
    sessions = []
    
    # Look for common session patterns in IROS websites
    # This is a basic parser that can be enhanced when the program becomes available
    
    # Try to find session or program information
    for element in soup.find_all(['div', 'section', 'table']):
        if element.get('class') and any('session' in str(cls).lower() or 'program' in str(cls).lower() 
                                       for cls in element.get('class', [])):
            session_title = element.get_text(strip=True)
            if session_title and len(session_title) > 10:  # Avoid very short titles
                sessions.append({
                    "code": f"iros25_session_{len(sessions) + 1}",
                    "title": session_title[:200],  # Limit title length
                    "time": "",  # To be filled when program is available
                    "location": "",
                    "talks": [],
                    "url": ""
                })
    
    # If no specific sessions found, create a placeholder
    if not sessions:
        sessions.append({
            "code": "iros25_general",
            "title": "IROS 2025 - Program information will be available closer to the conference date",
            "time": "Oct 19-25, 2025",
            "location": "Hangzhou, China",
            "talks": [],
            "url": "http://irmv.sjtu.edu.cn/iros2025/"
        })
    
    return sessions


def parse_humanoids25(soup: BeautifulSoup) -> List[Dict[str, Any]]:
    """
    Parse Humanoids 2025 specific conference data.
    
    Args:
        soup: BeautifulSoup object of the parsed HTML content
        
    Returns:
        A list of session dictionaries with talk information
    """
    sessions = []
    
    # Look for common session patterns in Humanoids websites
    # This is a basic parser that can be enhanced when the program becomes available
    
    # Try to find program or schedule information
    for element in soup.find_all(['div', 'section', 'table']):
        text = element.get_text().lower()
        if any(keyword in text for keyword in ['program', 'schedule', 'session', 'keynote', 'tutorial']):
            session_text = element.get_text(strip=True)
            if session_text and len(session_text) > 10:
                sessions.append({
                    "code": f"humanoids25_session_{len(sessions) + 1}",
                    "title": session_text[:200],  # Limit title length
                    "time": "",  # To be filled when program is available
                    "location": "",
                    "talks": [],
                    "url": ""
                })
    
    # If no specific sessions found, create a placeholder
    if not sessions:
        sessions.append({
            "code": "humanoids25_general",
            "title": "Humanoids 2025 - Program information will be available closer to the conference date",
            "time": "Sep 30 - Oct 2, 2025",
            "location": "Seoul, Korea (South)",
            "talks": [],
            "url": "http://2025.ieee-humanoids.org/"
        })
    
    return sessions


def fetch_session_details(session_url: str) -> List[Dict[str, Any]]:
    """
    Fetch detailed information about talks within a session.
    
    Args:
        session_url: URL of the session detail page
        
    Returns:
        A list of talk dictionaries with detailed information
    """
    # This would parse the detailed session page to extract individual talks
    # Not implemented in this initial version as it requires additional page scraping
    # Would be a future enhancement
    return [] 
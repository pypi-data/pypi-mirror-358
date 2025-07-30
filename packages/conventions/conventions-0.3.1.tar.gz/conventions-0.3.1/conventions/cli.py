#!/usr/bin/env python
"""
Command line interface for the conventions package.
"""
import click
import yaypp
import os
from conventions.conferences import get_conference
from conventions.search import search_conference
from conventions.cache import cache
from conventions.config import CONFERENCES, MAX_RESULTS


@click.group()
def cli():
    """Search for conference talks via CLI."""
    pass


@cli.command()
@click.argument("query")
@click.option(
    "--conference", "-c", default="ICRA25", help="Conference identifier (default: ICRA25)"
)
@click.option(
    "--max-results", "-m", default=MAX_RESULTS, help="Maximum number of results to show"
)
def search(query, conference, max_results):
    """Search for talks containing the query in the specified conference."""
    click.echo(f"Searching for '{query}' in {conference}...")
    
    try:
        conf_data = get_conference(conference)
        results = search_conference(conf_data, query)
        
        if not results:
            click.echo("No matching talks found.")
            return
        
        # Limit results
        if len(results) > max_results:
            click.echo(f"Found {len(results)} matching talks. Showing top {max_results}:")
            results = results[:max_results]
        else:
            click.echo(f"Found {len(results)} matching talks:")
            
        for idx, result in enumerate(results, 1):
            click.echo(f"\n{idx}. {result['title']}")
            click.echo(f"   Session: {result['session']}")
            click.echo(f"   Time: {result['time']}")
            click.echo(f"   Location: {result['location']}")
            if result.get('authors'):
                click.echo(f"   Authors: {result['authors']}")
            if result.get('url'):
                click.echo(f"   URL: {result['url']}")
    except Exception as e:
        click.echo(f"Error searching conference: {str(e)}", err=True)


@cli.command(name="list")
def list_conferences():
    """List all available conferences."""
    click.echo("Available conferences:")
    for conf_id, conf_data in CONFERENCES.items():
        click.echo(f"- {conf_id} ({conf_data['name']})")
        click.echo(f"  Dates: {conf_data['dates']}")
        click.echo(f"  Location: {conf_data['location']}")


@cli.command()
@click.argument("conference_id")
def info(conference_id):
    """Show information about a specific conference."""
    try:
        if conference_id not in CONFERENCES:
            click.echo(f"Conference '{conference_id}' not found.", err=True)
            return
            
        conf_data = get_conference(conference_id)
        
        click.echo(f"Conference: {conf_data['title']}")
        click.echo(f"Dates: {conf_data.get('dates', 'N/A')}")
        click.echo(f"Location: {conf_data.get('location', 'N/A')}")
        click.echo(f"URL: {conf_data['url']}")
        
        session_count = len(conf_data.get('sessions', []))
        click.echo(f"Number of sessions: {session_count}")
    except Exception as e:
        click.echo(f"Error retrieving conference info: {str(e)}", err=True)


@cli.command()
@click.argument("conference_id", required=False)
@click.option("--all", "-a", is_flag=True, help="Clear cache for all conferences")
def clear_cache(conference_id, all):
    """Clear the cache for a specific conference or all conferences."""
    if all:
        cache.clear()
        click.echo("Cache cleared for all conferences.")
    elif conference_id:
        if conference_id not in CONFERENCES:
            click.echo(f"Conference '{conference_id}' not found.", err=True)
            return
        cache.clear(conference_id)
        click.echo(f"Cache cleared for conference '{conference_id}'.")
    else:
        click.echo("Please specify a conference ID or use --all to clear all caches.", err=True)


@cli.command()
@click.argument("conference_id")
@click.option("--output", "-o", help="Output file path (default: {conference_id}.yaml)")
@click.option("--include-talks", "-t", is_flag=True, help="Include individual talks in the export")
def export(conference_id, output, include_talks):
    """Export conference data to YAML format."""
    try:
        if conference_id not in CONFERENCES:
            click.echo(f"Conference '{conference_id}' not found.", err=True)
            return
        
        # Get conference data
        conf_data = get_conference(conference_id)
        
        # Prepare data for export
        export_data = {
            "conference": {
                "id": conf_data["id"],
                "title": conf_data["title"],
                "name": conf_data.get("name", ""),
                "dates": conf_data.get("dates", ""),
                "location": conf_data.get("location", ""),
                "url": conf_data["url"]
            },
            "sessions": []
        }
        
        # Add sessions data
        for session in conf_data.get("sessions", []):
            session_data = {
                "code": session.get("code", ""),
                "title": session.get("title", ""),
                "time": session.get("time", ""),
                "location": session.get("location", ""),
                "url": session.get("url", "")
            }
            
            # Include talks if requested
            if include_talks and session.get("talks"):
                session_data["talks"] = session["talks"]
            
            export_data["sessions"].append(session_data)
        
        # Determine output file path
        if not output:
            output = f"{conference_id.lower()}.yaml"
        
        # Export to YAML using yaypp
        with open(output, 'w') as f:
            # First dump to YAML string
            yaml_str = yaypp.yaml.dump(export_data, default_flow_style=False, indent=2, sort_keys=False)
            # Then format it nicely with yaypp
            formatted_yaml = yaypp.format_yaml(yaml_str)
            f.write(formatted_yaml)
        
        click.echo(f"Conference data exported to {output}")
        click.echo(f"Sessions exported: {len(export_data['sessions'])}")
        
    except Exception as e:
        click.echo(f"Error exporting conference data: {str(e)}", err=True)


def main():
    """Main entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main() 
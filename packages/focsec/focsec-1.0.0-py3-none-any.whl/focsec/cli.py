"""
Command line interface for Focsec SDK.
"""

import json
import os
import sys
from dataclasses import asdict

import click

from .client import FocsecClient
from .exceptions import FocsecError


@click.group()
@click.option(
    "-k", "--api-key",
    envvar="FOCSEC_API_KEY",
    help="Your Focsec API key (or set FOCSEC_API_KEY env var)"
)
@click.option(
    "-t", "--timeout",
    default=30,
    type=int,
    help="Request timeout in seconds (default: 30)"
)
@click.pass_context
def cli(ctx, api_key, timeout):
    """Focsec Threat Intelligence and VPN detection."""
    ctx.ensure_object(dict)
    ctx.obj['api_key'] = api_key
    ctx.obj['timeout'] = timeout


@cli.command()
@click.argument("address")
@click.option(
    "-j", "--json",
    "output_json",
    is_flag=True,
    help="Output raw JSON response"
)
@click.pass_context
def ip(ctx, address, output_json):
    """Look up IP address information."""
    api_key = ctx.obj.get('api_key')
    
    if not api_key:
        click.echo("Error: API key required. Use --api-key or set FOCSEC_API_KEY env var", err=True)
        sys.exit(1)
    
    try:
        client = FocsecClient(api_key=api_key, timeout=ctx.obj.get('timeout', 30))
        result = client.ip(address)
        
        # Convert dataclass to dict
        output = asdict(result)
        
        if output_json:
            # Compact JSON for piping/processing
            click.echo(json.dumps(output, ensure_ascii=False))
        else:
            # Pretty formatted JSON for human reading
            click.echo(json.dumps(output, indent=4, ensure_ascii=False))
            
    except FocsecError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except KeyboardInterrupt:
        click.echo("\nInterrupted", err=True)
        sys.exit(130)
    except Exception as e:
        click.echo(f"Unexpected error: {e}", err=True)
        sys.exit(1)


def main():
    """Entry point for the CLI."""
    cli(obj={})


if __name__ == "__main__":
    main()
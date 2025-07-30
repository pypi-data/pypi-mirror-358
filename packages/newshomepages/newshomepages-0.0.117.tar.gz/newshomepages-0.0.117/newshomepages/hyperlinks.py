"""Save all of a site's hyperlinks as JSON."""

from __future__ import annotations

from pathlib import Path

import click
from playwright.sync_api import sync_playwright
from playwright.sync_api._generated import BrowserContext
from retry import retry
from rich import print

from . import utils


@click.command()
@click.argument("handle")
@click.option("-o", "--output-dir", "output_dir", default="./")
@click.option("-v", "--verbose", "verbose", default=False, is_flag=True)
def cli(handle, output_dir="./", verbose=False):
    """Save all of a site's hyperlinks as JSON."""
    # Get the site
    site = utils.get_site(handle)

    # Start the browser
    with sync_playwright() as p:
        # Open a browser
        context = utils._load_persistent_context(
            p,
            verbose=verbose,
            adguard=site["no_adguard"] is not True,
        )

        # Get lnks
        link_list = _get_links(context, site, verbose=verbose)

        # Close the browser
        context.close()

    # Write out the data
    output_path = Path(output_dir) / f"{site['handle']}.hyperlinks.json"
    utils.write_json(link_list, output_path)


@retry(tries=3, delay=5, backoff=2)
def _get_links(
    context: BrowserContext, data: dict, verbose: bool = False
) -> list[dict]:
    """Get all hyperlinks from a page.

    Args:
        context (BrowserContext): The browser context to use.
        data (dict): The site data.
        verbose (bool, optional): Whether to print verbose output. Defaults to False.

    Returns:
        list[dict]: A list of dictionaries with link data.
    """
    # Open a page like in screenshot()
    page = utils._load_new_page_disable_javascript(
        context=context,
        url=data["url"],
        handle=data["handle"],
        verbose=verbose,
    )

    # Parse out the data we want to keep in JavaScript
    if verbose:
        print("🔗 Parsing hyperlinks")
    link_list = page.evaluate(
        """
        Array.from(
        document.getElementsByTagName("a"))             // get all links
            .map((a) => [a, a.getBoundingClientRect()]) // make an Array [link, bbox]
            .map(([a, rect]) => ({                      // transform to a Object
                "text": a.text,
                "url": a.href,
                "top": rect.top,
                "left": rect.left,
                "bottom": rect.bottom,
                "right": rect.right
            })
        )
        """
    )
    data_list = [item for item in link_list if item["url"]]
    if verbose:
        print(f"{len(data_list)} hyperlinks found")

    # Close the page
    page.close()

    # Verify we actually got something back
    assert len(data_list) > 0, "No hyperlinks found"

    # Return the result
    return data_list


if __name__ == "__main__":
    cli()

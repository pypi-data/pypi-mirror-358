import click

from sciop_scraping.cli.api import sciop_api
from sciop_scraping.quests.chronicling.cli import chronicling_america


@click.group("sciop-scrape")
def cli() -> None:
    """Distributed scraping with sciop :)"""
    pass


cli.add_command(chronicling_america)
cli.add_command(sciop_api)

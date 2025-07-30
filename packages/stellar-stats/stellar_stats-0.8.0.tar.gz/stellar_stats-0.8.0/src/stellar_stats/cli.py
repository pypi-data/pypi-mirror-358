import os

import click
import streamlit.web.bootstrap as bootstrap
from streamlit.web.cli import configurator_options

from .config import load_config
from .data import load_returns
from .utils import generate_investors_from_cashflow


def run_streamlit(file_path, args=None, **kwargs):
    """
    Run a Streamlit app with proper context initialization
    """
    if args is None:
        args = []

    # Initialize bootstrap configuration
    bootstrap.load_config_options(flag_options=kwargs)

    # Run the Streamlit app
    bootstrap.run(file_path, is_hello=False, args=args, flag_options=kwargs)


@click.group()
def main():
    """CLI tool for running Streamlit app"""
    pass


@main.command()
@click.argument("args", nargs=-1)
@configurator_options
def run(args, **kwargs):
    """Run the Streamlit application"""
    dirname = os.path.dirname(__file__)
    filepath = os.path.join(dirname, "app.py")
    run_streamlit(filepath, args=args, **kwargs)


@main.command()
@click.argument("account_name")
@click.option("--investor-name", required=True, help="Name of the investor")
@click.option(
    "--rebate-threshold",
    default=0.01,
    type=float,
    help="Threshold below which cashflows are considered rebates",
)
@click.option(
    "--output",
    "-o",
    help="Output file path (default: investors.csv in account directory)",
)
def gen_investors(account_name, investor_name, rebate_threshold, output):
    """Generate investors.csv for specified account from cashflow data"""
    try:
        # Load configuration
        cfg, pro, accounts, datadirs, index_funcs = load_config()

        # Check if account exists
        if account_name not in accounts:
            click.echo(
                f"Account '{account_name}' not found. Available accounts: {', '.join(accounts)}",
                err=True,
            )
            raise click.Abort()

        # Load returns data for the account
        returns = load_returns([account_name], datadirs)

        # Generate investors data
        investors_df = generate_investors_from_cashflow(
            returns, investor_name, account_name, rebate_threshold
        )

        # Determine output file path
        if output is None:
            output = os.path.join(datadirs[account_name], "investors.csv")

        # Save to CSV
        investors_df.to_csv(output, index=False)
        click.echo(
            f"Generated investors.csv with {len(investors_df)} entries at: {output}"
        )

    except Exception as e:
        click.echo(f"Error generating investors.csv: {str(e)}", err=True)
        raise click.Abort()


if __name__ == "__main__":
    main()

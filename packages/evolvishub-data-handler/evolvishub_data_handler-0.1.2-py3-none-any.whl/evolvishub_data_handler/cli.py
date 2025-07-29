"""Command-line interface for the data handler."""
import click
import signal
import sys
from loguru import logger

from .cdc_handler import CDCHandler
from .config_loader import load_config
from .config import SyncMode


@click.group()
def cli():
    """Data handler CLI."""
    pass


@cli.command()
@click.option("--config", "-c", required=True, help="Path to configuration file")
@click.option("--mode", "-m",
              type=click.Choice([mode.value for mode in SyncMode]),
              help="Sync mode (overrides config file setting)")
@click.option("--cron", help="Cron expression for scheduled sync (overrides config file setting)")
@click.option("--log-level", "-l",
              type=click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR']),
              default='INFO', help="Log level")
@click.option("--log-file", help="Log file path")
def run(config, mode, cron, log_level, log_file):
    """Run data synchronization with specified mode."""
    try:
        # Configure logging
        logger.remove()  # Remove default handler
        logger.add(sys.stderr, level=log_level)
        if log_file:
            logger.add(log_file, level=log_level, rotation="10 MB", retention="10 days")

        # Load configuration
        config_data = load_config(config)

        # Override sync mode if specified
        if mode:
            config_data.sync.mode = SyncMode(mode)

        # Override cron expression if specified
        if cron:
            config_data.sync.cron_expression = cron
            config_data.sync.mode = SyncMode.CRON

        # Create handler
        handler = CDCHandler(config_data)

        # Set up signal handlers for graceful shutdown
        def signal_handler(signum, frame):
            logger.info("Received interrupt signal, stopping...")
            handler.stop()
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        # Run based on mode
        logger.info(f"Starting sync in {config_data.sync.mode.value} mode...")
        handler.run()

    except Exception as e:
        logger.error(f"Error during sync: {str(e)}")
        raise click.ClickException(str(e))


@cli.command()
@click.option("--config", "-c", required=True, help="Path to configuration file")
@click.option("--log-level", "-l",
              type=click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR']),
              default='INFO', help="Log level")
@click.option("--log-file", help="Log file path")
def sync(config, log_level, log_file):
    """Run a one-time sync (legacy command)."""
    try:
        # Configure logging
        logger.remove()
        logger.add(sys.stderr, level=log_level)
        if log_file:
            logger.add(log_file, level=log_level, rotation="10 MB", retention="10 days")

        config_data = load_config(config)
        config_data.sync.mode = SyncMode.ONE_TIME
        handler = CDCHandler(config_data)
        handler.sync()
    except Exception as e:
        logger.error(f"Error during sync: {str(e)}")
        raise click.ClickException(str(e))


@cli.command()
@click.option("--config", "-c", required=True, help="Path to configuration file")
@click.option("--log-level", "-l",
              type=click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR']),
              default='INFO', help="Log level")
@click.option("--log-file", help="Log file path")
def continuous_sync(config, log_level, log_file):
    """Run continuous sync (legacy command)."""
    try:
        # Configure logging
        logger.remove()
        logger.add(sys.stderr, level=log_level)
        if log_file:
            logger.add(log_file, level=log_level, rotation="10 MB", retention="10 days")

        config_data = load_config(config)
        config_data.sync.mode = SyncMode.CONTINUOUS
        handler = CDCHandler(config_data)

        # Set up signal handlers for graceful shutdown
        def signal_handler(signum, frame):
            logger.info("Received interrupt signal, stopping...")
            handler.stop()
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        handler.run_continuous()
    except Exception as e:
        logger.error(f"Error during continuous sync: {str(e)}")
        raise click.ClickException(str(e))


def main():
    """Entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()
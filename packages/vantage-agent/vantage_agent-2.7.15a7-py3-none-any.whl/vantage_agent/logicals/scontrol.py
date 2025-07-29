"""Core module for defining operations related to the scontrol command."""

import asyncio
import subprocess

from jsondiff import diff
from loguru import logger

from vantage_agent.helpers import (
    load_cached_dict,
    parse_slurm_config,
    parse_slurm_nodes,
    parse_slurm_partitions,
    parse_slurm_queue,
)
from vantage_agent.logicals.vantage_api import (
    upload_slurm_config,
    upload_slurm_nodes,
    upload_slurm_partitions,
    upload_slurm_queue,
)
from vantage_agent.settings import SETTINGS


def upload_scontrol_config():
    """Upload Slurm's configuration to the Vantage API."""
    logger.debug("Getting Slurm's configuration")
    result = subprocess.run([SETTINGS.SCONTROL_PATH, "show", "config"], stdout=subprocess.PIPE, text=True)
    output = result.stdout

    logger.debug("Parsing Slurm's configuration")
    current_config = parse_slurm_config(output)

    logger.debug("Loading cached Slurm's configuration")
    cached_config = load_cached_dict("slurm_config.json")

    logger.debug("Computing difference between cached and current configurations")
    diff_config = diff(cached_config, current_config, marshal=True)

    if diff_config:
        logger.debug("Detected changes in Slurm's configuration. Uploading to the API...")
        asyncio.run(upload_slurm_config(diff_config))
    else:
        logger.debug("No changes detected in Slurm's configuration.")


def upload_scontrol_partition():
    """Upload Slurm's partitions information to the Vantage API."""
    logger.debug("Getting Slurm's partition information")
    result = subprocess.run([SETTINGS.SCONTROL_PATH, "show", "partition"], stdout=subprocess.PIPE, text=True)
    output = result.stdout

    logger.debug("Parsing Slurm's partitions")
    current_config = parse_slurm_partitions(output)

    logger.debug("Loading cached Slurm's partitions")
    cached_config = load_cached_dict("slurm_partitions.json")

    logger.debug("Computing difference between cached and current partitions")
    diff_partitions = diff(cached_config, current_config, marshal=True)

    if diff_partitions:
        logger.debug("Detected changes in Slurm's configuration. Uploading to the API...")
        asyncio.run(upload_slurm_partitions(diff_partitions))
    else:
        logger.debug("No changes detected in Slurm's partitions.")


def upload_scontrol_queue():
    """Upload Slurm's queues information to the Vantage API."""
    logger.debug("Getting Slurm's queue information")
    result = subprocess.run([SETTINGS.SQUEUE_PATH, "-o", f"%all", "-h"], stdout=subprocess.PIPE, text=True)
    output = result.stdout

    logger.debug("Parsing Slurm's queue")
    current_config = parse_slurm_queue(output)

    logger.debug("Loading cached Slurm's queue")
    cached_config = load_cached_dict("slurm_queue.json")

    logger.debug("Computing difference between cached and current queue")
    diff_queue = diff(cached_config, current_config, marshal=True)

    if diff_queue:
        logger.debug("Detected changes in Slurm's configuration. Uploading to the API...")
        asyncio.run(upload_slurm_queue(diff_queue))
    else:
        logger.debug("No changes detected in Slurm's queue.")


def upload_scontrol_node():
    """Upload Slurm's nodes information to the Vantage API."""
    logger.debug("Getting Slurm's node information")
    result = subprocess.run([SETTINGS.SCONTROL_PATH, "show", "node"], stdout=subprocess.PIPE, text=True)
    output = result.stdout

    logger.debug("Parsing Slurm's nodes")
    current_config = parse_slurm_nodes(output)

    logger.debug("Loading cached Slurm's nodes")
    cached_config = load_cached_dict("slurm_nodes.json")

    logger.debug("Computing difference between cached and current nodes")
    diff_nodes = diff(cached_config, current_config, marshal=True)

    if diff_nodes:
        logger.debug("Detected changes in Slurm's nodes. Uploading to the API...")
        asyncio.run(upload_slurm_nodes(diff_nodes))
    else:
        logger.debug("No changes detected in Slurm's nodes.")
    pass

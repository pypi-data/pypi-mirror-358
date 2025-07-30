"""
CachedParallelProcessor: A utility for parallel processing with caching support.

This module provides efficient parallel processing of string inputs with automatic
caching to avoid reprocessing identical inputs.
"""

import hashlib
import json
import logging
import os.path
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, Optional

from tqdm import tqdm

# Configure logging
logger = logging.getLogger(__name__)


def get_string_hash(s: str) -> str:
    """
    Generate MD5 hash for a string to use as cache key.

    Args:
        s: Input string to hash

    Returns:
        MD5 hash as hexadecimal string
    """
    # Strip whitespace to ensure consistent hashing
    return hashlib.md5(s.strip().encode("utf-8")).hexdigest()


class CachedParallelProcessor:
    """
    A parallel processor with caching capabilities for string processing tasks.

    This class enables efficient processing of large datasets by:
    - Caching results to avoid reprocessing identical inputs
    - Processing inputs in parallel using thread pool
    - Providing retry mechanism for failed processing attempts
    - Showing progress with tqdm progress bar

    Attributes:
        process_func: Function to process each input string
        max_retry_cnt: Maximum number of retry attempts for failed processing
        cache_filename: Path to cache file (JSONL format)
        cache_file_free: If True, use in-memory cache only
    """

    def __init__(
        self,
        process_func: Callable[[str], str],
        max_retry_cnt: int = 3,
        cache_filename: Optional[str] = None,
        cache_file_free: bool = False,
    ):
        """
        Initialize the CachedParallelProcessor.

        Args:
            process_func: Function that takes a string and returns processed string
            max_retry_cnt: Maximum retry attempts for failed processing (default: 3)
            cache_filename: Path to cache file (default: "cache.jsonl")
            cache_file_free: If True, use in-memory cache only (default: False)
        """
        self.process_func = process_func
        self.max_retry_cnt = max_retry_cnt

        # Set default cache filename if not provided
        if cache_filename is None:
            logger.warning(
                "cache_filename is not set, using default cache filename: cache.jsonl"
            )
            cache_filename = "cache.jsonl"

        self.cache_dic = None  # Will store cache data as {hash: result}
        self.dynamic_cache_set = None  # Set of hashes for O(1) lookup
        self.cache_filename = cache_filename
        self.cache_file_free = cache_file_free

        logger.info(
            f"Initialized CachedParallelProcessor with cache file: {cache_filename}"
        )
        logger.info(
            f"Max retry count: {max_retry_cnt}, File-free mode: {cache_file_free}"
        )

    def read_cache(self) -> dict:
        """
        Read cache from file or return in-memory cache.

        Returns:
            Dictionary mapping hash strings to results
        """
        # Return in-memory cache if file-free mode is enabled
        if self.cache_file_free:
            logger.debug("Using in-memory cache (file-free mode)")
            return self.cache_dic or {}

        # Create cache file if it doesn't exist
        if not os.path.exists(self.cache_filename):
            logger.info(f"Creating new cache file: {self.cache_filename}")
            open(self.cache_filename, "a").close()
            return {}

        # Read existing cache file
        logger.info(f"Reading cache from: {self.cache_filename}")
        try:
            with open(self.cache_filename) as f:
                lines = [json.loads(line) for line in f.readlines()]
                cache_dic = {item["shash"]: item["result"] for item in lines}
                logger.info(f"Loaded {len(cache_dic)} cached items")
                return cache_dic
        except Exception as e:
            logger.error(f"Error reading cache file: {e}")
            return {}

    def append_cache(self, data: dict) -> None:
        """
        Append new result to cache (file or memory).

        Args:
            data: Dictionary with 'shash' and 'result' keys
        """
        # Always update in-memory cache for fast lookup
        self.dynamic_cache_set.add(data["shash"])

        if self.cache_file_free:
            # Only update in-memory cache
            self.cache_dic[data["shash"]] = data["result"]
            logger.debug(f"Added to in-memory cache: {data['shash'][:8]}...")
            return

        # Write to cache file
        try:
            with open(self.cache_filename, "a+") as f:
                f.write(json.dumps(data) + "\n")
            logger.debug(f"Written to cache file: {data['shash'][:8]}...")
        except Exception as e:
            logger.error(f"Error writing to cache file: {e}")

    def process_one_sample(self, input_str: str) -> None:
        """
        Process a single input string with retry logic.

        Args:
            input_str: Input string to process
        """
        # Skip non-string inputs
        if not isinstance(input_str, str):
            logger.warning(f"Skipping non-string input: {type(input_str)}")
            return

        # Generate hash for caching
        shash = get_string_hash(input_str)

        # Skip if already in cache
        if shash in self.dynamic_cache_set:
            logger.debug(f"Cache hit for hash: {shash[:8]}...")
            return

        # Try processing with retry logic
        for attempt in range(self.max_retry_cnt):
            try:
                logger.debug(
                    f"Processing attempt {attempt + 1}/{self.max_retry_cnt}: "
                    f"{input_str[:50]}..."
                )
                result = self.process_func(input_str)

                # Skip if processing returned None
                if result is None:
                    logger.warning(
                        f"Process function returned None for: {input_str[:50]}..."
                    )
                    continue

                # Cache successful result
                self.append_cache({"shash": shash, "result": result})
                logger.debug(f"Successfully processed: {input_str[:50]}...")
                break

            except Exception as e:
                logger.warning(
                    f"Attempt {attempt + 1} failed for '{input_str[:50]}...': "
                    f"{type(e).__name__}"
                )
                if attempt == self.max_retry_cnt - 1:
                    logger.error(f"All attempts failed for: {input_str[:50]}...")

    def run(self, input_lis: list[str], num_threads: int = 10) -> None:
        """
        Process a list of inputs in parallel.

        Args:
            input_lis: List of input strings to process
            num_threads: Number of parallel threads (default: 10)
        """
        # Load existing cache
        self.cache_dic = self.read_cache()
        self.dynamic_cache_set = set(self.cache_dic.keys())

        # Calculate cache statistics
        total_inputs = len(input_lis)
        unique_inputs = len(
            set(get_string_hash(s) for s in input_lis if isinstance(s, str))
        )
        already_cached = sum(
            1
            for s in input_lis
            if isinstance(s, str) and get_string_hash(s) in self.dynamic_cache_set
        )

        print(f"\n{'=' * 50}")
        print(f"Starting parallel processing with {num_threads} threads")
        print(f"Total inputs: {total_inputs:,}")
        print(f"Unique inputs: {unique_inputs:,}")
        print(f"Already cached: {already_cached:,}")
        print(f"To be processed: {unique_inputs - already_cached:,}")
        print(f"{'=' * 50}\n")

        # Process inputs in parallel with progress bar
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            list(
                tqdm(
                    executor.map(self.process_one_sample, input_lis),
                    total=len(input_lis),
                    desc="Processing",
                    unit="item",
                )
            )

        print("\nProcessing completed!")
        logger.info(f"Completed processing {total_inputs} inputs")

    def get_result(self, input_lis: list[str]) -> list[str]:
        """
        Retrieve cached results for a list of inputs.

        Args:
            input_lis: List of input strings

        Returns:
            List of results (empty string for failed/missing items)
        """
        # Reload cache to get latest results
        self.cache_dic = self.read_cache()

        # Retrieve results, using empty string for missing items
        result_lis = [
            self.cache_dic.get(get_string_hash(input_str), "")
            for input_str in input_lis
        ]

        # Calculate statistics
        err_cnt = result_lis.count("")
        success_cnt = len(result_lis) - err_cnt

        print(f"\n{'=' * 50}")
        print("Results Summary:")
        print(f"  Total requested: {len(result_lis):,}")
        print(f"  Successfully retrieved: {success_cnt:,}")
        print(f"  Failed/Missing: {err_cnt:,}")
        print(f"  Success rate: {success_cnt / len(result_lis) * 100:.1f}%")
        print(f"{'=' * 50}\n")

        logger.info(
            f"Retrieved {success_cnt} successful results "
            f"out of {len(result_lis)} requests"
        )

        return result_lis

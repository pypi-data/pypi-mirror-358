#!/usr/bin/env python3
"""
pyRNAither - A Python package for RNAi data analysis

This module provides the main entry point for the pyRNAither package.
"""

import argparse
import sys
from typing import Optional, List, Dict, Any, Union
import pandas as pd
# Import local logger from the logging module
from pyrnaither.logging import logger

logger = logger.setup_logger()




# Import package modules
try:
    from pyrnaither.data.datasets import generate_dataset_file
    from pyrnaither.normalization import normalizer
    from pyrnaither.stats import qc as stats_qc
    from pyrnaither.stats import stattests as stats_tests
    from pyrnaither.visualization import visualizer
    from pyrnaither.utils import utilities
    from pyrnaither.pipeline import workflow

    logger.info("Successfully imported all package modules")
except ImportError as e:
    logger.error(f"Failed to import required modules: {e}")
    raise


class PyRNAither:
    """
    Main class for the pyRNAither package.
    Provides a high-level interface for RNAi data analysis workflows.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the PyRNAither instance.

        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.data = None
        self.metadata = None
        logger.info("Initialized PyRNAither instance", exc_info=True)

    def load_data(self, file_path: str, **kwargs) -> None:
        """
        Load data from a file.

        Args:
            file_path: Path to the input file
            **kwargs: Additional arguments passed to the loader
        """
        try:
            self.data, self.metadata = generate_dataset_file (file_path, **kwargs)
            logger.info(f"Successfully loaded data from {file_path}")
        except Exception as e:
            logger.error(f"Failed to load data: {e}", exc_info=True)
            raise

    def normalize(self, method: str = "quantile", **kwargs) -> None:
        """
        Normalize the loaded data.

        Args:
            method: Normalization method to use
            **kwargs: Additional arguments for the normalization function
        """
        if self.data is None:
            logger.error("No data loaded. Please load data first.")
            raise ValueError("No data available for normalization")

        try:
            #self.data = normalizer.normalize_data(self.data, method=method, **kwargs)
            logger.info(f"Applied {method} normalization to the data")
        except Exception as e:
            logger.error(f"Normalization failed: {e}", exc_info=True)
            raise

    def run_quality_control(self, **kwargs) -> Dict[str, Any]:
        """
        Run quality control analysis on the data.

        Args:
            **kwargs: Additional arguments for QC functions

        Returns:
            Dictionary containing QC results
        """
        if self.data is None:
            logger.error("No data loaded. Please load data first.")
            raise ValueError("No data available for quality control")

        try:
            qc_results = {}
            # Add QC functions here
            logger.info("Quality control analysis completed")
            return qc_results
        except Exception as e:
            logger.error(f"Quality control failed: {e}", exc_info=True)
            raise

    def visualize(self, plot_type: str = "plate", **kwargs) -> None:
        """
        Generate visualizations of the data.

        Args:
            plot_type: Type of plot to generate
            **kwargs: Additional arguments for visualization functions
        """
        if self.data is None:
            logger.error("No data loaded. Please load data first.")
            raise ValueError("No data available for visualization")

        try:
            if plot_type == "plate":
                visualizer.plot_96_well_plate_with_intensity(data=self.data, **kwargs)
            # Add more plot types as needed
            logger.info(f"Generated {plot_type} visualization")
        except Exception as e:
            logger.error(f"Visualization failed: {e}", exc_info=True)
            raise


def parse_arguments() -> argparse.Namespace:
    """
    Parse command line arguments.

    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="pyRNAither - RNAi data analysis tool",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "-i", "--input", type=str, required=True, help="Input file path"
    )
    parser.add_argument(
        "-o", "--output", type=str, default="output", help="Output file prefix"
    )

    parser.add_argument(
        "--normalize", action="store_true", help="Perform data normalization"
    )
    parser.add_argument(
        "--qc", action="store_true", help="Run quality control analysis"
    )
    parser.add_argument(
        "--visualize", action="store_true", help="Generate visualizations"
    )

    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose output"
    )

    return parser.parse_args()


def main() -> None:
    """
    Main entry point for the command line interface.
    """
    try:
        args = parse_arguments()

        if args.verbose:
            logger.getLogger().setLevel(logger.DEBUG)

        logger.info("Starting pyRNAither analysis")

        analyzer = PyRNAither()

        analyzer.load_data(args.input)
        if args.normalize:
            logger.info("Running normalization...")
            analyzer.normalize()

        if args.qc:
            logger.info("Running quality control...")
            analyzer.run_quality_control()

        if args.visualize:
            logger.info("Generating visualizations...")
            analyzer.visualize()

        logger.info("Analysis completed successfully")

    except Exception as e:
        logger.error(f"An error occurred: {e}", exc_info=True)
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Analysis interrupted by user")
        sys.exit(0)


if __name__ == "__main__":
    main()

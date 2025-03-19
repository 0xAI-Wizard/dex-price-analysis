#!/usr/bin/env python3
"""
Test script for the price analysis application.
This script validates the functionality of key components without making actual API calls.
"""

import os
import sys
import unittest
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import jinja2
import logging

# Configure basic logging for tests
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("test_app")

# Import functions from price_analysis
try:
    from price_analysis import (
        find_arbitrage_opportunities,
        generate_visualizations,
        generate_html_report,
        save_results,
        VIZ_DIR,
        REPORT_DIR,
        CACHE_DIR,
    )

    logger.info("Successfully imported modules from price_analysis.py")
except ImportError as e:
    logger.error(f"Failed to import from price_analysis.py: {str(e)}")
    logger.error("Make sure price_analysis.py is in the same directory")
    sys.exit(1)


class TestPriceAnalysis(unittest.TestCase):
    """Test cases for price analysis functionality"""

    def setUp(self):
        """Set up test fixtures"""
        # Create test directories if they don't exist
        os.makedirs(CACHE_DIR, exist_ok=True)
        os.makedirs(VIZ_DIR, exist_ok=True)
        os.makedirs(REPORT_DIR, exist_ok=True)

        # Create sample data for testing
        self.sample_data = pd.DataFrame(
            {
                "token": [
                    "wrapped-bitcoin",
                    "wrapped-bitcoin",
                    "ethereum",
                    "ethereum",
                    "tether",
                ],
                "network": ["ethereum", "arbitrum", "ethereum", "optimism", "ethereum"],
                "dex": [
                    "uniswap-v3",
                    "uniswap-v3",
                    "balancer",
                    "velodrome",
                    "sushiswap",
                ],
                "price_usd": [65000.5, 64900.75, 3000.25, 3025.5, 1.001],
                "reference_price": [65000.0, 65000.0, 3010.0, 3010.0, 1.000],
                "price_difference_percent": [0.0077, -0.153, -0.324, 0.515, 0.1],
                "timestamp": [datetime.utcnow().isoformat()] * 5,
            }
        )

    def test_find_arbitrage_opportunities(self):
        """Test finding arbitrage opportunities"""
        logger.info("Testing arbitrage opportunity detection")

        # Create data with clear arbitrage opportunity
        arb_data = pd.DataFrame(
            {
                "token": ["ethereum", "ethereum"],
                "network": ["ethereum", "optimism"],
                "dex": ["uniswap-v3", "velodrome"],
                "price_usd": [3000.0, 3045.0],  # 1.5% difference
                "reference_price": [3020.0, 3020.0],
                "price_difference_percent": [-0.662, 0.828],
                "timestamp": [datetime.utcnow().isoformat()] * 2,
            }
        )

        # Test with threshold that should find opportunities
        opportunities = find_arbitrage_opportunities(arb_data, min_profit_percent=0.5)
        self.assertFalse(opportunities.empty, "Should find arbitrage opportunities")
        self.assertEqual(len(opportunities), 1, "Should find exactly one opportunity")

        # Test with threshold that should not find opportunities
        opportunities = find_arbitrage_opportunities(arb_data, min_profit_percent=2.0)
        self.assertTrue(
            opportunities.empty,
            "Should not find arbitrage opportunities with high threshold",
        )

    def test_generate_visualizations(self):
        """Test visualization generation"""
        logger.info("Testing visualization generation")

        # Generate visualizations from sample data
        try:
            generate_visualizations(self.sample_data)

            # Check if files were created
            expected_files = [
                os.path.join(VIZ_DIR, "wrapped-bitcoin_price_comparison.png"),
                os.path.join(VIZ_DIR, "ethereum_price_comparison.png"),
                os.path.join(VIZ_DIR, "price_differences_boxplot.png"),
            ]

            for file_path in expected_files:
                self.assertTrue(
                    os.path.exists(file_path),
                    f"Missing expected visualization: {file_path}",
                )

        except Exception as e:
            self.fail(f"Visualization generation failed with error: {str(e)}")

    def test_generate_html_report(self):
        """Test HTML report generation"""
        logger.info("Testing HTML report generation")

        # Create sample arbitrage data
        arb_data = pd.DataFrame(
            {
                "token": ["ethereum"],
                "buy_network": ["ethereum"],
                "buy_dex": ["uniswap-v3"],
                "buy_price": [3000.0],
                "sell_network": ["optimism"],
                "sell_dex": ["velodrome"],
                "sell_price": [3045.0],
                "profit_percent": [1.5],
                "timestamp": [datetime.utcnow().isoformat()],
            }
        )

        # Generate report
        try:
            report_path = generate_html_report(self.sample_data, arb_data)
            self.assertTrue(
                os.path.exists(report_path), f"Report not generated at {report_path}"
            )

            # Check file size to ensure it's not empty
            self.assertGreater(
                os.path.getsize(report_path),
                1000,
                "Report file too small, may be empty",
            )

        except Exception as e:
            self.fail(f"HTML report generation failed with error: {str(e)}")

    def test_save_results(self):
        """Test saving results to CSV"""
        logger.info("Testing results saving")

        from price_analysis import RESULTS_FILE

        # Save results
        try:
            save_results(self.sample_data)
            self.assertTrue(
                os.path.exists(RESULTS_FILE),
                f"Results file not created at {RESULTS_FILE}",
            )

            # Read back and verify
            read_data = pd.read_csv(RESULTS_FILE)
            self.assertEqual(
                len(read_data), len(self.sample_data), "Saved data has different length"
            )

        except Exception as e:
            self.fail(f"Saving results failed with error: {str(e)}")

    def tearDown(self):
        """Clean up test files"""
        # We're not deleting test files here to allow inspection
        # In a real test environment, you might want to clean up
        pass


def quick_dependency_check():
    """Verify required Python packages are available"""
    logger.info("Checking dependencies...")

    try:
        # Test pandas
        df = pd.DataFrame({"test": [1, 2, 3]})
        logger.info("✓ pandas working")

        # Test matplotlib/seaborn
        fig, ax = plt.subplots()
        plt.close(fig)
        logger.info("✓ matplotlib working")

        # Test jinja2
        template = jinja2.Template("Hello {{ name }}!")
        template.render(name="World")
        logger.info("✓ jinja2 working")

        return True
    except Exception as e:
        logger.error(f"Dependency check failed: {str(e)}")
        return False


if __name__ == "__main__":
    logger.info("Starting price analysis application tests")

    # Check dependencies first
    if not quick_dependency_check():
        logger.error("Dependency check failed - please install required packages")
        sys.exit(1)

    # Run the tests
    unittest.main(argv=["first-arg-is-ignored"], exit=False)
    logger.info("All tests completed")

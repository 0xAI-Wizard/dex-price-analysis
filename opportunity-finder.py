# Additions to price_analysis.py

import matplotlib.pyplot as plt
import seaborn as sns
from jinja2 import Template
from datetime import datetime
import os

# Directory constants
VIZ_DIR = "visualizations"
REPORT_DIR = "reports"
os.makedirs(VIZ_DIR, exist_ok=True)
os.makedirs(REPORT_DIR, exist_ok=True)


def find_arbitrage_opportunities(
    df: pd.DataFrame, min_profit_percent: float = 0.5
) -> pd.DataFrame:
    """
    Find arbitrage opportunities across DEXs and networks.

    Args:
        df: DataFrame with price analysis results
        min_profit_percent: Minimum profit percentage to consider

    Returns:
        DataFrame with arbitrage opportunities
    """
    opportunities = []

    for token in df["token"].unique():
        token_data = df[df["token"] == token].copy()

        # Find min and max prices for each token
        min_price_row = token_data.loc[token_data["price_usd"].idxmin()]
        max_price_row = token_data.loc[token_data["price_usd"].idxmax()]

        price_diff_percent = (
            (max_price_row["price_usd"] - min_price_row["price_usd"])
            / min_price_row["price_usd"]
            * 100
        )

        if price_diff_percent >= min_profit_percent:
            opportunities.append(
                {
                    "token": token,
                    "buy_network": min_price_row["network"],
                    "buy_dex": min_price_row["dex"],
                    "buy_price": min_price_row["price_usd"],
                    "sell_network": max_price_row["network"],
                    "sell_dex": max_price_row["dex"],
                    "sell_price": max_price_row["price_usd"],
                    "profit_percent": price_diff_percent,
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )

    return pd.DataFrame(opportunities)


def generate_visualizations(df: pd.DataFrame) -> None:
    """
    Generate visualizations for price analysis results.
    """
    # Set style
    plt.style.use("seaborn")

    # 1. Price comparison plots for each token
    for token in df["token"].unique():
        token_data = df[df["token"] == token]

        plt.figure(figsize=(12, 6))
        sns.barplot(data=token_data, x="dex", y="price_usd", hue="network")
        plt.title(f"{token} Prices Across DEXs and Networks")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(os.path.join(VIZ_DIR, f"{token}_price_comparison.png"))
        plt.close()

    # 2. Price differences boxplot
    plt.figure(figsize=(10, 6))
    sns.boxplot(data=df, x="token", y="price_difference_percent")
    plt.title("Price Differences Distribution by Token")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(VIZ_DIR, "price_differences_boxplot.png"))
    plt.close()


def generate_html_report(
    price_data: pd.DataFrame, arb_opportunities: pd.DataFrame
) -> str:
    """
    Generate an HTML report with analysis results.

    Returns:
        str: Path to generated report
    """
    template_str = """
    <html>
    <head>
        <title>Price Analysis Report</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            table { border-collapse: collapse; width: 100%; margin: 20px 0; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background-color: #f5f5f5; }
            .visualization { margin: 20px 0; }
            h2 { color: #333; }
        </style>
    </head>
    <body>
        <h1>Price Analysis Report</h1>
        <p>Generated on: {{ timestamp }}</p>
        
        <h2>Price Analysis Results</h2>
        {{ price_table }}
        
        <h2>Arbitrage Opportunities</h2>
        {{ arb_table }}
        
        <h2>Visualizations</h2>
        <div class="visualization">
            {% for viz in visualizations %}
            <img src="{{ viz }}" style="max-width: 100%; margin: 10px 0;">
            {% endfor %}
        </div>
    </body>
    </html>
    """

    template = Template(template_str)

    # Get list of visualization files
    viz_files = [
        os.path.join("..", VIZ_DIR, f)
        for f in os.listdir(VIZ_DIR)
        if f.endswith(".png")
    ]

    # Generate HTML
    html_content = template.render(
        timestamp=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
        price_table=price_data.to_html(classes="dataframe"),
        arb_table=arb_opportunities.to_html(classes="dataframe"),
        visualizations=viz_files,
    )

    # Save report
    report_path = os.path.join(
        REPORT_DIR,
        f'price_analysis_report_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}.html',
    )
    with open(report_path, "w") as f:
        f.write(html_content)

    return report_path


def main():
    """Main entry point of the script"""
    try:
        logger.info("Starting price analysis")

        # Get price data (using existing functionality)
        df = analyze_prices()

        if df.empty:
            logger.warning("No price data found")
            return

        # Save results
        save_results(df)

        # Find arbitrage opportunities
        opportunities = find_arbitrage_opportunities(df)

        # Generate visualizations
        generate_visualizations(df)

        # Generate report
        report_path = generate_html_report(df, opportunities)

        # Display summary
        print("\nAnalysis Summary:")
        print(
            f"- Analyzed {len(df)} price points across {len(df['token'].unique())} tokens"
        )
        print(f"- Found {len(opportunities)} potential arbitrage opportunities")
        print(f"- Report generated at: {report_path}")
        print("\nArbitrage Opportunities:")
        if not opportunities.empty:
            print(opportunities.to_string(index=False))
        else:
            print("No significant arbitrage opportunities found")

    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
    finally:
        save_cache()


if __name__ == "__main__":
    main()

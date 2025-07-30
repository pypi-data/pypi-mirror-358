#!/usr/bin/env python3
"""
Bitcoin DCA Analysis Terminal Application
Advanced Bitcoin price analysis with DCA recommendations and backtesting
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt
from rich.text import Text
import warnings
import os
import requests
from pathlib import Path

from bitcoin_dca.market_indicators import MarketCycleAnalyzer
import subprocess
import json

from bitcoin_dca.data_loader import DataLoader, LazyFeatureManager

# Version management
from . import __version__ as APP_VERSION
REPO_URL = "https://github.com/obokaman-com/bitcoin-dca"

def get_app_directory():
    """Get the application directory, creating it if needed"""
    app_dir = Path.home() / '.bitcoin-dca'
    app_dir.mkdir(exist_ok=True)

    # Create subdirectories
    (app_dir / 'data').mkdir(exist_ok=True)
    (app_dir / '.cache').mkdir(exist_ok=True)

    return app_dir

def get_default_csv_path():
    """Get the default CSV file path in the app directory"""
    return get_app_directory() / 'data' / 'btc_daily_2010_2025.csv'


def check_for_updates():
    """Check if a newer version is available on PyPI (non-blocking)"""
    try:
        import requests
        from packaging import version

        # Get current version
        current_version = APP_VERSION

        # Quick timeout to avoid blocking
        response = requests.get(
            "https://pypi.org/pypi/bitcoin-dca/json",
            timeout=3
        )

        if response.status_code == 200:
            data = response.json()
            latest_version = data["info"]["version"]

            # Compare versions using packaging library
            if version.parse(latest_version) > version.parse(current_version):
                return True, latest_version

        return False, None
    except:
        # Silently fail - network issues shouldn't block the app
        return False, None


# Lazy imports - only import when needed
_predictor_module = None
_dca_analyzer_module = None
_backtester_module = None

warnings.filterwarnings('ignore')
console = Console()

def get_predictor():
    """Lazy import of predictor module"""
    global _predictor_module
    if _predictor_module is None:
        console.print("[dim]Loading 3-model ensemble (RF + XGBoost + LSTM)...[/dim]")
        from bitcoin_dca.predictor import BitcoinPredictor
        _predictor_module = BitcoinPredictor()
    return _predictor_module

def get_dca_analyzer():
    """Lazy import of DCA analyzer"""
    global _dca_analyzer_module
    if _dca_analyzer_module is None:
        from bitcoin_dca.dca_analyzer import DCAAnalyzer
        _dca_analyzer_module = DCAAnalyzer()
    return _dca_analyzer_module

def get_backtester():
    """Lazy import of backtester"""
    global _backtester_module
    if _backtester_module is None:
        from bitcoin_dca.backtester import DCABacktester
        _backtester_module = DCABacktester()
    return _backtester_module

class BTCAnalyzer:
    def __init__(self, csv_path: str):
        self.csv_path = csv_path
        self.data_loader = DataLoader(csv_path)
        self.feature_manager = LazyFeatureManager(self.data_loader)
        self.basic_data = None

    def download_btc_data(self):
        """Download Bitcoin price data from stooq.com if CSV doesn't exist"""
        url = "https://stooq.com/q/d/l/?s=btcusd&i=d"

        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
            task = progress.add_task("Downloading Bitcoin price data from stooq.com...", total=None)

            try:
                response = requests.get(url, timeout=30)
                response.raise_for_status()

                with open(self.csv_path, 'w', encoding='utf-8') as f:
                    f.write(response.text)

                progress.update(task, description="✅ Bitcoin data downloaded successfully")

                # Verify the downloaded data
                test_df = pd.read_csv(self.csv_path)
                if len(test_df) == 0 or 'Date' not in test_df.columns:
                    raise ValueError("Downloaded data appears to be invalid")
                console.print(f"[green]📊 Downloaded {len(test_df):,} records of Bitcoin price data[/green]")

            except Exception as e:
                progress.update(task, description="❌ Download failed")
                console.print(f"[red]❌ Failed to download Bitcoin data: {str(e)}[/red]")
                raise

    def load_basic_data(self):
        """Load minimal data for fast startup"""
        # Check if CSV file exists
        if not os.path.exists(self.csv_path):
            console.print(f"[yellow]📁 Bitcoin data file not found: {self.csv_path}[/yellow]")
            console.print("[cyan]🌐 Downloading latest Bitcoin price data...[/cyan]")
            self.download_btc_data()

        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
            task = progress.add_task("Quick startup loading...", total=None)

            def update_progress_callback(message):
                progress.update(task, description=message)

            try:
                self.basic_data = self.data_loader.load_basic_data(progress_callback=update_progress_callback)
                progress.update(task, description="✅ Ready! (Features loaded on-demand)")
            except Exception as e:
                progress.update(task, description="❌ Loading failed")
                console.print(f"[red]❌ Error loading data: {str(e)}[/red]")
                raise

    def show_welcome(self):
        """Display welcome screen"""
        welcome_text = Text()
        welcome_text.append("🚀 Bitcoin DCA Analysis Terminal\n", style="bold yellow")
        welcome_text.append("Advanced Bitcoin price analysis and DCA optimization\n", style="cyan")
        welcome_text.append(f"Version: {APP_VERSION}\n", style="dim")
        welcome_text.append(f"Data range: {self.basic_data.index[0].strftime('%Y-%m-%d')} to {self.basic_data.index[-1].strftime('%Y-%m-%d')}\n", style="dim")
        welcome_text.append(f"Total records: {len(self.basic_data):,}\n", style="dim")
        welcome_text.append("⚡ Features computed on-demand for faster startup", style="green")

        console.print(Panel(welcome_text, title="Welcome", border_style="blue"))

        # Check for updates in background
        if self.check_and_offer_update():
            return True  # Signal restart needed

    def show_menu(self):
        """Display main menu"""
        table = Table(title="📊 Analysis Options", show_header=False, box=None)
        table.add_column("Option", style="cyan", width=4)
        table.add_column("Description", style="white")

        table.add_row("1", "📊 Market Overview")
        table.add_row("2", "🔮 Price Prediction")
        table.add_row("3", "📈 DCA Recommendations")
        table.add_row("4", "🧪 DCA Backtesting")
        table.add_row("5", "📥 Update Dataset")
        table.add_row("6", "🧹 Clear Cache")
        table.add_row("q", "❌ Quit")

        console.print(table)

    def handle_prediction(self):
        """Handle price prediction requests with enhanced feedback"""
        console.print("\n[bold cyan]🔮 Bitcoin Price Prediction[/bold cyan]")
        console.print("[dim]Using advanced ensemble model (Random Forest + XGBoost + LSTM)[/dim]\n")
        
        date_str = Prompt.ask("Enter target date (YYYY-MM-DD)")

        try:
            target_date = datetime.strptime(date_str, "%Y-%m-%d").date()

            # Get data with prediction features (lazy loaded)
            data = self.feature_manager.get_data_for_analysis('prediction')
            
            # Show available date range
            console.print(f"\n[dim]Available data range: {data.index[0].strftime('%Y-%m-%d')} to {data.index[-1].strftime('%Y-%m-%d')}[/dim]")
            
            # Ask for custom date range for training
            use_custom_dates = Prompt.ask("Use custom date range for training data?", choices=["y", "n"], default="n")
            
            training_data = data
            date_range_text = "full dataset"
            
            if use_custom_dates == "y":
                start_date, end_date = self._get_date_range(data)
                if start_date and end_date:
                    # Filter data to selected range
                    training_data = data[(data.index >= start_date) & (data.index <= end_date)]
                    date_range_text = f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
                    
                    if len(training_data) < 365:  # Warn if less than 1 year of data
                        console.print(f"[yellow]⚠️  Warning: Training period is only {len(training_data)} days. Prediction may be less reliable.[/yellow]")
                    
                    if len(training_data) < 100:  # Minimum data requirement
                        console.print(f"[red]❌ Error: Training period has only {len(training_data)} days. Minimum 100 days required.[/red]")
                        return

            console.print(f"[cyan]📊 Training models on {date_range_text} ({len(training_data):,} records)[/cyan]")

            predictor = get_predictor()
            prediction = predictor.predict_price(training_data, target_date)

            self.display_prediction_result(target_date, prediction)

        except ValueError:
            console.print("[red]❌ Invalid date format. Please use YYYY-MM-DD[/red]")
        except Exception as e:
            console.print(f"[red]❌ Prediction error: {str(e)}[/red]")

    def handle_dca_recommendations(self):
        """Handle DCA recommendation analysis"""
        console.print("\n[bold cyan]📈 DCA Recommendations[/bold cyan]")

        # Get data with DCA features (lazy loaded)
        data = self.feature_manager.get_data_for_analysis('dca_analysis')

        # Show available date range
        console.print(f"\n[dim]Available data range: {data.index[0].strftime('%Y-%m-%d')} to {data.index[-1].strftime('%Y-%m-%d')}[/dim]")

        # Ask for custom date range
        use_custom_dates = Prompt.ask("Use custom date range for analysis?", choices=["y", "n"], default="n")

        analysis_data = data
        date_range_text = "full dataset"

        if use_custom_dates == "y":
            start_date, end_date = self._get_date_range(data)
            if start_date and end_date:
                # Filter data to selected range
                analysis_data = data[(data.index >= start_date) & (data.index <= end_date)]
                date_range_text = f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"

                if len(analysis_data) < 365:  # Warn if less than 1 year of data
                    console.print(f"[yellow]⚠️  Warning: Analysis period is only {len(analysis_data)} days. Results may be less reliable.[/yellow]")

        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
            task = progress.add_task(f"Analyzing optimal DCA patterns ({date_range_text})...", total=None)
            analyzer = get_dca_analyzer()
            recommendations = analyzer.analyze_optimal_days(analysis_data)
            progress.update(task, description="✅ Analysis completed")

        self.display_dca_recommendations(recommendations, date_range_text)

    def handle_backtesting(self):
        """Handle DCA backtesting"""
        console.print("\n[bold cyan]🧪 DCA Backtesting[/bold cyan]")

        try:
            amount = float(Prompt.ask("Monthly investment amount ($)"))

            console.print("\n[dim]Strategy Options:[/dim]")
            console.print("[dim]• day_of_month: Invest on a specific day each month (e.g., 15th)[/dim]")
            console.print("[dim]• optimal: Invest on the weekday closest to your chosen day of month[/dim]")

            strategy = Prompt.ask("Strategy", choices=["day_of_month", "optimal"], default="day_of_month")

            # Get data for backtesting (lazy loaded)
            data = self.feature_manager.get_data_for_analysis('backtesting')

            # Get date range for backtesting
            console.print(f"\n[dim]Available data range: {data.index[0].strftime('%Y-%m-%d')} to {data.index[-1].strftime('%Y-%m-%d')}[/dim]")

            use_custom_dates = Prompt.ask("Use custom date range for backtesting?", choices=["y", "n"], default="n")

            start_date = None
            end_date = None

            if use_custom_dates == "y":
                start_date_str = Prompt.ask("Start date (YYYY-MM-DD)", default=data.index[100].strftime('%Y-%m-%d'))
                end_date_str = Prompt.ask("End date (YYYY-MM-DD)", default=data.index[-1].strftime('%Y-%m-%d'))

                try:
                    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
                    end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
                except ValueError:
                    console.print("[red]❌ Invalid date format. Using full data range.[/red]")
                    start_date = None
                    end_date = None

            backtester = get_backtester()

            if strategy == "day_of_month":
                day = int(Prompt.ask("Day of month (1-28)", default="15"))
                results = backtester.backtest_monthly_dca(
                    data, amount, day_of_month=day,
                    start_date=start_date, end_date=end_date
                )
            else:  # optimal strategy
                day_of_month = int(Prompt.ask("Target day of month (1-28)", default="15"))
                console.print("\n[dim]Days of week: 0=Monday, 1=Tuesday, 2=Wednesday, 3=Thursday, 4=Friday, 5=Saturday, 6=Sunday[/dim]")
                day_of_week = int(Prompt.ask("Preferred weekday (0-6)", default="2"))
                results = backtester.backtest_optimal_dca(
                    data, amount, day_of_month=day_of_month, day_of_week=day_of_week,
                    start_date=start_date, end_date=end_date
                )

            self.display_backtest_results(results, amount, strategy)

        except ValueError:
            console.print("[red]❌ Invalid input. Please enter valid numbers.[/red]")
        except Exception as e:
            console.print(f"[red]❌ Backtesting error: {str(e)}[/red]")

    def handle_update_dataset(self):
        """Handle dataset update by forcing fresh download"""
        console.print("\n[bold cyan]📥 Update Dataset[/bold cyan]")

        # Show current data info
        try:
            current_data = self.basic_data
            if current_data is not None:
                console.print(f"[dim]Current data: {len(current_data):,} records from {current_data.index[0].strftime('%Y-%m-%d')} to {current_data.index[-1].strftime('%Y-%m-%d')}[/dim]")
        except:
            console.print("[dim]No current data loaded[/dim]")

        # Confirm update
        confirm = Prompt.ask("Download fresh Bitcoin price data from stooq.com?", choices=["y", "n"], default="y")

        if confirm == "y":
            try:
                # Force download by updating the CSV file
                console.print("[cyan]🌐 Downloading latest Bitcoin price data...[/cyan]")
                self.download_btc_data()

                # Clear cache to force reload
                self.data_loader.clear_cache()
                self.feature_manager.feature_cache.clear()

                # Reload basic data
                with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
                    task = progress.add_task("Reloading data...", total=None)
                    self.basic_data = self.data_loader.load_basic_data()
                    progress.update(task, description="✅ Data updated successfully")

                # Show new data info
                console.print(f"[green]✅ Dataset updated: {len(self.basic_data):,} records from {self.basic_data.index[0].strftime('%Y-%m-%d')} to {self.basic_data.index[-1].strftime('%Y-%m-%d')}[/green]")

            except Exception as e:
                console.print(f"[red]❌ Error updating dataset: {str(e)}[/red]")
        else:
            console.print("[yellow]Dataset update cancelled[/yellow]")

    def handle_clear_cache(self):
        """Clear cached features"""
        try:
            self.data_loader.clear_cache()
            self.feature_manager.feature_cache.clear()
            console.print("[green]✅ Cache cleared successfully[/green]")
        except Exception as e:
            console.print(f"[red]❌ Error clearing cache: {str(e)}[/red]")



    def show_market_overview(self):
        """Display market overview with CBBI-style cycle analysis"""
        console.print("\n[bold cyan]📊 Market Overview[/bold cyan]")

        # Get data with basic technical indicators
        data = self.feature_manager.get_data_for_analysis('overview')

        current_price = data['Close'].iloc[-1]
        price_30d_ago = data['Close'].iloc[-30] if len(data) >= 30 else data['Close'].iloc[0]
        price_1y_ago = data['Close'].iloc[-365] if len(data) >= 365 else data['Close'].iloc[0]

        # Calculate market cycle indicators
        cycle_analyzer = MarketCycleAnalyzer()
        cycle_data = cycle_analyzer.calculate_market_cycle_score(data)

        # Basic Market Data Table
        table = Table(title="Bitcoin Market Summary", show_header=True)
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="yellow")

        table.add_row("Current Price", f"${current_price:,.2f}")
        table.add_row("30-Day Change", f"{((current_price / price_30d_ago - 1) * 100):+.2f}%")
        table.add_row("1-Year Change", f"{((current_price / price_1y_ago - 1) * 100):+.2f}%")
        table.add_row("All-Time High", f"${data['High'].max():,.2f}")
        table.add_row("All-Time Low", f"${data['Low'].min():.8f}")

        if 'Volatility' in data.columns:
            recent_volatility = data['Volatility'].iloc[-1] * 100
            table.add_row("Recent Volatility", f"{recent_volatility:.1f}%")

        console.print(table)

        # Market Cycle Analysis Panel
        cycle_score = cycle_data['score']
        phase = cycle_data['phase']
        phase_color = cycle_data['phase_color']
        recommendation = cycle_data['recommendation']
        confidence = cycle_data['confidence']

        # Create market cycle gauge visual
        gauge_length = 20
        filled_length = int(cycle_score / 100 * gauge_length)
        gauge_bar = "█" * filled_length + "░" * (gauge_length - filled_length)

        # Color the gauge based on phase
        if phase_color == "green":
            gauge_display = f"[green]{gauge_bar}[/green]"
        elif phase_color == "yellow":
            gauge_display = f"[yellow]{gauge_bar}[/yellow]"
        else:
            gauge_display = f"[red]{gauge_bar}[/red]"

        cycle_content = f"""[bold]Market Cycle Score:[/bold] {cycle_score}/100
{gauge_display} [{phase_color}]{phase}[/{phase_color}]

[bold]DCA Recommendation:[/bold] {recommendation}
[dim]Confidence: {confidence:.0f}% (based on available indicators)[/dim]"""

        cycle_panel = Panel(
            cycle_content,
            title="🔄 Bitcoin Market Cycle Analysis",
            border_style=phase_color,
            expand=False
        )

        console.print("\n")
        console.print(cycle_panel)

        # Technical Indicators Detail Table (if user wants more detail)
        if cycle_data['indicators']:
            console.print("\n[dim]Detailed Technical Indicators:[/dim]")
            detail_table = Table(show_header=True, header_style="bold cyan")
            detail_table.add_column("Indicator", style="cyan")
            detail_table.add_column("Value", style="yellow")
            detail_table.add_column("Score", style="magenta")

            indicators = cycle_data['indicators']

            if 'mayer_multiple' in indicators:
                detail_table.add_row(
                    "Mayer Multiple",
                    f"{indicators['mayer_multiple']:.2f}",
                    f"{indicators['mayer_score']:.1f}/100"
                )

            if 'two_year_ma_multiple' in indicators:
                detail_table.add_row(
                    "2-Year MA Multiple",
                    f"{indicators['two_year_ma_multiple']:.2f}",
                    f"{indicators['two_year_ma_score']:.1f}/100"
                )

            if 'ath_drawdown' in indicators:
                detail_table.add_row(
                    "ATH Drawdown",
                    f"{indicators['ath_drawdown']:.1f}%",
                    f"{indicators['drawdown_score']:.1f}/100"
                )

            if 'rsi_14' in indicators:
                detail_table.add_row(
                    "RSI (14-day)",
                    f"{indicators['rsi_14']:.1f}",
                    f"{indicators['rsi_score']:.1f}/100"
                )

            if 'puell_multiple' in indicators:
                detail_table.add_row(
                    "Puell Multiple (approx)",
                    f"{indicators['puell_multiple']:.2f}",
                    f"{indicators['puell_score']:.1f}/100"
                )

            console.print(detail_table)

    def check_and_offer_update(self):
        """Check for updates and inform user how to update (non-blocking)"""
        try:
            # Quick, silent background check - no progress spinner to avoid blocking
            has_update, latest_version = check_for_updates()

            if has_update:
                console.print()
                console.print("[yellow]🔄 A newer version is available![/yellow]")
                console.print(f"[dim]Current: v{APP_VERSION}[/dim]")
                console.print(f"[dim]Latest:  v{latest_version}[/dim]")
                console.print()
                console.print("[green]To update, run:[/green]")
                console.print("[bold cyan]pip install --upgrade bitcoin-dca[/bold cyan]")
                console.print()

        except Exception as e:
            # Silently fail version check - don't interrupt user experience
            pass

        return False

    # Display methods (same as original but shorter for brevity)
    def display_prediction_result(self, target_date, prediction):
        # Main prediction table
        table = Table(title=f"🔮 Price Prediction for {target_date}")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="yellow")

        table.add_row("Predicted Price", f"${prediction['price']:,.2f}")
        table.add_row("Confidence", f"{prediction['confidence']:.1%}")
        table.add_row("Model", prediction['model'])
        table.add_row("Features Used", str(prediction.get('features', 'N/A')))

        # Add caching info if available
        if prediction.get('model_details', {}).get('cached'):
            table.add_row("Cache Status", "✅ Loaded from cache (fast)")
        else:
            table.add_row("Cache Status", "🔄 Models trained fresh")

        console.print(table)

        # Individual model predictions table
        if 'individual_predictions' in prediction and len(prediction['individual_predictions']) > 1:
            model_table = Table(title="🤖 Individual Model Predictions")
            model_table.add_column("Model", style="cyan")
            model_table.add_column("Prediction", style="yellow")
            model_table.add_column("Difference", style="green")

            avg_pred = prediction['price']
            for model_name, pred_value in prediction['individual_predictions'].items():
                diff = pred_value - avg_pred
                diff_pct = (diff / avg_pred) * 100
                model_table.add_row(
                    model_name,
                    f"${pred_value:,.2f}",
                    f"{diff:+,.0f} ({diff_pct:+.1f}%)"
                )

            console.print(model_table)

        # Ensemble details
        if prediction.get('ensemble_details'):
            ensemble_info = prediction['ensemble_details']
            if 'rf_weight' in ensemble_info:
                ensemble_text = f"🎯 Ensemble Weighting:\n"
                ensemble_text += f"Random Forest: {ensemble_info['rf_weight']:.1%} (MAE: {ensemble_info['rf_mae']:.0f})\n"
                ensemble_text += f"LSTM Neural Net: {ensemble_info['lstm_weight']:.1%} (MAE: {ensemble_info['lstm_mae']:.0f})\n"
                ensemble_text += f"\n💡 Better performing model gets higher weight"
                console.print(Panel(ensemble_text, title="⚖️ Model Ensemble Details", border_style="blue"))

        # Model training details
        if prediction.get('model_details'):
            details = prediction['model_details']
            detail_text = f"🔧 Model Architecture:\n"
            detail_text += f"LSTM Trained: {'✅ Yes' if details.get('lstm_trained') else '❌ No'}\n"
            if details.get('lstm_trained'):
                detail_text += f"Sequence Length: {details.get('sequence_length', 'N/A')} days\n"
            detail_text += f"Feature Count: {len(details.get('feature_names', []))}\n"

            if not details.get('cached'):
                perf = prediction.get('training_performance', {})
                if perf.get('rf_mae'):
                    detail_text += f"\n📊 Training Performance:\n"
                    detail_text += f"Random Forest MAE: ${perf['rf_mae']:,.0f}\n"
                    if perf.get('lstm_mae'):
                        detail_text += f"LSTM MAE: ${perf['lstm_mae']:,.0f}"

            console.print(Panel(detail_text, title="🔍 Technical Details", border_style="dim"))

        # Confidence breakdown
        if prediction.get('confidence_details'):
            conf_details = prediction['confidence_details']
            if not conf_details.get('fallback') and not conf_details.get('single_model'):
                conf_text = f"📈 Confidence Analysis:\n"
                if 'model_agreement' in conf_details:
                    conf_text += f"Model Agreement: {conf_details['model_agreement']:.1%}\n"
                conf_text += f"Market Volatility Factor: Considered\n"
                conf_text += f"\n💡 Higher model agreement = Higher confidence"
                console.print(Panel(conf_text, title="🎯 Confidence Breakdown", border_style="yellow"))

        # Market analysis
        if 'analysis' in prediction:
            console.print(Panel(prediction['analysis'], title="📊 Market Analysis", border_style="green"))

    def display_dca_recommendations(self, recommendations, date_range_text="full dataset"):
        console.print(f"\n[bold yellow]📅 Optimal DCA Days Analysis ({date_range_text})[/bold yellow]")

        # Best day of month
        monthly_table = Table(title="📆 Best Days of Month for DCA")
        monthly_table.add_column("Rank", style="cyan", width=6)
        monthly_table.add_column("Day", style="yellow", width=8)
        monthly_table.add_column("Avg Return", style="green", width=12)
        monthly_table.add_column("Success Rate", style="blue", width=12)

        for i, (day, row) in enumerate(recommendations['monthly'].head().iterrows(), 1):
            monthly_table.add_row(
                str(i), str(day), f"{row['avg_return']:.2%}", f"{row['success_rate']:.1%}"
            )

        console.print(monthly_table)

        # Best combination or simple strategy
        best_combo = recommendations['best_combination']
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

        if best_combo.get('is_simple_better', False) or best_combo.get('day_of_week') is None:
            # Simple day-of-month strategy is better
            strategy_text = f"🎯 Optimal Strategy: Invest on the {best_combo['day_of_month']}{self._ordinal(best_combo['day_of_month'])} of each month\n"
            strategy_text += f"Total return: {best_combo['expected_return']:.2%}\n"
            strategy_text += f"✅ Simple day-of-month strategy outperforms weekday combinations!"
            title = "💡 Best DCA Strategy (Simple)"
            border_style = "green"
        else:
            # Complex weekday + day-of-month strategy
            strategy_text = f"🎯 Optimal Strategy: Invest on {days[best_combo['day_of_week']]} closest to the {best_combo['day_of_month']}{self._ordinal(best_combo['day_of_month'])} of each month\n"
            strategy_text += f"Total return: {best_combo['expected_return']:.2%}"
            title = "💡 Best DCA Strategy (Complex)"
            border_style = "yellow"

        console.print(Panel(
            strategy_text,
            title=title,
            border_style=border_style
        ))

    def display_backtest_results(self, results, amount, strategy):
        table = Table(title="🧪 DCA Backtesting Results")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="yellow")

        table.add_row("Strategy", strategy.replace("_", " ").title())
        table.add_row("Monthly Investment", f"${amount:,.2f}")
        table.add_row("Total Invested", f"${results['total_invested']:,.2f}")
        table.add_row("Final Portfolio Value", f"${results['final_value']:,.2f}")
        table.add_row("Total Return", f"{results['total_return']:.2%}")
        table.add_row("Annualized Return", f"{results['annualized_return']:.2%}")
        table.add_row("Total Bitcoin", f"{results['total_btc']:.8f} BTC")

        console.print(table)

        if results['total_return'] > 0:
            profit_text = f"💰 Profit: ${results['final_value'] - results['total_invested']:,.2f}"
            console.print(Panel(profit_text, title="Success!", border_style="green"))
        else:
            loss_text = f"📉 Loss: ${abs(results['final_value'] - results['total_invested']):,.2f}"
            console.print(Panel(loss_text, title="Loss", border_style="red"))

    def _get_date_range(self, data):
        """Get and validate date range from user input"""
        try:
            start_date_str = Prompt.ask(
                "Start date (YYYY-MM-DD)",
                default=data.index[100].strftime('%Y-%m-%d') if len(data) > 100 else data.index[0].strftime('%Y-%m-%d')
            )
            end_date_str = Prompt.ask(
                "End date (YYYY-MM-DD)",
                default=data.index[-1].strftime('%Y-%m-%d')
            )

            start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d")

            # Validation
            data_start = data.index[0].to_pydatetime()
            data_end = data.index[-1].to_pydatetime()

            if start_date < data_start:
                console.print(f"[red]❌ Start date cannot be before {data_start.strftime('%Y-%m-%d')}[/red]")
                return None, None

            if end_date > data_end:
                console.print(f"[red]❌ End date cannot be after {data_end.strftime('%Y-%m-%d')}[/red]")
                return None, None

            if start_date >= end_date:
                console.print("[red]❌ Start date must be before end date[/red]")
                return None, None

            if (end_date - start_date).days < 90:
                console.print("[red]❌ Date range must be at least 90 days for meaningful analysis[/red]")
                return None, None

            return start_date, end_date

        except ValueError:
            console.print("[red]❌ Invalid date format. Please use YYYY-MM-DD[/red]")
            return None, None

    def _ordinal(self, n):
        if 10 <= n % 100 <= 20:
            suffix = 'th'
        else:
            suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')
        return suffix

    def run(self):
        """Main application loop"""
        try:
            self.load_basic_data()
            if self.show_welcome():
                return  # Exit if restart needed after update

            while True:
                console.print()
                self.show_menu()
                choice = Prompt.ask("\nSelect an option", choices=["1", "2", "3", "4", "5", "6", "q"], default="q")

                if choice == "1":
                    self.show_market_overview()
                elif choice == "2":
                    self.handle_prediction()
                elif choice == "3":
                    self.handle_dca_recommendations()
                elif choice == "4":
                    self.handle_backtesting()
                elif choice == "5":
                    self.handle_update_dataset()
                elif choice == "6":
                    self.handle_clear_cache()
                elif choice == "q":
                    console.print("\n[yellow]👋 Thanks for using Bitcoin DCA Analyzer![/yellow]")
                    break

        except KeyboardInterrupt:
            console.print("\n[yellow]👋 Goodbye![/yellow]")
        except Exception as e:
            console.print(f"[red]❌ Application error: {str(e)}[/red]")

@click.command()
@click.option('--csv', default=None, help='Path to Bitcoin price CSV file')
def main(csv):
    """Bitcoin DCA Analysis Terminal Application"""
    try:
        if csv is None:
            csv = str(get_default_csv_path())
        analyzer = BTCAnalyzer(csv)
        analyzer.run()
    except ImportError as e:
        console.print(f"[red]❌ Missing required dependency: {e}[/red]")
        console.print("[yellow]Please ensure all dependencies are installed:[/yellow]")
        console.print("  pip3 install -r requirements.txt --user")
        console.print("[dim]Or reinstall the application:[/dim]")
        console.print("  curl -fsSL https://raw.githubusercontent.com/obokaman-com/bitcoin-dca/main/install.sh | bash")
        exit(1)
    except Exception as e:
        console.print(f"[red]❌ Application startup error: {e}[/red]")
        console.print("[yellow]If this persists, try reinstalling:[/yellow]")
        console.print("  curl -fsSL https://raw.githubusercontent.com/obokaman-com/bitcoin-dca/main/uninstall.sh | bash")
        console.print("  curl -fsSL https://raw.githubusercontent.com/obokaman-com/bitcoin-dca/main/install.sh | bash")
        exit(1)

if __name__ == "__main__":
    main()

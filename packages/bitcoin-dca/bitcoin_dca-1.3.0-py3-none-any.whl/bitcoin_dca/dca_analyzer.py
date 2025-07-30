"""
DCA (Dollar Cost Averaging) analysis module
Finds optimal investment timing based on historical performance
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from collections import defaultdict
import itertools

class DCAAnalyzer:
    def __init__(self):
        self.analysis_results = {}
        self.transaction_fee = 0.001  # 0.1% transaction fee (same as backtester)
        
    def analyze_optimal_days(self, df: pd.DataFrame) -> dict:
        """Analyze optimal days for DCA based on historical performance"""
        
        # Analyze monthly patterns
        monthly_analysis = self._analyze_monthly_patterns(df)
        
        # Analyze weekly patterns  
        weekly_analysis = self._analyze_weekly_patterns(df)
        
        # Find best combination
        best_combination = self._find_best_combination(df, monthly_analysis, weekly_analysis)
        
        return {
            'monthly': monthly_analysis,
            'weekly': weekly_analysis,
            'best_combination': best_combination
        }
        
    def _analyze_monthly_patterns(self, df: pd.DataFrame) -> pd.Series:
        """Analyze which days of the month are best for DCA using actual DCA simulation"""
        
        if len(df) == 0:
            # Return empty DataFrame with expected structure
            return pd.DataFrame(columns=['avg_return', 'success_rate', 'volatility', 'total_trades'])
        
        # Create a copy with day of month
        analysis_df = df.copy()
        if not isinstance(analysis_df.index, pd.DatetimeIndex):
            return pd.DataFrame(columns=['avg_return', 'success_rate', 'volatility', 'total_trades'])
            
        analysis_df['Day_of_Month'] = analysis_df.index.day
        analysis_df['Month_Year'] = analysis_df.index.to_period('M')
        
        day_performance = {}
        
        # Analyze each day of month (1-28 to ensure all months have the day)
        for day in range(1, 29):
            # Simulate DCA strategy for this day of month
            dca_result = self._simulate_dca_strategy(df, target_day_of_month=day)
            day_performance[day] = dca_result
                
        # Convert to DataFrame and sort by avg_return
        if day_performance:
            performance_df = pd.DataFrame.from_dict(day_performance, orient='index')
            return performance_df.sort_values('avg_return', ascending=False)
        else:
            return pd.DataFrame(columns=['avg_return', 'success_rate', 'volatility', 'total_trades'])
    
    def _simulate_dca_strategy(self, df: pd.DataFrame, target_day_of_month: int, 
                              target_day_of_week: int = None, monthly_amount: float = 1000) -> dict:
        """Simulate DCA strategy and calculate total invested vs final value"""
        
        # Create copy with time features
        analysis_df = df.copy()
        analysis_df['Day_of_Month'] = analysis_df.index.day
        analysis_df['Day_of_Week'] = analysis_df.index.dayofweek
        analysis_df['Month_Year'] = analysis_df.index.to_period('M')
        
        total_invested = 0
        total_btc = 0
        transactions = []
        
        # Group by month and simulate monthly investments
        for month_year, month_data in analysis_df.groupby('Month_Year'):
            if len(month_data) == 0:
                continue
                
            # Find the best day to buy this month
            if target_day_of_week is None:
                # Simple: find day closest to target day of month
                month_data['Distance'] = abs(month_data['Day_of_Month'] - target_day_of_month)
                best_day = month_data.loc[month_data['Distance'].idxmin()]
            else:
                # Complex: find target weekday closest to target day of month
                target_days = month_data[
                    (month_data['Day_of_Week'] == target_day_of_week) &
                    (month_data['Day_of_Month'] <= target_day_of_month + 7) &
                    (month_data['Day_of_Month'] >= target_day_of_month - 7)
                ]
                
                if len(target_days) == 0:
                    # Fallback: any day with target weekday
                    target_days = month_data[month_data['Day_of_Week'] == target_day_of_week]
                    
                if len(target_days) == 0:
                    # Fallback: closest day to target day of month
                    month_data['Distance'] = abs(month_data['Day_of_Month'] - target_day_of_month)
                    best_day = month_data.loc[month_data['Distance'].idxmin()]
                else:
                    # Choose the day closest to target day of month
                    target_days['Distance'] = abs(target_days['Day_of_Month'] - target_day_of_month)
                    best_day = target_days.loc[target_days['Distance'].idxmin()]
            
            # Execute the purchase (with transaction fees)
            buy_price = best_day['Close']
            net_investment = monthly_amount * (1 - self.transaction_fee)
            btc_purchased = net_investment / buy_price
            
            total_invested += monthly_amount
            total_btc += btc_purchased
            
            transactions.append({
                'date': best_day.name,
                'price': buy_price,
                'amount': monthly_amount,
                'btc': btc_purchased
            })
        
        if len(transactions) == 0:
            return {
                'avg_return': 0.0,
                'success_rate': 0.0,
                'volatility': 0.0,
                'total_trades': 0
            }
        
        # Calculate final portfolio value
        final_price = df['Close'].iloc[-1]
        final_value = total_btc * final_price
        
        # Calculate total return
        total_return = (final_value - total_invested) / total_invested if total_invested > 0 else 0
        
        # Calculate individual trade success rate (for compatibility)
        successful_trades = 0
        individual_returns = []
        
        for transaction in transactions:
            individual_return = (final_price - transaction['price']) / transaction['price']
            individual_returns.append(individual_return)
            if individual_return > 0:
                successful_trades += 1
        
        success_rate = successful_trades / len(transactions) if len(transactions) > 0 else 0
        volatility = np.std(individual_returns) if individual_returns else 0
        
        return {
            'avg_return': total_return,
            'success_rate': success_rate,
            'volatility': volatility,
            'total_trades': len(transactions),
            'total_invested': total_invested,
            'final_value': final_value,
            'total_btc': total_btc
        }
        
    def _analyze_weekly_patterns(self, df: pd.DataFrame) -> pd.Series:
        """Analyze which days of the week are best for DCA"""
        
        if len(df) == 0:
            # Return empty DataFrame with expected structure
            return pd.DataFrame(columns=['avg_return', 'success_rate', 'volatility', 'total_trades'])
        
        analysis_df = df.copy()
        if not isinstance(analysis_df.index, pd.DatetimeIndex):
            return pd.DataFrame(columns=['avg_return', 'success_rate', 'volatility', 'total_trades'])
            
        analysis_df['Day_of_Week'] = analysis_df.index.dayofweek  # Monday=0, Sunday=6
        
        day_performance = {}
        
        # Analyze each day of week
        for day_of_week in range(7):
            day_data = analysis_df[analysis_df['Day_of_Week'] == day_of_week]
            
            returns = []
            success_count = 0
            total_count = 0
            
            # Calculate returns for each occurrence of this day
            for i in range(len(day_data)):
                buy_price = day_data['Close'].iloc[i]
                buy_date = day_data.index[i]
                
                # Calculate returns over different periods
                for period_days in [30, 90, 180, 365]:
                    future_date = buy_date + timedelta(days=period_days)
                    
                    # Find closest future price
                    future_data = df[df.index >= future_date]
                    if len(future_data) > 0:
                        future_price = future_data['Close'].iloc[0]
                        period_return = (future_price - buy_price) / buy_price
                        returns.append(period_return)
                        total_count += 1
                        if period_return > 0:
                            success_count += 1
                            
            if returns:
                day_performance[day_of_week] = {
                    'avg_return': np.mean(returns),
                    'median_return': np.median(returns),
                    'success_rate': success_count / total_count if total_count > 0 else 0,
                    'volatility': np.std(returns),
                    'total_trades': total_count
                }
            else:
                day_performance[day_of_week] = {
                    'avg_return': 0,
                    'median_return': 0,
                    'success_rate': 0,
                    'volatility': 0,
                    'total_trades': 0
                }
                
        # Convert to DataFrame
        detailed_performance = pd.DataFrame(day_performance).T
        
        # Sort by average return
        detailed_performance = detailed_performance.sort_values('avg_return', ascending=False)
        
        return detailed_performance
        
    def _find_best_combination(self, df: pd.DataFrame, monthly_analysis: pd.DataFrame, weekly_analysis: pd.DataFrame) -> dict:
        """Find the best combination of day of week and day of month using DCA simulation"""
        
        try:
            # Get top performing days
            if len(monthly_analysis) == 0:
                return {
                    'day_of_month': 15,
                    'day_of_week': 2,  # Wednesday
                    'expected_return': 0.0,
                    'is_simple_better': False
                }
                
            top_monthly_days = monthly_analysis.head(5).index.tolist()
            weekdays = [0, 1, 2, 3, 4]  # Monday to Friday
            
            best_combination = None
            best_return = -float('inf')
            
            # Test combinations of top performing days with all weekdays
            for day_of_month in top_monthly_days:
                for day_of_week in weekdays:
                    # Use the same DCA simulation method
                    combination_result = self._simulate_dca_strategy(
                        df, 
                        target_day_of_month=day_of_month, 
                        target_day_of_week=day_of_week
                    )
                    
                    combination_return = combination_result['avg_return']
                    
                    if combination_return > best_return:
                        best_return = combination_return
                        best_combination = {
                            'day_of_month': day_of_month,
                            'day_of_week': day_of_week,
                            'expected_return': combination_return,
                            'total_invested': combination_result['total_invested'],
                            'final_value': combination_result['final_value'],
                            'is_simple_better': False
                        }
                        
            # Compare with simple day-of-month strategy (best performing)
            if len(monthly_analysis) > 0:
                best_simple_day = monthly_analysis.index[0]  # Top performing day
                simple_return = monthly_analysis.iloc[0]['avg_return']
                
                # If simple strategy is better, recommend it
                if simple_return > best_return:
                    best_combination = {
                        'day_of_month': best_simple_day,
                        'day_of_week': None,  # No weekday constraint
                        'expected_return': simple_return,
                        'is_simple_better': True
                    }
                        
            return best_combination if best_combination else {
                'day_of_month': 15,
                'day_of_week': 2,
                'expected_return': 0.0,
                'is_simple_better': False
            }
            
        except Exception as e:
            # Fallback to reasonable defaults
            return {
                'day_of_month': 15,
                'day_of_week': 2,  # Wednesday  
                'expected_return': 0.0,
                'is_simple_better': False
            }
        
        
    def get_optimal_strategy_summary(self, analysis_results: dict) -> str:
        """Generate a summary of the optimal DCA strategy"""
        
        best_monthly = analysis_results['monthly'].iloc[0]
        best_weekly = analysis_results['weekly'].iloc[0]
        best_combo = analysis_results['best_combination']
        
        days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        summary = f"""
OPTIMAL DCA STRATEGY ANALYSIS
=============================

Best Day of Month: {analysis_results['monthly'].index[0]}
- Average Return: {best_monthly['avg_return']:.2%}
- Success Rate: {best_monthly['success_rate']:.1%}
- Total Trades Analyzed: {best_monthly['total_trades']}

Best Day of Week: {days_of_week[analysis_results['weekly'].index[0]]}
- Average Return: {best_weekly['avg_return']:.2%}
- Success Rate: {best_weekly['success_rate']:.1%}
- Total Trades Analyzed: {best_weekly['total_trades']}

OPTIMAL COMBINATION:
Invest on {days_of_week[best_combo['day_of_week']]} closest to the {best_combo['day_of_month']}{self._ordinal(best_combo['day_of_month'])} of each month
Expected Annual Return: {best_combo['expected_return'] * 4:.2%}
"""
        
        return summary
        
    def _ordinal(self, n):
        """Convert number to ordinal (1st, 2nd, 3rd, etc.)"""
        if 10 <= n % 100 <= 20:
            suffix = 'th'
        else:
            suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')
        return suffix
        
    def analyze_market_timing_patterns(self, df: pd.DataFrame) -> dict:
        """Analyze broader market timing patterns"""
        
        patterns = {}
        
        # Monthly patterns
        df_copy = df.copy()
        df_copy['Month'] = df_copy.index.month
        monthly_returns = df_copy.groupby('Month')['Close'].last() / df_copy.groupby('Month')['Close'].first() - 1
        patterns['monthly_seasonality'] = monthly_returns.sort_values(ascending=False)
        
        # Quarterly patterns
        df_copy['Quarter'] = df_copy.index.quarter
        quarterly_returns = df_copy.groupby('Quarter')['Close'].last() / df_copy.groupby('Quarter')['Close'].first() - 1
        patterns['quarterly_seasonality'] = quarterly_returns.sort_values(ascending=False)
        
        # Market cycle analysis (based on halving cycles)
        if 'Days_Since_Halving' in df.columns:
            # Divide halving cycle into phases
            df_copy['Halving_Phase'] = pd.cut(
                df_copy['Days_Since_Halving'], 
                bins=[0, 365, 730, 1095, 1460], 
                labels=['Year 1', 'Year 2', 'Year 3', 'Year 4'],
                include_lowest=True
            )
            
            phase_returns = {}
            for phase in ['Year 1', 'Year 2', 'Year 3', 'Year 4']:
                phase_data = df_copy[df_copy['Halving_Phase'] == phase]
                if len(phase_data) > 0:
                    phase_return = phase_data['Close'].pct_change().mean() * 365  # Annualized
                    phase_returns[phase] = phase_return
                    
            patterns['halving_cycle_performance'] = phase_returns
            
        return patterns
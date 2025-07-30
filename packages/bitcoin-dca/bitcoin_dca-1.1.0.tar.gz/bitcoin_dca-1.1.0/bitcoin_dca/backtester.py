"""
DCA backtesting module
Simulates historical DCA strategies to evaluate performance
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import calendar

class DCABacktester:
    def __init__(self):
        self.transaction_fee = 0.001  # 0.1% transaction fee
        
    def backtest_monthly_dca(self, df: pd.DataFrame, monthly_amount: float, 
                           day_of_month: int = 15, start_date: Optional[datetime] = None,
                           end_date: Optional[datetime] = None) -> Dict:
        """Backtest monthly DCA strategy on a specific day of month"""
        
        if start_date is None:
            start_date = df.index[0] + timedelta(days=30)  # Start after first month
        if end_date is None:
            end_date = df.index[-1]
            
        transactions = []
        total_invested = 0
        total_btc = 0
        
        # Generate investment dates
        investment_dates = self._generate_monthly_dates(start_date, end_date, day_of_month)
        
        for inv_date in investment_dates:
            # Find closest trading day
            trading_date, price = self._find_closest_trading_day(df, inv_date)
            
            if trading_date is not None and price is not None:
                # Calculate BTC purchased (after fees)
                net_investment = monthly_amount * (1 - self.transaction_fee)
                btc_purchased = net_investment / price
                
                transactions.append({
                    'date': trading_date,
                    'price': price,
                    'amount_invested': monthly_amount,
                    'btc_purchased': btc_purchased,
                    'cumulative_btc': total_btc + btc_purchased,
                    'cumulative_invested': total_invested + monthly_amount
                })
                
                total_invested += monthly_amount
                total_btc += btc_purchased
                
        if not transactions:
            return self._empty_backtest_result()
            
        # Calculate final portfolio value
        final_price = df['Close'].iloc[-1]
        final_value = total_btc * final_price
        
        return self._calculate_performance_metrics(
            transactions, total_invested, total_btc, final_value, final_price
        )
        
    def backtest_weekly_dca(self, df: pd.DataFrame, weekly_amount: float,
                          day_of_week: int = 2, start_date: Optional[datetime] = None,
                          end_date: Optional[datetime] = None) -> Dict:
        """Backtest weekly DCA strategy on a specific day of week"""
        
        if start_date is None:
            start_date = df.index[0] + timedelta(days=7)
        if end_date is None:
            end_date = df.index[-1]
            
        transactions = []
        total_invested = 0
        total_btc = 0
        
        # Generate investment dates (weekly)
        investment_dates = self._generate_weekly_dates(start_date, end_date, day_of_week)
        
        for inv_date in investment_dates:
            trading_date, price = self._find_closest_trading_day(df, inv_date)
            
            if trading_date is not None and price is not None:
                net_investment = weekly_amount * (1 - self.transaction_fee)
                btc_purchased = net_investment / price
                
                transactions.append({
                    'date': trading_date,
                    'price': price,
                    'amount_invested': weekly_amount,
                    'btc_purchased': btc_purchased,
                    'cumulative_btc': total_btc + btc_purchased,
                    'cumulative_invested': total_invested + weekly_amount
                })
                
                total_invested += weekly_amount
                total_btc += btc_purchased
                
        if not transactions:
            return self._empty_backtest_result()
            
        final_price = df['Close'].iloc[-1]
        final_value = total_btc * final_price
        
        return self._calculate_performance_metrics(
            transactions, total_invested, total_btc, final_value, final_price
        )
        
    def backtest_optimal_dca(self, df: pd.DataFrame, monthly_amount: float,
                           day_of_week: int = 2, day_of_month: int = 21,
                           start_date: Optional[datetime] = None,
                           end_date: Optional[datetime] = None) -> Dict:
        """Backtest optimal DCA strategy (specific day of week closest to day of month)"""
        
        if start_date is None:
            start_date = df.index[0] + timedelta(days=30)
        if end_date is None:
            end_date = df.index[-1]
            
        transactions = []
        total_invested = 0
        total_btc = 0
        
        # Generate optimal investment dates
        investment_dates = self._generate_optimal_dates(start_date, end_date, day_of_week, day_of_month)
        
        for inv_date in investment_dates:
            trading_date, price = self._find_closest_trading_day(df, inv_date)
            
            if trading_date is not None and price is not None:
                net_investment = monthly_amount * (1 - self.transaction_fee)
                btc_purchased = net_investment / price
                
                transactions.append({
                    'date': trading_date,
                    'price': price,
                    'amount_invested': monthly_amount,
                    'btc_purchased': btc_purchased,
                    'cumulative_btc': total_btc + btc_purchased,
                    'cumulative_invested': total_invested + monthly_amount
                })
                
                total_invested += monthly_amount
                total_btc += btc_purchased
                
        if not transactions:
            return self._empty_backtest_result()
            
        final_price = df['Close'].iloc[-1]
        final_value = total_btc * final_price
        
        return self._calculate_performance_metrics(
            transactions, total_invested, total_btc, final_value, final_price
        )
        
    def backtest_custom_strategy(self, df: pd.DataFrame, strategy_func, amount: float,
                                start_date: Optional[datetime] = None,
                                end_date: Optional[datetime] = None) -> Dict:
        """Backtest a custom strategy defined by a function"""
        
        if start_date is None:
            start_date = df.index[0]
        if end_date is None:
            end_date = df.index[-1]
            
        # Strategy function should return list of investment dates
        investment_dates = strategy_func(start_date, end_date)
        
        transactions = []
        total_invested = 0
        total_btc = 0
        
        for inv_date in investment_dates:
            trading_date, price = self._find_closest_trading_day(df, inv_date)
            
            if trading_date is not None and price is not None:
                net_investment = amount * (1 - self.transaction_fee)
                btc_purchased = net_investment / price
                
                transactions.append({
                    'date': trading_date,
                    'price': price,
                    'amount_invested': amount,
                    'btc_purchased': btc_purchased,
                    'cumulative_btc': total_btc + btc_purchased,
                    'cumulative_invested': total_invested + amount
                })
                
                total_invested += amount
                total_btc += btc_purchased
                
        if not transactions:
            return self._empty_backtest_result()
            
        final_price = df['Close'].iloc[-1]
        final_value = total_btc * final_price
        
        return self._calculate_performance_metrics(
            transactions, total_invested, total_btc, final_value, final_price
        )
        
    def compare_strategies(self, df: pd.DataFrame, amount: float) -> Dict:
        """Compare multiple DCA strategies"""
        
        strategies = {
            'Monthly 1st': self.backtest_monthly_dca(df, amount, 1),
            'Monthly 15th': self.backtest_monthly_dca(df, amount, 15),
            'Monthly 28th': self.backtest_monthly_dca(df, amount, 28),
            'Weekly Monday': self.backtest_weekly_dca(df, amount/4, 0),
            'Weekly Wednesday': self.backtest_weekly_dca(df, amount/4, 2),
            'Weekly Friday': self.backtest_weekly_dca(df, amount/4, 4),
            'Optimal Strategy': self.backtest_optimal_dca(df, amount, 2, 21)
        }
        
        # Rank strategies by total return
        strategy_ranking = sorted(
            strategies.items(),
            key=lambda x: x[1]['total_return'],
            reverse=True
        )
        
        return {
            'strategies': strategies,
            'ranking': strategy_ranking,
            'best_strategy': strategy_ranking[0] if strategy_ranking else None
        }
        
    def _generate_monthly_dates(self, start_date: datetime, end_date: datetime, 
                              day_of_month: int) -> List[datetime]:
        """Generate monthly investment dates"""
        dates = []
        current_date = start_date.replace(day=1)  # Start of month
        
        while current_date <= end_date:
            try:
                # Try to create date with target day
                target_date = current_date.replace(day=min(day_of_month, 
                                                         calendar.monthrange(current_date.year, current_date.month)[1]))
                if target_date >= start_date:
                    dates.append(target_date)
            except ValueError:
                pass
                
            # Move to next month
            if current_date.month == 12:
                current_date = current_date.replace(year=current_date.year + 1, month=1)
            else:
                current_date = current_date.replace(month=current_date.month + 1)
                
        return dates
        
    def _generate_weekly_dates(self, start_date: datetime, end_date: datetime,
                             day_of_week: int) -> List[datetime]:
        """Generate weekly investment dates"""
        dates = []
        
        # Find first occurrence of target day of week
        days_ahead = day_of_week - start_date.weekday()
        if days_ahead <= 0:  # Target day already happened this week
            days_ahead += 7
            
        current_date = start_date + timedelta(days=days_ahead)
        
        while current_date <= end_date:
            dates.append(current_date)
            current_date += timedelta(days=7)
            
        return dates
        
    def _generate_optimal_dates(self, start_date: datetime, end_date: datetime,
                              day_of_week: int, day_of_month: int) -> List[datetime]:
        """Generate optimal investment dates (day of week closest to day of month)"""
        dates = []
        current_date = start_date.replace(day=1)
        
        while current_date <= end_date:
            try:
                # Find target day of month
                max_day = calendar.monthrange(current_date.year, current_date.month)[1]
                target_day = min(day_of_month, max_day)
                target_date = current_date.replace(day=target_day)
                
                # Find closest occurrence of target day of week
                days_to_target = (day_of_week - target_date.weekday()) % 7
                if days_to_target > 3:  # If more than 3 days away, go to previous week
                    days_to_target -= 7
                    
                optimal_date = target_date + timedelta(days=days_to_target)
                
                # Ensure date is within the month and after start_date
                if (optimal_date.month == current_date.month and 
                    optimal_date >= start_date and 
                    optimal_date <= end_date):
                    dates.append(optimal_date)
                    
            except ValueError:
                pass
                
            # Move to next month
            if current_date.month == 12:
                current_date = current_date.replace(year=current_date.year + 1, month=1)
            else:
                current_date = current_date.replace(month=current_date.month + 1)
                
        return dates
        
    def _find_closest_trading_day(self, df: pd.DataFrame, target_date: datetime) -> Tuple[Optional[datetime], Optional[float]]:
        """Find closest available trading day and price"""
        
        # Convert to date if datetime
        if hasattr(target_date, 'date'):
            target_date = target_date.date()
            
        # Look for exact match first
        exact_matches = df[df.index.date == target_date]
        if len(exact_matches) > 0:
            return exact_matches.index[0], exact_matches['Close'].iloc[0]
            
        # Find closest date within 7 days
        for days_offset in range(1, 8):
            # Try forward
            future_date = target_date + timedelta(days=days_offset)
            future_matches = df[df.index.date == future_date]
            if len(future_matches) > 0:
                return future_matches.index[0], future_matches['Close'].iloc[0]
                
            # Try backward
            past_date = target_date - timedelta(days=days_offset)
            past_matches = df[df.index.date == past_date]
            if len(past_matches) > 0:
                return past_matches.index[0], past_matches['Close'].iloc[0]
                
        return None, None
        
    def _calculate_performance_metrics(self, transactions: List[Dict], total_invested: float,
                                     total_btc: float, final_value: float, final_price: float) -> Dict:
        """Calculate comprehensive performance metrics"""
        
        if total_invested == 0:
            return self._empty_backtest_result()
            
        # Basic metrics
        total_return = (final_value - total_invested) / total_invested
        avg_price = total_invested / total_btc if total_btc > 0 else 0
        
        # Time-based metrics
        start_date = transactions[0]['date']
        end_date = transactions[-1]['date']
        total_days = (end_date - start_date).days
        total_years = total_days / 365.25
        
        annualized_return = ((final_value / total_invested) ** (1 / total_years) - 1) if total_years > 0 else 0
        
        # Advanced metrics
        transaction_df = pd.DataFrame(transactions)
        transaction_df['date'] = pd.to_datetime(transaction_df['date'])
        transaction_df.set_index('date', inplace=True)
        
        # Calculate volatility of returns
        transaction_df['portfolio_value'] = transaction_df['cumulative_btc'] * final_price
        transaction_df['returns'] = transaction_df['portfolio_value'].pct_change()
        volatility = transaction_df['returns'].std() * np.sqrt(252) if len(transaction_df) > 1 else 0
        
        # Sharpe ratio (simplified, assuming 0% risk-free rate)
        sharpe_ratio = annualized_return / volatility if volatility > 0 else 0
        
        # Maximum drawdown
        transaction_df['cumulative_returns'] = (1 + transaction_df['returns']).cumprod()
        transaction_df['running_max'] = transaction_df['cumulative_returns'].expanding().max()
        transaction_df['drawdown'] = transaction_df['cumulative_returns'] / transaction_df['running_max'] - 1
        max_drawdown = transaction_df['drawdown'].min()
        
        # Win rate
        profitable_transactions = sum(1 for t in transactions if t['price'] < final_price)
        win_rate = profitable_transactions / len(transactions) if transactions else 0
        
        return {
            'total_invested': total_invested,
            'final_value': final_value,
            'total_btc': total_btc,
            'total_return': total_return,
            'annualized_return': annualized_return,
            'avg_price': avg_price,
            'final_price': final_price,
            'total_transactions': len(transactions),
            'investment_period_days': total_days,
            'investment_period_years': total_years,
            'volatility': volatility,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'win_rate': win_rate,
            'transactions': transactions,
            'start_date': start_date,
            'end_date': end_date
        }
        
    def _empty_backtest_result(self) -> Dict:
        """Return empty result structure for failed backtests"""
        return {
            'total_invested': 0,
            'final_value': 0,
            'total_btc': 0,
            'total_return': 0,
            'annualized_return': 0,
            'avg_price': 0,
            'final_price': 0,
            'total_transactions': 0,
            'investment_period_days': 0,
            'investment_period_years': 0,
            'volatility': 0,
            'sharpe_ratio': 0,
            'max_drawdown': 0,
            'win_rate': 0,
            'transactions': [],
            'start_date': None,
            'end_date': None
        }
        
    def generate_performance_report(self, results: Dict) -> str:
        """Generate a detailed performance report"""
        
        if results['total_transactions'] == 0:
            return "No transactions found for the specified period."
            
        report = f"""
DCA BACKTEST PERFORMANCE REPORT
===============================

Investment Summary:
- Total Invested: ${results['total_invested']:,.2f}
- Final Portfolio Value: ${results['final_value']:,.2f}
- Total Bitcoin Acquired: {results['total_btc']:.8f} BTC
- Average Price Paid: ${results['avg_price']:,.2f}

Performance Metrics:
- Total Return: {results['total_return']:.2%}
- Annualized Return: {results['annualized_return']:.2%}
- Win Rate: {results['win_rate']:.1%}
- Sharpe Ratio: {results['sharpe_ratio']:.2f}
- Maximum Drawdown: {results['max_drawdown']:.2%}
- Volatility: {results['volatility']:.2%}

Investment Details:
- Number of Transactions: {results['total_transactions']}
- Investment Period: {results['investment_period_years']:.1f} years
- Start Date: {results['start_date'].strftime('%Y-%m-%d') if results['start_date'] else 'N/A'}
- End Date: {results['end_date'].strftime('%Y-%m-%d') if results['end_date'] else 'N/A'}
"""
        
        return report
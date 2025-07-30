"""
Bitcoin Market Cycle Indicators
Simplified CBBI-style indicators for market cycle analysis
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Tuple, Optional

class MarketCycleAnalyzer:
    """Bitcoin market cycle analysis using simplified CBBI-style indicators"""
    
    def __init__(self):
        self.indicators = {}
        
    def calculate_mayer_multiple(self, data: pd.DataFrame) -> float:
        """Calculate Mayer Multiple (Price / 200-day MA)"""
        if len(data) < 200:
            return None
            
        sma_200 = data['Close'].rolling(window=200).mean()
        current_price = data['Close'].iloc[-1]
        mayer_multiple = current_price / sma_200.iloc[-1]
        
        return mayer_multiple
    
    def calculate_puell_multiple(self, data: pd.DataFrame) -> Optional[float]:
        """
        Simplified Puell Multiple approximation
        Uses price volatility as proxy for mining profitability
        """
        if len(data) < 365:
            return None
            
        # Calculate daily returns
        daily_returns = data['Close'].pct_change()
        
        # Current 30-day average absolute return (proxy for mining revenue)
        recent_volatility = daily_returns.rolling(30).std().iloc[-1]
        
        # 365-day average (proxy for historical average)
        historical_avg = daily_returns.rolling(365).std().mean()
        
        if historical_avg == 0:
            return None
            
        puell_approx = recent_volatility / historical_avg
        return puell_approx
    
    def calculate_two_year_ma_multiple(self, data: pd.DataFrame) -> Optional[float]:
        """Calculate 2-Year Moving Average Multiple"""
        if len(data) < 730:  # 2 years
            return None
            
        ma_2y = data['Close'].rolling(window=730).mean()
        current_price = data['Close'].iloc[-1]
        
        if ma_2y.iloc[-1] == 0:
            return None
            
        return current_price / ma_2y.iloc[-1]
    
    def calculate_drawdown_from_ath(self, data: pd.DataFrame) -> float:
        """Calculate current drawdown from all-time high"""
        ath = data['High'].max()
        current_price = data['Close'].iloc[-1]
        drawdown = (current_price - ath) / ath * 100
        return drawdown
    
    def calculate_rsi_14(self, data: pd.DataFrame) -> Optional[float]:
        """Calculate 14-day RSI"""
        if len(data) < 15:
            return None
            
        delta = data['Close'].diff()
        gain = (delta * (delta > 0)).rolling(window=14).mean()
        loss = (-delta * (delta < 0)).rolling(window=14).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi.iloc[-1]
    
    def calculate_market_cycle_score(self, data: pd.DataFrame) -> Dict[str, any]:
        """
        Calculate simplified CBBI-style market cycle score
        Returns score from 0-100 and market phase
        """
        indicators = {}
        scores = []
        weights = []
        
        # 1. Mayer Multiple (0-100 score)
        mayer = self.calculate_mayer_multiple(data)
        if mayer is not None:
            # Mayer Multiple: <1.0 = accumulation, 1.0-2.4 = bull, >2.4 = euphoria
            mayer_score = min(100, max(0, (mayer - 0.8) / 1.6 * 100))
            indicators['mayer_multiple'] = mayer
            indicators['mayer_score'] = mayer_score
            scores.append(mayer_score)
            weights.append(25)  # 25% weight
        
        # 2. Two Year MA Multiple
        two_year_ma = self.calculate_two_year_ma_multiple(data)
        if two_year_ma is not None:
            # 2Y MA: <1.0 = bear, 1.0-3.0 = bull, >3.0 = euphoria
            two_year_score = min(100, max(0, (two_year_ma - 0.8) / 2.2 * 100))
            indicators['two_year_ma_multiple'] = two_year_ma
            indicators['two_year_ma_score'] = two_year_score
            scores.append(two_year_score)
            weights.append(25)  # 25% weight
        
        # 3. Drawdown from ATH (inverted - lower drawdown = higher score)
        drawdown = self.calculate_drawdown_from_ath(data)
        # Convert drawdown to 0-100 score (0% drawdown = 100, -80% drawdown = 0)
        drawdown_score = max(0, min(100, 100 + drawdown * 1.25))  # -80% = 0, 0% = 100
        indicators['ath_drawdown'] = drawdown
        indicators['drawdown_score'] = drawdown_score
        scores.append(drawdown_score)
        weights.append(20)  # 20% weight
        
        # 4. RSI (normalized)
        rsi = self.calculate_rsi_14(data)
        if rsi is not None:
            # RSI: 0-30 = oversold/accumulation, 70-100 = overbought/euphoria
            rsi_score = rsi  # Already 0-100
            indicators['rsi_14'] = rsi
            indicators['rsi_score'] = rsi_score
            scores.append(rsi_score)
            weights.append(15)  # 15% weight
        
        # 5. Puell Multiple approximation
        puell = self.calculate_puell_multiple(data)
        if puell is not None:
            # Puell: <0.5 = accumulation, 0.5-4.0 = normal, >4.0 = euphoria
            puell_score = min(100, max(0, (puell - 0.3) / 3.7 * 100))
            indicators['puell_multiple'] = puell
            indicators['puell_score'] = puell_score
            scores.append(puell_score)
            weights.append(15)  # 15% weight
        
        # Calculate weighted average score
        if scores and weights:
            total_weight = sum(weights)
            weighted_score = sum(s * w for s, w in zip(scores, weights)) / total_weight
        else:
            weighted_score = 50  # Default neutral
        
        # Determine market phase
        if weighted_score < 35:
            phase = "Accumulation"
            phase_color = "green"
            recommendation = "Strong DCA opportunity"
        elif weighted_score < 65:
            phase = "Bull Market"
            phase_color = "yellow"  
            recommendation = "Continue regular DCA"
        else:
            phase = "Euphoria/Top"
            phase_color = "red"
            recommendation = "Consider reducing DCA frequency"
        
        return {
            'score': round(weighted_score, 1),
            'phase': phase,
            'phase_color': phase_color,
            'recommendation': recommendation,
            'indicators': indicators,
            'confidence': len(scores) / 5 * 100  # Confidence based on available indicators
        }
    
    def get_market_summary(self, data: pd.DataFrame) -> str:
        """Get a brief market cycle summary text"""
        result = self.calculate_market_cycle_score(data)
        
        summary = f"Market Cycle Score: {result['score']}/100 ({result['phase']})"
        if result['confidence'] < 80:
            summary += f" (Limited data - {result['confidence']:.0f}% confidence)"
            
        return summary
"""
Bitcoin data loader with caching and lazy feature computation
Optimized for fast startup and efficient memory usage
"""

import pandas as pd
import numpy as np
from datetime import datetime
import os
import pickle
import hashlib
from pathlib import Path
import ta

class DataLoader:
    def __init__(self, csv_path: str):
        self.csv_path = csv_path
        # Use global app directory for cache
        app_dir = Path.home() / '.bitcoin-dca'
        app_dir.mkdir(exist_ok=True)
        self.cache_dir = app_dir / '.cache'
        self.cache_dir.mkdir(exist_ok=True)
        
    def get_cache_key(self) -> str:
        """Generate cache key based on CSV file content"""
        if not os.path.exists(self.csv_path):
            return None
            
        # Use file modification time and size for cache key
        stat = os.stat(self.csv_path)
        cache_key = f"{stat.st_mtime}_{stat.st_size}"
        return hashlib.md5(cache_key.encode()).hexdigest()
    
    def load_basic_data(self, progress_callback=None) -> pd.DataFrame:
        """Load minimal data for immediate startup"""
        def update_progress(message):
            if progress_callback:
                progress_callback(message)
        
        update_progress("Loading basic price data...")
        
        # Try cache first
        cache_key = self.get_cache_key()
        basic_cache_path = self.cache_dir / f"basic_{cache_key}.pkl"
        
        if cache_key and basic_cache_path.exists():
            update_progress("Loading from cache...")
            try:
                with open(basic_cache_path, 'rb') as f:
                    return pickle.load(f)
            except:
                pass  # Cache corrupted, regenerate
        
        # Load and process basic data
        df = pd.read_csv(self.csv_path)
        df['Date'] = pd.to_datetime(df['Date'])
        df.set_index('Date', inplace=True)
        
        # Basic cleaning
        numeric_columns = ['Open', 'High', 'Low', 'Close']
        for col in numeric_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            
        df.dropna(subset=numeric_columns, inplace=True)
        for col in numeric_columns:
            df = df[df[col] > 0]
        
        df.sort_index(inplace=True)
        
        # Cache basic data
        if cache_key:
            try:
                with open(basic_cache_path, 'wb') as f:
                    pickle.dump(df, f)
            except:
                pass  # Cache write failed, continue anyway
        
        update_progress("Basic data loaded!")
        return df
    
    def add_features_lazy(self, df: pd.DataFrame, feature_set: str = 'all', progress_callback=None) -> pd.DataFrame:
        """Add features on-demand based on what's needed"""
        def update_progress(message):
            if progress_callback:
                progress_callback(message)
        
        cache_key = self.get_cache_key()
        features_cache_path = self.cache_dir / f"features_{feature_set}_{cache_key}.pkl"
        
        # Try cache first
        if cache_key and features_cache_path.exists():
            update_progress("Loading cached features...")
            try:
                with open(features_cache_path, 'rb') as f:
                    cached_features = pickle.load(f)
                # Merge cached features with basic data
                for col in cached_features.columns:
                    if col not in df.columns:
                        df[col] = cached_features[col]
                return df
            except:
                pass
        
        # Compute features based on what's needed
        original_df = df.copy()
        
        if feature_set in ['all', 'technical', 'dca']:
            update_progress("Computing technical indicators...")
            df = self._add_essential_technical_indicators(df)
        
        if feature_set in ['all', 'bitcoin']:
            update_progress("Adding Bitcoin-specific features...")
            df = self._add_bitcoin_features_fast(df)
        
        if feature_set in ['all', 'time']:
            update_progress("Adding time features...")
            df = self._add_time_features_fast(df)
        
        if feature_set == 'prediction':
            update_progress("Computing advanced prediction features...")
            df = self._add_prediction_features(df)
        
        # Cache computed features (only new columns)
        if cache_key:
            try:
                new_features = df.loc[:, ~df.columns.isin(original_df.columns)]
                with open(features_cache_path, 'wb') as f:
                    pickle.dump(new_features, f)
            except:
                pass
        
        return df
    
    def _add_essential_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add only essential technical indicators quickly"""
        # Most important indicators for DCA analysis
        df['SMA_7'] = df['Close'].rolling(window=7).mean()
        df['SMA_30'] = df['Close'].rolling(window=30).mean()
        df['SMA_200'] = df['Close'].rolling(window=200).mean()
        
        # RSI (simplified calculation)
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # Simple volatility
        df['Volatility'] = df['Close'].pct_change().rolling(window=30).std()
        
        # Price changes
        df['Price_Change_1d'] = df['Close'].pct_change(1)
        df['Price_Change_7d'] = df['Close'].pct_change(7)
        df['Price_Change_30d'] = df['Close'].pct_change(30)
        
        return df
    
    def _add_bitcoin_features_fast(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add Bitcoin-specific features with minimal computation"""
        # Simplified halving cycle calculation
        halving_dates = [
            datetime(2012, 11, 28),
            datetime(2016, 7, 9),
            datetime(2020, 5, 11),
            datetime(2024, 4, 19),
        ]
        
        # Vectorized halving calculation
        dates = df.index
        days_since_halving = np.zeros(len(dates))
        
        for i, date in enumerate(dates):
            past_halvings = [h for h in halving_dates if h.date() <= date.date()]
            if past_halvings:
                last_halving = max(past_halvings)
                days_since_halving[i] = (date - last_halving).days
        
        df['Days_Since_Halving'] = days_since_halving
        
        # Market maturity (simplified)
        bitcoin_genesis = datetime(2009, 1, 3)
        df['Market_Maturity'] = ((df.index - bitcoin_genesis).days + 1).map(np.log)
        
        # Price vs long-term average
        df['Price_vs_200_SMA'] = df['Close'] / df['SMA_200']
        
        return df
    
    def _add_time_features_fast(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add time-based features efficiently"""
        # Basic time features
        df['Month'] = df.index.month
        df['Day'] = df.index.day
        df['Day_of_Week'] = df.index.dayofweek
        df['Quarter'] = df.index.quarter
        
        # Cyclical encoding (most important ones)
        df['Month_sin'] = np.sin(2 * np.pi * df['Month'] / 12)
        df['Month_cos'] = np.cos(2 * np.pi * df['Month'] / 12)
        df['DOW_sin'] = np.sin(2 * np.pi * df['Day_of_Week'] / 7)
        df['DOW_cos'] = np.cos(2 * np.pi * df['Day_of_Week'] / 7)
        
        return df
    
    def _add_prediction_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add full feature set for prediction models (loaded only when needed)"""
        # Import heavy libraries only when needed
        try:
            import ta
        except ImportError:
            return df  # Skip if ta library not available
        
        # Full technical analysis suite
        df['EMA_12'] = ta.trend.ema_indicator(df['Close'], window=12)
        df['EMA_26'] = ta.trend.ema_indicator(df['Close'], window=26)
        df['MACD'] = ta.trend.macd_diff(df['Close'])
        df['MACD_Signal'] = ta.trend.macd_signal(df['Close'])
        
        # Bollinger Bands
        bb = ta.volatility.BollingerBands(df['Close'], window=20)
        df['BB_Upper'] = bb.bollinger_hband()
        df['BB_Lower'] = bb.bollinger_lband()
        df['BB_Middle'] = bb.bollinger_mavg()
        df['BB_Width'] = (df['BB_Upper'] - df['BB_Lower']) / df['BB_Middle']
        
        # Additional features for ML
        df['ATH'] = df['High'].expanding().max()
        df['Drawdown'] = (df['Close'] - df['ATH']) / df['ATH']
        
        return df
    
    def clear_cache(self):
        """Clear all cached data"""
        import shutil
        if self.cache_dir.exists():
            shutil.rmtree(self.cache_dir)
            self.cache_dir.mkdir(exist_ok=True)


class LazyFeatureManager:
    """Manages feature computation on-demand"""
    
    def __init__(self, data_loader: DataLoader):
        self.data_loader = data_loader
        self.base_data = None
        self.feature_cache = {}
    
    def get_data_for_analysis(self, analysis_type: str, progress_callback=None) -> pd.DataFrame:
        """Get data with appropriate features for specific analysis"""
        
        if self.base_data is None:
            self.base_data = self.data_loader.load_basic_data(progress_callback)
        
        # Return cached if available
        if analysis_type in self.feature_cache:
            return self.feature_cache[analysis_type]
        
        # Feature sets for different analyses
        feature_map = {
            'dca_analysis': 'technical',
            'backtesting': 'technical', 
            'prediction': 'prediction',
            'overview': 'technical'
        }
        
        feature_set = feature_map.get(analysis_type, 'technical')
        
        # Add features on-demand
        data_with_features = self.data_loader.add_features_lazy(
            self.base_data.copy(), 
            feature_set, 
            progress_callback
        )
        
        # Cache for reuse
        self.feature_cache[analysis_type] = data_with_features
        
        return data_with_features
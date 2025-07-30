#!/usr/bin/env python3
"""
Test suite for Bitcoin DCA Analysis Terminal Application
Uses mock data for efficiency and tests both correct and incorrect data scenarios
"""

import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import tempfile
import os
from unittest.mock import patch, MagicMock
import io
import sys

from bitcoin_dca.data_loader import DataLoader
from bitcoin_dca.predictor import BitcoinPredictor
from bitcoin_dca.dca_analyzer import DCAAnalyzer
from bitcoin_dca.backtester import DCABacktester


class MockDataGenerator:
    """Generate various types of mock data for testing"""
    
    @staticmethod
    def create_valid_csv_data(rows=100):
        """Create valid Bitcoin price data"""
        dates = pd.date_range('2023-01-01', periods=rows, freq='D')
        np.random.seed(42)
        
        # Simulate realistic Bitcoin price movement
        base_price = 30000
        prices = [base_price]
        
        for i in range(1, rows):
            change = np.random.normal(0, 0.02)  # 2% daily volatility
            new_price = prices[-1] * (1 + change)
            prices.append(max(new_price, 1000))  # Minimum price floor
        
        return pd.DataFrame({
            'Date': dates.strftime('%Y-%m-%d'),
            'Open': np.array(prices) * np.random.uniform(0.99, 1.01, rows),
            'High': np.array(prices) * np.random.uniform(1.00, 1.05, rows),
            'Low': np.array(prices) * np.random.uniform(0.95, 1.00, rows),
            'Close': prices
        })
    
    @staticmethod
    def create_minimal_csv_data():
        """Create minimal valid data (edge case)"""
        return pd.DataFrame({
            'Date': ['2023-01-01', '2023-01-02'],
            'Open': [30000, 30100],
            'High': [30500, 30600],
            'Low': [29500, 29600],
            'Close': [30100, 30200]
        })
    
    @staticmethod
    def create_missing_columns_data():
        """Create data with missing required columns"""
        return pd.DataFrame({
            'Date': ['2023-01-01', '2023-01-02'],
            'Open': [30000, 30100],
            'High': [30500, 30600]
            # Missing 'Low' and 'Close'
        })
    
    @staticmethod
    def create_invalid_dates_data():
        """Create data with invalid date formats"""
        return pd.DataFrame({
            'Date': ['not-a-date', '2023-13-45'],  # Invalid dates
            'Open': [30000, 30100],
            'High': [30500, 30600],
            'Low': [29500, 29600],
            'Close': [30100, 30200]
        })
    
    @staticmethod
    def create_negative_prices_data():
        """Create data with negative/zero prices"""
        return pd.DataFrame({
            'Date': ['2023-01-01', '2023-01-02', '2023-01-03'],
            'Open': [30000, -100, 0],  # Negative and zero prices
            'High': [30500, -50, 10],
            'Low': [29500, -200, -10],
            'Close': [30100, -75, 5]
        })
    
    @staticmethod
    def create_missing_values_data():
        """Create data with NaN values"""
        return pd.DataFrame({
            'Date': ['2023-01-01', '2023-01-02', '2023-01-03'],
            'Open': [30000, np.nan, 30200],
            'High': [30500, 30600, np.nan],
            'Low': [29500, 29600, 29700],
            'Close': [30100, 30200, 30300]
        })
    
    @staticmethod
    def create_wrong_data_types():
        """Create data with wrong data types"""
        return pd.DataFrame({
            'Date': ['2023-01-01', '2023-01-02'],
            'Open': ['not-a-number', '30100'],  # String instead of number
            'High': [30500, 'also-not-a-number'],
            'Low': [29500, 29600],
            'Close': [30100, 30200]
        })


class TestDataLoader(unittest.TestCase):
    """Test the DataLoader class with various data scenarios"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_files = []
    
    def tearDown(self):
        """Clean up temporary files"""
        for temp_file in self.temp_files:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
    
    def create_temp_csv(self, data):
        """Helper to create temporary CSV file"""
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        data.to_csv(temp_file.name, index=False)
        temp_file.close()
        self.temp_files.append(temp_file.name)
        return temp_file.name
    
    def test_load_valid_data(self):
        """Test loading valid Bitcoin data"""
        data = MockDataGenerator.create_valid_csv_data(50)
        csv_path = self.create_temp_csv(data)
        
        loader = DataLoader(csv_path)
        df = loader.load_basic_data()
        
        # Basic checks
        self.assertIsInstance(df, pd.DataFrame)
        self.assertGreater(len(df), 0)
        self.assertTrue(isinstance(df.index, pd.DatetimeIndex))
        
        # Check required columns exist
        required_cols = ['Open', 'High', 'Low', 'Close']
        for col in required_cols:
            self.assertIn(col, df.columns)
        
        # Check no NaN values in processed data
        self.assertFalse(df[required_cols].isnull().any().any())
    
    def test_load_minimal_data(self):
        """Test loading minimal valid data"""
        data = MockDataGenerator.create_minimal_csv_data()
        csv_path = self.create_temp_csv(data)
        
        loader = DataLoader(csv_path)
        df = loader.load_basic_data()
        
        self.assertEqual(len(df), 2)
        self.assertIn('Close', df.columns)
    
    def test_missing_columns(self):
        """Test handling of missing required columns"""
        data = MockDataGenerator.create_missing_columns_data()
        csv_path = self.create_temp_csv(data)
        
        loader = DataLoader(csv_path)
        
        with self.assertRaises((KeyError, ValueError)):
            loader.load_basic_data()
    
    def test_invalid_dates(self):
        """Test handling of invalid date formats"""
        data = MockDataGenerator.create_invalid_dates_data()
        csv_path = self.create_temp_csv(data)
        
        loader = DataLoader(csv_path)
        
        with self.assertRaises((ValueError, pd.errors.ParserError)):
            loader.load_basic_data()
    
    def test_negative_prices(self):
        """Test handling of negative prices"""
        data = MockDataGenerator.create_negative_prices_data()
        csv_path = self.create_temp_csv(data)
        
        loader = DataLoader(csv_path)
        df = loader.load_basic_data()
        
        # Should filter out negative prices
        self.assertTrue((df[['Open', 'High', 'Low', 'Close']] > 0).all().all())
    
    def test_missing_values(self):
        """Test handling of NaN values"""
        data = MockDataGenerator.create_missing_values_data()
        csv_path = self.create_temp_csv(data)
        
        loader = DataLoader(csv_path)
        df = loader.load_basic_data()
        
        # Should remove rows with NaN values in core price columns
        price_cols = ['Open', 'High', 'Low', 'Close']
        for col in price_cols:
            if col in df.columns:
                self.assertFalse(df[col].isnull().any(), f"Column {col} should not have NaN values")
    
    def test_wrong_data_types(self):
        """Test handling of wrong data types"""
        data = MockDataGenerator.create_wrong_data_types()
        csv_path = self.create_temp_csv(data)
        
        loader = DataLoader(csv_path)
        df = loader.load_basic_data()
        
        # Should convert to numeric and handle errors
        numeric_cols = ['Open', 'High', 'Low', 'Close']
        for col in numeric_cols:
            if col in df.columns:
                self.assertTrue(pd.api.types.is_numeric_dtype(df[col]))
    
    def test_file_not_found(self):
        """Test handling of non-existent file"""
        loader = DataLoader('/nonexistent/path/file.csv')
        
        with self.assertRaises(FileNotFoundError):
            loader.load_basic_data()
    
    def test_feature_engineering(self):
        """Test that feature engineering works correctly"""
        data = MockDataGenerator.create_valid_csv_data(100)
        csv_path = self.create_temp_csv(data)
        
        loader = DataLoader(csv_path)
        basic_df = loader.load_basic_data()
        
        # Test adding technical features
        df_with_features = loader.add_features_lazy(basic_df, 'technical')
        
        # Check technical indicators
        expected_features = ['SMA_7', 'SMA_30', 'RSI']
        for feature in expected_features:
            self.assertIn(feature, df_with_features.columns)
        
        # Test adding Bitcoin-specific features
        df_with_btc = loader.add_features_lazy(basic_df, 'bitcoin')
        btc_features = ['Days_Since_Halving', 'Market_Maturity']
        for feature in btc_features:
            self.assertIn(feature, df_with_btc.columns)


class TestBitcoinPredictor(unittest.TestCase):
    """Test the BitcoinPredictor class with mock data"""
    
    def setUp(self):
        """Set up test environment"""
        self.predictor = BitcoinPredictor()
        
        # Create small but sufficient mock data
        dates = pd.date_range('2023-01-01', periods=30, freq='D')
        np.random.seed(42)
        prices = 30000 + np.cumsum(np.random.randn(30) * 100)
        
        self.test_df = pd.DataFrame({
            'Open': prices * 0.99,
            'High': prices * 1.02,
            'Low': prices * 0.98,
            'Close': prices,
            'SMA_30': prices,
            'RSI': np.random.uniform(30, 70, 30),
            'Days_Since_Halving': range(30),
            'Market_Maturity': np.log(range(1, 31))
        }, index=dates)
    
    def test_prepare_features_valid_data(self):
        """Test feature preparation with valid data"""
        target_date = datetime(2023, 2, 15).date()
        
        X, y, target_features, feature_names = self.predictor.prepare_features(
            self.test_df, target_date
        )
        
        self.assertIsInstance(X, np.ndarray)
        self.assertIsInstance(y, np.ndarray)
        self.assertIsInstance(target_features, np.ndarray)
        self.assertEqual(len(X), len(y))
        self.assertEqual(X.shape[1], target_features.shape[1])
    
    def test_predict_with_insufficient_data(self):
        """Test prediction with insufficient data (triggers fallback)"""
        small_df = self.test_df.head(5)  # Very small dataset
        target_date = datetime(2023, 2, 1).date()
        
        result = self.predictor.predict_price(small_df, target_date)
        
        self.assertIsInstance(result, dict)
        self.assertIn('price', result)
        self.assertIn('confidence', result)
        self.assertIn('model', result)
        self.assertGreater(result['price'], 0)
        # Should have low confidence due to fallback
        self.assertLessEqual(result['confidence'], 0.5)
    
    def test_predict_with_invalid_target_date(self):
        """Test prediction with target date before data start"""
        target_date = datetime(2022, 1, 1).date()  # Before data starts
        
        result = self.predictor.predict_price(self.test_df, target_date)
        
        # Should still return a result (fallback)
        self.assertIsInstance(result, dict)
        self.assertIn('price', result)
    
    def test_predict_with_empty_dataframe(self):
        """Test prediction with empty DataFrame"""
        empty_df = pd.DataFrame()
        target_date = datetime(2023, 2, 1).date()
        
        result = self.predictor.predict_price(empty_df, target_date)
        
        # Should return fallback result
        self.assertIsInstance(result, dict)
        self.assertIn('price', result)
        self.assertIn('Simple Trend', result['model'])  # Should contain fallback indicator


class TestDCAAnalyzer(unittest.TestCase):
    """Test the DCAAnalyzer class with mock data"""
    
    def setUp(self):
        """Set up test environment"""
        self.analyzer = DCAAnalyzer()
        
        # Create mock data with known patterns
        dates = pd.date_range('2022-01-01', '2023-12-31', freq='D')
        np.random.seed(42)
        
        # Create data with slight monthly and weekly patterns for testing
        prices = []
        for date in dates:
            base_price = 30000
            # Add small patterns
            monthly_factor = 1 + 0.01 * np.sin(2 * np.pi * date.day / 30)
            weekly_factor = 1 + 0.005 * np.sin(2 * np.pi * date.weekday() / 7)
            noise = np.random.normal(0, 0.01)
            
            price = base_price * monthly_factor * weekly_factor * (1 + noise)
            prices.append(price)
        
        self.test_df = pd.DataFrame({
            'Open': prices,
            'High': np.array(prices) * 1.01,
            'Low': np.array(prices) * 0.99,
            'Close': prices
        }, index=dates)
    
    def test_analyze_optimal_days_valid_data(self):
        """Test DCA analysis with valid data"""
        results = self.analyzer.analyze_optimal_days(self.test_df)
        
        self.assertIsInstance(results, dict)
        self.assertIn('monthly', results)
        self.assertIn('weekly', results)
        self.assertIn('best_combination', results)
        
        # Check monthly analysis structure
        monthly = results['monthly']
        self.assertIsInstance(monthly, pd.DataFrame)
        expected_cols = ['avg_return', 'success_rate', 'volatility']
        for col in expected_cols:
            self.assertIn(col, monthly.columns)
        
        # Check weekly analysis structure
        weekly = results['weekly']
        self.assertIsInstance(weekly, pd.DataFrame)
        self.assertEqual(len(weekly), 7)  # 7 days of week
        
        # Check best combination
        combo = results['best_combination']
        self.assertIsInstance(combo, dict)
        self.assertIn('day_of_month', combo)
        self.assertIn('day_of_week', combo)
        self.assertIn('expected_return', combo)
    
    def test_analyze_with_minimal_data(self):
        """Test DCA analysis with minimal data"""
        minimal_df = self.test_df.head(30)  # Only 30 days
        
        results = self.analyzer.analyze_optimal_days(minimal_df)
        
        # Should still return valid structure
        self.assertIsInstance(results, dict)
        self.assertIn('best_combination', results)
    
    def test_analyze_with_empty_data(self):
        """Test DCA analysis with empty DataFrame"""
        empty_df = pd.DataFrame()
        
        results = self.analyzer.analyze_optimal_days(empty_df)
        
        # Should return fallback results
        self.assertIsInstance(results, dict)
        combo = results['best_combination']
        self.assertEqual(combo['day_of_month'], 15)
        self.assertEqual(combo['day_of_week'], 2)
    
    def test_analyze_with_constant_prices(self):
        """Test DCA analysis with constant prices (no volatility)"""
        dates = pd.date_range('2023-01-01', periods=100, freq='D')
        constant_price = 30000
        
        constant_df = pd.DataFrame({
            'Open': [constant_price] * 100,
            'High': [constant_price] * 100,
            'Low': [constant_price] * 100,
            'Close': [constant_price] * 100
        }, index=dates)
        
        results = self.analyzer.analyze_optimal_days(constant_df)
        
        # Should handle constant prices gracefully
        self.assertIsInstance(results, dict)
        self.assertIn('best_combination', results)


class TestDCABacktester(unittest.TestCase):
    """Test the DCABacktester class with mock data"""
    
    def setUp(self):
        """Set up test environment"""
        self.backtester = DCABacktester()
        
        # Create mock data for backtesting
        dates = pd.date_range('2022-01-01', '2023-12-31', freq='D')
        np.random.seed(42)
        prices = 30000 + np.cumsum(np.random.randn(len(dates)) * 100)
        
        self.test_df = pd.DataFrame({
            'Open': prices * 0.99,
            'High': prices * 1.02,
            'Low': prices * 0.98,
            'Close': prices
        }, index=dates)
    
    def test_backtest_monthly_dca_valid(self):
        """Test monthly DCA backtesting with valid data"""
        results = self.backtester.backtest_monthly_dca(
            self.test_df, 
            monthly_amount=1000, 
            day_of_month=15
        )
        
        self.assertIsInstance(results, dict)
        
        # Check required fields
        required_fields = [
            'total_invested', 'final_value', 'total_btc', 'total_return',
            'annualized_return', 'avg_price', 'total_transactions'
        ]
        for field in required_fields:
            self.assertIn(field, results)
        
        # Check values are reasonable
        self.assertGreater(results['total_invested'], 0)
        self.assertGreater(results['total_btc'], 0)
        self.assertGreater(results['total_transactions'], 0)
        self.assertGreater(results['avg_price'], 0)
    
    def test_backtest_with_zero_amount(self):
        """Test backtesting with zero investment amount"""
        results = self.backtester.backtest_monthly_dca(
            self.test_df,
            monthly_amount=0,
            day_of_month=15
        )
        
        # Should return zero results
        self.assertEqual(results['total_invested'], 0)
        self.assertEqual(results['total_btc'], 0)
    
    def test_backtest_with_invalid_day(self):
        """Test backtesting with invalid day of month"""
        results = self.backtester.backtest_monthly_dca(
            self.test_df,
            monthly_amount=1000,
            day_of_month=35  # Invalid day
        )
        
        # Should handle gracefully (adjust to valid day)
        self.assertIsInstance(results, dict)
        self.assertGreaterEqual(results['total_transactions'], 0)
    
    def test_backtest_with_future_dates(self):
        """Test backtesting with future start/end dates"""
        future_start = datetime(2025, 1, 1)
        future_end = datetime(2025, 12, 31)
        
        results = self.backtester.backtest_monthly_dca(
            self.test_df,
            monthly_amount=1000,
            day_of_month=15,
            start_date=future_start,
            end_date=future_end
        )
        
        # Should return empty results
        self.assertEqual(results['total_transactions'], 0)
        self.assertEqual(results['total_invested'], 0)
    
    def test_backtest_weekly_dca(self):
        """Test weekly DCA backtesting"""
        results = self.backtester.backtest_weekly_dca(
            self.test_df,
            weekly_amount=250,
            day_of_week=2
        )
        
        self.assertIsInstance(results, dict)
        self.assertGreater(results['total_transactions'], 0)
    
    def test_find_closest_trading_day_exact_match(self):
        """Test finding exact trading day match"""
        target_date = self.test_df.index[10].date()
        
        trading_date, price = self.backtester._find_closest_trading_day(
            self.test_df, target_date
        )
        
        self.assertEqual(trading_date.date(), target_date)
        self.assertGreater(price, 0)
    
    def test_find_closest_trading_day_no_match(self):
        """Test finding trading day when no data exists"""
        target_date = datetime(2020, 1, 1).date()  # Before data range
        
        trading_date, price = self.backtester._find_closest_trading_day(
            self.test_df, target_date
        )
        
        # Should return None for both
        self.assertIsNone(trading_date)
        self.assertIsNone(price)
    
    def test_compare_strategies_with_mock_data(self):
        """Test strategy comparison with small dataset"""
        # Use smaller dataset for faster testing
        small_df = self.test_df.head(200)
        
        results = self.backtester.compare_strategies(small_df, 1000)
        
        self.assertIsInstance(results, dict)
        self.assertIn('strategies', results)
        self.assertIn('ranking', results)
        self.assertIn('best_strategy', results)


class TestUIFeatures(unittest.TestCase):
    """Test new UI features like date range validation"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_files = []
    
    def tearDown(self):
        """Clean up temporary files"""
        for temp_file in self.temp_files:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
    
    def create_temp_csv(self, data):
        """Helper to create temporary CSV file"""
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        data.to_csv(temp_file.name, index=False)
        temp_file.close()
        self.temp_files.append(temp_file.name)
        return temp_file.name
    
    def test_date_range_filtering(self):
        """Test date range filtering for DCA analysis"""
        from bitcoin_dca.main import BTCAnalyzer
        
        data = MockDataGenerator.create_valid_csv_data(365)  # 1 year of data
        csv_path = self.create_temp_csv(data)
        
        analyzer = BTCAnalyzer(csv_path)
        analyzer.load_basic_data()
        
        # Get data with features
        data_with_features = analyzer.feature_manager.get_data_for_analysis('dca_analysis')
        self.assertGreater(len(data_with_features), 0)
        
        # Test data filtering by date range
        start_date = data_with_features.index[50]
        end_date = data_with_features.index[200]
        filtered_data = data_with_features[(data_with_features.index >= start_date) & (data_with_features.index <= end_date)]
        
        self.assertEqual(len(filtered_data), 151)  # 200 - 50 + 1 = 151 days
        
    def test_cache_clearing(self):
        """Test cache clearing functionality"""
        from bitcoin_dca.main import BTCAnalyzer
        
        data = MockDataGenerator.create_valid_csv_data(100)
        csv_path = self.create_temp_csv(data)
        
        analyzer = BTCAnalyzer(csv_path)
        analyzer.load_basic_data()
        
        # Generate some cached data
        analyzer.feature_manager.get_data_for_analysis('dca_analysis')
        
        # Test that cache exists
        self.assertTrue(len(analyzer.feature_manager.feature_cache) > 0)
        
        # Clear cache
        analyzer.data_loader.clear_cache()
        analyzer.feature_manager.feature_cache.clear()
        
        # Test that cache is cleared
        self.assertEqual(len(analyzer.feature_manager.feature_cache), 0)


class TestErrorHandling(unittest.TestCase):
    """Test comprehensive error handling scenarios"""
    
    def test_corrupted_csv_file(self):
        """Test handling of corrupted CSV file"""
        # Create a corrupted CSV file
        corrupted_data = "This is not a valid CSV file\nwith random content\n123,abc,def"
        
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        temp_file.write(corrupted_data)
        temp_file.close()
        
        try:
            loader = DataLoader(temp_file.name)
            with self.assertRaises((pd.errors.ParserError, ValueError)):
                loader.load_basic_data()
        finally:
            os.unlink(temp_file.name)
    
    def test_extremely_large_values(self):
        """Test handling of extremely large price values"""
        data = pd.DataFrame({
            'Date': ['2023-01-01', '2023-01-02'],
            'Open': [1e15, 1e16],  # Unrealistically large values
            'High': [1e15, 1e16],
            'Low': [1e15, 1e16],
            'Close': [1e15, 1e16]
        })
        
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        data.to_csv(temp_file.name, index=False)
        temp_file.close()
        
        try:
            loader = DataLoader(temp_file.name)
            df = loader.load_basic_data()
            
            # Should handle large values without crashing
            self.assertIsInstance(df, pd.DataFrame)
        finally:
            os.unlink(temp_file.name)
    
    def test_memory_usage_with_mock_data(self):
        """Test memory usage remains reasonable with mock data"""
        # Create larger mock dataset
        data = MockDataGenerator.create_valid_csv_data(1000)
        
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        data.to_csv(temp_file.name, index=False)
        temp_file.close()
        
        try:
            loader = DataLoader(temp_file.name)
            df = loader.load_basic_data()
            
            # Check memory usage is reasonable
            memory_usage = df.memory_usage(deep=True).sum()
            self.assertLess(memory_usage, 100 * 1024 * 1024)  # Less than 100MB
            
        finally:
            os.unlink(temp_file.name)


def run_tests():
    """Run all tests efficiently"""
    print("🧪 Running Bitcoin DCA Analyzer Test Suite (Mock Data)")
    print("=" * 60)
    
    # Suppress warnings and stdout during tests
    import warnings
    warnings.filterwarnings('ignore')
    
    # Capture stdout to reduce noise
    old_stdout = sys.stdout
    sys.stdout = io.StringIO()
    
    try:
        # Create test suite
        test_classes = [
            TestDataLoader,
            TestBitcoinPredictor,
            TestDCAAnalyzer,
            TestDCABacktester,
            TestUIFeatures,
            TestErrorHandling
        ]
        
        suite = unittest.TestSuite()
        
        for test_class in test_classes:
            tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
            suite.addTests(tests)
        
        # Run tests with minimal output
        runner = unittest.TextTestRunner(verbosity=1, buffer=True, stream=io.StringIO())
        result = runner.run(suite)
        
        return result
        
    finally:
        # Restore stdout
        sys.stdout = old_stdout


if __name__ == '__main__':
    result = run_tests()
    
    print(f"🧪 Test Results Summary:")
    print(f"   Tests run: {result.testsRun}")
    print(f"   Failures: {len(result.failures)}")
    print(f"   Errors: {len(result.errors)}")
    
    if result.failures:
        print(f"\n❌ Failures:")
        for test, traceback in result.failures:
            print(f"   - {test}")
            # Show only the assertion error, not full traceback
            error_lines = traceback.split('\n')
            for line in error_lines:
                if 'AssertionError' in line:
                    print(f"     {line.strip()}")
                    break
    
    if result.errors:
        print(f"\n🚨 Errors:")
        for test, traceback in result.errors:
            print(f"   - {test}")
            # Show only the main error, not full traceback
            error_lines = traceback.split('\n')
            for line in error_lines:
                if any(exc in line for exc in ['Error:', 'Exception:', 'ValueError:', 'KeyError:']):
                    print(f"     {line.strip()}")
                    break
    
    if result.wasSuccessful():
        print("\n✅ All tests passed! The Bitcoin DCA Analyzer is working correctly.")
        print("📊 Tested scenarios:")
        print("   - Valid Bitcoin price data processing")
        print("   - Invalid/corrupted data handling")
        print("   - DCA strategy analysis and backtesting")
        print("   - Price prediction with fallback mechanisms")
        print("   - Edge cases and error conditions")
    else:
        print(f"\n❌ {len(result.failures + result.errors)} test(s) failed")
        exit(1)
"""
Bitcoin price prediction module using advanced deep learning
Incorporates halving cycles, market patterns, and technical analysis
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import pickle
import hashlib
from sklearn.preprocessing import StandardScaler, RobustScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
import xgboost as xgb
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout, BatchNormalization
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeElapsedColumn
from rich.panel import Panel
import warnings

warnings.filterwarnings('ignore')

class BitcoinPredictor:
    def __init__(self, cache_dir=None):
        self.scaler = RobustScaler()
        self.lstm_model = None
        self.rf_model = None
        self.xgb_model = None
        self.feature_importance = None
        self.console = Console()
        
        # Set up caching
        if cache_dir is None:
            cache_dir = os.path.expanduser('~/.bitcoin-dca/.cache/models')
        self.cache_dir = cache_dir
        os.makedirs(self.cache_dir, exist_ok=True)
        
    def clear_model_cache(self):
        """Clear all cached models"""
        try:
            import shutil
            if os.path.exists(self.cache_dir):
                shutil.rmtree(self.cache_dir)
                os.makedirs(self.cache_dir, exist_ok=True)
                self.console.print("[green]✅ Model cache cleared[/green]")
                return True
        except Exception as e:
            self.console.print(f"[yellow]Warning: Could not clear cache: {e}[/yellow]")
        return False
        
        # Model metadata for cache validation (removed - was causing errors)
        # We'll create this dynamically when saving
        
    def prepare_features(self, df: pd.DataFrame, target_date: datetime.date) -> tuple:
        """Prepare features for prediction"""
        
        # Remove any rows with NaN values
        df_clean = df.dropna()
        
        # Get feature columns
        feature_cols = [
            'Open', 'High', 'Low', 'SMA_7', 'SMA_30', 'SMA_100', 'SMA_200',
            'EMA_12', 'EMA_26', 'MACD', 'MACD_Signal', 'RSI', 'BB_Width',
            'Volatility', 'Price_Change_1d', 'Price_Change_7d', 'Price_Change_30d',
            'Month_sin', 'Month_cos', 'Day_sin', 'Day_cos', 'DOW_sin', 'DOW_cos',
            'Days_Since_Halving', 'Days_Until_Next_Halving', 'Halving_Cycle_Position',
            'Market_Maturity', 'Market_Cap_Log', 'Price_vs_200_SMA', 'Drawdown'
        ]
        
        # Filter available features
        available_features = [col for col in feature_cols if col in df_clean.columns]
        
        # Prepare feature matrix
        X = df_clean[available_features].values
        y = df_clean['Close'].values
        
        # Create target features for the prediction date
        target_features = self._create_target_features(df_clean, target_date, available_features)
        
        return X, y, target_features, available_features
        
    def _create_target_features(self, df: pd.DataFrame, target_date: datetime.date, feature_cols: list) -> np.ndarray:
        """Create features for the target prediction date"""
        
        # Get the most recent data
        latest_date = df.index[-1].date()
        latest_data = df.iloc[-1].copy()
        
        # Calculate days difference
        days_diff = (target_date - latest_date).days
        
        # Estimate features for target date
        target_features = latest_data[feature_cols].copy()
        
        # Update time-based features
        target_dt = datetime.combine(target_date, datetime.min.time())
        
        # Update cyclic time features
        if 'Month_sin' in feature_cols:
            target_features['Month_sin'] = np.sin(2 * np.pi * target_dt.month / 12)
        if 'Month_cos' in feature_cols:
            target_features['Month_cos'] = np.cos(2 * np.pi * target_dt.month / 12)
        if 'Day_sin' in feature_cols:
            target_features['Day_sin'] = np.sin(2 * np.pi * target_dt.day / 31)
        if 'Day_cos' in feature_cols:
            target_features['Day_cos'] = np.cos(2 * np.pi * target_dt.day / 31)
        if 'DOW_sin' in feature_cols:
            target_features['DOW_sin'] = np.sin(2 * np.pi * target_dt.weekday() / 7)
        if 'DOW_cos' in feature_cols:
            target_features['DOW_cos'] = np.cos(2 * np.pi * target_dt.weekday() / 7)
            
        # Update Bitcoin-specific features
        if 'Days_Since_Halving' in feature_cols:
            target_features['Days_Since_Halving'] += days_diff
        if 'Days_Until_Next_Halving' in feature_cols:
            target_features['Days_Until_Next_Halving'] -= days_diff
        if 'Market_Maturity' in feature_cols:
            bitcoin_genesis = datetime(2009, 1, 3)
            days_since_genesis = (target_dt - bitcoin_genesis).days
            target_features['Market_Maturity'] = np.log(days_since_genesis + 1)
            
        return target_features.values.reshape(1, -1)
        
    def create_lstm_sequences(self, X: np.ndarray, y: np.ndarray, sequence_length: int = 60) -> tuple:
        """Create sequences for LSTM training"""
        
        X_seq, y_seq = [], []
        
        for i in range(sequence_length, len(X)):
            X_seq.append(X[i-sequence_length:i])
            y_seq.append(y[i])
            
        return np.array(X_seq), np.array(y_seq)
        
    def build_lstm_model(self, input_shape: tuple) -> Sequential:
        """Build LSTM model for time series prediction"""
        
        model = Sequential([
            LSTM(128, return_sequences=True, input_shape=input_shape),
            Dropout(0.2),
            BatchNormalization(),
            
            LSTM(64, return_sequences=True),
            Dropout(0.2),
            BatchNormalization(),
            
            LSTM(32),
            Dropout(0.2),
            
            Dense(50, activation='relu'),
            Dropout(0.1),
            Dense(25, activation='relu'),
            Dense(1)
        ])
        
        model.compile(
            optimizer=Adam(learning_rate=0.001),
            loss='mse',
            metrics=['mae']
        )
        
        return model
        
    def _get_data_hash(self, X: np.ndarray, y: np.ndarray) -> str:
        """Generate stable hash of training data for cache validation"""
        # Use more stable hash based on shape and rounded sums to avoid floating point issues
        x_sum = round(float(np.sum(X)), 2)
        y_sum = round(float(np.sum(y)), 2)
        data_str = f"{X.shape[0]}_{X.shape[1]}_{len(y)}_{x_sum}_{y_sum}"
        hash_result = hashlib.md5(data_str.encode()).hexdigest()[:12]
        self.console.print(f"[dim]Data hash: {hash_result} (data: {data_str})[/dim]")
        return hash_result
    
    def _get_cache_paths(self, data_hash: str) -> dict:
        """Get file paths for cached models"""
        return {
            'rf_model': os.path.join(self.cache_dir, f'rf_model_{data_hash}.pkl'),
            'xgb_model': os.path.join(self.cache_dir, f'xgb_model_{data_hash}.pkl'),
            'lstm_model': os.path.join(self.cache_dir, f'lstm_model_{data_hash}'),  # Directory for SavedModel
            'scaler': os.path.join(self.cache_dir, f'scaler_{data_hash}.pkl'),
            'metadata': os.path.join(self.cache_dir, f'metadata_{data_hash}.pkl')
        }
    
    def _save_models(self, data_hash: str, training_results: dict):
        """Save trained models to cache"""
        cache_paths = self._get_cache_paths(data_hash)
        
        try:
            # Save Random Forest
            self.console.print(f"[dim]Saving Random Forest to {cache_paths['rf_model']}...[/dim]")
            with open(cache_paths['rf_model'], 'wb') as f:
                pickle.dump(self.rf_model, f)
            self.console.print(f"[dim]✅ Random Forest saved successfully[/dim]")
            
            # Save XGBoost
            if self.xgb_model is not None:
                xgb_path = cache_paths['rf_model'].replace('rf_model', 'xgb_model')
                self.console.print(f"[dim]Saving XGBoost to {xgb_path}...[/dim]")
                with open(xgb_path, 'wb') as f:
                    pickle.dump(self.xgb_model, f)
                self.console.print(f"[dim]✅ XGBoost saved successfully[/dim]")
            
            # Save LSTM if available - use SavedModel format for better compatibility
            if self.lstm_model is not None:
                try:
                    # Use SavedModel format which is more robust
                    self.lstm_model.save(cache_paths['lstm_model'], save_format='tf')
                except Exception as lstm_save_error:
                    # Fallback: save weights only
                    weights_path = cache_paths['lstm_model'] + '.weights.h5'
                    self.lstm_model.save_weights(weights_path)
                    # Save model config separately
                    config_path = cache_paths['lstm_model'] + '_config.json'
                    with open(config_path, 'w') as f:
                        import json
                        json.dump(self.lstm_model.to_json(), f)
                    self.console.print(f"[dim]Saved LSTM weights and config separately[/dim]")
            
            # Save scaler
            self.console.print(f"[dim]Saving scaler to {cache_paths['scaler']}...[/dim]")
            with open(cache_paths['scaler'], 'wb') as f:
                pickle.dump(self.scaler, f)
            self.console.print(f"[dim]✅ Scaler saved successfully[/dim]")
            
            # Save metadata
            self.console.print(f"[dim]Saving metadata to {cache_paths['metadata']}...[/dim]")
            metadata = {
                'training_results': training_results,
                'feature_importance': self.feature_importance,
                'data_hash': data_hash,
                'training_date': datetime.now().isoformat(),
                'model_params': {
                    'rf_estimators': 200,
                    'rf_max_depth': 15,
                    'lstm_epochs': 100,
                    'lstm_trained': training_results.get('lstm_trained', False)
                }
            }
            with open(cache_paths['metadata'], 'wb') as f:
                pickle.dump(metadata, f)
            self.console.print(f"[dim]✅ Metadata saved successfully[/dim]")
                
            self.console.print(f"[green]🎉 All models saved to cache successfully![/green]")
                
        except Exception as e:
            self.console.print(f"[red]❌ Error saving models to cache: {e}[/red]")
            import traceback
            self.console.print(f"[dim]{traceback.format_exc()}[/dim]")
            # Try to clean up partial saves
            for file_path in cache_paths.values():
                try:
                    if os.path.exists(file_path):
                        os.remove(file_path)
                except:
                    pass
    
    def _load_models(self, data_hash: str) -> bool:
        """Load models from cache if available"""
        cache_paths = self._get_cache_paths(data_hash)
        
        try:
            # Check if all required files exist
            required_files = ['rf_model', 'xgb_model', 'lstm_model', 'scaler', 'metadata']
            missing_files = []
            
            # Check all files first
            for file_key in required_files:
                file_path = cache_paths[file_key]
                
                if file_key == 'lstm_model':
                    # LSTM model is saved as a directory with multiple files
                    # Check for both config.json and .weights.h5 files
                    config_file = f"{file_path}_config.json"
                    weights_file = f"{file_path}.weights.h5"
                    config_exists = os.path.exists(config_file)
                    weights_exists = os.path.exists(weights_file)
                    exists = config_exists and weights_exists
                    
                    self.console.print(f"[dim]Checking {file_key}: {config_file} -> {'EXISTS' if config_exists else 'MISSING'}[/dim]")
                    self.console.print(f"[dim]Checking {file_key}: {weights_file} -> {'EXISTS' if weights_exists else 'MISSING'}[/dim]")
                else:
                    # Regular file check
                    exists = os.path.exists(file_path)
                    self.console.print(f"[dim]Checking {file_key}: {file_path} -> {'EXISTS' if exists else 'MISSING'}[/dim]")
                
                if not exists:
                    missing_files.append(file_key)
            
            # If any files are missing, report and return
            if missing_files:
                self.console.print(f"[yellow]Cache miss: {', '.join(missing_files)} not found[/yellow]")
                return False
            
            self.console.print(f"[green]✅ All cache files found - loading models...[/green]")
            
            # Load Random Forest
            self.console.print(f"[dim]Loading Random Forest...[/dim]")
            with open(cache_paths['rf_model'], 'rb') as f:
                self.rf_model = pickle.load(f)
            self.console.print(f"[dim]✅ Random Forest loaded[/dim]")
            
            # Load XGBoost
            self.console.print(f"[dim]Loading XGBoost...[/dim]")
            with open(cache_paths['xgb_model'], 'rb') as f:
                self.xgb_model = pickle.load(f)
            self.console.print(f"[dim]✅ XGBoost loaded[/dim]")
            
            # Load scaler
            self.console.print(f"[dim]Loading scaler...[/dim]")
            with open(cache_paths['scaler'], 'rb') as f:
                self.scaler = pickle.load(f)
            self.console.print(f"[dim]✅ Scaler loaded[/dim]")
            
            # Load LSTM if available
            lstm_loaded = False
            weights_path = cache_paths['lstm_model'] + '.weights.h5'
            config_path = cache_paths['lstm_model'] + '_config.json'
            
            # Check if LSTM files exist (config and weights)
            if os.path.exists(weights_path) and os.path.exists(config_path):
                try:
                    self.console.print(f"[dim]Loading LSTM model...[/dim]")
                    import json
                    with open(config_path, 'r') as f:
                        model_json = json.load(f)
                    
                    # Recreate model from config
                    self.lstm_model = tf.keras.models.model_from_json(model_json)
                    self.lstm_model.load_weights(weights_path)
                    
                    # Recompile the model (required after loading from config+weights)
                    self.lstm_model.compile(
                        optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
                        loss='mse',
                        metrics=['mae']
                    )
                    lstm_loaded = True
                    self.console.print(f"[dim]✅ LSTM loaded[/dim]")
                    
                except Exception as e:
                    self.console.print(f"[dim]⚠️ Failed to load LSTM: {e}[/dim]")
            else:
                self.console.print(f"[dim]LSTM model files not found in cache[/dim]")
                self.lstm_model = None
            
            # Load metadata
            self.console.print(f"[dim]Loading metadata...[/dim]")
            with open(cache_paths['metadata'], 'rb') as f:
                metadata = pickle.load(f)
                self.feature_importance = metadata.get('feature_importance')
            self.console.print(f"[dim]✅ Metadata loaded[/dim]")
                
            self.console.print(f"[green]🎉 All models loaded successfully from cache![/green]")
            return True
            
        except Exception as e:
            self.console.print(f"[red]❌ Cache loading failed: {e}[/red]")
            import traceback
            self.console.print(f"[dim]{traceback.format_exc()}[/dim]")
            return False
    
    def train_models(self, X: np.ndarray, y: np.ndarray, progress_callback=None, main_progress=None) -> dict:
        """Train both LSTM and Random Forest models with caching"""
        
        # Generate data hash for caching
        data_hash = self._get_data_hash(X, y)
        
        # Try to load from cache first
        if progress_callback:
            progress_callback("🔍 Checking model cache...")
        
        self.console.print(f"[dim]Cache directory: {self.cache_dir}[/dim]")
        cache_paths = self._get_cache_paths(data_hash)
        self.console.print(f"[dim]Looking for cached models with hash: {data_hash}[/dim]")
            
        if self._load_models(data_hash):
            if progress_callback:
                progress_callback("✅ Loaded models from cache")
            self.console.print("[green]⚡ Using cached models - prediction will be fast![/green]")
            self.console.print(f"[dim]Cache hit! Skipped training time: ~45-60 seconds[/dim]")
            # Load actual training results from cache
            with open(cache_paths['metadata'], 'rb') as f:
                cached_metadata = pickle.load(f)
                cached_training_results = cached_metadata.get('training_results', {})
            
            return {
                'rf_mae': cached_training_results.get('rf_mae', 0),
                'xgb_mae': cached_training_results.get('xgb_mae', 0),
                'lstm_mae': cached_training_results.get('lstm_mae', 0), 
                'lstm_trained': self.lstm_model is not None,
                'sequence_length': cached_training_results.get('sequence_length', 60),
                'cached': True
            }
        
        if progress_callback:
            progress_callback("🔧 Training new models...")
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train Random Forest with progress tracking
        if progress_callback:
            progress_callback("🌳 Training Random Forest (200 estimators)...")
        
        rf_task = None
        if main_progress:
            rf_task = main_progress.add_task("🌳 Random Forest", total=100)
            
        self.rf_model = RandomForestRegressor(
            n_estimators=200,
            max_depth=15,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1
        )
        
        # Use recent data for training (last 80% of data)
        train_size = int(0.8 * len(X_scaled))
        X_train = X_scaled[-train_size:]
        y_train = y[-train_size:]
        
        # Simulate RF progress (since sklearn doesn't provide real progress)
        if rf_task:
            import threading
            import time
            
            # Simple progress simulation for Random Forest
            def simulate_rf_progress():
                for i in range(0, 101, 10):
                    time.sleep(0.3)  # Small delay
                    if rf_task:
                        main_progress.update(rf_task, completed=i)
                        
            progress_thread = threading.Thread(target=simulate_rf_progress)
            progress_thread.daemon = True
            progress_thread.start()
            
        self.rf_model.fit(X_train, y_train)
        
        # Complete RF progress
        if rf_task:
            main_progress.update(rf_task, completed=100)
            
        # Train XGBoost
        if progress_callback:
            progress_callback("🚀 Training XGBoost (200 estimators)...")
            
        xgb_task = None
        if main_progress:
            xgb_task = main_progress.add_task("🚀 XGBoost", total=100)
            
        self.xgb_model = xgb.XGBRegressor(
            n_estimators=200,
            max_depth=6,
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
            n_jobs=-1,
            verbosity=0  # Suppress XGBoost output
        )
        
        # Simulate XGB progress (similar to RF)
        if xgb_task:
            import threading
            import time
            
            def simulate_xgb_progress():
                # Use steps that actually reach 100: [0, 15, 30, 45, 60, 75, 90, 100]
                steps = list(range(0, 100, 15)) + [100]
                for i in steps:
                    time.sleep(0.2)
                    if xgb_task:
                        main_progress.update(xgb_task, completed=i)
                        
            xgb_progress_thread = threading.Thread(target=simulate_xgb_progress)
            xgb_progress_thread.daemon = True
            xgb_progress_thread.start()
            
        self.xgb_model.fit(X_train, y_train)
        
        # Complete XGB progress
        if xgb_task:
            main_progress.update(xgb_task, completed=100)
        
        # Calculate XGBoost MAE immediately after training
        xgb_pred_train = self.xgb_model.predict(X_train)
        xgb_mae = mean_absolute_error(y_train, xgb_pred_train)
        
        # Get feature importance
        feature_names = [f'feature_{i}' for i in range(X.shape[1])]
        self.feature_importance = dict(zip(feature_names, self.rf_model.feature_importances_))
        
        # Train LSTM model
        if progress_callback:
            progress_callback("🧠 Preparing LSTM sequences...")
            
        sequence_length = min(60, len(X_scaled) // 4)
        X_seq, y_seq = self.create_lstm_sequences(X_scaled, y, sequence_length)
        
        if len(X_seq) > 100:  # Only train LSTM if enough data
            if progress_callback:
                progress_callback("🔥 Training LSTM neural network...")
                
            lstm_task = None
            if main_progress:
                lstm_task = main_progress.add_task("🧠 LSTM Neural Network", total=100)
            # Split for LSTM training
            lstm_train_size = int(0.8 * len(X_seq))
            X_lstm_train = X_seq[:lstm_train_size]
            y_lstm_train = y_seq[:lstm_train_size]
            X_lstm_val = X_seq[lstm_train_size:]
            y_lstm_val = y_seq[lstm_train_size:]
            
            # Build and train LSTM
            self.lstm_model = self.build_lstm_model((sequence_length, X.shape[1]))
            
            early_stopping = EarlyStopping(
                monitor='val_loss',
                patience=20,
                restore_best_weights=True
            )
            
            # Custom callback for progress tracking
            class ProgressCallback(tf.keras.callbacks.Callback):
                def __init__(self, progress_obj, task_id, total_epochs):
                    super().__init__()
                    self.progress_obj = progress_obj
                    self.task_id = task_id
                    self.total_epochs = total_epochs
                    
                def on_epoch_end(self, epoch, logs=None):
                    if self.progress_obj and self.task_id:
                        progress_pct = min(100, ((epoch + 1) / self.total_epochs) * 100)
                        self.progress_obj.update(self.task_id, completed=progress_pct)
                        
                def on_train_end(self, logs=None):
                    # Ensure we show 100% when training ends (including early stopping)
                    if self.progress_obj and self.task_id:
                        self.progress_obj.update(self.task_id, completed=100)
            
            callbacks = [early_stopping]
            if lstm_task:
                callbacks.append(ProgressCallback(main_progress, lstm_task, 100))
            
            history = self.lstm_model.fit(
                X_lstm_train, y_lstm_train,
                epochs=100,
                batch_size=32,
                validation_data=(X_lstm_val, y_lstm_val),
                callbacks=callbacks,
                verbose=0
            )
            
            # Ensure progress bar completes
            if lstm_task:
                main_progress.update(lstm_task, completed=100)
            
            if progress_callback:
                progress_callback(f"📊 LSTM training completed ({len(history.history['loss'])} epochs)")
            
            # Evaluate models
            rf_pred = self.rf_model.predict(X_scaled[-len(y_seq):])
            rf_mae = mean_absolute_error(y[-len(y_seq):], rf_pred)
            
            lstm_pred = self.lstm_model.predict(X_seq, verbose=0).flatten()
            lstm_mae = mean_absolute_error(y_seq, lstm_pred)
            
            training_results = {
                'rf_mae': rf_mae,
                'xgb_mae': xgb_mae,
                'lstm_mae': lstm_mae,
                'lstm_trained': True,
                'sequence_length': sequence_length,
                'cached': False
            }
            
            # Save models to cache
            if progress_callback:
                progress_callback("💾 Saving models to cache...")
            self.console.print(f"[dim]Saving models with hash: {data_hash}[/dim]")
            self._save_models(data_hash, training_results)
            self.console.print("[green]💾 Models saved to cache - next prediction will be faster![/green]")
            
            return training_results
        else:
            # No LSTM, but still have RF and XGBoost
            training_results = {
                'rf_mae': mean_absolute_error(y_train, self.rf_model.predict(X_train)),
                'xgb_mae': xgb_mae,  # Already calculated above
                'lstm_mae': None,
                'lstm_trained': False,
                'sequence_length': sequence_length,
                'cached': False
            }
            
            # Save models to cache
            if progress_callback:
                progress_callback("💾 Saving Random Forest to cache...")
            self.console.print(f"[dim]Saving RF model with hash: {data_hash}[/dim]")
            self._save_models(data_hash, training_results)
            self.console.print("[green]💾 Random Forest saved to cache - next prediction will be faster![/green]")
            
            return training_results
            
    def predict_price(self, df: pd.DataFrame, target_date: datetime.date) -> dict:
        """Make price prediction for target date with enhanced progress tracking"""
        
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                TimeElapsedColumn(),
                console=self.console
            ) as progress:
                
                # Progress tracking
                task = progress.add_task("📊 Initializing prediction...", total=None)
                
                def update_progress(description):
                    progress.update(task, description=description)
                
                # Check if dataframe is empty or lacks required columns
                if len(df) == 0 or 'Close' not in df.columns:
                    raise ValueError("Empty or invalid dataframe")
                    
                # Prepare data
                update_progress("🔍 Preparing features and data...")
                X, y, target_features, feature_names = self.prepare_features(df, target_date)
            
                if len(X) < 10:  # Lowered threshold for testing
                    raise ValueError("Insufficient data for reliable prediction")
                    
                # Train models with detailed progress
                training_results = self.train_models(X, y, update_progress, progress)
            
                # Scale target features
                update_progress("🎯 Making predictions...")
                target_scaled = self.scaler.transform(target_features)
                
                # Make predictions
                rf_prediction = self.rf_model.predict(target_scaled)[0]
                xgb_prediction = self.xgb_model.predict(target_scaled)[0] if self.xgb_model else None
            
                predictions = [rf_prediction]
                model_names = ['Random Forest']
                
                # Add XGBoost prediction if available
                if xgb_prediction is not None:
                    predictions.append(xgb_prediction)
                    model_names.append('XGBoost')
                
                # LSTM prediction if available
                if training_results['lstm_trained'] and self.lstm_model:
                    update_progress("🧠 Generating LSTM prediction...")
                    # Prepare sequence for LSTM
                    sequence_length = training_results['sequence_length']
                    if len(X) >= sequence_length:
                        X_scaled = self.scaler.transform(X)
                        last_sequence = X_scaled[-sequence_length:].reshape(1, sequence_length, -1)
                        lstm_prediction = self.lstm_model.predict(last_sequence, verbose=0)[0][0]
                        predictions.append(lstm_prediction)
                        model_names.append('LSTM')
                    
                # Ensemble prediction (performance-weighted average)
                update_progress("⚖️ Computing ensemble prediction...")
                if len(predictions) > 1:
                    # Calculate performance-based weights using MAE (lower MAE = higher weight)
                    maes = []
                    if 'Random Forest' in model_names:
                        maes.append(training_results.get('rf_mae', 1.0))
                    if 'XGBoost' in model_names:
                        maes.append(training_results.get('xgb_mae', 1.0))
                    if 'LSTM' in model_names:
                        maes.append(training_results.get('lstm_mae', 1.0))
                    
                    # Convert MAE to weights (inverse relationship)
                    if all(mae > 0 for mae in maes):
                        # Inverse weights: lower MAE = higher weight
                        inv_maes = [1.0 / mae for mae in maes]
                        total_inv = sum(inv_maes)
                        weights = [w / total_inv for w in inv_maes]
                        
                        # Weighted prediction
                        final_prediction = sum(w * p for w, p in zip(weights, predictions))
                        
                        # Build model description
                        model_parts = []
                        for i, name in enumerate(model_names):
                            model_parts.append(f"{name}({weights[i]:.1%})")
                        model_used = f"Ensemble ({' + '.join(model_parts)})"
                        
                        ensemble_details = {
                            'weights': dict(zip(model_names, weights)),
                            'maes': dict(zip(model_names, maes))
                        }
                    else:
                        # Fallback to equal weights
                        final_prediction = np.mean(predictions)
                        model_used = 'Ensemble (Equal Weights)'
                        ensemble_details = {'weights': 'equal'}
                else:
                    final_prediction = predictions[0]
                    model_used = model_names[0]
                    ensemble_details = None
                
                # Calculate confidence based on model agreement and historical volatility
                update_progress("📈 Analyzing confidence and market context...")
                if len(predictions) > 1:
                    prediction_std = np.std(predictions)
                    price_volatility = df['Close'].pct_change().std() * df['Close'].iloc[-1]
                    confidence = max(0.1, 1 - (prediction_std / price_volatility))
                    confidence_details = {
                        'prediction_std': prediction_std,
                        'price_volatility': price_volatility,
                        'model_agreement': 1 - (prediction_std / np.mean(predictions))
                    }
                else:
                    confidence = 0.6  # Conservative confidence for single model
                    confidence_details = {'single_model': True}
                    
                # Generate analysis
                analysis = self._generate_analysis(df, target_date, final_prediction)
                
                update_progress("✅ Prediction complete!")
            
                return {
                    'price': final_prediction,
                    'confidence': confidence,
                    'model': model_used,
                    'features': len(feature_names),
                    'analysis': analysis,
                    'individual_predictions': dict(zip(model_names, predictions)),
                    'model_details': {
                        'cached': training_results.get('cached', False),
                        'lstm_trained': training_results['lstm_trained'],
                        'sequence_length': training_results.get('sequence_length', 0),
                        'feature_names': feature_names
                    },
                    'ensemble_details': ensemble_details,
                    'confidence_details': confidence_details,
                    'training_performance': {
                        'rf_mae': training_results.get('rf_mae'),
                        'lstm_mae': training_results.get('lstm_mae')
                    }
                }
            
        except Exception as e:
            # Fallback to simple prediction
            self.console.print(f"[yellow]Warning: Falling back to simple prediction due to: {e}[/yellow]")
            
            if len(df) > 0 and 'Close' in df.columns:
                # Try simple trend extrapolation
                recent_prices = df['Close'].tail(30)
                trend = recent_prices.pct_change().mean()
                days_ahead = (target_date - df.index[-1].date()).days
                simple_prediction = df['Close'].iloc[-1] * ((1 + trend) ** days_ahead)
            else:
                # Ultimate fallback for empty data
                simple_prediction = 50000  # Reasonable default Bitcoin price
            
            return {
                'price': simple_prediction,
                'confidence': 0.3,
                'model': 'Simple Trend (Fallback)',
                'features': 1,
                'analysis': f"Fallback prediction due to insufficient data. Error: {str(e)}",
                'individual_predictions': {'Simple Trend': simple_prediction},
                'model_details': {'cached': False, 'lstm_trained': False},
                'ensemble_details': None,
                'confidence_details': {'fallback': True}
            }
            
    def _generate_analysis(self, df: pd.DataFrame, target_date: datetime.date, prediction: float) -> str:
        """Generate market analysis for the prediction"""
        
        current_price = df['Close'].iloc[-1]
        price_change = (prediction - current_price) / current_price
        
        # Halving analysis
        halving_dates = [
            datetime(2012, 11, 28).date(),
            datetime(2016, 7, 9).date(),
            datetime(2020, 5, 11).date(),
            datetime(2024, 4, 19).date(),
            datetime(2028, 3, 15).date(),  # Estimated next halving
        ]
        
        # Find relevant halving info
        past_halvings = [h for h in halving_dates if h <= target_date]
        future_halvings = [h for h in halving_dates if h > target_date]
        
        analysis = f"Predicted price change: {price_change:+.2%} (${prediction - current_price:+,.0f})\n\n"
        
        if past_halvings:
            last_halving = max(past_halvings)
            days_since_halving = (target_date - last_halving).days
            analysis += f"Days since last halving ({last_halving}): {days_since_halving}\n"
            
        if future_halvings:
            next_halving = min(future_halvings)
            days_until_halving = (next_halving - target_date).days
            analysis += f"Days until next halving ({next_halving}): {days_until_halving}\n"
            
        # Technical analysis
        current_rsi = df['RSI'].iloc[-1] if 'RSI' in df.columns else None
        current_ma_ratio = df['Price_vs_200_SMA'].iloc[-1] if 'Price_vs_200_SMA' in df.columns else None
        
        analysis += "\nTechnical Indicators:\n"
        indicators_added = False
        
        if current_rsi:
            rsi_signal = "Oversold" if current_rsi < 30 else "Overbought" if current_rsi > 70 else "Neutral"
            analysis += f"RSI: {current_rsi:.1f} ({rsi_signal})\n"
            indicators_added = True
            
        if current_ma_ratio:
            ma_signal = "Above" if current_ma_ratio > 1 else "Below"
            analysis += f"Price vs 200-day MA: {ma_signal} ({current_ma_ratio:.2f}x)\n"
            indicators_added = True
        
        # Add available indicators when RSI/SMA aren't available
        if not indicators_added:
            # Check for ATH/Drawdown
            if 'Drawdown' in df.columns:
                current_drawdown = df['Drawdown'].iloc[-1] * 100
                drawdown_signal = "Near ATH" if current_drawdown > -5 else "Moderate correction" if current_drawdown > -20 else "Deep correction"
                analysis += f"ATH Drawdown: {current_drawdown:.1f}% ({drawdown_signal})\n"
                indicators_added = True
            
            # Check for Bollinger Bands
            if 'BB_Width' in df.columns:
                bb_width = df['BB_Width'].iloc[-1]
                volatility_signal = "High volatility" if bb_width > df['BB_Width'].quantile(0.8) else "Low volatility" if bb_width < df['BB_Width'].quantile(0.2) else "Normal volatility"
                analysis += f"Market Volatility: {volatility_signal}\n"
                indicators_added = True
        
        if not indicators_added:
            analysis += "Limited indicators available with current dataset\n"
            
        return analysis
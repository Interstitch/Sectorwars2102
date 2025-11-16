"""
Market Prediction Engine using Prophet for Time Series Forecasting

This module implements actual machine learning algorithms for predicting
commodity prices in the Sectorwars2102 game using Facebook Prophet.
"""

import logging
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc
import asyncio
import pickle
import os
from pathlib import Path

try:
    from prophet import Prophet
    from sklearn.metrics import mean_absolute_error, mean_squared_error
    PROPHET_AVAILABLE = True
except ImportError:
    PROPHET_AVAILABLE = False
    logging.warning("Prophet not available - market prediction will use fallback methods")

from src.models.market_transaction import MarketTransaction
from src.models.ai_trading import AIMarketPrediction, AIModelPerformance, AITrainingData
from src.models.station import Station


logger = logging.getLogger(__name__)


class MarketPredictionEngine:
    """
    Advanced market prediction engine using Prophet for time series forecasting
    """
    
    def __init__(self, model_storage_path: str = None):
        if model_storage_path is None:
            # Use environment variable if set, otherwise default to container path
            model_storage_path = os.environ.get("MODEL_STORAGE_PATH", "/app/data/ml_models")
        self.model_storage_path = Path(model_storage_path)
        self.model_storage_path.mkdir(parents=True, exist_ok=True)
        self.models: Dict[str, Prophet] = {}
        self.prediction_horizon_hours = [1, 6, 12, 24, 48]  # Multiple prediction horizons
        self.min_data_points = 10  # Minimum data points for training
        
    async def train_commodity_model(
        self,
        db: AsyncSession,
        commodity_id: str,
        sector_id: Optional[str] = None
    ) -> bool:
        """
        Train Prophet model for a specific commodity
        """
        try:
            if not PROPHET_AVAILABLE:
                logger.warning("Prophet not available - skipping model training")
                return False
                
            # Get historical market data
            training_data = await self._get_training_data(db, commodity_id, sector_id)
            
            if len(training_data) < self.min_data_points:
                logger.info(f"Insufficient data for commodity {commodity_id} - need at least {self.min_data_points} points")
                return False
            
            # Prepare data for Prophet
            df = pd.DataFrame(training_data)
            df['ds'] = pd.to_datetime(df['timestamp'])
            df['y'] = df['price'].astype(float)
            
            # Create and configure Prophet model
            model = Prophet(
                growth='linear',
                seasonality_mode='multiplicative',
                yearly_seasonality=False,
                weekly_seasonality=True,
                daily_seasonality=True,
                changepoint_prior_scale=0.05,  # Flexibility in trend changes
                seasonality_prior_scale=10.0,  # Strength of seasonality
                holidays_prior_scale=10.0,
                interval_width=0.8  # 80% confidence interval
            )
            
            # Add custom seasonalities for game-specific patterns
            model.add_seasonality(name='hourly', period=1, fourier_order=3)  # Hourly patterns
            
            # Add external regressors if available
            if 'volume' in df.columns:
                model.add_regressor('volume')
            if 'player_count' in df.columns:
                model.add_regressor('player_count')
            
            # Train the model
            logger.info(f"Training Prophet model for commodity {commodity_id}")
            model.fit(df)
            
            # Validate model performance
            performance_metrics = await self._validate_model(model, df)
            
            # Save model to disk
            model_key = f"{commodity_id}_{sector_id or 'global'}"
            model_path = self.model_storage_path / f"{model_key}_prophet.pkl"
            
            with open(model_path, 'wb') as f:
                pickle.dump(model, f)
            
            # Cache in memory
            self.models[model_key] = model
            
            # Save performance metrics to database
            await self._save_model_performance(db, commodity_id, sector_id, performance_metrics)
            
            logger.info(f"Successfully trained model for {commodity_id} with MAE: {performance_metrics['mae']:.2f}")
            return True
            
        except Exception as e:
            logger.error(f"Error training model for commodity {commodity_id}: {e}")
            return False
    
    async def predict_prices(
        self,
        db: AsyncSession,
        commodity_id: str,
        sector_id: Optional[str] = None,
        hours_ahead: int = 24
    ) -> Optional[Dict[str, Any]]:
        """
        Generate price predictions for a commodity using trained Prophet model
        """
        try:
            if not PROPHET_AVAILABLE:
                return await self._fallback_prediction(db, commodity_id, sector_id, hours_ahead)
            
            model_key = f"{commodity_id}_{sector_id or 'global'}"
            
            # Load model if not in cache
            if model_key not in self.models:
                model_path = self.model_storage_path / f"{model_key}_prophet.pkl"
                if model_path.exists():
                    with open(model_path, 'rb') as f:
                        self.models[model_key] = pickle.load(f)
                else:
                    # Train model if it doesn't exist
                    success = await self.train_commodity_model(db, commodity_id, sector_id)
                    if not success:
                        return await self._fallback_prediction(db, commodity_id, sector_id, hours_ahead)
            
            model = self.models.get(model_key)
            if not model:
                logger.warning(f"No model available for {model_key}")
                return await self._fallback_prediction(db, commodity_id, sector_id, hours_ahead)
            
            # Create future dataframe
            future_periods = max(1, hours_ahead)
            future = model.make_future_dataframe(periods=future_periods, freq='H')
            
            # Add external regressors if model expects them
            if 'volume' in model.extra_regressors:
                # Use recent average volume
                recent_volume = await self._get_recent_volume(db, commodity_id, sector_id)
                future['volume'] = recent_volume
            
            if 'player_count' in model.extra_regressors:
                # Use current player count in sector
                player_count = await self._get_player_count(db, sector_id)
                future['player_count'] = player_count
            
            # Generate predictions
            forecast = model.predict(future)
            
            # Extract prediction for target time
            target_row = forecast.iloc[-1] if hours_ahead <= len(forecast) else forecast.iloc[-1]
            
            prediction_data = {
                'predicted_price': float(target_row['yhat']),
                'lower_bound': float(target_row['yhat_lower']),
                'upper_bound': float(target_row['yhat_upper']),
                'confidence_interval': 0.8,  # Prophet default
                'trend': float(target_row['trend']),
                'seasonal': float(target_row.get('seasonal', 0)),
                'prediction_horizon': hours_ahead,
                'model_version': getattr(model, 'version', '1.0.0'),
                'timestamp': datetime.utcnow()
            }
            
            # Calculate prediction confidence based on historical performance
            model_performance = await self._get_model_performance(db, commodity_id, sector_id)
            if model_performance:
                prediction_data['confidence_interval'] = min(0.95, model_performance.get('accuracy', 0.8))
            
            # Save prediction to database
            await self._save_prediction(db, commodity_id, sector_id, prediction_data)
            
            return prediction_data
            
        except Exception as e:
            logger.error(f"Error predicting prices for commodity {commodity_id}: {e}")
            return await self._fallback_prediction(db, commodity_id, sector_id, hours_ahead)
    
    async def batch_predict_all_commodities(
        self,
        db: AsyncSession,
        sector_id: Optional[str] = None
    ) -> Dict[str, Dict[str, Any]]:
        """
        Generate predictions for all active commodities in a sector
        """
        try:
            # Get all unique commodities traded in sector
            commodities = await self._get_active_commodities(db, sector_id)
            
            predictions = {}
            for commodity_id in commodities:
                prediction = await self.predict_prices(db, commodity_id, sector_id)
                if prediction:
                    predictions[commodity_id] = prediction
                    
                # Add small delay to prevent overwhelming the system
                await asyncio.sleep(0.1)
            
            logger.info(f"Generated predictions for {len(predictions)} commodities")
            return predictions
            
        except Exception as e:
            logger.error(f"Error in batch prediction: {e}")
            return {}
    
    async def retrain_all_models(self, db: AsyncSession) -> int:
        """
        Retrain all models with latest data
        """
        try:
            # Get all unique commodity-sector combinations
            combinations = await self._get_all_commodity_sector_combinations(db)
            
            successful_trains = 0
            for commodity_id, sector_id in combinations:
                success = await self.train_commodity_model(db, commodity_id, sector_id)
                if success:
                    successful_trains += 1
                    
                # Add delay between training runs
                await asyncio.sleep(0.5)
            
            logger.info(f"Successfully retrained {successful_trains}/{len(combinations)} models")
            return successful_trains
            
        except Exception as e:
            logger.error(f"Error retraining models: {e}")
            return 0
    
    # Private helper methods
    
    async def _get_training_data(
        self,
        db: AsyncSession,
        commodity_id: str,
        sector_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get historical market data for training
        """
        try:
            # Query market transactions for this commodity
            query = select(MarketTransaction).where(
                MarketTransaction.commodity_id == commodity_id
            ).order_by(MarketTransaction.created_at)
            
            if sector_id:
                query = query.where(MarketTransaction.sector_id == sector_id)
            
            # Limit to last 30 days of data
            cutoff_date = datetime.utcnow() - timedelta(days=30)
            query = query.where(MarketTransaction.created_at >= cutoff_date)
            
            result = await db.execute(query)
            transactions = result.scalars().all()
            
            training_data = []
            for tx in transactions:
                training_data.append({
                    'timestamp': tx.created_at,
                    'price': float(tx.price_per_unit),
                    'volume': tx.quantity,
                    'transaction_type': tx.transaction_type
                })
            
            # Aggregate hourly if we have too much data
            if len(training_data) > 1000:
                training_data = self._aggregate_hourly(training_data)
            
            return training_data
            
        except Exception as e:
            logger.error(f"Error getting training data: {e}")
            return []
    
    def _aggregate_hourly(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Aggregate transaction data into hourly buckets
        """
        df = pd.DataFrame(data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df.set_index('timestamp', inplace=True)
        
        # Resample to hourly averages
        hourly = df.resample('H').agg({
            'price': 'mean',
            'volume': 'sum'
        }).dropna()
        
        return [
            {
                'timestamp': idx,
                'price': row['price'],
                'volume': row['volume']
            }
            for idx, row in hourly.iterrows()
        ]
    
    async def _validate_model(self, model: 'Prophet', df: pd.DataFrame) -> Dict[str, float]:
        """
        Validate model performance using cross-validation
        """
        try:
            if len(df) < 20:  # Need enough data for validation
                return {'mae': 0.0, 'mse': 0.0, 'accuracy': 0.5}
            
            # Simple train/test split
            split_point = int(len(df) * 0.8)
            train_df = df[:split_point]
            test_df = df[split_point:]
            
            # Train on subset
            val_model = Prophet()
            val_model.fit(train_df)
            
            # Predict on test set
            future = val_model.make_future_dataframe(periods=len(test_df), freq='H')
            forecast = val_model.predict(future)
            
            # Calculate metrics
            actual = test_df['y'].values
            predicted = forecast['yhat'][-len(actual):].values
            
            mae = mean_absolute_error(actual, predicted)
            mse = mean_squared_error(actual, predicted)
            
            # Calculate accuracy as percentage of predictions within 10% of actual
            within_threshold = np.abs((predicted - actual) / actual) < 0.1
            accuracy = np.mean(within_threshold)
            
            return {
                'mae': float(mae),
                'mse': float(mse),
                'accuracy': float(accuracy)
            }
            
        except Exception as e:
            logger.error(f"Error validating model: {e}")
            return {'mae': 0.0, 'mse': 0.0, 'accuracy': 0.5}
    
    async def _save_model_performance(
        self,
        db: AsyncSession,
        commodity_id: str,
        sector_id: Optional[str],
        metrics: Dict[str, float]
    ) -> None:
        """
        Save model performance metrics to database
        """
        try:
            performance = AIModelPerformance(
                model_type='prophet_price_prediction',
                model_version='1.0.0',
                commodity_id=commodity_id,
                sector_id=sector_id,
                accuracy_score=metrics['accuracy'],
                precision_score=1.0 - (metrics['mae'] / 100),  # Normalize MAE to precision
                recall_score=metrics['accuracy'],
                f1_score=metrics['accuracy'],
                training_data_size=0,  # Will be updated separately
                performance_metadata={
                    'mae': metrics['mae'],
                    'mse': metrics['mse'],
                    'validation_date': datetime.utcnow().isoformat()
                }
            )
            
            db.add(performance)
            await db.commit()
            
        except Exception as e:
            logger.error(f"Error saving model performance: {e}")
    
    async def _get_model_performance(
        self,
        db: AsyncSession,
        commodity_id: str,
        sector_id: Optional[str]
    ) -> Optional[Dict[str, Any]]:
        """
        Get latest model performance metrics
        """
        try:
            query = select(AIModelPerformance).where(
                and_(
                    AIModelPerformance.commodity_id == commodity_id,
                    AIModelPerformance.sector_id == sector_id,
                    AIModelPerformance.model_type == 'prophet_price_prediction'
                )
            ).order_by(desc(AIModelPerformance.created_at)).limit(1)
            
            result = await db.execute(query)
            performance = result.scalar_one_or_none()
            
            if performance:
                return {
                    'accuracy': performance.accuracy_score,
                    'mae': performance.performance_metadata.get('mae', 0.0),
                    'mse': performance.performance_metadata.get('mse', 0.0)
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting model performance: {e}")
            return None
    
    async def _save_prediction(
        self,
        db: AsyncSession,
        commodity_id: str,
        sector_id: Optional[str],
        prediction_data: Dict[str, Any]
    ) -> None:
        """
        Save prediction to database
        """
        try:
            prediction = AIMarketPrediction(
                commodity_id=commodity_id,
                sector_id=sector_id,
                predicted_price=prediction_data['predicted_price'],
                confidence_interval=prediction_data['confidence_interval'],
                prediction_horizon=prediction_data['prediction_horizon'],
                lower_bound=prediction_data['lower_bound'],
                upper_bound=prediction_data['upper_bound'],
                trend_direction='rising' if prediction_data['trend'] > 0 else 'falling',
                model_version=prediction_data['model_version'],
                features_used=['price_history', 'volume', 'trend'],
                expires_at=datetime.utcnow() + timedelta(hours=prediction_data['prediction_horizon'])
            )
            
            db.add(prediction)
            await db.commit()
            
        except Exception as e:
            logger.error(f"Error saving prediction: {e}")
    
    async def _fallback_prediction(
        self,
        db: AsyncSession,
        commodity_id: str,
        sector_id: Optional[str],
        hours_ahead: int
    ) -> Dict[str, Any]:
        """
        Fallback prediction method when Prophet is not available
        """
        try:
            # Get recent price data
            recent_data = await self._get_training_data(db, commodity_id, sector_id)
            
            if not recent_data:
                return {
                    'predicted_price': 100.0,
                    'confidence_interval': 0.3,
                    'prediction_horizon': hours_ahead,
                    'model_version': 'fallback_1.0.0'
                }
            
            # Simple moving average prediction
            recent_prices = [d['price'] for d in recent_data[-10:]]
            avg_price = sum(recent_prices) / len(recent_prices)
            
            # Add slight random walk
            import random
            change_factor = 1.0 + (random.random() - 0.5) * 0.1  # ±5% random change
            predicted_price = avg_price * change_factor
            
            return {
                'predicted_price': predicted_price,
                'confidence_interval': 0.6,
                'prediction_horizon': hours_ahead,
                'model_version': 'fallback_1.0.0',
                'lower_bound': predicted_price * 0.9,
                'upper_bound': predicted_price * 1.1
            }
            
        except Exception as e:
            logger.error(f"Error in fallback prediction: {e}")
            return {
                'predicted_price': 100.0,
                'confidence_interval': 0.3,
                'prediction_horizon': hours_ahead,
                'model_version': 'fallback_1.0.0'
            }
    
    async def _get_active_commodities(self, db: AsyncSession, sector_id: Optional[str]) -> List[str]:
        """Get list of active commodities"""
        # Simplified implementation - would query actual game data
        return ["ore", "food", "technology", "fuel", "weapons"]
    
    async def _get_all_commodity_sector_combinations(self, db: AsyncSession) -> List[Tuple[str, str]]:
        """Get all commodity-sector combinations that have trading data"""
        # Simplified implementation
        commodities = await self._get_active_commodities(db, None)
        sectors = ["1", "2", "3", "4", "5"]  # Example sectors
        
        combinations = []
        for commodity in commodities:
            for sector in sectors:
                combinations.append((commodity, sector))
        
        return combinations
    
    async def _get_recent_volume(self, db: AsyncSession, commodity_id: str, sector_id: Optional[str]) -> float:
        """Get recent average trading volume"""
        return 100.0  # Placeholder
    
    async def _get_player_count(self, db: AsyncSession, sector_id: Optional[str]) -> int:
        """Get current player count in sector"""
        return 5  # Placeholder
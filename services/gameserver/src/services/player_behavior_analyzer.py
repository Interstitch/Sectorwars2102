"""
Player Behavior Analysis Engine using Machine Learning

This module implements player trading pattern recognition, risk assessment,
and behavioral clustering using scikit-learn algorithms.
"""

import logging
import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc, func
import asyncio
import pickle
import os
from pathlib import Path

try:
    from sklearn.cluster import KMeans, DBSCAN
    from sklearn.preprocessing import StandardScaler, MinMaxScaler
    from sklearn.ensemble import RandomForestClassifier, IsolationForest
    from sklearn.metrics import silhouette_score
    from sklearn.decomposition import PCA
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logging.warning("scikit-learn not available - player analysis will use fallback methods")

from src.models.player import Player
from src.models.market_transaction import MarketTransaction
from src.models.ai_trading import PlayerTradingProfile, AITrainingData
from src.models.sector import Sector


logger = logging.getLogger(__name__)


class PlayerBehaviorAnalyzer:
    """
    Advanced player behavior analysis using machine learning algorithms
    """
    
    def __init__(self, model_storage_path: str = "/app/data/ml_models"):
        self.model_storage_path = Path(model_storage_path)
        self.model_storage_path.mkdir(parents=True, exist_ok=True)
        self.scaler = StandardScaler() if SKLEARN_AVAILABLE else None
        self.clustering_model = None
        self.risk_classifier = None
        self.anomaly_detector = None
        
        # Trading pattern categories
        self.trading_patterns = {
            'conservative': {'risk_threshold': 0.3, 'profit_variance': 0.2},
            'moderate': {'risk_threshold': 0.6, 'profit_variance': 0.4},
            'aggressive': {'risk_threshold': 0.8, 'profit_variance': 0.6},
            'day_trader': {'trades_per_day': 10, 'avg_hold_time': 2},
            'long_term': {'trades_per_day': 2, 'avg_hold_time': 24},
            'arbitrage': {'sector_diversity': 0.8, 'profit_margin': 0.1}
        }
        
    async def analyze_player_behavior(
        self,
        db: AsyncSession,
        player_id: str,
        analysis_period_days: int = 30
    ) -> Dict[str, Any]:
        """
        Comprehensive analysis of a player's trading behavior
        """
        try:
            if not SKLEARN_AVAILABLE:
                return await self._fallback_analysis(db, player_id, analysis_period_days)
            
            # Get player trading data
            trading_data = await self._get_player_trading_data(db, player_id, analysis_period_days)
            
            if len(trading_data) < 5:
                logger.info(f"Insufficient trading data for player {player_id}")
                return await self._create_basic_profile(db, player_id)
            
            # Extract behavioral features
            features = self._extract_behavioral_features(trading_data)
            
            # Classify trading style
            trading_style = await self._classify_trading_style(features)
            
            # Assess risk tolerance
            risk_tolerance = self._assess_risk_tolerance(trading_data, features)
            
            # Detect anomalies in behavior
            anomalies = await self._detect_behavioral_anomalies(trading_data, features)
            
            # Calculate performance metrics
            performance = self._calculate_performance_metrics(trading_data)
            
            # Predict future behavior patterns
            predictions = await self._predict_future_behavior(features, trading_data)
            
            analysis_result = {
                'player_id': player_id,
                'analysis_date': datetime.utcnow(),
                'trading_style': trading_style,
                'risk_tolerance': risk_tolerance,
                'performance_metrics': performance,
                'behavioral_features': features,
                'anomalies': anomalies,
                'predictions': predictions,
                'recommendation_preferences': self._generate_recommendation_preferences(trading_style, risk_tolerance),
                'confidence_score': self._calculate_analysis_confidence(len(trading_data), features)
            }
            
            # Update player's trading profile
            await self._update_player_profile(db, player_id, analysis_result)
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"Error analyzing player behavior for {player_id}: {e}")
            return await self._fallback_analysis(db, player_id, analysis_period_days)
    
    async def cluster_players_by_behavior(
        self,
        db: AsyncSession,
        min_trades: int = 10
    ) -> Dict[str, List[str]]:
        """
        Cluster all players into behavioral groups using K-means clustering
        """
        try:
            if not SKLEARN_AVAILABLE:
                logger.warning("Clustering not available without scikit-learn")
                return {}
            
            # Get all players with sufficient trading data
            players_data = await self._get_all_players_trading_data(db, min_trades)
            
            if len(players_data) < 10:
                logger.info("Insufficient players for meaningful clustering")
                return {}
            
            # Extract features for all players
            feature_matrix = []
            player_ids = []
            
            for player_id, trading_data in players_data.items():
                features = self._extract_behavioral_features(trading_data)
                feature_vector = self._features_to_vector(features)
                feature_matrix.append(feature_vector)
                player_ids.append(player_id)
            
            # Normalize features
            feature_matrix = np.array(feature_matrix)
            normalized_features = self.scaler.fit_transform(feature_matrix)
            
            # Determine optimal number of clusters
            optimal_k = self._find_optimal_clusters(normalized_features)
            
            # Perform K-means clustering
            kmeans = KMeans(n_clusters=optimal_k, random_state=42, n_init=10)
            cluster_labels = kmeans.fit_predict(normalized_features)
            
            # Save clustering model
            model_path = self.model_storage_path / "player_clustering_model.pkl"
            with open(model_path, 'wb') as f:
                pickle.dump({'kmeans': kmeans, 'scaler': self.scaler}, f)
            
            # Group players by cluster
            clusters = {}
            for i, player_id in enumerate(player_ids):
                cluster_id = f"cluster_{cluster_labels[i]}"
                if cluster_id not in clusters:
                    clusters[cluster_id] = []
                clusters[cluster_id].append(player_id)
            
            # Analyze cluster characteristics
            cluster_analysis = self._analyze_clusters(normalized_features, cluster_labels, players_data)
            
            logger.info(f"Successfully clustered {len(player_ids)} players into {optimal_k} groups")
            
            return {
                'clusters': clusters,
                'cluster_analysis': cluster_analysis,
                'optimal_k': optimal_k,
                'silhouette_score': silhouette_score(normalized_features, cluster_labels)
            }
            
        except Exception as e:
            logger.error(f"Error clustering players: {e}")
            return {}
    
    async def detect_unusual_behavior(
        self,
        db: AsyncSession,
        player_id: str,
        lookback_days: int = 7
    ) -> Dict[str, Any]:
        """
        Detect unusual trading behavior that might indicate problems or opportunities
        """
        try:
            if not SKLEARN_AVAILABLE:
                return {'unusual_behavior': False, 'reason': 'Analysis not available'}
            
            # Get recent and historical trading data
            recent_data = await self._get_player_trading_data(db, player_id, lookback_days)
            historical_data = await self._get_player_trading_data(db, player_id, 90)  # 3 months
            
            if len(historical_data) < 20:
                return {'unusual_behavior': False, 'reason': 'Insufficient historical data'}
            
            # Extract features for both periods
            recent_features = self._extract_behavioral_features(recent_data)
            historical_features = self._extract_behavioral_features(historical_data)
            
            # Compare patterns
            deviations = self._calculate_feature_deviations(recent_features, historical_features)
            
            # Use isolation forest for anomaly detection
            if not self.anomaly_detector:
                self.anomaly_detector = IsolationForest(contamination=0.1, random_state=42)
                
                # Train on historical data
                historical_vectors = []
                for i in range(max(1, len(historical_data) - 10), len(historical_data)):
                    week_data = historical_data[max(0, i-7):i]
                    if week_data:
                        features = self._extract_behavioral_features(week_data)
                        vector = self._features_to_vector(features)
                        historical_vectors.append(vector)
                
                if historical_vectors:
                    self.anomaly_detector.fit(historical_vectors)
            
            # Check if recent behavior is anomalous
            recent_vector = self._features_to_vector(recent_features)
            is_anomaly = self.anomaly_detector.predict([recent_vector])[0] == -1
            
            anomaly_score = self.anomaly_detector.score_samples([recent_vector])[0]
            
            # Identify specific unusual patterns
            unusual_patterns = []
            threshold = 2.0  # Standard deviations
            
            for feature, deviation in deviations.items():
                if abs(deviation) > threshold:
                    direction = "increased" if deviation > 0 else "decreased"
                    unusual_patterns.append({
                        'feature': feature,
                        'deviation': deviation,
                        'description': f"{feature.replace('_', ' ').title()} has {direction} significantly"
                    })
            
            return {
                'unusual_behavior': is_anomaly or len(unusual_patterns) > 0,
                'anomaly_score': float(anomaly_score),
                'unusual_patterns': unusual_patterns,
                'risk_level': 'high' if anomaly_score < -0.5 else 'medium' if anomaly_score < -0.2 else 'low',
                'recommendations': self._generate_behavior_recommendations(unusual_patterns)
            }
            
        except Exception as e:
            logger.error(f"Error detecting unusual behavior for {player_id}: {e}")
            return {'unusual_behavior': False, 'reason': f'Analysis error: {e}'}
    
    # Private helper methods
    
    async def _get_player_trading_data(
        self,
        db: AsyncSession,
        player_id: str,
        days: int
    ) -> List[Dict[str, Any]]:
        """
        Get player's trading data for analysis
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            query = select(MarketTransaction).where(
                and_(
                    MarketTransaction.player_id == player_id,
                    MarketTransaction.created_at >= cutoff_date
                )
            ).order_by(MarketTransaction.created_at)
            
            result = await db.execute(query)
            transactions = result.scalars().all()
            
            trading_data = []
            for tx in transactions:
                trading_data.append({
                    'transaction_id': str(tx.id),
                    'timestamp': tx.created_at,
                    'transaction_type': tx.transaction_type,
                    'commodity_id': tx.commodity_id,
                    'sector_id': tx.sector_id,
                    'quantity': tx.quantity,
                    'price_per_unit': float(tx.price_per_unit),
                    'total_value': float(tx.total_value),
                    'profit': float(tx.profit) if tx.profit else 0.0
                })
            
            return trading_data
            
        except Exception as e:
            logger.error(f"Error getting trading data for player {player_id}: {e}")
            return []
    
    def _extract_behavioral_features(self, trading_data: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Extract behavioral features from trading data
        """
        if not trading_data:
            return {}
        
        df = pd.DataFrame(trading_data)
        
        # Basic trading metrics
        total_trades = len(df)
        total_profit = df['profit'].sum()
        avg_profit_per_trade = df['profit'].mean()
        profit_variance = df['profit'].var()
        
        # Trading frequency
        time_span = (df['timestamp'].max() - df['timestamp'].min()).total_seconds() / 3600  # hours
        trades_per_hour = total_trades / max(1, time_span)
        
        # Commodity diversity
        unique_commodities = df['commodity_id'].nunique()
        commodity_diversity = unique_commodities / max(1, total_trades)
        
        # Sector diversity
        unique_sectors = df['sector_id'].nunique()
        sector_diversity = unique_sectors / max(1, total_trades)
        
        # Risk metrics
        profit_std = df['profit'].std()
        max_loss = df['profit'].min()
        max_gain = df['profit'].max()
        
        # Trading pattern metrics
        buy_ratio = len(df[df['transaction_type'] == 'buy']) / total_trades
        sell_ratio = len(df[df['transaction_type'] == 'sell']) / total_trades
        
        # Volume patterns
        avg_trade_size = df['total_value'].mean()
        trade_size_variance = df['total_value'].var()
        
        # Timing patterns
        df['hour'] = pd.to_datetime(df['timestamp']).dt.hour
        peak_trading_hour = df['hour'].mode().iloc[0] if not df['hour'].mode().empty else 12
        
        return {
            'total_trades': float(total_trades),
            'avg_profit_per_trade': float(avg_profit_per_trade),
            'profit_variance': float(profit_variance),
            'trades_per_hour': float(trades_per_hour),
            'commodity_diversity': float(commodity_diversity),
            'sector_diversity': float(sector_diversity),
            'profit_std': float(profit_std),
            'max_loss': float(max_loss),
            'max_gain': float(max_gain),
            'buy_ratio': float(buy_ratio),
            'sell_ratio': float(sell_ratio),
            'avg_trade_size': float(avg_trade_size),
            'trade_size_variance': float(trade_size_variance),
            'peak_trading_hour': float(peak_trading_hour),
            'risk_reward_ratio': float(max_gain / abs(max_loss)) if max_loss < 0 else 1.0
        }
    
    async def _classify_trading_style(self, features: Dict[str, float]) -> str:
        """
        Classify player's trading style based on features
        """
        try:
            # Rule-based classification for now
            if features.get('trades_per_hour', 0) > 1.0:
                return 'day_trader'
            elif features.get('sector_diversity', 0) > 0.7:
                return 'arbitrage'
            elif features.get('profit_variance', 0) > 10000:
                return 'aggressive'
            elif features.get('profit_variance', 0) < 1000:
                return 'conservative'
            else:
                return 'moderate'
                
        except Exception as e:
            logger.error(f"Error classifying trading style: {e}")
            return 'moderate'
    
    def _assess_risk_tolerance(self, trading_data: List[Dict[str, Any]], features: Dict[str, float]) -> float:
        """
        Assess player's risk tolerance (0.0 = very conservative, 1.0 = very aggressive)
        """
        try:
            # Base risk from profit variance
            variance_risk = min(1.0, features.get('profit_variance', 0) / 50000)
            
            # Risk from trade size variance
            size_risk = min(1.0, features.get('trade_size_variance', 0) / 100000)
            
            # Risk from sector/commodity diversity
            diversity_risk = (features.get('sector_diversity', 0) + features.get('commodity_diversity', 0)) / 2
            
            # Risk from max loss tolerance
            loss_risk = min(1.0, abs(features.get('max_loss', 0)) / 10000)
            
            # Weighted average
            risk_tolerance = (variance_risk * 0.3 + size_risk * 0.2 + diversity_risk * 0.3 + loss_risk * 0.2)
            
            return max(0.0, min(1.0, risk_tolerance))
            
        except Exception as e:
            logger.error(f"Error assessing risk tolerance: {e}")
            return 0.5  # Default moderate risk
    
    def _features_to_vector(self, features: Dict[str, float]) -> List[float]:
        """
        Convert features dictionary to vector for ML algorithms
        """
        vector_keys = [
            'total_trades', 'avg_profit_per_trade', 'profit_variance', 'trades_per_hour',
            'commodity_diversity', 'sector_diversity', 'profit_std', 'buy_ratio',
            'avg_trade_size', 'trade_size_variance', 'risk_reward_ratio'
        ]
        
        return [features.get(key, 0.0) for key in vector_keys]
    
    def _find_optimal_clusters(self, data: np.ndarray, max_k: int = 8) -> int:
        """
        Find optimal number of clusters using elbow method
        """
        try:
            if len(data) < 4:
                return 2
            
            max_k = min(max_k, len(data) // 2)
            silhouette_scores = []
            
            for k in range(2, max_k + 1):
                kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
                labels = kmeans.fit_predict(data)
                score = silhouette_score(data, labels)
                silhouette_scores.append(score)
            
            # Return k with highest silhouette score
            optimal_k = silhouette_scores.index(max(silhouette_scores)) + 2
            return optimal_k
            
        except Exception as e:
            logger.error(f"Error finding optimal clusters: {e}")
            return 3  # Default
    
    async def _fallback_analysis(self, db: AsyncSession, player_id: str, days: int) -> Dict[str, Any]:
        """
        Fallback analysis when ML libraries are not available
        """
        try:
            trading_data = await self._get_player_trading_data(db, player_id, days)
            
            if not trading_data:
                return await self._create_basic_profile(db, player_id)
            
            # Simple statistical analysis
            df = pd.DataFrame(trading_data)
            total_trades = len(df)
            avg_profit = df['profit'].mean()
            profit_std = df['profit'].std()
            
            # Simple risk assessment
            risk_tolerance = min(1.0, profit_std / 1000) if profit_std > 0 else 0.5
            
            # Simple style classification
            if total_trades > 50:
                style = 'active'
            elif avg_profit > 1000:
                style = 'aggressive'
            else:
                style = 'conservative'
            
            return {
                'player_id': player_id,
                'analysis_date': datetime.utcnow(),
                'trading_style': style,
                'risk_tolerance': risk_tolerance,
                'total_trades': total_trades,
                'avg_profit': avg_profit,
                'confidence_score': 0.6,
                'method': 'fallback_analysis'
            }
            
        except Exception as e:
            logger.error(f"Error in fallback analysis: {e}")
            return await self._create_basic_profile(db, player_id)
    
    async def _create_basic_profile(self, db: AsyncSession, player_id: str) -> Dict[str, Any]:
        """
        Create basic profile for new players
        """
        return {
            'player_id': player_id,
            'analysis_date': datetime.utcnow(),
            'trading_style': 'beginner',
            'risk_tolerance': 0.5,
            'total_trades': 0,
            'confidence_score': 0.3,
            'method': 'default_profile'
        }
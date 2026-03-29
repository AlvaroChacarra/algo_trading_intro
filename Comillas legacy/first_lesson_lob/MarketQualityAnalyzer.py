"""
📊 Market Quality Analyzer - Análisis Cuantitativo de Mercados

Esta clase implementa métricas profesionales de calidad de mercado utilizadas por 
traders institucionales, reguladores y académicos para evaluar la salud y eficiencia 
de los mercados financieros.

Autor: Sistema de Enseñanza LOB
Versión: 1.0
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

class MarketQualityAnalyzer:
    """
    Analizador avanzado de calidad de mercado para LOB (Limit Order Book)
    
    Esta clase calcula y visualiza métricas críticas de microestructura de mercados:
    - Spread Analysis (Quoted, Effective, Realized)
    - Market Depth & Liquidity
    - Price Impact & Market Resilience
    - Volatility & Price Discovery Efficiency
    """
    
    def __init__(self, ultimate_lob_simulator=None):
        """
        Inicializar el analizador de calidad de mercado
        
        Args:
            ultimate_lob_simulator: Instancia de UltimateOrderBookLesson con datos históricos
        """
        self.simulator = ultimate_lob_simulator
        self.metrics_cache = {}
        
        # Configuración de colores profesionales
        self.colors = {
            'bid': '#00C851',           # Verde institucional
            'ask': '#FF4444',           # Rojo institucional  
            'mid': '#FFD700',           # Dorado para mid-price
            'spread': '#FF6B35',        # Naranja para spread
            'volume': '#007BFF',        # Azul para volumen
            'volatility': '#6610F2',    # Púrpura para volatilidad
            'depth': '#20C997',         # Verde azulado para profundidad
            'impact': '#E83E8C',        # Rosa para impacto
            'background': '#1E1E1E',    # Fondo oscuro profesional
            'grid': '#404040'           # Grid sutil
        }
    
    def extract_market_data(self) -> Dict:
        """
        Extrae y estructura los datos del simulador para análisis
        
        Returns:
            Dict con series temporales de precios, spreads, volúmenes, etc.
        """
        if not self.simulator:
            raise ValueError("No se ha proporcionado un simulador LOB")
        
        if not self.simulator.mid_price_history:
            raise ValueError("No hay datos históricos en el simulador")
        
        # Extraer series temporales
        data = {
            'timestamps': list(range(len(self.simulator.mid_price_history))),
            'mid_prices': self.simulator.mid_price_history.copy(),
            'spreads': self.simulator.spread_history.copy(),
            'best_bids': self.simulator.best_bid_history.copy(),
            'best_asks': self.simulator.best_ask_history.copy(),
            'volatility': self.simulator.volatility_history.copy() if hasattr(self.simulator, 'volatility_history') else [],
            'n_periods': len(self.simulator.mid_price_history)
        }
        
        # Calcular métricas derivadas
        data['returns'] = self._calculate_returns(data['mid_prices'])
        data['log_returns'] = self._calculate_log_returns(data['mid_prices'])
        data['price_changes'] = self._calculate_price_changes(data['mid_prices'])
        
        return data
    
    def _calculate_returns(self, prices: List[float]) -> List[float]:
        """Calcula retornos simples"""
        if len(prices) < 2:
            return []
        return [(prices[i] - prices[i-1]) / prices[i-1] for i in range(1, len(prices))]
    
    def _calculate_log_returns(self, prices: List[float]) -> List[float]:
        """Calcula retornos logarítmicos"""
        if len(prices) < 2:
            return []
        return [np.log(prices[i] / prices[i-1]) for i in range(1, len(prices))]
    
    def _calculate_price_changes(self, prices: List[float]) -> List[float]:
        """Calcula cambios absolutos de precio"""
        if len(prices) < 2:
            return []
        return [prices[i] - prices[i-1] for i in range(1, len(prices))]
    
    def calculate_spread_metrics(self) -> Dict:
        """
        Calcula métricas avanzadas de spread
        
        Returns:
            Dict con métricas de spread: promedio, volatilidad, percentiles, etc.
        """
        data = self.extract_market_data()
        spreads = data['spreads']
        mid_prices = data['mid_prices']
        
        if not spreads:
            return {"error": "No hay datos de spread disponibles"}
        
        # Métricas básicas de spread
        metrics = {
            # Spread absoluto
            'quoted_spread_mean': np.mean(spreads),
            'quoted_spread_std': np.std(spreads),
            'quoted_spread_min': np.min(spreads),
            'quoted_spread_max': np.max(spreads),
            'quoted_spread_median': np.median(spreads),
            
            # Percentiles
            'quoted_spread_p25': np.percentile(spreads, 25),
            'quoted_spread_p75': np.percentile(spreads, 75),
            'quoted_spread_p95': np.percentile(spreads, 95),
            'quoted_spread_p99': np.percentile(spreads, 99),
        }
        
        # Spread relativo (basis points)
        if mid_prices:
            relative_spreads = [(s / m) * 10000 for s, m in zip(spreads, mid_prices) if m > 0]
            metrics.update({
                'relative_spread_mean_bps': np.mean(relative_spreads) if relative_spreads else 0,
                'relative_spread_std_bps': np.std(relative_spreads) if relative_spreads else 0,
                'relative_spread_median_bps': np.median(relative_spreads) if relative_spreads else 0,
            })
        
        # Spread stability (coeficiente de variación)
        if metrics['quoted_spread_mean'] > 0:
            metrics['spread_stability'] = metrics['quoted_spread_std'] / metrics['quoted_spread_mean']
        else:
            metrics['spread_stability'] = float('inf')
        
        # Tiempo en spread estrecho (< percentil 25)
        tight_spread_threshold = metrics['quoted_spread_p25']
        tight_periods = sum(1 for s in spreads if s <= tight_spread_threshold)
        metrics['tight_spread_ratio'] = tight_periods / len(spreads)
        
        # Tiempo en spread ancho (> percentil 75)
        wide_spread_threshold = metrics['quoted_spread_p75']
        wide_periods = sum(1 for s in spreads if s >= wide_spread_threshold)
        metrics['wide_spread_ratio'] = wide_periods / len(spreads)
        
        return metrics
    
    def calculate_depth_metrics(self) -> Dict:
        """
        Calcula métricas de profundidad y liquidez del mercado
        
        Returns:
            Dict con métricas de liquidez y profundidad
        """
        if not self.simulator:
            return {"error": "No hay simulador disponible"}
        
        # Obtener estado actual del LOB
        current_bids = getattr(self.simulator, 'current_bids', {})
        current_asks = getattr(self.simulator, 'current_asks', {})
        
        if not current_bids or not current_asks:
            return {"error": "No hay datos de profundidad disponibles"}
        
        # Calcular profundidad total
        total_bid_volume = sum(current_bids.values())
        total_ask_volume = sum(current_asks.values())
        total_volume = total_bid_volume + total_ask_volume
        
        # Niveles de precio
        bid_levels = len(current_bids)
        ask_levels = len(current_asks)
        total_levels = bid_levels + ask_levels
        
        # Concentración de liquidez (% en primer nivel)
        best_bid_price = max(current_bids.keys()) if current_bids else 0
        best_ask_price = min(current_asks.keys()) if current_asks else 0
        
        top_bid_volume = current_bids.get(best_bid_price, 0)
        top_ask_volume = current_asks.get(best_ask_price, 0)
        
        bid_concentration = (top_bid_volume / total_bid_volume) if total_bid_volume > 0 else 0
        ask_concentration = (top_ask_volume / total_ask_volume) if total_ask_volume > 0 else 0
        
        # Desequilibrio de liquidez
        liquidity_imbalance = (total_bid_volume - total_ask_volume) / (total_bid_volume + total_ask_volume) if total_volume > 0 else 0
        
        # Profundidad promedio por nivel
        avg_bid_depth = total_bid_volume / bid_levels if bid_levels > 0 else 0
        avg_ask_depth = total_ask_volume / ask_levels if ask_levels > 0 else 0
        
        metrics = {
            'total_bid_volume': total_bid_volume,
            'total_ask_volume': total_ask_volume,
            'total_volume': total_volume,
            'bid_levels': bid_levels,
            'ask_levels': ask_levels,
            'total_levels': total_levels,
            'bid_concentration': bid_concentration,
            'ask_concentration': ask_concentration,
            'avg_concentration': (bid_concentration + ask_concentration) / 2,
            'liquidity_imbalance': liquidity_imbalance,
            'avg_bid_depth': avg_bid_depth,
            'avg_ask_depth': avg_ask_depth,
            'depth_symmetry': min(avg_bid_depth, avg_ask_depth) / max(avg_bid_depth, avg_ask_depth) if max(avg_bid_depth, avg_ask_depth) > 0 else 0
        }
        
        return metrics
    
    def calculate_volatility_metrics(self) -> Dict:
        """
        Calcula métricas de volatilidad y variabilidad de precios
        
        Returns:
            Dict con métricas de volatilidad
        """
        data = self.extract_market_data()
        
        if len(data['returns']) < 2:
            return {"error": "Insuficientes datos para calcular volatilidad"}
        
        returns = np.array(data['returns'])
        log_returns = np.array(data['log_returns'])
        price_changes = np.array(data['price_changes'])
        spreads = np.array(data['spreads'])
        
        # Volatilidad realized (desviación estándar de retornos)
        realized_volatility = np.std(returns)
        log_volatility = np.std(log_returns)
        
        # Volatilidad anualizada (asumiendo 252 días de trading)
        annualized_volatility = realized_volatility * np.sqrt(252 * 24 * 60)  # minutos en un año
        
        # Price variability
        price_variability = np.std(price_changes)
        
        # Volatilidad de spread
        spread_volatility = np.std(spreads)
        
        # Ratio de Sharpe modificado (excess return per unit of risk)
        mean_return = np.mean(returns)
        sharpe_ratio = mean_return / realized_volatility if realized_volatility > 0 else 0
        
        # Skewness y Kurtosis
        skewness = self._calculate_skewness(returns)
        kurtosis = self._calculate_kurtosis(returns)
        
        # Maximum drawdown
        cumulative_returns = np.cumprod(1 + returns)
        running_max = np.maximum.accumulate(cumulative_returns)
        drawdown = (cumulative_returns - running_max) / running_max
        max_drawdown = np.min(drawdown)
        
        # Volatility clustering (autocorrelación de retornos al cuadrado)
        squared_returns = returns ** 2
        volatility_clustering = np.corrcoef(squared_returns[:-1], squared_returns[1:])[0, 1] if len(squared_returns) > 1 else 0
        
        metrics = {
            'realized_volatility': realized_volatility,
            'log_volatility': log_volatility,
            'annualized_volatility': annualized_volatility,
            'price_variability': price_variability,
            'spread_volatility': spread_volatility,
            'sharpe_ratio': sharpe_ratio,
            'skewness': skewness,
            'kurtosis': kurtosis,
            'max_drawdown': max_drawdown,
            'volatility_clustering': volatility_clustering,
            'volatility_stability': spread_volatility / np.mean(spreads) if np.mean(spreads) > 0 else float('inf')
        }
        
        return metrics
    
    def _calculate_skewness(self, returns: np.ndarray) -> float:
        """Calcula skewness de la distribución de retornos"""
        if len(returns) < 3:
            return 0
        mean_return = np.mean(returns)
        std_return = np.std(returns)
        if std_return == 0:
            return 0
        skew = np.mean(((returns - mean_return) / std_return) ** 3)
        return skew
    
    def _calculate_kurtosis(self, returns: np.ndarray) -> float:
        """Calcula kurtosis de la distribución de retornos"""
        if len(returns) < 4:
            return 0
        mean_return = np.mean(returns)
        std_return = np.std(returns)
        if std_return == 0:
            return 0
        kurt = np.mean(((returns - mean_return) / std_return) ** 4) - 3  # Excess kurtosis
        return kurt
    
    def calculate_price_impact_metrics(self) -> Dict:
        """
        Calcula métricas de impacto de precio y eficiencia del mercado
        
        Returns:
            Dict con métricas de impacto de precio
        """
        data = self.extract_market_data()
        
        if len(data['price_changes']) < 5:
            return {"error": "Insuficientes datos para calcular impacto de precio"}
        
        price_changes = np.array(data['price_changes'])
        spreads = np.array(data['spreads'])
        
        # Price impact (correlación entre cambios de precio y spread)
        if len(price_changes) == len(spreads):
            price_spread_correlation = np.corrcoef(np.abs(price_changes), spreads)[0, 1] if len(price_changes) > 1 else 0
        else:
            # Ajustar longitudes
            min_len = min(len(price_changes), len(spreads))
            price_spread_correlation = np.corrcoef(np.abs(price_changes[:min_len]), spreads[:min_len])[0, 1] if min_len > 1 else 0
        
        # Persistence of price changes (autocorrelación)
        price_persistence = np.corrcoef(price_changes[:-1], price_changes[1:])[0, 1] if len(price_changes) > 1 else 0
        
        # Volatility of price changes
        price_impact_volatility = np.std(np.abs(price_changes))
        
        # Market efficiency (menor persistencia = más eficiente)
        market_efficiency = 1 - abs(price_persistence)
        
        # Mean reversion strength
        mean_reversion = -price_persistence if price_persistence < 0 else 0
        
        # Price discovery speed (basado en autocorrelación de retornos)
        discovery_speed = 1 / (1 + abs(price_persistence)) if price_persistence != -1 else float('inf')
        
        metrics = {
            'price_spread_correlation': price_spread_correlation,
            'price_persistence': price_persistence,
            'price_impact_volatility': price_impact_volatility,
            'market_efficiency': market_efficiency,
            'mean_reversion_strength': mean_reversion,
            'price_discovery_speed': discovery_speed,
            'impact_asymmetry': np.mean(price_changes) / np.std(price_changes) if np.std(price_changes) > 0 else 0
        }
        
        return metrics
    
    def generate_comprehensive_report(self) -> Dict:
        """
        Genera un reporte completo de todas las métricas de calidad del mercado
        
        Returns:
            Dict con todas las métricas organizadas por categoría
        """
        report = {
            'spread_metrics': self.calculate_spread_metrics(),
            'depth_metrics': self.calculate_depth_metrics(),
            'volatility_metrics': self.calculate_volatility_metrics(),
            'price_impact_metrics': self.calculate_price_impact_metrics(),
            'timestamp': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Cache del reporte
        self.metrics_cache = report
        
        return report
    
    def create_metrics_dashboard(self, title: str = "📊 Market Quality Dashboard") -> go.Figure:
        """
        Crea un dashboard visual completo con todas las métricas
        
        Args:
            title: Título del dashboard
            
        Returns:
            Figura de Plotly con dashboard interactivo
        """
        # Generar reporte completo
        report = self.generate_comprehensive_report()
        data = self.extract_market_data()
        
        # Crear subplots
        fig = make_subplots(
            rows=3, cols=2,
            subplot_titles=[
                "💰 Evolución de Precios", "📏 Spread Dynamics",
                "📊 Profundidad del Mercado", "⚡ Volatilidad",
                "🔄 Price Impact", "📈 Métricas Clave"
            ],
            specs=[
                [{"secondary_y": True}, {"secondary_y": False}],
                [{"type": "bar"}, {"secondary_y": True}],
                [{"secondary_y": False}, {"type": "indicator"}]
            ]
        )
        
        timestamps = data['timestamps']
        
        # 1. Evolución de Precios (Row 1, Col 1)
        fig.add_trace(
            go.Scatter(
                x=timestamps, y=data['best_bids'],
                mode='lines', name='Best Bid',
                line=dict(color=self.colors['bid'], width=2)
            ),
            row=1, col=1
        )
        fig.add_trace(
            go.Scatter(
                x=timestamps, y=data['mid_prices'],
                mode='lines', name='Mid Price',
                line=dict(color=self.colors['mid'], width=3)
            ),
            row=1, col=1
        )
        fig.add_trace(
            go.Scatter(
                x=timestamps, y=data['best_asks'],
                mode='lines', name='Best Ask',
                line=dict(color=self.colors['ask'], width=2)
            ),
            row=1, col=1
        )
        
        # 2. Spread Dynamics (Row 1, Col 2)
        fig.add_trace(
            go.Scatter(
                x=timestamps, y=data['spreads'],
                mode='lines+markers', name='Quoted Spread',
                line=dict(color=self.colors['spread'], width=2),
                marker=dict(size=4)
            ),
            row=1, col=2
        )
        
        # Línea de spread promedio
        if 'spread_metrics' in report and 'quoted_spread_mean' in report['spread_metrics']:
            avg_spread = report['spread_metrics']['quoted_spread_mean']
            fig.add_hline(
                y=avg_spread, line_dash="dash",
                line_color=self.colors['spread'],
                annotation_text=f"Avg: ${avg_spread:.3f}",
                row=1, col=2
            )
        
        # 3. Profundidad del Mercado (Row 2, Col 1)
        if 'depth_metrics' in report and 'total_bid_volume' in report['depth_metrics']:
            depth = report['depth_metrics']
            fig.add_trace(
                go.Bar(
                    x=['Bid Volume', 'Ask Volume'],
                    y=[depth.get('total_bid_volume', 0), depth.get('total_ask_volume', 0)],
                    marker_color=[self.colors['bid'], self.colors['ask']],
                    name='Market Depth'
                ),
                row=2, col=1
            )
        
        # 4. Volatilidad (Row 2, Col 2)
        if len(data['returns']) > 0:
            # Rolling volatility (ventana de 10 períodos)
            window = min(10, len(data['returns']))
            rolling_vol = []
            for i in range(len(data['returns'])):
                start_idx = max(0, i - window + 1)
                window_returns = data['returns'][start_idx:i+1]
                rolling_vol.append(np.std(window_returns) if len(window_returns) > 1 else 0)
            
            fig.add_trace(
                go.Scatter(
                    x=timestamps[1:len(rolling_vol)+1], y=rolling_vol,
                    mode='lines', name='Rolling Volatility',
                    line=dict(color=self.colors['volatility'], width=2)
                ),
                row=2, col=2
            )
        
        # 5. Price Impact (Row 3, Col 1)
        if len(data['price_changes']) > 0:
            fig.add_trace(
                go.Scatter(
                    x=timestamps[1:len(data['price_changes'])+1], y=data['price_changes'],
                    mode='markers', name='Price Changes',
                    marker=dict(
                        color=data['price_changes'],
                        colorscale='RdYlGn_r',
                        size=8,
                        showscale=True,
                        colorbar=dict(x=0.45, len=0.3)
                    )
                ),
                row=3, col=1
            )
        
        # 6. Métricas Clave (Row 3, Col 2) - Indicadores
        if 'spread_metrics' in report:
            spread_metrics = report['spread_metrics']
            avg_spread = spread_metrics.get('quoted_spread_mean', 0)
            
            fig.add_trace(
                go.Indicator(
                    mode="gauge+number+delta",
                    value=avg_spread,
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': "Avg Spread ($)"},
                    gauge={
                        'axis': {'range': [None, avg_spread * 2]},
                        'bar': {'color': self.colors['spread']},
                        'steps': [
                            {'range': [0, avg_spread * 0.5], 'color': "lightgray"},
                            {'range': [avg_spread * 0.5, avg_spread * 1.5], 'color': "gray"}
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': avg_spread * 1.5
                        }
                    }
                ),
                row=3, col=2
            )
        
        # Configuración de layout
        fig.update_layout(
            title=dict(
                text=title,
                x=0.5,
                font=dict(size=20, color='white')
            ),
            showlegend=True,
            height=900,
            paper_bgcolor=self.colors['background'],
            plot_bgcolor=self.colors['background'],
            font=dict(color='white', size=12),
            legend=dict(
                bgcolor="rgba(0,0,0,0.5)",
                bordercolor="white",
                borderwidth=1
            )
        )
        
        # Configurar ejes
        for i in range(1, 4):
            for j in range(1, 3):
                fig.update_xaxes(
                    gridcolor=self.colors['grid'],
                    showgrid=True,
                    row=i, col=j
                )
                fig.update_yaxes(
                    gridcolor=self.colors['grid'],
                    showgrid=True,
                    row=i, col=j
                )
        
        return fig
    
    def print_summary_report(self):
        """
        Imprime un resumen ejecutivo de las métricas de calidad del mercado
        """
        report = self.generate_comprehensive_report()
        
        print("=" * 70)
        print("📊 MARKET QUALITY ANALYSIS REPORT")
        print("=" * 70)
        print(f"⏰ Generated: {report['timestamp']}")
        print()
        
        # Spread Metrics
        if 'spread_metrics' in report and not report['spread_metrics'].get('error'):
            sm = report['spread_metrics']
            print("💰 SPREAD ANALYSIS:")
            print(f"   • Average Spread: ${sm.get('quoted_spread_mean', 0):.4f}")
            print(f"   • Spread Volatility: ${sm.get('quoted_spread_std', 0):.4f}")
            print(f"   • Relative Spread: {sm.get('relative_spread_mean_bps', 0):.2f} bps")
            print(f"   • Spread Stability: {sm.get('spread_stability', 0):.3f}")
            print(f"   • Tight Market Time: {sm.get('tight_spread_ratio', 0)*100:.1f}%")
            print()
        
        # Depth Metrics
        if 'depth_metrics' in report and not report['depth_metrics'].get('error'):
            dm = report['depth_metrics']
            print("📊 LIQUIDITY & DEPTH:")
            print(f"   • Total Volume: {dm.get('total_volume', 0):,.0f} shares")
            print(f"   • Market Levels: {dm.get('total_levels', 0)} price levels")
            print(f"   • Liquidity Imbalance: {dm.get('liquidity_imbalance', 0)*100:+.1f}%")
            print(f"   • Depth Symmetry: {dm.get('depth_symmetry', 0):.3f}")
            print(f"   • Top-Level Concentration: {dm.get('avg_concentration', 0)*100:.1f}%")
            print()
        
        # Volatility Metrics
        if 'volatility_metrics' in report and not report['volatility_metrics'].get('error'):
            vm = report['volatility_metrics']
            print("⚡ VOLATILITY & RISK:")
            print(f"   • Realized Volatility: {vm.get('realized_volatility', 0)*100:.3f}%")
            print(f"   • Annualized Volatility: {vm.get('annualized_volatility', 0)*100:.1f}%")
            print(f"   • Sharpe Ratio: {vm.get('sharpe_ratio', 0):.3f}")
            print(f"   • Skewness: {vm.get('skewness', 0):+.3f}")
            print(f"   • Max Drawdown: {vm.get('max_drawdown', 0)*100:.2f}%")
            print()
        
        # Price Impact Metrics
        if 'price_impact_metrics' in report and not report['price_impact_metrics'].get('error'):
            pm = report['price_impact_metrics']
            print("🔄 PRICE DISCOVERY & EFFICIENCY:")
            print(f"   • Market Efficiency: {pm.get('market_efficiency', 0)*100:.1f}%")
            print(f"   • Price Discovery Speed: {pm.get('price_discovery_speed', 0):.3f}")
            print(f"   • Mean Reversion: {pm.get('mean_reversion_strength', 0):.3f}")
            print(f"   • Price Persistence: {pm.get('price_persistence', 0):+.3f}")
            print()
        
        print("=" * 70)
        
        # Interpretación básica
        print("🎯 MARKET HEALTH INTERPRETATION:")
        self._print_market_health_interpretation(report)
        print("=" * 70)
    
    def _print_market_health_interpretation(self, report: Dict):
        """Imprime interpretación de la salud del mercado"""
        
        # Evaluar spread
        if 'spread_metrics' in report and not report['spread_metrics'].get('error'):
            spread_stability = report['spread_metrics'].get('spread_stability', float('inf'))
            if spread_stability < 0.2:
                print("   ✅ SPREAD: Stable and predictable")
            elif spread_stability < 0.5:
                print("   ⚠️  SPREAD: Moderately volatile")
            else:
                print("   🚨 SPREAD: Highly volatile - Market stress")
        
        # Evaluar liquidez
        if 'depth_metrics' in report and not report['depth_metrics'].get('error'):
            liquidity_imbalance = abs(report['depth_metrics'].get('liquidity_imbalance', 0))
            if liquidity_imbalance < 0.1:
                print("   ✅ LIQUIDITY: Well balanced")
            elif liquidity_imbalance < 0.3:
                print("   ⚠️  LIQUIDITY: Slight imbalance")
            else:
                print("   🚨 LIQUIDITY: Severe imbalance detected")
        
        # Evaluar eficiencia
        if 'price_impact_metrics' in report and not report['price_impact_metrics'].get('error'):
            efficiency = report['price_impact_metrics'].get('market_efficiency', 0)
            if efficiency > 0.8:
                print("   ✅ EFFICIENCY: Highly efficient price discovery")
            elif efficiency > 0.6:
                print("   ⚠️  EFFICIENCY: Moderately efficient")
            else:
                print("   🚨 EFFICIENCY: Poor price discovery")
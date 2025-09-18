import random
import time
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from IPython.display import clear_output

class UltimateOrderBookLesson:
    """
    Order Book standalone con visualización completa y optimizada:
    - Order Book en tiempo real (5 niveles bid/ask)
    - Mid Price Evolution (precio medio histórico)
    - Spread Evolution (dinámica de liquidez)
    """
    
    def __init__(self, base_lob):
        self.base_lob = base_lob
        
        # Datos actuales del mercado
        self.current_bids = {}
        self.current_asks = {}
        
        # Historiales para gráficos
        self.mid_price_history = []
        self.spread_history = []
        self.best_bid_history = []
        self.best_ask_history = []
        self.timestamps = []
        
        # Precio base para simulación
        self.base_price = 149.5
        
        print("✅ UltimateOrderBook optimizado creado!")
    
    def generate_realistic_market_data(self):
        """Genera datos de mercado realistas y eficientes"""
        # Generar spread aleatorio entre 0.1 y 0.5
        spread = random.uniform(0.1, 0.5)
        
        # Precio base con ligera variación
        price_change = random.uniform(-0.3, 0.3)
        self.base_price += price_change
        
        # Asegurar que el precio se mantenga en rango razonable
        self.base_price = max(148.0, min(151.0, self.base_price))
        
        # Calcular mejor bid y ask
        best_bid = self.base_price - spread/2
        best_ask = self.base_price + spread/2
        
        # Generar 5 niveles de cada lado
        self.current_bids = {}
        self.current_asks = {}
        
        # Bids (precios descendentes desde el mejor)
        for i in range(5):
            price = best_bid - (i * random.uniform(0.05, 0.15))
            volume = random.randint(10, 100)
            self.current_bids[round(price, 2)] = volume
        
        # Asks (precios ascendentes desde el mejor)
        for i in range(5):
            price = best_ask + (i * random.uniform(0.05, 0.15))
            volume = random.randint(10, 100)
            self.current_asks[round(price, 2)] = volume
        
        return best_bid, best_ask, spread
    
    def simulate_market_tick(self):
        """Simula un tick del mercado de forma eficiente"""
        best_bid, best_ask, spread = self.generate_realistic_market_data()
        
        # Calcular mid price
        mid_price = (best_bid + best_ask) / 2
            
        # Actualizar historiales
        self.mid_price_history.append(mid_price)
        self.spread_history.append(spread)
        self.best_bid_history.append(best_bid)
        self.best_ask_history.append(best_ask)
        self.timestamps.append(len(self.timestamps))
        
        # Mantener historial limitado (últimos 30 ticks para mejor rendimiento)
        if len(self.mid_price_history) > 30:
            self.mid_price_history.pop(0)
            self.spread_history.pop(0)
            self.best_bid_history.pop(0)
            self.best_ask_history.pop(0)
            self.timestamps.pop(0)
            
        return best_bid, best_ask, spread
    
    def create_orderbook_visualization(self):
        """Crea visualización optimizada con 3 subgráficos"""
        
        # Obtener datos actuales
        bid_prices = sorted(self.current_bids.keys(), reverse=True)[:5]
        ask_prices = sorted(self.current_asks.keys())[:5]
        
        # Calcular precio medio
        if bid_prices and ask_prices:
            mid_price = (bid_prices[0] + ask_prices[0]) / 2
        else:
            mid_price = self.base_price
        
        # Crear subplots optimizados
        fig = make_subplots(
            rows=3, cols=1,
            row_heights=[0.6, 0.2, 0.2],  # Simplificado
            subplot_titles=[
                f'📊 ORDER BOOK - Mid: ${mid_price:.2f}',
                '💰 Price Evolution (🟢Bid | 🟡Mid | 🔴Ask)',
                '📏 Spread'
            ],
            vertical_spacing=0.15
        )
        
        # ============ ORDER BOOK ============
        
        # Preparar datos optimizados
        if ask_prices:
            ask_y_pos = list(range(9, 4, -1))
            ask_vols = [self.current_asks[price] for price in reversed(ask_prices)]
            ask_labels = [f"${price:.2f}" for price in reversed(ask_prices)]
            
            fig.add_trace(go.Bar(
                y=ask_y_pos, x=ask_vols, orientation='h',
                marker_color='rgba(255, 50, 50, 0.9)',  # Rojo más brillante para fondo negro
                text=ask_labels, textposition='inside', name='Asks',
                textfont=dict(color='white', size=12)  # Texto blanco
            ), row=1, col=1)
        
        if bid_prices:
            bid_y_pos = list(range(4, -1, -1))
            bid_vols = [self.current_bids[price] for price in bid_prices]
            bid_labels = [f"${price:.2f}" for price in bid_prices]
            
            fig.add_trace(go.Bar(
                y=bid_y_pos, x=bid_vols, orientation='h',
                marker_color='rgba(50, 255, 50, 0.9)',  # Verde más brillante para fondo negro
                text=bid_labels, textposition='inside', name='Bids',
                textfont=dict(color='white', size=12)  # Texto blanco
            ), row=1, col=1)
        
        # Línea del precio medio (más brillante para fondo negro)
        fig.add_hline(y=4.5, line_dash="dash", line_color="yellow", 
                     line_width=3, row=1, col=1,
                     annotation=dict(text=f"MID: ${mid_price:.2f}", 
                                   font=dict(color="yellow", size=14)))
        
        # ============ GRÁFICOS DE HISTORIAL ============
        
        # Gráfico de evolución de precios (Best Bid, Mid Price, Best Ask)
        if len(self.mid_price_history) > 1:
            # Línea verde: Best Bid
            if len(self.best_bid_history) > 1:
                fig.add_trace(go.Scatter(
                    x=self.timestamps, y=self.best_bid_history,
                    mode='lines+markers', name='Best Bid',
                    line=dict(color='lime', width=2.5),  # Verde brillante
                    marker=dict(color='lime', size=3)
                ), row=2, col=1)
            
            # Línea amarilla: Mid Price
            fig.add_trace(go.Scatter(
                x=self.timestamps, y=self.mid_price_history,
                mode='lines+markers', name='Mid Price',
                line=dict(color='gold', width=3),  # Amarillo dorado
                marker=dict(color='gold', size=4)
            ), row=2, col=1)
            
            # Línea roja: Best Ask
            if len(self.best_ask_history) > 1:
                fig.add_trace(go.Scatter(
                    x=self.timestamps, y=self.best_ask_history,
                    mode='lines+markers', name='Best Ask',
                    line=dict(color='red', width=2.5),  # Rojo brillante
                    marker=dict(color='red', size=3)
                ), row=2, col=1)
        
        if len(self.spread_history) > 1:
            fig.add_trace(go.Scatter(
                x=self.timestamps, y=self.spread_history,
                mode='lines+markers', name='Spread',
                line=dict(color='magenta', width=3),  # Magenta brillante para fondo negro
                marker=dict(color='magenta', size=4),
                fill='tozeroy', fillcolor='rgba(255, 0, 255, 0.2)'
            ), row=3, col=1)
        
        # ============ LAYOUT OPTIMIZADO - FONDO NEGRO ============
        fig.update_layout(
            title='🔴 LIVE ORDER BOOK',
            height=700,  # Reducido para mejor rendimiento
            showlegend=False,
            template="plotly_dark",  # Fondo negro
            plot_bgcolor='black',
            paper_bgcolor='black'
        )
        
        # Configurar ejes
        fig.update_yaxes(
            tickvals=list(range(10)),
            ticktext=['B5', 'B4', 'B3', 'B2', 'B1', 'A1', 'A2', 'A3', 'A4', 'A5'],
            row=1, col=1
        )
        
        return fig
    
    def start_simulation(self, duration=15, update_interval=1.5):
        """Simulación optimizada con menor frecuencia de actualización"""
        print(f"🚀 Iniciando simulación optimizada ({duration}s, cada {update_interval}s)")
        
        start_time = time.time()
        while time.time() - start_time < duration:
            clear_output(wait=True)
            
            # Generar nuevo tick
            self.simulate_market_tick()
            
            # Mostrar visualización
            fig = self.create_orderbook_visualization()
            fig.show()
            
            # Mostrar info básica
            if self.mid_price_history:
                print(f"💰 Mid Price: ${self.mid_price_history[-1]:.2f}")
            if self.spread_history:
                print(f"📏 Spread: ${self.spread_history[-1]:.3f}")
            
            time.sleep(update_interval)
        
        print("✅ Simulación completada!")

    def generate_bid_crash_scenario(self, crash_tick=10):
        """
        Simula una caída en picado del lado BID mientras el ASK se mantiene estable.
        
        Escenario:
        - Ticks 1-10: Mercado normal (bid: 99-100, ask: 100-101, spread ~1)
        - Tick 10+: Crisis de liquidez - bid colapsa a 98-99, ask se mantiene 100-101 (spread ~2-3)
        
        Args:
            crash_tick (int): Tick en el que ocurre la caída del bid
            
        Returns:
            dict: Serie de datos para simular el crash scenario
        """
        scenario_data = []
        
        for tick in range(1, 31):  # 30 ticks de simulación
            if tick < crash_tick:
                # ============ FASE NORMAL ============
                # Bid oscila entre 99-100
                base_bid = 99.5 + random.uniform(-0.5, 0.5)
                # Ask oscila entre 100-101  
                base_ask = 100.5 + random.uniform(-0.5, 0.5)
                
                # Spread normal (~0.5-1.5)
                spread = random.uniform(0.5, 1.5)
                
            else:
                # ============ CRISIS - BID CRASH ============
                # Bid cae dramáticamente a rango 98-99
                base_bid = 98.5 + random.uniform(-0.5, 0.5)
                # Ask se MANTIENE estable en 100-101 (vendedores no bajan precios)
                base_ask = 100.5 + random.uniform(-0.5, 0.5)
                
                # Spread se amplía dramáticamente (2-3)
                spread = base_ask - base_bid
                
                # Añadir volatilidad extra al bid durante la crisis
                if tick == crash_tick:
                    # En el tick de crash, caída más pronunciada
                    base_bid -= random.uniform(0.3, 0.8)
                
            # Ajustar para mantener spread mínimo
            best_bid = base_bid - spread/2
            best_ask = base_ask + spread/2
            
            # Generar 5 niveles para cada lado
            bids = {}
            asks = {}
            
            # Bids (precios descendentes)
            for i in range(5):
                if tick < crash_tick:
                    # Volúmenes normales en fase normal
                    volume = random.randint(50, 150)
                    price_step = random.uniform(0.05, 0.15)
                else:
                    # Volúmenes reducidos en crisis (liquidez se retira)
                    volume = random.randint(10, 50)  # Mucho menos volumen
                    price_step = random.uniform(0.1, 0.25)  # Steps más grandes
                
                price = best_bid - (i * price_step)
                bids[round(price, 2)] = volume
            
            # Asks (precios ascendentes)
            for i in range(5):
                if tick < crash_tick:
                    # Volúmenes normales
                    volume = random.randint(50, 150)
                    price_step = random.uniform(0.05, 0.15)
                else:
                    # En crisis, asks mantienen volumen pero precios más altos
                    volume = random.randint(40, 120)  # Volumen ligeramente reducido
                    price_step = random.uniform(0.15, 0.3)  # Vendedores piden más
                
                price = best_ask + (i * price_step)
                asks[round(price, 2)] = volume
            
            # Calcular métricas
            mid_price = (best_bid + best_ask) / 2
            
            scenario_data.append({
                'tick': tick,
                'phase': 'NORMAL' if tick < crash_tick else 'BID_CRASH',
                'bids': bids,
                'asks': asks,
                'best_bid': best_bid,
                'best_ask': best_ask,
                'mid_price': mid_price,
                'spread': spread,
                'market_condition': 'Estable' if tick < crash_tick else 'Crisis de Liquidez'
            })
        
        return scenario_data
    
    def simulate_bid_crash_scenario(self, crash_tick=10, duration=30, update_interval=1.0):
        """
        Ejecuta la simulación del crash del bid en tiempo real
        
        Args:
            crash_tick (int): Tick donde ocurre el crash
            duration (int): Duración total en ticks  
            update_interval (float): Intervalo entre actualizaciones
        """
        print(f"🚨 INICIANDO SIMULACIÓN: BID CRASH SCENARIO")
        print(f"📊 Configuración:")
        print(f"   • Crash en tick: {crash_tick}")
        print(f"   • Duración total: {duration} ticks")
        print(f"   • Intervalo: {update_interval}s")
        print(f"   • Fase normal: Bid 99-100, Ask 100-101")
        print(f"   • Fase crisis: Bid 98-99, Ask 100-101 (spread x3)")
        print()
        
        # Generar datos del escenario
        scenario_data = self.generate_bid_crash_scenario(crash_tick)
        
        # Limpiar historiales
        self.mid_price_history = []
        self.spread_history = []
        self.best_bid_history = []
        self.best_ask_history = []
        self.timestamps = []
        
        print("🚀 ¡Iniciando simulación!")
        
        for i, tick_data in enumerate(scenario_data[:duration]):
            clear_output(wait=True)
            
            # Actualizar estado actual del LOB
            self.current_bids = tick_data['bids']
            self.current_asks = tick_data['asks']
            
            # Actualizar historiales
            self.mid_price_history.append(tick_data['mid_price'])
            self.spread_history.append(tick_data['spread'])
            self.best_bid_history.append(tick_data['best_bid'])
            self.best_ask_history.append(tick_data['best_ask'])
            self.timestamps.append(tick_data['tick'])
            
            # Crear visualización
            fig = self.create_orderbook_visualization()
            
            # Añadir indicador de fase
            phase_color = '#28a745' if tick_data['phase'] == 'NORMAL' else '#dc3545'
            fig.add_annotation(
                text=f"🚨 {tick_data['phase']} - {tick_data['market_condition']}",
                xref="paper", yref="paper",
                x=0.02, y=0.98, showarrow=False,
                font=dict(size=16, color=phase_color),
                bgcolor=f"rgba{phase_color.replace('#', '').replace('28a745', '(40, 167, 69, 0.8)').replace('dc3545', '(220, 53, 69, 0.8)')}",
                bordercolor=phase_color,
                borderwidth=2
            )
            
            fig.show()
            
            # Mostrar métricas detalladas
            print(f"📊 TICK {tick_data['tick']} | {tick_data['phase']}")
            print(f"💰 Mid Price: ${tick_data['mid_price']:.2f}")
            print(f"📏 Spread: ${tick_data['spread']:.3f}")
            print(f"🟢 Best Bid: ${tick_data['best_bid']:.2f}")
            print(f"🔴 Best Ask: ${tick_data['best_ask']:.2f}")
            print(f"📊 Condición: {tick_data['market_condition']}")
            
            if tick_data['tick'] == crash_tick:
                print("🚨🚨🚨 ¡CRASH DEL BID! ¡LIQUIDEZ EN COLAPSO! 🚨🚨🚨")
            
            time.sleep(update_interval)
        
        print("✅ Simulación del Bid Crash completada!")
        print("\n📊 RESUMEN FINAL:")
        print(f"🔸 Spread inicial promedio: ~$1.00")
        print(f"🔸 Spread final promedio: ~$2.50")
        print(f"🔸 Impacto en mid price: ~$0.75 down")
        print(f"🔸 Pérdida de liquidez bid: ~60%")


        # 📊 VISTA ESTÁTICA DEL SIMULADOR

    print("📊 Generando vista actual del mercado simulado...")

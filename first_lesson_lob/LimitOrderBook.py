# 🏗️ LIMIT ORDER BOOK CLASS
# Clase para simular un Limit Order Book

# 📚 Importaciones necesarias
import time
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from IPython.display import HTML, display

class LimitOrderBook:
    """
    🏛️ Clase para simular un Limit Order Book
    
    Esta clase mantiene las órdenes de compra (bids) y venta (asks)
    organizadas por precio y tiempo de llegada.
    """
    
    def __init__(self, symbol="AAPL"):
        self.symbol = symbol
        # 📘 Bids: diccionario {precio: [cantidad_total, timestamp]}
        self.bids = {}
        # 📕 Asks: diccionario {precio: [cantidad_total, timestamp]}  
        self.asks = {}
        self.trades = []  # Historial de transacciones
        
    def add_order(self, side, price, quantity, timestamp=None):
        """
        ➕ Añadir una orden al book
        
        Args:
            side: 'bid' o 'ask'
            price: precio de la orden
            quantity: cantidad de acciones
            timestamp: momento de llegada (opcional)
        """
        if timestamp is None:
            import time
            timestamp = time.time()
            
        if side.lower() == 'bid':
            if price in self.bids:
                # Sumar cantidad si ya existe el precio
                self.bids[price][0] += quantity
            else:
                # Nuevo nivel de precio
                self.bids[price] = [quantity, timestamp]
                
        elif side.lower() == 'ask':
            if price in self.asks:
                self.asks[price][0] += quantity
            else:
                self.asks[price] = [quantity, timestamp]
    
    def get_best_bid(self):
        """💰 Obtener el mejor precio de compra (más alto)"""
        if not self.bids:
            return None
        return max(self.bids.keys())
    
    def get_best_ask(self):
        """💸 Obtener el mejor precio de venta (más bajo)"""
        if not self.asks:
            return None
        return min(self.asks.keys())
    
    def get_spread(self):
        """📏 Calcular el spread (diferencia entre ask y bid)"""
        best_bid = self.get_best_bid()
        best_ask = self.get_best_ask()
        
        if best_bid is None or best_ask is None:
            return None
        return round(best_ask - best_bid, 2)
    
    def get_mid_price(self):
        """📊 Calcular el precio medio"""
        best_bid = self.get_best_bid()
        best_ask = self.get_best_ask()
        
        if best_bid is None or best_ask is None:
            return None
        return round((best_bid + best_ask) / 2, 2)
    
    def get_book_summary(self):
        """📋 Resumen del estado actual del book"""
        return {
            'symbol': self.symbol,
            'best_bid': self.get_best_bid(),
            'best_ask': self.get_best_ask(),
            'spread': self.get_spread(),
            'mid_price': self.get_mid_price(),
            'bid_levels': len(self.bids),
            'ask_levels': len(self.asks)
        }
    
    def load_sample_data(self):
        """
        🎲 Cargar datos de ejemplo para demostración
        
        Este método llena el LOB con órdenes realistas de AAPL
        para propósitos educativos y de testing.
        """
        # 📘 Órdenes BID (compra) - precios decrecientes
        bid_orders = [
            (149.95, 500),   # Mejor bid
            (149.90, 200),
            (149.85, 800),
            (149.80, 300),
            (149.75, 150),
            (149.70, 600),
            (149.65, 250),
            (149.60, 400),
        ]

        # 📕 Órdenes ASK (venta) - precios crecientes  
        ask_orders = [
            (150.05, 300),   # Mejor ask
            (150.10, 150),
            (150.15, 600),
            (150.20, 400),
            (150.25, 200),
            (150.30, 350),
            (150.35, 500),
            (150.40, 100),
        ]

        # Limpiar LOB actual
        self.bids = {}
        self.asks = {}

        # Llenar el LOB con las órdenes de ejemplo
        for price, qty in bid_orders:
            self.add_order('bid', price, qty)

        for price, qty in ask_orders:
            self.add_order('ask', price, qty)

        return {
            'bid_orders_added': len(bid_orders),
            'ask_orders_added': len(ask_orders),
            'status': 'Sample data loaded successfully'
        }
    
    def plot_static(self, title="📊 Limit Order Book - Vista Estática"):
        """
        🎨 Crear visualización estática del Limit Order Book usando Plotly
        
        Args:
            title: Título del gráfico
        
        Returns:
            fig: Figura de Plotly para mostrar o guardar
        """
        
        # Preparar datos para visualización
        bid_prices = sorted(self.bids.keys(), reverse=True)  # Mayor a menor
        bid_quantities = [self.bids[price][0] for price in bid_prices]
        
        ask_prices = sorted(self.asks.keys())  # Menor a mayor
        ask_quantities = [self.asks[price][0] for price in ask_prices]
        
        # Crear subplots
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=["📘 BID SIDE (Compra)", "📕 ASK SIDE (Venta)"],
            shared_yaxes=True,
            horizontal_spacing=0.15
        )
        
        # 📘 BID SIDE (lado izquierdo)
        fig.add_trace(
            go.Bar(
                x=[-q for q in bid_quantities],  # Negativo para ir hacia la izquierda
                y=bid_prices,
                orientation='h',
                name='Bids',
                marker=dict(
                    color='rgba(46, 204, 113, 0.8)',  # Verde
                    line=dict(color='rgba(46, 204, 113, 1.0)', width=1)
                ),
                text=[f'${p:.2f}<br>{q:,} shares' for p, q in zip(bid_prices, bid_quantities)],
                textposition='inside',
                hovertemplate='<b>Precio:</b> $%{y:.2f}<br><b>Cantidad:</b> %{customdata:,}<br><extra></extra>',
                customdata=bid_quantities
            ),
            row=1, col=1
        )
        
        # 📕 ASK SIDE (lado derecho)  
        fig.add_trace(
            go.Bar(
                x=ask_quantities,
                y=ask_prices,
                orientation='h',
                name='Asks',
                marker=dict(
                    color='rgba(231, 76, 60, 0.8)',  # Rojo
                    line=dict(color='rgba(231, 76, 60, 1.0)', width=1)
                ),
                text=[f'${p:.2f}<br>{q:,} shares' for p, q in zip(ask_prices, ask_quantities)],
                textposition='inside',
                hovertemplate='<b>Precio:</b> $%{y:.2f}<br><b>Cantidad:</b> %{x:,}<br><extra></extra>'
            ),
            row=1, col=2
        )
        
        # Añadir líneas para best bid y best ask
        best_bid = self.get_best_bid()
        best_ask = self.get_best_ask()
        
        if best_bid:
            fig.add_hline(
                y=best_bid, 
                line_dash="dash", 
                line_color="green",
                annotation_text=f"Best Bid: ${best_bid:.2f}",
                annotation_position="bottom right"
            )
        
        if best_ask:
            fig.add_hline(
                y=best_ask, 
                line_dash="dash", 
                line_color="red",
                annotation_text=f"Best Ask: ${best_ask:.2f}",
                annotation_position="top right"
            )
        
        # Configuración del layout
        fig.update_layout(
            title=dict(
                text=title,
                x=0.5,
                font=dict(size=20, color='#2c3e50')
            ),
            height=600,
            showlegend=False,
            plot_bgcolor='rgba(248, 249, 250, 0.8)',
            paper_bgcolor='white',
            font=dict(size=12)
        )
        
        # Configurar ejes
        fig.update_xaxes(title_text="📊 Cantidad (shares)", row=1, col=1)
        fig.update_xaxes(title_text="📊 Cantidad (shares)", row=1, col=2)
        fig.update_yaxes(title_text="💰 Precio ($)", row=1, col=1)
        
        # Mostrar métricas en texto
        summary = self.get_book_summary()
        metrics_text = f"""
        <div style='background: linear-gradient(135deg, #74b9ff, #0984e3); padding: 15px; border-radius: 8px; color: white; margin: 10px 0;'>
            <h4>📊 Métricas del Mercado:</h4>
            <p><b>💰 Best Bid:</b> ${summary['best_bid']:.2f} | <b>💸 Best Ask:</b> ${summary['best_ask']:.2f}</p>
            <p><b>📏 Spread:</b> ${summary['spread']:.2f} | <b>📊 Mid Price:</b> ${summary['mid_price']:.2f}</p>
        </div>
        """
        
        display(HTML(metrics_text))
        
        return fig

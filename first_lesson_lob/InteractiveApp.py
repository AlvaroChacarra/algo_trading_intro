# 🎯 INTERACTIVE LOB APP CLASS
# Aplicación interactiva completa del LOB con funcionalidad integrada

# 📚 Importaciones necesarias
import ipywidgets as widgets
from IPython.display import display, clear_output, HTML
import plotly.graph_objects as go
import time

class InteractiveApp:
    """
    🎮 Aplicación interactiva completa para el Limit Order Book
    
    Esta clase integra tanto la lógica del LOB como la interfaz de usuario,
    proporcionando una solución completa y simple.
    """
    
    def __init__(self, initial_orders=None):
        """
        🏗️ Inicializar la aplicación interactiva
        
        Args:
            initial_orders: Lista de órdenes iniciales [(side, price, qty), ...]
        """
        # Atributos del LOB integrados
        self.bids = {}  # precio -> cantidad
        self.asks = {}  # precio -> cantidad
        self.last_price = 100.0
        self.trade_history = []
        
        # Cargar órdenes iniciales si se proporcionan
        if initial_orders:
            for side, price, qty in initial_orders:
                self.add_limit_order(side, price, qty)
        
        # Output widget para gráficos (debe estar antes de _setup_layout)
        self.plot_output = widgets.Output()
        
        # Crear widgets de interfaz
        self._create_widgets()
        
        # Configurar layout
        self._setup_layout()
        
        # Conectar eventos
        self._connect_events()
        
        # No actualizar vistas aquí - se hará cuando se carguen datos
    
    # ===== MÉTODOS DEL LOB INTEGRADOS =====
    
    def add_limit_order(self, side, price, quantity):
        """Agregar orden limitada"""
        if side == 'BUY':
            if price in self.bids:
                self.bids[price] += quantity
            else:
                self.bids[price] = quantity
        else:  # SELL
            if price in self.asks:
                self.asks[price] += quantity
            else:
                self.asks[price] = quantity
    
    def execute_market_order(self, side, quantity):
        """Ejecutar orden de mercado"""
        executed_qty = 0
        executed_price = 0
        
        if side == 'BUY':
            # Comprar: ejecutar contra las mejores asks
            sorted_asks = sorted(self.asks.items())
            for price, available_qty in sorted_asks:
                if executed_qty >= quantity:
                    break
                    
                take_qty = min(quantity - executed_qty, available_qty)
                executed_qty += take_qty
                executed_price = price
                
                # Actualizar el LOB
                self.asks[price] -= take_qty
                if self.asks[price] == 0:
                    del self.asks[price]
                    
                # Registrar trade
                self.trade_history.append({
                    'price': price, 
                    'quantity': take_qty, 
                    'side': 'BUY'
                })
                
                self.last_price = price
                
        else:  # SELL
            # Vender: ejecutar contra los mejores bids
            sorted_bids = sorted(self.bids.items(), reverse=True)
            for price, available_qty in sorted_bids:
                if executed_qty >= quantity:
                    break
                    
                take_qty = min(quantity - executed_qty, available_qty)
                executed_qty += take_qty
                executed_price = price
                
                # Actualizar el LOB
                self.bids[price] -= take_qty
                if self.bids[price] == 0:
                    del self.bids[price]
                    
                # Registrar trade
                self.trade_history.append({
                    'price': price, 
                    'quantity': take_qty, 
                    'side': 'SELL'
                })
                
                self.last_price = price
        
        return executed_qty, executed_price
    
    def get_best_bid_ask(self):
        """Obtener mejor bid y ask"""
        best_bid = max(self.bids.keys()) if self.bids else None
        best_ask = min(self.asks.keys()) if self.asks else None
        return best_bid, best_ask
    
    def get_spread(self):
        """Calcular spread"""
        best_bid, best_ask = self.get_best_bid_ask()
        if best_bid and best_ask:
            return best_ask - best_bid
        return None
    
    def plot_interactive(self):
        """
        🎨 Visualizar LOB interactivo con estilo mejorado
        
        Returns:
            fig: Figura de Plotly para mostrar o manipular
        """
        fig = go.Figure()
        
        # Preparar datos
        if self.bids:
            bid_prices = sorted(self.bids.keys(), reverse=True)
            bid_quantities = [self.bids[p] for p in bid_prices]
            bid_colors = ['#2E8B57' if i == 0 else '#90EE90' for i in range(len(bid_prices))]
        else:
            bid_prices, bid_quantities, bid_colors = [], [], []
            
        if self.asks:
            ask_prices = sorted(self.asks.keys())
            ask_quantities = [self.asks[p] for p in ask_prices]
            ask_colors = ['#DC143C' if i == 0 else '#FFB6C1' for i in range(len(ask_prices))]
        else:
            ask_prices, ask_quantities, ask_colors = [], [], []
        
        # Bids (verde degradado)
        if bid_prices:
            fig.add_trace(go.Bar(
                x=bid_quantities,
                y=bid_prices,
                orientation='h',
                name='💚 Bids (Compra)',
                marker_color=bid_colors,
                text=[f'${p:.2f}<br>{q} unidades' for p, q in zip(bid_prices, bid_quantities)],
                textposition='auto',
                hovertemplate='<b>BID</b><br>Precio: $%{y:.2f}<br>Cantidad: %{x}<br><extra></extra>'
            ))
        
        # Asks (rojo degradado)
        if ask_prices:
            fig.add_trace(go.Bar(
                x=ask_quantities,
                y=ask_prices,
                orientation='h',
                name='❤️ Asks (Venta)',
                marker_color=ask_colors,
                text=[f'${p:.2f}<br>{q} unidades' for p, q in zip(ask_prices, ask_quantities)],
                textposition='auto',
                hovertemplate='<b>ASK</b><br>Precio: $%{y:.2f}<br>Cantidad: %{x}<br><extra></extra>'
            ))
        
        # Información del spread y mejores precios
        best_bid, best_ask = self.get_best_bid_ask()
        spread = self.get_spread()
        
        # Línea del último precio
        if best_bid and best_ask:
            fig.add_hline(
                y=self.last_price, 
                line_dash="dash", 
                line_color="orange", 
                line_width=2,
                annotation_text=f"💰 Último: ${self.last_price:.2f}",
                annotation_position="top right"
            )
        
        # Título dinámico
        if spread:
            title_text = f"🎯 <b>LOB Interactivo</b> | 💰 Último: <span style='color:orange'>${self.last_price:.2f}</span> | 📏 Spread: <span style='color:purple'>${spread:.2f}</span>"
            if best_bid:
                title_text += f" | 💚 Best Bid: <span style='color:green'>${best_bid:.2f}</span>"
            if best_ask:
                title_text += f" | ❤️ Best Ask: <span style='color:red'>${best_ask:.2f}</span>"
        else:
            title_text = f"🎯 <b>LOB Interactivo</b> | 💰 Último: <span style='color:orange'>${self.last_price:.2f}</span>"
        
        fig.update_layout(
            title={
                'text': title_text,
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 14}  # Reducido de 16 a 14 para que quepa mejor
            },
            xaxis_title="📊 Cantidad de Acciones",
            yaxis_title="💲 Precio ($)",
            height=600,
            barmode='overlay',
            plot_bgcolor='rgba(240,248,255,0.8)',
            paper_bgcolor='white',
            font={'family': 'Arial, sans-serif'},
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="center",
                x=0.5
            )
        )
        
        # Personalizar ejes
        fig.update_xaxes(
            gridcolor='rgba(0,0,0,0.1)',
            gridwidth=1,
            zeroline=True,
            zerolinecolor='rgba(0,0,0,0.3)'
        )
        
        fig.update_yaxes(
            gridcolor='rgba(0,0,0,0.1)',
            gridwidth=1,
            tickformat='$.2f'
        )
        
        return fig
    
    def _create_widgets(self):
        """� Crear todos los widgets de la interfaz"""
        
        # --- CONTROLES DE ORDEN ---
        self.order_type = widgets.Dropdown(
            options=['LIMIT', 'MARKET'],
            value='LIMIT',
            description='Tipo:',
            style={'description_width': 'initial'},
            layout=widgets.Layout(width='140px')  # Más compacto
        )
        
        self.side_selector = widgets.Dropdown(
            options=['BUY', 'SELL'],
            value='BUY',
            description='Lado:',
            style={'description_width': 'initial'},
            layout=widgets.Layout(width='140px')  # Más compacto
        )
        
        self.price_input = widgets.FloatText(
            value=100.0,
            description='Precio ($):',
            step=0.1,
            style={'description_width': 'initial'},
            layout=widgets.Layout(width='140px')  # Más compacto
        )
        
        self.quantity_input = widgets.IntText(
            value=10,
            description='Cantidad:',
            style={'description_width': 'initial'},
            layout=widgets.Layout(width='140px')  # Más compacto
        )
        
        self.send_button = widgets.Button(
            description='📤 Enviar Orden',
            button_style='primary',
            layout=widgets.Layout(width='120px')  # Más compacto
        )
        
        # --- BOTONES RÁPIDOS ---
        self.quick_buy_button = widgets.Button(
            description='💚 Compra Rápida',
            button_style='success',
            layout=widgets.Layout(width='130px')  # Más compacto
        )
        
        self.quick_sell_button = widgets.Button(
            description='❤️ Venta Rápida',
            button_style='danger',
            layout=widgets.Layout(width='130px')  # Más compacto
        )
        
        # --- ESTADÍSTICAS ---
        self.stats_output = widgets.Output()
        
        # --- HISTORIAL DE TRADES ---
        self.trades_output = widgets.Output()
        
        # --- CONTROLES DE RESET ---
        self.reset_button = widgets.Button(
            description='🔄 Reset LOB',
            button_style='warning',
            layout=widgets.Layout(width='120px')
        )
    
    def _setup_layout(self):
        """📐 Configurar el layout de la interfaz"""
        
        # Grupo de controles de orden
        order_controls = widgets.VBox([
            widgets.HTML("<h3>🎯 Controles de Orden</h3>"),
            widgets.HBox([self.order_type, self.side_selector]),
            widgets.HBox([self.price_input, self.quantity_input]),
            self.send_button
        ])
        
        # Grupo de botones rápidos
        quick_controls = widgets.VBox([
            widgets.HTML("<h3>⚡ Acciones Rápidas</h3>"),
            self.quick_buy_button,
            self.quick_sell_button,
            self.reset_button
        ])
        
        # Panel de estadísticas
        stats_panel = widgets.VBox([
            widgets.HTML("<h3>📊 Estadísticas del LOB</h3>"),
            self.stats_output
        ])
        
        # Panel de trades
        trades_panel = widgets.VBox([
            widgets.HTML("<h3>📈 Historial de Trades</h3>"),
            self.trades_output
        ])
        
        # NUEVO LAYOUT: Panel izquierdo (controles + stats) y derecho (LOB)
        
        # Panel superior izquierdo: Estadísticas e Historial
        top_left_panels = widgets.HBox([
            stats_panel,
            trades_panel
        ])
        
        # Panel inferior izquierdo: Controles compactos
        bottom_left_controls = widgets.HBox([
            order_controls,
            quick_controls
        ])
        
        # Panel izquierdo completo (controles + estadísticas) - ANCHO FIJO
        left_panel = widgets.VBox([
            top_left_panels,      # Stats e Historial arriba
            bottom_left_controls  # Controles abajo
        ], layout=widgets.Layout(width='50%'))  # Ancho fijo para panel izquierdo
        
        # Panel derecho: LOB con título - RESTO DEL ESPACIO
        right_panel = widgets.VBox([
            widgets.HTML("<h3>📊 Visualización del LOB en Tiempo Real</h3>"),
            self.plot_output
        ], layout=widgets.Layout(width='50%'))  # Resto del espacio para LOB
        
        # Layout principal: Izquierda (controles) + Derecha (LOB)
        self.main_layout = widgets.HBox([
            left_panel,   # Panel izquierdo compacto
            right_panel   # Panel derecho con LOB grande
        ])
    
    def _connect_events(self):
        """🔗 Conectar eventos de los widgets"""
        self.send_button.on_click(self._send_order)
        self.quick_buy_button.on_click(self._quick_buy)
        self.quick_sell_button.on_click(self._quick_sell)
        self.reset_button.on_click(self._reset_lob)
        
        # Actualizar precio cuando cambia el tipo de orden
        self.order_type.observe(self._on_order_type_change, names='value')
    
    def _send_order(self, button):
        """📤 Enviar orden al LOB"""
        try:
            order_type = self.order_type.value
            side = self.side_selector.value
            price = self.price_input.value
            quantity = self.quantity_input.value
            
            if order_type == 'LIMIT':
                self.add_limit_order(side, price, quantity)
                self._show_message(f"✅ Orden LIMIT {side} añadida: {quantity} @ ${price:.2f}")
            else:  # MARKET
                executed_qty, executed_price = self.execute_market_order(side, quantity)
                if executed_qty > 0:
                    self._show_message(f"✅ Orden MARKET {side} ejecutada: {executed_qty} @ ${executed_price:.2f}")
                else:
                    self._show_message(f"❌ No se pudo ejecutar orden MARKET {side}")
            
            self._update_stats()
            self._update_plot()
            self._update_trades()
            
        except Exception as e:
            self._show_message(f"❌ Error: {str(e)}")
    
    def _quick_buy(self, button):
        """💚 Compra rápida al mejor ask"""
        try:
            best_bid, best_ask = self.get_best_bid_ask()
            if best_ask:
                executed_qty, executed_price = self.execute_market_order('BUY', 10)
                if executed_qty > 0:
                    self._show_message(f"💚 Compra rápida: {executed_qty} @ ${executed_price:.2f}")
                    self._update_stats()
                    self._update_plot()
                    self._update_trades()
                else:
                    self._show_message("❌ No hay asks disponibles")
            else:
                self._show_message("❌ No hay asks en el LOB")
        except Exception as e:
            self._show_message(f"❌ Error en compra rápida: {str(e)}")
    
    def _quick_sell(self, button):
        """❤️ Venta rápida al mejor bid"""
        try:
            best_bid, best_ask = self.get_best_bid_ask()
            if best_bid:
                executed_qty, executed_price = self.execute_market_order('SELL', 10)
                if executed_qty > 0:
                    self._show_message(f"❤️ Venta rápida: {executed_qty} @ ${executed_price:.2f}")
                    self._update_stats()
                    self._update_plot()
                    self._update_trades()
                else:
                    self._show_message("❌ No hay bids disponibles")
            else:
                self._show_message("❌ No hay bids en el LOB")
        except Exception as e:
            self._show_message(f"❌ Error en venta rápida: {str(e)}")
    
    def _reset_lob(self, button):
        """🔄 Resetear el LOB"""
        self.bids = {}
        self.asks = {}
        self.trade_history = []
        self.last_price = 100.0
        
        self._show_message("🔄 LOB reseteado")
        self._update_stats()
        self._update_plot()
        self._update_trades()
    
    def _on_order_type_change(self, change):
        """🔄 Actualizar interfaz cuando cambia el tipo de orden"""
        if change['new'] == 'MARKET':
            self.price_input.disabled = True
            self.price_input.description = 'Precio (N/A):'
        else:
            self.price_input.disabled = False
            self.price_input.description = 'Precio ($):'
    
    def _update_stats(self):
        """📊 Actualizar estadísticas del LOB"""
        with self.stats_output:
            clear_output(wait=True)
            
            best_bid, best_ask = self.get_best_bid_ask()
            spread = self.get_spread()
            
            # Formatear valores con manejo de None
            best_bid_str = f"${best_bid:.2f}" if best_bid is not None else "N/A"
            best_ask_str = f"${best_ask:.2f}" if best_ask is not None else "N/A"
            spread_str = f"${spread:.2f}" if spread is not None else "N/A"
            
            stats_html = f"""
            <div style='background: linear-gradient(135deg, #74b9ff, #0984e3); padding: 15px; border-radius: 8px; color: white;'>
                <h4>📊 Métricas en Tiempo Real</h4>
                <p><b>💰 Último Precio:</b> ${self.last_price:.2f}</p>
                <p><b>💚 Best Bid:</b> {best_bid_str}</p>
                <p><b>❤️ Best Ask:</b> {best_ask_str}</p>
                <p><b>📏 Spread:</b> {spread_str}</p>
                <p><b>📘 Niveles Bid:</b> {len(self.bids)}</p>
                <p><b>📕 Niveles Ask:</b> {len(self.asks)}</p>
                <p><b>📈 Total Trades:</b> {len(self.trade_history)}</p>
            </div>
            """
            # Usar display() DENTRO del contexto with - esto lo mantiene en el widget
            display(HTML(stats_html))
    
    def _update_plot(self):
        """📊 Actualizar visualización del LOB"""
        with self.plot_output:
            clear_output(wait=True)
            fig = self.plot_interactive()
            fig.show()
    
    def _update_trades(self):
        """📈 Actualizar historial de trades"""
        with self.trades_output:
            clear_output(wait=True)
            
            if self.trade_history:
                recent_trades = self.trade_history[-5:]  # Últimos 5 trades
                trades_html = "<div style='max-height: 200px; overflow-y: auto;'>"
                
                for i, trade in enumerate(reversed(recent_trades), 1):
                    color = '#2ecc71' if trade['side'] == 'BUY' else '#e74c3c'
                    emoji = '💚' if trade['side'] == 'BUY' else '❤️'
                    
                    trades_html += f"""
                    <div style='background: {color}; color: white; padding: 8px; margin: 5px 0; border-radius: 5px;'>
                        {emoji} {trade['side']}: {trade['quantity']} @ ${trade['price']:.2f}
                    </div>
                    """
                
                trades_html += "</div>"
                # Usar display() DENTRO del contexto with - esto lo mantiene en el widget
                display(HTML(trades_html))
            else:
                # Usar display() DENTRO del contexto with - esto lo mantiene en el widget
                display(HTML("<p>No hay trades aún</p>"))
    
    def _show_message(self, message):
        """💬 Mostrar mensaje temporal"""
        print(message)  # Por ahora usar print, se puede mejorar con widgets
    
    def run_app(self):
        """
        🚀 Ejecutar la aplicación interactiva
        
        Muestra la interfaz completa y activa todos los controles
        """
        print("🎮 Iniciando aplicación interactiva del LOB...")
        print("✅ Controles listos - ¡Empieza a tradear!")
        
        # Mostrar la interfaz
        display(self.main_layout)
        
        # No retornar self para evitar output extraño
        return None
    
    def load_sample_data(self):
        """
        🎲 Cargar datos de muestra para la demostración
        """
        sample_orders = [
            ('SELL', 102, 50), ('SELL', 101.5, 30), ('SELL', 101, 40),
            ('BUY', 100, 35), ('BUY', 99.5, 45), ('BUY', 99, 60)
        ]
        
        for side, price, qty in sample_orders:
            self.add_limit_order(side, price, qty)
        
        self._update_stats()
        self._update_plot()
        
        print("🎲 Datos de muestra cargados en el LOB")
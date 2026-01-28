from odoo import models, fields, api
from datetime import datetime, timedelta


class BreadSubscription(models.Model):
    _name = 'bread.subscription'
    _description = 'Suscripción de Pan'
    _rec_name = 'name'
    _order = 'date_start DESC'

    name = fields.Char(
        string='Nombre',
        required=True,
        readonly=True,
        default='Nuevo'
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Cliente',
        required=True,
        ondelete='cascade'
    )
    
    quantity = fields.Integer(
        string='Cantidad de Pan',
        required=True,
        default=20,
        help='Cantidad de unidades de pan: 10, 20 o 50'
    )
    
    # Producto para registro en ventas
    product_id = fields.Many2one(
        'product.product',
        string='Producto de Pan',
        required=True,
        domain=[('type', '=', 'product')]
    )
    
    date_start = fields.Date(
        string='Fecha Inicio',
        required=True,
        default=fields.Date.context_today
    )
    date_end = fields.Date(
        string='Fecha Fin',
        required=True
    )
    
    state = fields.Selection(
        [
            ('draft', 'Borrador'),
            ('active', 'Activa'),
            ('paused', 'Pausada'),
            ('ended', 'Finalizada'),
            ('canceled', 'Cancelada')
        ],
        string='Estado',
        default='draft'
    )
    
    frequency = fields.Selection(
        [
            ('weekly', 'Semanal'),
            ('biweekly', 'Quincenal'),
            ('monthly', 'Mensual')
        ],
        string='Frecuencia',
        required=True,
        default='weekly'
    )
    
    unit_price = fields.Float(
        string='Precio Unitario',
        required=True,
        default=0.0
    )
    total_price = fields.Float(
        string='Precio Total',
        compute='_compute_total_price',
        store=True
    )
    
    notes = fields.Text(string='Notas')
    
    delivery_ids = fields.One2many(
        'bread.subscription.delivery',
        'subscription_id',
        string='Entregas'
    )
    
    # Órdenes de venta relacionadas
    sale_order_ids = fields.One2many(
        'sale.order',
        'bread_subscription_id',
        string='Órdenes de Venta',
        readonly=True
    )
    
    # Movimientos de inventario relacionados
    stock_move_ids = fields.One2many(
        'stock.move',
        'bread_subscription_id',
        string='Movimientos de Stock',
        readonly=True
    )
    
    created_date = fields.Date(
        string='Fecha Creación',
        default=fields.Date.context_today,
        readonly=True
    )
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'Nuevo') == 'Nuevo':
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'bread.subscription.sequence'
                ) or 'SUB-000'
            # Validar cantidad
            qty = vals.get('quantity')
            if qty and qty not in [10, 20, 50]:
                raise ValueError('La cantidad debe ser 10, 20 o 50 unidades')
        return super().create(vals_list)
    
    @api.depends('quantity', 'unit_price')
    def _compute_total_price(self):
        for record in self:
            record.total_price = record.quantity * record.unit_price
    
    def action_activate(self):
        for record in self:
            record.state = 'active'
            record._generate_deliveries()
    
    def action_pause(self):
        self.state = 'paused'
    
    def action_resume(self):
        self.state = 'active'
    
    def action_end(self):
        self.state = 'ended'
    
    def action_cancel(self):
        self.state = 'canceled'
    
    def _generate_deliveries(self):
        BreadDelivery = self.env['bread.subscription.delivery']
        
        for record in self:
            current_date = record.date_start
            
            while current_date <= record.date_end:
                BreadDelivery.create({
                    'subscription_id': record.id,
                    'scheduled_date': current_date,
                    'state': 'scheduled'
                })
                
                if record.frequency == 'weekly':
                    current_date = current_date + timedelta(days=7)
                elif record.frequency == 'biweekly':
                    current_date = current_date + timedelta(days=14)
                elif record.frequency == 'monthly':
                    current_date = current_date + timedelta(days=30)


class BreadSubscriptionDelivery(models.Model):
    _name = 'bread.subscription.delivery'
    _description = 'Entrega de Suscripción'
    _rec_name = 'scheduled_date'
    _order = 'scheduled_date DESC'
    
    subscription_id = fields.Many2one(
        'bread.subscription',
        string='Suscripción',
        required=True,
        ondelete='cascade'
    )
    
    partner_id = fields.Many2one(
        'res.partner',
        related='subscription_id.partner_id',
        string='Cliente',
        readonly=True,
        store=True
    )
    
    product_id = fields.Many2one(
        'product.product',
        related='subscription_id.product_id',
        string='Producto',
        readonly=True,
        store=True
    )
    
    scheduled_date = fields.Date(
        string='Fecha Programada',
        required=True
    )
    
    delivery_date = fields.Date(
        string='Fecha Entrega'
    )
    
    quantity = fields.Integer(
        related='subscription_id.quantity',
        string='Cantidad de Pan',
        readonly=True,
        store=True
    )
    
    state = fields.Selection(
        [
            ('scheduled', 'Programada'),
            ('delivered', 'Entregada'),
            ('pending', 'Pendiente'),
            ('canceled', 'Cancelada')
        ],
        string='Estado',
        default='scheduled'
    )
    
    # Órdenes de venta relacionadas
    sale_order_line_id = fields.Many2one(
        'sale.order.line',
        string='Línea de Venta',
        readonly=True
    )
    
    # Movimiento de stock
    stock_move_id = fields.Many2one(
        'stock.move',
        string='Movimiento de Stock',
        readonly=True
    )
    
    notes = fields.Text(string='Notas')
    
    def action_mark_delivered(self):
        """Marcar como entregada y crear movimiento de stock + orden de venta"""
        for delivery in self:
            delivery.state = 'delivered'
            delivery.delivery_date = datetime.now().date()
            
            # Crear orden de venta
            delivery._create_sale_order()
            
            # Crear movimiento de stock
            delivery._create_stock_move()
    
    def action_mark_pending(self):
        self.state = 'pending'
    
    def action_cancel_delivery(self):
        self.state = 'canceled'
    
    def _create_sale_order(self):
        """Crear una orden de venta para la entrega"""
        SaleOrder = self.env['sale.order']
        
        if not self.subscription_id.product_id:
            return
        
        # Buscar si ya existe una orden para este cliente en este mes
        today = fields.Date.today()
        month_start = today.replace(day=1)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        existing_order = SaleOrder.search([
            ('partner_id', '=', self.subscription_id.partner_id.id),
            ('date_order', '>=', month_start),
            ('date_order', '<=', month_end),
            ('state', '=', 'draft'),
            ('bread_subscription_id', '=', self.subscription_id.id)
        ], limit=1)
        
        if existing_order:
            # Agregar línea a orden existente
            self.env['sale.order.line'].create({
                'order_id': existing_order.id,
                'product_id': self.subscription_id.product_id.id,
                'product_uom_qty': self.quantity,
                'price_unit': self.subscription_id.unit_price,
                'bread_subscription_delivery_id': self.id
            })
            self.sale_order_line_id = self.env['sale.order.line'].search([
                ('order_id', '=', existing_order.id),
                ('bread_subscription_delivery_id', '=', self.id)
            ], limit=1)
        else:
            # Crear nueva orden de venta
            sale_order = SaleOrder.create({
                'partner_id': self.subscription_id.partner_id.id,
                'bread_subscription_id': self.subscription_id.id,
                'order_line': [
                    (0, 0, {
                        'product_id': self.subscription_id.product_id.id,
                        'product_uom_qty': self.quantity,
                        'price_unit': self.subscription_id.unit_price,
                        'bread_subscription_delivery_id': self.id
                    })
                ]
            })
            self.sale_order_line_id = sale_order.order_line[0]
    
    def _create_stock_move(self):
        """Crear movimiento de stock (salida del almacén)"""
        StockMove = self.env['stock.move']
        Location = self.env['stock.location']
        
        if not self.subscription_id.product_id:
            return
        
        try:
            # Obtener ubicación de salida (típicamente Clientes/Entregas)
            customer_location = Location.search([
                ('usage', '=', 'customer')
            ], limit=1)
            
            # Obtener ubicación de stock
            stock_location = Location.search([
                ('usage', '=', 'internal'),
                ('name', 'ilike', 'Stock')
            ], limit=1)
            
            if not stock_location:
                stock_location = Location.search([
                    ('usage', '=', 'internal')
                ], limit=1)
            
            if customer_location and stock_location:
                stock_move = StockMove.create({
                    'name': f'Entrega Pan - {self.subscription_id.name}',
                    'product_id': self.subscription_id.product_id.id,
                    'product_uom_qty': self.quantity,
                    'product_uom': self.subscription_id.product_id.uom_id.id,
                    'location_id': stock_location.id,
                    'location_dest_id': customer_location.id,
                    'date': self.delivery_date,
                    'bread_subscription_id': self.subscription_id.id,
                    'state': 'draft'
                })
                
                self.stock_move_id = stock_move
                
                # Confirmar movimiento
                stock_move._action_confirm()
                stock_move._action_assign()
                
                # Marcar cantidad realizada en las líneas
                for line in stock_move.move_line_ids:
                    line.quantity = self.quantity
                
                # Marcar como realizado
                stock_move._action_done()
        except Exception as e:
            # Si hay error al crear movimiento de stock, continuar sin fallar
            import logging
            _logger = logging.getLogger(__name__)
            _logger.error(f'Error al crear movimiento de stock: {str(e)}')

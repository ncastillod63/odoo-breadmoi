from odoo import models, fields


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    bread_subscription_id = fields.Many2one(
        'bread.subscription',
        string='Suscripción de Pan',
        readonly=True,
        help='Suscripción de pan asociada a esta orden'
    )


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
    bread_subscription_delivery_id = fields.Many2one(
        'bread.subscription.delivery',
        string='Entrega de Suscripción',
        readonly=True,
        help='Entrega de suscripción asociada a esta línea'
    )


class StockMove(models.Model):
    _inherit = 'stock.move'
    
    bread_subscription_id = fields.Many2one(
        'bread.subscription',
        string='Suscripción de Pan',
        readonly=True,
        help='Suscripción de pan asociada a este movimiento'
    )

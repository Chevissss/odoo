from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal

class ReservaPortal(CustomerPortal):
    
    def _prepare_home_portal_values(self, counters):
        """Agregar contador de reservas al portal"""
        values = super()._prepare_home_portal_values(counters)
        
        if 'reserva_count' in counters:
            partner = request.env.user.partner_id
            cliente = request.env['reserva.cliente'].search([
                '|', ('email', '=', partner.email),
                ('user_id', '=', request.env.user.id)
            ], limit=1)
            
            if cliente:
                reserva_count = request.env['reserva.reserva'].search_count([
                    ('cliente_id', '=', cliente.id)
                ])
                values['reserva_count'] = reserva_count
        
        return values

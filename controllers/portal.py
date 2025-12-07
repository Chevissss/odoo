from odoo import http
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)

class PortalController(http.Controller):

    @http.route('/portal/reservas', auth='user', website=True)
    def portal_reservas(self, **kw):
        """Panel de control del cliente en portal"""
        try:
            user = request.env.user
            Reserva = request.env['reserva.reserva']
            
            mis_reservas = Reserva.search([
                ('partner_id', '=', user.partner_id.id)
            ], order='fecha DESC', limit=10)
            
            return request.render('reserva_canchas.portal_reservas_template', {
                'reservas': mis_reservas,
            })
        except Exception as e:
            _logger.error(f'Error en portal_reservas: {str(e)}')
            return request.not_found()

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

from odoo import http, fields
from odoo.http import request
import json
import logging
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)

class ReservaController(http.Controller):

    @http.route('/reservas', auth='public', website=True)
    def reservas_list(self, **kw):
        """Página principal de canchas"""
        try:
            Cancha = request.env['reserva.cancha'].sudo()
            canchas = Cancha.search([('estado', '=', 'disponible')])
            
            tipos_deporte = [('futbol', 'Fútbol'), ('futsal', 'Futsal'), ('basquet', 'Básquetbol'), 
                            ('voley', 'Vóleibol'), ('tenis', 'Tenis'), ('padel', 'Pádel')]
            
            return request.render('reserva_canchas.website_canchas_template', {
                'canchas': canchas,
                'tipos_deporte': tipos_deporte,
            })
        except Exception as e:
            _logger.error(f'Error en reservas_list: {str(e)}')
            return request.render('reserva_canchas.website_error_template', {
                'error': 'Error al cargar las canchas'
            })

    @http.route('/reservas/cancha/<int:cancha_id>', auth='public', website=True)
    def cancha_detalle(self, cancha_id, **kw):
        """Detalle de cancha y disponibilidad"""
        try:
            Cancha = request.env['reserva.cancha'].sudo()
            cancha = Cancha.browse(cancha_id)
            
            if not cancha.exists():
                return request.render('reserva_canchas.website_error_template', {
                    'error': 'Cancha no encontrada'
                })
            
            hoy = datetime.now().date()
            fecha_inicio = hoy
            fecha_fin = hoy + timedelta(days=30)
            
            return request.render('reserva_canchas.website_cancha_detalle_template', {
                'cancha': cancha,
                'fecha_inicio': fecha_inicio,
                'fecha_fin': fecha_fin,
            })
        except Exception as e:
            _logger.error(f'Error en cancha_detalle: {str(e)}')
            return request.render('reserva_canchas.website_error_template', {
                'error': 'Error al cargar el detalle de la cancha'
            })

    @http.route('/reservas/disponibilidad', auth='public', type='json', website=True)
    def get_disponibilidad(self, cancha_id, fecha, **kw):
        """API AJAX para obtener horarios disponibles"""
        try:
            Cancha = request.env['reserva.cancha'].sudo()
            Reserva = request.env['reserva.reserva'].sudo()
            
            cancha = Cancha.browse(int(cancha_id))
            if not cancha.exists() or cancha.estado != 'disponible':
                return {'error': 'Cancha no disponible', 'horarios': []}
            
            fecha_obj = datetime.strptime(fecha, '%Y-%m-%d').date()
            
            # Validar que no sea fecha pasada
            if fecha_obj < datetime.now().date():
                return {'error': 'No puedes reservar en fechas pasadas', 'horarios': []}
            
            # Obtener reservas existentes
            reservas_dia = Reserva.search([
                ('cancha_id', '=', cancha.id),
                ('fecha', '=', fecha_obj),
                ('estado', 'in', ['confirmada', 'en_curso'])
            ])
            
            horas_reservadas = set()
            for res in reservas_dia:
                for hora in range(int(res.hora_inicio), int(res.hora_fin)):
                    horas_reservadas.add(hora)
            
            # Generar horarios (6 AM a 10 PM)
            horarios = []
            for hora in range(6, 23):
                horarios.append({
                    'hora': hora,
                    'disponible': hora not in horas_reservadas,
                    'precio': cancha.precio_hora
                })
            
            return {
                'horarios': horarios,
                'error': None
            }
        except Exception as e:
            _logger.error(f'Error en get_disponibilidad: {str(e)}')
            return {'error': str(e), 'horarios': []}

    @http.route('/reservas/crear', auth='user', website=True)
    def crear_reserva(self, cancha_id=None, fecha=None, hora_inicio=None, hora_fin=None, **kw):
        """Formulario de creación de reserva"""
        try:
            user = request.env.user
            partner = user.partner_id
            
            cancha = request.env['reserva.cancha'].sudo().browse(int(cancha_id)) if cancha_id else None
            
            Cliente = request.env['reserva.cliente']
            cliente = Cliente.search([('partner_id', '=', partner.id)], limit=1)
            
            if not cliente:
                cliente = Cliente.create({
                    'name': partner.name,
                    'email': partner.email,
                    'telefono': partner.phone or '',
                    'partner_id': partner.id
                })
            
            return request.render('reserva_canchas.website_crear_reserva_template', {
                'cancha': cancha,
                'partner': partner,
                'cliente': cliente,
                'fecha': fecha,
                'hora_inicio': hora_inicio,
                'hora_fin': hora_fin,
            })
        except Exception as e:
            _logger.error(f'Error en crear_reserva: {str(e)}')
            return request.render('reserva_canchas.website_error_template', {
                'error': f'Error al crear la reserva: {str(e)}'
            })

    @http.route('/reservas/confirmar', auth='user', type='http', website=True, methods=['POST'])
    def confirmar_reserva(self, **post):
        """Procesar confirmación de reserva"""
        try:
            Reserva = request.env['reserva.reserva']
            Cliente = request.env['reserva.cliente']
            
            user = request.env.user
            partner = user.partner_id
            
            # Obtener o crear cliente
            cliente = Cliente.search([('partner_id', '=', partner.id)], limit=1)
            if not cliente:
                cliente = Cliente.create({
                    'name': partner.name,
                    'email': partner.email,
                    'telefono': post.get('telefono', partner.phone or ''),
                    'partner_id': partner.id
                })
            
            # Crear reserva
            reserva = Reserva.create({
                'cliente_id': cliente.id,
                'cancha_id': int(post.get('cancha_id')),
                'fecha': post.get('fecha'),
                'hora_inicio': float(post.get('hora_inicio', 0)),
                'hora_fin': float(post.get('hora_fin', 0)),
                'notas': post.get('notas', ''),
                'estado': 'confirmada',
                'partner_id': partner.id
            })
            
            return request.redirect(f'/reservas/confirmacion/{reserva.id}')
        except Exception as e:
            _logger.error(f'Error en confirmar_reserva: {str(e)}')
            return request.render('reserva_canchas.website_error_template', {
                'error': f'Error al confirmar la reserva: {str(e)}'
            })

    @http.route('/reservas/confirmacion/<int:reserva_id>', auth='user', website=True)
    def confirmacion(self, reserva_id, **kw):
        """Página de confirmación"""
        try:
            reserva = request.env['reserva.reserva'].browse(reserva_id)
            
            if not reserva.exists():
                return request.render('reserva_canchas.website_error_template', {
                    'error': 'Reserva no encontrada'
                })
            
            return request.render('reserva_canchas.website_confirmacion_template', {
                'reserva': reserva,
            })
        except Exception as e:
            _logger.error(f'Error en confirmacion: {str(e)}')
            return request.render('reserva_canchas.website_error_template', {
                'error': 'Error al cargar la confirmación'
            })

    @http.route('/mis-reservas', auth='user', website=True)
    def mis_reservas(self, **kw):
        """Lista de reservas del usuario"""
        try:
            user = request.env.user
            partner = user.partner_id
            
            Reserva = request.env['reserva.reserva']
            Cliente = request.env['reserva.cliente']
            
            cliente = Cliente.search([('partner_id', '=', partner.id)], limit=1)
            
            if not cliente:
                reservas_activas = []
                reservas_pasadas = []
            else:
                hoy = datetime.now().date()
                reservas_activas = Reserva.search([
                    ('cliente_id', '=', cliente.id),
                    ('fecha', '>=', hoy),
                    ('estado', 'in', ['confirmada', 'en_curso', 'borrador'])
                ], order='fecha ASC')
                
                reservas_pasadas = Reserva.search([
                    ('cliente_id', '=', cliente.id),
                    ('estado', 'in', ['completada', 'cancelada', 'no_asistio'])
                ], order='fecha DESC')
            
            return request.render('reserva_canchas.website_mis_reservas_template', {
                'cliente': cliente,
                'reservas_activas': reservas_activas,
                'reservas_pasadas': reservas_pasadas,
            })
        except Exception as e:
            _logger.error(f'Error en mis_reservas: {str(e)}')
            return request.render('reserva_canchas.website_error_template', {
                'error': 'Error al cargar tus reservas'
            })

    @http.route('/reservas/cancelar/<int:reserva_id>', auth='user', type='http', website=True, methods=['POST'])
    def cancelar_reserva(self, reserva_id, **post):
        """Cancelar una reserva"""
        try:
            reserva = request.env['reserva.reserva'].browse(reserva_id)
            
            if reserva.exists() and reserva.estado in ['confirmada', 'borrador']:
                reserva.action_cancelar()
                return request.redirect('/mis-reservas?cancelled=1')
            else:
                return request.redirect('/mis-reservas')
        except Exception as e:
            _logger.error(f'Error en cancelar_reserva: {str(e)}')
            return request.redirect('/mis-reservas')

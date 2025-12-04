from odoo import http, _
from odoo.http import request
from datetime import datetime, timedelta, date
import json

class ReservaCanchasWebsite(http.Controller):
    
    @http.route(['/reservas', '/reservas/canchas'], type='http', auth='public', website=True)
    def canchas_disponibles(self, **kwargs):
        """Página principal con lista de canchas disponibles"""
        canchas = request.env['reserva.cancha'].sudo().search([
            ('estado', '=', 'disponible')
        ], order='name')
        
        # Obtener tipos de deporte únicos
        tipos_deporte = canchas.mapped('tipo_deporte')
        tipos_deporte_dict = dict(request.env['reserva.cancha']._fields['tipo_deporte'].selection)
        
        values = {
            'canchas': canchas,
            'tipos_deporte': [(tipo, tipos_deporte_dict.get(tipo)) for tipo in set(tipos_deporte)],
            'page_name': 'canchas',
        }
        return request.render('reserva_canchas.website_canchas_template', values)
    
    @http.route(['/reservas/cancha/<int:cancha_id>'], type='http', auth='public', website=True)
    def cancha_detalle(self, cancha_id, **kwargs):
        """Detalle de una cancha específica"""
        cancha = request.env['reserva.cancha'].sudo().browse(cancha_id)
        
        if not cancha.exists() or cancha.estado != 'disponible':
            return request.render('website.404')
        
        # Obtener horarios disponibles para hoy y los próximos 7 días
        fecha_inicio = date.today()
        fecha_fin = fecha_inicio + timedelta(days=7)
        
        values = {
            'cancha': cancha,
            'fecha_inicio': fecha_inicio,
            'fecha_fin': fecha_fin,
            'page_name': 'cancha_detalle',
        }
        return request.render('reserva_canchas.website_cancha_detalle_template', values)
    
    @http.route(['/reservas/disponibilidad'], type='json', auth='public', methods=['POST'])
    def get_disponibilidad(self, cancha_id, fecha, **kwargs):
        """API para obtener horarios disponibles de una cancha en una fecha específica"""
        try:
            cancha = request.env['reserva.cancha'].sudo().browse(int(cancha_id))
            fecha_obj = datetime.strptime(fecha, '%Y-%m-%d').date()
            
            # No permitir reservas en el pasado
            if fecha_obj < date.today():
                return {'error': 'No se pueden hacer reservas en fechas pasadas'}
            
            # Obtener reservas existentes
            reservas = request.env['reserva.reserva'].sudo().search([
                ('cancha_id', '=', cancha.id),
                ('fecha', '=', fecha_obj),
                ('estado', 'in', ['confirmada', 'en_curso', 'borrador'])
            ])
            
            # Generar horarios (6 AM - 11 PM)
            horarios_ocupados = []
            for reserva in reservas:
                horarios_ocupados.append({
                    'inicio': reserva.hora_inicio,
                    'fin': reserva.hora_fin
                })
            
            # Generar todos los horarios disponibles
            horarios_disponibles = []
            for hora in range(6, 23):
                ocupado = False
                for ocupacion in horarios_ocupados:
                    if hora >= ocupacion['inicio'] and hora < ocupacion['fin']:
                        ocupado = True
                        break
                
                horarios_disponibles.append({
                    'hora': hora,
                    'disponible': not ocupado,
                    'precio': cancha.precio_hora
                })
            
            return {
                'horarios': horarios_disponibles,
                'precio_hora': cancha.precio_hora,
                'nombre_cancha': cancha.name
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    @http.route(['/reservas/crear'], type='http', auth='user', website=True, methods=['GET'])
    def reserva_formulario(self, cancha_id=None, fecha=None, hora_inicio=None, **kwargs):
        """Formulario para crear una reserva (requiere login)"""
        if not cancha_id:
            return request.redirect('/reservas')
        
        cancha = request.env['reserva.cancha'].sudo().browse(int(cancha_id))
        
        if not cancha.exists():
            return request.redirect('/reservas')
        
        # Buscar o crear cliente para el usuario actual
        partner = request.env.user.partner_id
        cliente = request.env['reserva.cliente'].sudo().search([
            '|', ('email', '=', partner.email),
            ('user_id', '=', request.env.user.id)
        ], limit=1)
        
        values = {
            'cancha': cancha,
            'fecha': fecha or date.today().strftime('%Y-%m-%d'),
            'hora_inicio': hora_inicio or 10,
            'cliente': cliente,
            'partner': partner,
            'page_name': 'crear_reserva',
        }
        return request.render('reserva_canchas.website_crear_reserva_template', values)
    
    @http.route(['/reservas/confirmar'], type='http', auth='user', website=True, methods=['POST'], csrf=True)
    def reserva_confirmar(self, **post):
        """Procesar la creación de una reserva"""
        try:
            # Buscar o crear cliente
            partner = request.env.user.partner_id
            cliente = request.env['reserva.cliente'].sudo().search([
                '|', ('email', '=', partner.email),
                ('user_id', '=', request.env.user.id)
            ], limit=1)
            
            if not cliente:
                cliente = request.env['reserva.cliente'].sudo().create({
                    'name': partner.name,
                    'email': partner.email,
                    'telefono': post.get('telefono', partner.phone or ''),
                    'user_id': request.env.user.id,
                    'tipo_cliente': 'nuevo'
                })
            
            # Crear la reserva
            fecha = datetime.strptime(post.get('fecha'), '%Y-%m-%d').date()
            hora_inicio = float(post.get('hora_inicio'))
            hora_fin = float(post.get('hora_fin'))
            
            reserva = request.env['reserva.reserva'].sudo().create({
                'cliente_id': cliente.id,
                'cancha_id': int(post.get('cancha_id')),
                'fecha': fecha,
                'hora_inicio': hora_inicio,
                'hora_fin': hora_fin,
                'tipo_reserva': 'online',
                'notas': post.get('notas', ''),
                'estado': 'borrador'
            })
            
            # Confirmar automáticamente
            reserva.action_confirmar()
            
            return request.redirect('/reservas/confirmacion/%s' % reserva.id)
            
        except Exception as e:
            return request.render('reserva_canchas.website_error_template', {
                'error': str(e),
                'page_name': 'error'
            })
    
    @http.route(['/reservas/confirmacion/<int:reserva_id>'], type='http', auth='user', website=True)
    def reserva_confirmacion(self, reserva_id, **kwargs):
        """Página de confirmación de reserva"""
        reserva = request.env['reserva.reserva'].sudo().browse(reserva_id)
        
        if not reserva.exists():
            return request.redirect('/reservas')
        
        # Verificar que el usuario sea el dueño de la reserva
        if reserva.cliente_id.user_id.id != request.env.user.id:
            return request.redirect('/reservas')
        
        values = {
            'reserva': reserva,
            'page_name': 'confirmacion',
        }
        return request.render('reserva_canchas.website_confirmacion_template', values)
    
    @http.route(['/mis-reservas'], type='http', auth='user', website=True)
    def mis_reservas(self, **kwargs):
        """Portal del usuario con sus reservas"""
        partner = request.env.user.partner_id
        cliente = request.env['reserva.cliente'].sudo().search([
            '|', ('email', '=', partner.email),
            ('user_id', '=', request.env.user.id)
        ], limit=1)
        
        reservas = request.env['reserva.reserva'].sudo().search([
            ('cliente_id', '=', cliente.id)
        ], order='fecha desc, hora_inicio desc')
        
        # Separar reservas activas y pasadas
        hoy = date.today()
        reservas_activas = reservas.filtered(
            lambda r: r.fecha >= hoy and r.estado in ['confirmada', 'borrador', 'en_curso']
        )
        reservas_pasadas = reservas.filtered(
            lambda r: r.fecha < hoy or r.estado in ['completada', 'cancelada', 'no_asistio']
        )
        
        values = {
            'cliente': cliente,
            'reservas_activas': reservas_activas,
            'reservas_pasadas': reservas_pasadas,
            'page_name': 'mis_reservas',
        }
        return request.render('reserva_canchas.website_mis_reservas_template', values)
    
    @http.route(['/reservas/cancelar/<int:reserva_id>'], type='http', auth='user', website=True, methods=['POST'], csrf=True)
    def cancelar_reserva(self, reserva_id, **kwargs):
        """Cancelar una reserva"""
        reserva = request.env['reserva.reserva'].sudo().browse(reserva_id)
        
        # Verificar que el usuario sea el dueño
        if reserva.cliente_id.user_id.id != request.env.user.id:
            return request.redirect('/mis-reservas')
        
        # Solo se pueden cancelar reservas confirmadas o en borrador
        if reserva.estado in ['confirmada', 'borrador']:
            reserva.action_cancelar()
        
        return request.redirect('/mis-reservas?cancelled=true')

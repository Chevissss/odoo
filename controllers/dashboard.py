from odoo import http, fields
from odoo.http import request
from datetime import datetime, timedelta
import json
import logging

_logger = logging.getLogger(__name__)

class DashboardController(http.Controller):

    @http.route('/reservas/dashboard', auth='user', website=True)
    def dashboard(self, **kw):
        """Dashboard de administración"""
        try:
            user = request.env.user
            
            # Verificar permisos
            if not user.has_group('reserva_canchas.group_reserva_admin'):
                return request.render('reserva_canchas.website_error_template', {
                    'error': 'No tienes permisos para acceder al dashboard'
                })
            
            Reserva = request.env['reserva.reserva'].sudo()
            Cancha = request.env['reserva.cancha'].sudo()
            Cliente = request.env['reserva.cliente'].sudo()
            
            hoy = datetime.now().date()
            mes_actual = hoy.replace(day=1)
            
            # Estadísticas
            reservas_hoy = Reserva.search_count([
                ('fecha', '=', hoy),
                ('estado', 'in', ['confirmada', 'en_curso'])
            ])
            
            reservas_mes = Reserva.search_count([
                ('fecha', '>=', mes_actual),
                ('estado', 'in', ['confirmada', 'completada'])
            ])
            
            reservas_completadas_mes = Reserva.search([
                ('fecha', '>=', mes_actual),
                ('estado', '=', 'completada')
            ])
            ingresos_mes = sum(r.monto_total for r in reservas_completadas_mes)
            
            total_canchas = Cancha.search_count([('estado', '=', 'disponible')])
            
            # Top canchas
            cancha_stats = []
            canchas = Cancha.search([])
            for cancha in canchas:
                reservas = Reserva.search([
                    ('cancha_id', '=', cancha.id),
                    ('estado', 'in', ['confirmada', 'completada'])
                ])
                ingresos = sum(r.monto_total for r in reservas)
                cancha_stats.append({
                    'nombre': cancha.name,
                    'reservas': len(reservas),
                    'ingresos': ingresos
                })
            cancha_stats = sorted(cancha_stats, key=lambda x: x['reservas'], reverse=True)[:5]
            
            # Top clientes
            clientes_top = Cliente.search([], order='total_gastado DESC', limit=5)
            
            # Horarios populares
            horarios_stats = {}
            reservas_todas = Reserva.search([
                ('fecha', '>=', hoy - timedelta(days=7)),
                ('estado', 'in', ['confirmada', 'completada'])
            ])
            for res in reservas_todas:
                hora = int(res.hora_inicio)
                horarios_stats[hora] = horarios_stats.get(hora, 0) + 1
            
            horarios_populares = sorted(
                [(h, c) for h, c in horarios_stats.items()],
                key=lambda x: x[1],
                reverse=True
            )[:5]
            
            # Datos para gráfico
            reservas_por_dia = []
            for i in range(7):
                fecha = hoy - timedelta(days=6-i)
                count = Reserva.search_count([
                    ('fecha', '=', fecha),
                    ('estado', 'in', ['confirmada', 'completada'])
                ])
                reservas_por_dia.append({
                    'fecha': fecha.strftime('%d/%m'),
                    'count': count
                })
            
            return request.render('reserva_canchas.dashboard_template', {
                'reservas_hoy': reservas_hoy,
                'reservas_mes': reservas_mes,
                'ingresos_mes': ingresos_mes,
                'total_canchas': total_canchas,
                'cancha_stats': cancha_stats,
                'clientes_top': clientes_top,
                'horarios_populares': horarios_populares,
                'reservas_por_dia': json.dumps(reservas_por_dia),
            })
        except Exception as e:
            _logger.error(f'Error en dashboard: {str(e)}')
            return request.render('reserva_canchas.website_error_template', {
                'error': f'Error al cargar el dashboard: {str(e)}'
            })

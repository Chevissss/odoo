from odoo import http
from odoo.http import request
from datetime import datetime, timedelta, date
import json

class DashboardController(http.Controller):
    
    @http.route(['/reservas/dashboard'], type='http', auth='user', website=True)
    def dashboard(self, **kwargs):
        """Dashboard con estadísticas para administradores"""
        
        # Verificar que el usuario sea administrador
        if not request.env.user.has_group('reserva_canchas.group_reserva_admin'):
            return request.redirect('/reservas')
        
        # Obtener estadísticas
        hoy = date.today()
        mes_actual = hoy.replace(day=1)
        mes_siguiente = (mes_actual + timedelta(days=32)).replace(day=1)
        
        # Reservas del día
        reservas_hoy = request.env['reserva.reserva'].search_count([
            ('fecha', '=', hoy),
            ('estado', 'in', ['confirmada', 'en_curso'])
        ])
        
        # Reservas del mes
        reservas_mes = request.env['reserva.reserva'].search([
            ('fecha', '>=', mes_actual),
            ('fecha', '<', mes_siguiente),
        ])
        
        # Ingresos del mes
        ingresos_mes = sum(reservas_mes.filtered(
            lambda r: r.estado in ['confirmada', 'completada']
        ).mapped('monto_total'))
        
        # Canchas más reservadas
        canchas = request.env['reserva.cancha'].search([])
        cancha_stats = []
        for cancha in canchas:
            reservas = len(cancha.reserva_ids.filtered(
                lambda r: r.estado in ['confirmada', 'completada', 'en_curso']
            ))
            cancha_stats.append({
                'nombre': cancha.name,
                'reservas': reservas,
                'ingresos': cancha.ingresos_total
            })
        
        cancha_stats = sorted(cancha_stats, key=lambda x: x['reservas'], reverse=True)[:5]
        
        # Clientes frecuentes
        clientes = request.env['reserva.cliente'].search([], order='total_reservas desc', limit=5)
        
        # Horarios más solicitados
        horarios = {}
        for reserva in reservas_mes.filtered(lambda r: r.estado != 'cancelada'):
            hora = int(reserva.hora_inicio)
            if hora not in horarios:
                horarios[hora] = 0
            horarios[hora] += 1
        
        horarios_ordenados = sorted(horarios.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Gráfico de reservas por día (últimos 7 días)
        reservas_por_dia = []
        for i in range(7):
            dia = hoy - timedelta(days=6-i)
            count = request.env['reserva.reserva'].search_count([
                ('fecha', '=', dia),
                ('estado', 'in', ['confirmada', 'completada', 'en_curso'])
            ])
            reservas_por_dia.append({
                'fecha': dia.strftime('%d/%m'),
                'count': count
            })
        
        values = {
            'reservas_hoy': reservas_hoy,
            'reservas_mes': len(reservas_mes),
            'ingresos_mes': ingresos_mes,
            'total_canchas': len(canchas),
            'cancha_stats': cancha_stats,
            'clientes_top': clientes,
            'horarios_populares': horarios_ordenados,
            'reservas_por_dia': reservas_por_dia,
            'page_name': 'dashboard',
        }
        
        return request.render('reserva_canchas.dashboard_template', values)
    
    @http.route(['/reservas/stats/json'], type='json', auth='user')
    def get_stats_json(self, periodo='mes', **kwargs):
        """API JSON para obtener estadísticas"""
        
        if not request.env.user.has_group('reserva_canchas.group_reserva_admin'):
            return {'error': 'No autorizado'}
        
        hoy = date.today()
        
        if periodo == 'dia':
            fecha_inicio = hoy
            fecha_fin = hoy
        elif periodo == 'semana':
            fecha_inicio = hoy - timedelta(days=hoy.weekday())
            fecha_fin = fecha_inicio + timedelta(days=6)
        elif periodo == 'mes':
            fecha_inicio = hoy.replace(day=1)
            fecha_fin = (fecha_inicio + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        else:
            fecha_inicio = hoy.replace(month=1, day=1)
            fecha_fin = hoy.replace(month=12, day=31)
        
        reservas = request.env['reserva.reserva'].search([
            ('fecha', '>=', fecha_inicio),
            ('fecha', '<=', fecha_fin),
        ])
        
        return {
            'total_reservas': len(reservas),
            'confirmadas': len(reservas.filtered(lambda r: r.estado == 'confirmada')),
            'completadas': len(reservas.filtered(lambda r: r.estado == 'completada')),
            'canceladas': len(reservas.filtered(lambda r: r.estado == 'cancelada')),
            'ingresos': sum(reservas.filtered(
                lambda r: r.estado in ['confirmada', 'completada']
            ).mapped('monto_total')),
        }

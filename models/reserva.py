from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, timedelta

class Reserva(models.Model):
    _name = 'reserva.reserva'
    _description = 'Reserva de Cancha'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'fecha desc, hora_inicio desc'

    name = fields.Char(string='Número de Reserva', required=True, copy=False, readonly=True, default='Nuevo')
    
    # Información del cliente
    cliente_id = fields.Many2one('reserva.cliente', string='Cliente', required=True, tracking=True)
    telefono_cliente = fields.Char(related='cliente_id.telefono', string='Teléfono', readonly=True)
    email_cliente = fields.Char(related='cliente_id.email', string='Email', readonly=True)
    
    # Información de la reserva
    cancha_id = fields.Many2one('reserva.cancha', string='Cancha', required=True, tracking=True)
    fecha = fields.Date(string='Fecha de Reserva', required=True, default=fields.Date.today, tracking=True)
    hora_inicio = fields.Float(string='Hora de Inicio', required=True, tracking=True)
    hora_fin = fields.Float(string='Hora de Fin', required=True, tracking=True)
    duracion = fields.Float(string='Duración (horas)', compute='_compute_duracion', store=True)
    
    # Tipo de reserva
    tipo_reserva = fields.Selection([
        ('online', 'Reserva Online'),
        ('presencial', 'Reserva Presencial')
    ], string='Tipo de Reserva', required=True, default='presencial', tracking=True)
    
    # Estado
    estado = fields.Selection([
        ('borrador', 'Borrador'),
        ('confirmada', 'Confirmada'),
        ('en_curso', 'En Curso'),
        ('completada', 'Completada'),
        ('cancelada', 'Cancelada'),
        ('no_asistio', 'No Asistió')
    ], string='Estado', default='borrador', required=True, tracking=True)
    
    # Información financiera
    precio_hora = fields.Float(related='cancha_id.precio_hora', string='Precio/Hora', readonly=True)
    monto_total = fields.Float(string='Monto Total', compute='_compute_monto_total', store=True, tracking=True)
    pagado = fields.Boolean(string='Pagado', default=False, tracking=True)
    metodo_pago = fields.Selection([
        ('efectivo', 'Efectivo'),
        ('tarjeta', 'Tarjeta'),
        ('transferencia', 'Transferencia'),
        ('yape', 'Yape/Plin'),
        ('otro', 'Otro')
    ], string='Método de Pago')
    
    # Información adicional
    notas = fields.Text(string='Notas')
    usuario_registro_id = fields.Many2one('res.users', string='Registrado por', default=lambda self: self.env.user, readonly=True)
    fecha_registro = fields.Datetime(string='Fecha de Registro', default=fields.Datetime.now, readonly=True)
    
    # Campos para control
    activa = fields.Boolean(string='Activa', default=True)
    color = fields.Integer(string='Color', compute='_compute_color')
    
    @api.model
    def create(self, vals):
        if vals.get('name', 'Nuevo') == 'Nuevo':
            vals['name'] = self.env['ir.sequence'].next_by_code('reserva.reserva') or 'Nuevo'
        return super(Reserva, self).create(vals)
    
    @api.depends('hora_inicio', 'hora_fin')
    def _compute_duracion(self):
        for record in self:
            if record.hora_inicio and record.hora_fin:
                record.duracion = record.hora_fin - record.hora_inicio
            else:
                record.duracion = 0
    
    @api.depends('duracion', 'precio_hora')
    def _compute_monto_total(self):
        for record in self:
            record.monto_total = record.duracion * record.precio_hora
    
    @api.depends('estado')
    def _compute_color(self):
        colores = {
            'borrador': 0,
            'confirmada': 4,
            'en_curso': 2,
            'completada': 10,
            'cancelada': 1,
            'no_asistio': 3
        }
        for record in self:
            record.color = colores.get(record.estado, 0)
    
    @api.constrains('fecha', 'hora_inicio', 'hora_fin', 'cancha_id')
    def _check_disponibilidad(self):
        for record in self:
            if record.hora_inicio >= record.hora_fin:
                raise ValidationError('La hora de fin debe ser mayor a la hora de inicio.')
            
            if record.hora_inicio < 6 or record.hora_fin > 23:
                raise ValidationError('El horario permitido es de 6:00 AM a 11:00 PM.')
            
            # Verificar que la cancha esté disponible
            if record.cancha_id.estado != 'disponible':
                raise ValidationError('La cancha seleccionada no está disponible.')
            
            # Verificar conflictos de horario
            conflictos = self.env['reserva.reserva'].search([
                ('id', '!=', record.id),
                ('cancha_id', '=', record.cancha_id.id),
                ('fecha', '=', record.fecha),
                ('estado', 'in', ['confirmada', 'en_curso', 'borrador']),
                '|',
                '&', ('hora_inicio', '<', record.hora_fin), ('hora_inicio', '>=', record.hora_inicio),
                '&', ('hora_fin', '>', record.hora_inicio), ('hora_fin', '<=', record.hora_fin)
            ])
            
            if conflictos:
                raise ValidationError('Ya existe una reserva en ese horario para esta cancha.')
    
    @api.constrains('fecha')
    def _check_fecha(self):
        for record in self:
            if record.fecha < fields.Date.today():
                raise ValidationError('No se pueden crear reservas en fechas pasadas.')
    
    def action_confirmar(self):
        self.estado = 'confirmada'
        # Enviar notificación al cliente
        self.message_post(body=f'Reserva confirmada para {self.fecha} de {self.hora_inicio:.2f} a {self.hora_fin:.2f} horas.')
    
    def action_iniciar(self):
        self.estado = 'en_curso'
    
    def action_completar(self):
        if not self.pagado:
            raise UserError('No se puede completar una reserva sin pago.')
        self.estado = 'completada'
    
    def action_cancelar(self):
        self.estado = 'cancelada'
        self.activa = False
    
    def action_marcar_no_asistio(self):
        self.estado = 'no_asistio'
        self.activa = False
    
    def action_marcar_pagado(self):
        if not self.metodo_pago:
            raise UserError('Debe seleccionar un método de pago.')
        self.pagado = True
    
    @api.model
    def get_horarios_disponibles(self, cancha_id, fecha):
        """Retorna los horarios disponibles para una cancha en una fecha específica"""
        reservas = self.search([
            ('cancha_id', '=', cancha_id),
            ('fecha', '=', fecha),
            ('estado', 'in', ['confirmada', 'en_curso', 'borrador'])
        ])
        
        horarios_ocupados = []
        for reserva in reservas:
            horarios_ocupados.append({
                'inicio': reserva.hora_inicio,
                'fin': reserva.hora_fin
            })
        
        return horarios_ocupados

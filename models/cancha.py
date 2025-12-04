from odoo import models, fields, api
from odoo.exceptions import ValidationError

class Cancha(models.Model):
    _name = 'reserva.cancha'
    _description = 'Cancha Deportiva'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Nombre de la Cancha', required=True, tracking=True)
    codigo = fields.Char(string='Código', required=True, copy=False, readonly=True, default='Nuevo')
    tipo_deporte = fields.Selection([
        ('futbol', 'Fútbol'),
        ('futsal', 'Futsal'),
        ('basquet', 'Básquetbol'),
        ('voley', 'Vóleibol'),
        ('tenis', 'Tenis'),
        ('padel', 'Pádel'),
        ('otro', 'Otro')
    ], string='Tipo de Deporte', required=True, tracking=True)
    
    tipo_superficie = fields.Selection([
        ('cesped_natural', 'Césped Natural'),
        ('cesped_sintetico', 'Césped Sintético'),
        ('cemento', 'Cemento'),
        ('parquet', 'Parquet'),
        ('tierra', 'Tierra'),
        ('otro', 'Otro')
    ], string='Tipo de Superficie', tracking=True)
    
    capacidad = fields.Integer(string='Capacidad (jugadores)', default=10)
    precio_hora = fields.Float(string='Precio por Hora', required=True, tracking=True)
    estado = fields.Selection([
        ('disponible', 'Disponible'),
        ('mantenimiento', 'En Mantenimiento'),
        ('inactiva', 'Inactiva')
    ], string='Estado', default='disponible', required=True, tracking=True)
    
    techada = fields.Boolean(string='Techada', default=False)
    iluminacion = fields.Boolean(string='Iluminación Nocturna', default=False)
    vestuarios = fields.Boolean(string='Vestuarios', default=False)
    estacionamiento = fields.Boolean(string='Estacionamiento', default=False)
    
    descripcion = fields.Text(string='Descripción')
    imagen = fields.Binary(string='Imagen de la Cancha')
    
    # Relaciones
    reserva_ids = fields.One2many('reserva.reserva', 'cancha_id', string='Reservas')
    reservas_count = fields.Integer(string='Total Reservas', compute='_compute_reservas_count')
    
    # Campos calculados
    disponibilidad_hoy = fields.Boolean(string='Disponible Hoy', compute='_compute_disponibilidad_hoy')
    ingresos_total = fields.Float(string='Ingresos Totales', compute='_compute_ingresos_total')
    
    _sql_constraints = [
        ('codigo_unique', 'UNIQUE(codigo)', 'El código de la cancha debe ser único!')
    ]
    
    @api.model
    def create(self, vals):
        if vals.get('codigo', 'Nuevo') == 'Nuevo':
            vals['codigo'] = self.env['ir.sequence'].next_by_code('reserva.cancha') or 'Nuevo'
        return super(Cancha, self).create(vals)
    
    @api.depends('reserva_ids')
    def _compute_reservas_count(self):
        for record in self:
            record.reservas_count = len(record.reserva_ids)
    
    @api.depends('reserva_ids', 'estado')
    def _compute_disponibilidad_hoy(self):
        for record in self:
            if record.estado != 'disponible':
                record.disponibilidad_hoy = False
            else:
                hoy = fields.Date.today()
                reservas_hoy = self.env['reserva.reserva'].search([
                    ('cancha_id', '=', record.id),
                    ('fecha', '=', hoy),
                    ('estado', 'in', ['confirmada', 'en_curso'])
                ])
                record.disponibilidad_hoy = len(reservas_hoy) < 12  # Asumiendo 12 horas disponibles
    
    @api.depends('reserva_ids', 'reserva_ids.monto_total', 'reserva_ids.estado')
    def _compute_ingresos_total(self):
        for record in self:
            reservas_pagadas = record.reserva_ids.filtered(lambda r: r.estado in ['confirmada', 'completada'])
            record.ingresos_total = sum(reservas_pagadas.mapped('monto_total'))
    
    @api.constrains('precio_hora')
    def _check_precio_hora(self):
        for record in self:
            if record.precio_hora <= 0:
                raise ValidationError('El precio por hora debe ser mayor a cero.')
    
    def action_set_disponible(self):
        self.estado = 'disponible'
    
    def action_set_mantenimiento(self):
        self.estado = 'mantenimiento'
    
    def action_ver_reservas(self):
        return {
            'name': 'Reservas de ' + self.name,
            'type': 'ir.actions.act_window',
            'res_model': 'reserva.reserva',
            'view_mode': 'tree,form,calendar',
            'domain': [('cancha_id', '=', self.id)],
            'context': {'default_cancha_id': self.id}
        }

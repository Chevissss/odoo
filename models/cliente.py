from odoo import models, fields, api

class Cliente(models.Model):
    _name = 'reserva.cliente'
    _description = 'Cliente'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Nombre Completo', required=True, tracking=True)
    partner_id = fields.Many2one('res.partner', string='Contacto', ondelete='cascade')
    
    dni = fields.Char(string='DNI', required=True, tracking=True)
    telefono = fields.Char(string='Teléfono', required=True)
    email = fields.Char(string='Email')
    direccion = fields.Text(string='Dirección')
    
    tipo_cliente = fields.Selection([
        ('nuevo', 'Nuevo'),
        ('ocasional', 'Ocasional'),
        ('frecuente', 'Frecuente')
    ], string='Tipo de Cliente', default='nuevo', compute='_compute_tipo_cliente', store=True)
    
    reserva_ids = fields.One2many('reserva.reserva', 'cliente_id', string='Reservas')
    total_reservas = fields.Integer(string='Total Reservas', compute='_compute_total_reservas')
    total_gastado = fields.Float(string='Total Gastado', compute='_compute_total_gastado')
    
    _sql_constraints = [
        ('dni_unique', 'UNIQUE(dni)', '¡El DNI ya está registrado!')
    ]
    
    @api.depends('reserva_ids')
    def _compute_total_reservas(self):
        for record in self:
            record.total_reservas = len(record.reserva_ids.filtered(lambda r: r.estado == 'completada'))
    
    @api.depends('reserva_ids.monto_total', 'reserva_ids.estado')
    def _compute_total_gastado(self):
        for record in self:
            reservas_pagadas = record.reserva_ids.filtered(lambda r: r.estado in ['completada', 'confirmada'])
            record.total_gastado = sum(reservas_pagadas.mapped('monto_total'))
    
    @api.depends('total_reservas')
    def _compute_tipo_cliente(self):
        for record in self:
            if record.total_reservas == 0:
                record.tipo_cliente = 'nuevo'
            elif record.total_reservas < 5:
                record.tipo_cliente = 'ocasional'
            else:
                record.tipo_cliente = 'frecuente'

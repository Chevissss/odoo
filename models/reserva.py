from odoo import models, fields, api
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError

class Reserva(models.Model):
    _name = 'reserva.reserva'
    _description = 'Reserva de Cancha'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Número de Reserva', readonly=True, copy=False, default='Nuevo')
    cliente_id = fields.Many2one('reserva.cliente', string='Cliente', required=True, tracking=True)
    partner_id = fields.Many2one('res.partner', string='Contacto', related='cliente_id.partner_id')
    cancha_id = fields.Many2one('reserva.cancha', string='Cancha', required=True, tracking=True)
    
    fecha = fields.Date(string='Fecha', required=True, tracking=True)
    hora_inicio = fields.Float(string='Hora Inicio', required=True, tracking=True)
    hora_fin = fields.Float(string='Hora Fin', required=True, tracking=True)
    duracion = fields.Float(string='Duración (horas)', compute='_compute_duracion', store=True)
    
    estado = fields.Selection([
        ('borrador', 'Borrador'),
        ('confirmada', 'Confirmada'),
        ('en_curso', 'En Curso'),
        ('completada', 'Completada'),
        ('cancelada', 'Cancelada'),
        ('no_asistio', 'No Asistió')
    ], string='Estado', default='borrador', required=True, tracking=True)
    
    monto_total = fields.Float(string='Monto Total', compute='_compute_monto_total', store=True)
    metodo_pago = fields.Selection([
        ('efectivo', 'Efectivo'),
        ('tarjeta', 'Tarjeta'),
        ('transferencia', 'Transferencia'),
        ('yape', 'Yape/Plin'),
        ('otro', 'Otro')
    ], string='Método de Pago')
    pagado = fields.Boolean(string='Pagado', default=False, tracking=True)
    
    notas = fields.Text(string='Notas Adicionales')
    
    _sql_constraints = [
        ('fecha_hora_cancha_unique', 'UNIQUE(cancha_id, fecha, hora_inicio)', 
         '¡La cancha ya tiene una reserva en ese horario!')
    ]
    
    @api.model
    def create(self, vals):
        if vals.get('name', 'Nuevo') == 'Nuevo':
            vals['name'] = self.env['ir.sequence'].next_by_code('reserva.reserva') or 'Nuevo'
        return super(Reserva, self).create(vals)
    
    @api.depends('hora_inicio', 'hora_fin')
    def _compute_duracion(self):
        for record in self:
            record.duracion = record.hora_fin - record.hora_inicio
    
    @api.depends('duracion', 'cancha_id')
    def _compute_monto_total(self):
        for record in self:
            record.monto_total = record.duracion * record.cancha_id.precio_hora
    
    @api.constrains('hora_inicio', 'hora_fin')
    def _check_horarios(self):
        for record in self:
            if record.hora_inicio < 6 or record.hora_fin > 23:
                raise ValidationError('Los horarios disponibles son de 6:00 a 23:00')
            if record.hora_inicio >= record.hora_fin:
                raise ValidationError('La hora de inicio debe ser menor a la hora de fin')
    
    @api.constrains('fecha')
    def _check_fecha(self):
        for record in self:
            if record.fecha < fields.Date.today():
                raise ValidationError('No se pueden hacer reservas en fechas pasadas')
    
    def action_confirmar(self):
        self.write({'estado': 'confirmada'})
    
    def action_completar(self):
        self.write({'estado': 'completada'})
    
    def action_cancelar(self):
        self.write({'estado': 'cancelada'})
    
    def action_no_asistio(self):
        self.write({'estado': 'no_asistio'})

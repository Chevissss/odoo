from odoo import models, fields, api
from odoo.exceptions import ValidationError
import re

class Cliente(models.Model):
    _name = 'reserva.cliente'
    _description = 'Cliente'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char(string='Nombre Completo', required=True, tracking=True)
    documento = fields.Char(string='DNI/Documento', tracking=True)
    telefono = fields.Char(string='Teléfono', required=True, tracking=True)
    email = fields.Char(string='Email', tracking=True)
    direccion = fields.Char(string='Dirección')
    fecha_nacimiento = fields.Date(string='Fecha de Nacimiento')
    
    # Información adicional
    tipo_cliente = fields.Selection([
        ('frecuente', 'Frecuente'),
        ('ocasional', 'Ocasional'),
        ('nuevo', 'Nuevo')
    ], string='Tipo de Cliente', default='nuevo', tracking=True)
    
    activo = fields.Boolean(string='Activo', default=True)
    notas = fields.Text(string='Notas')
    
    # Relaciones
    reserva_ids = fields.One2many('reserva.reserva', 'cliente_id', string='Reservas')
    
    # Campos calculados
    total_reservas = fields.Integer(string='Total de Reservas', compute='_compute_estadisticas')
    total_gastado = fields.Float(string='Total Gastado', compute='_compute_estadisticas')
    ultima_reserva = fields.Date(string='Última Reserva', compute='_compute_estadisticas')
    
    # Portal
    user_id = fields.Many2one('res.users', string='Usuario Portal')
    
    _sql_constraints = [
        ('documento_unique', 'UNIQUE(documento)', 'El documento ya está registrado!')
    ]
    
    @api.depends('reserva_ids')
    def _compute_estadisticas(self):
        for record in self:
            reservas_validas = record.reserva_ids.filtered(lambda r: r.estado in ['confirmada', 'completada', 'en_curso'])
            record.total_reservas = len(reservas_validas)
            record.total_gastado = sum(reservas_validas.mapped('monto_total'))
            
            if reservas_validas:
                record.ultima_reserva = max(reservas_validas.mapped('fecha'))
            else:
                record.ultima_reserva = False
    
    @api.constrains('email')
    def _check_email(self):
        for record in self:
            if record.email:
                if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', record.email):
                    raise ValidationError('El formato del email no es válido.')
    
    @api.constrains('telefono')
    def _check_telefono(self):
        for record in self:
            if record.telefono:
                if not re.match(r'^[0-9+\-\s()]{7,15}$', record.telefono):
                    raise ValidationError('El formato del teléfono no es válido.')
    
    @api.onchange('total_reservas')
    def _onchange_tipo_cliente(self):
        """Actualiza automáticamente el tipo de cliente según sus reservas"""
        for record in self:
            if record.total_reservas == 0:
                record.tipo_cliente = 'nuevo'
            elif record.total_reservas <= 5:
                record.tipo_cliente = 'ocasional'
            else:
                record.tipo_cliente = 'frecuente'
    
    def action_ver_reservas(self):
        return {
            'name': 'Reservas de ' + self.name,
            'type': 'ir.actions.act_window',
            'res_model': 'reserva.reserva',
            'view_mode': 'tree,form,calendar',
            'domain': [('cliente_id', '=', self.id)],
            'context': {'default_cliente_id': self.id}
        }
    
    def action_crear_usuario_portal(self):
        """Crea un usuario de portal para el cliente"""
        if self.user_id:
            raise ValidationError('Este cliente ya tiene un usuario de portal.')
        
        if not self.email:
            raise ValidationError('El cliente debe tener un email para crear un usuario de portal.')
        
        # Crear usuario de portal
        usuario = self.env['res.users'].create({
            'name': self.name,
            'login': self.email,
            'email': self.email,
            'groups_id': [(6, 0, [self.env.ref('base.group_portal').id])],
            'partner_id': self.env['res.partner'].create({
                'name': self.name,
                'email': self.email,
                'phone': self.telefono,
            }).id
        })
        
        self.user_id = usuario.id
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Usuario Creado',
                'message': f'Usuario de portal creado exitosamente para {self.name}',
                'type': 'success',
                'sticky': False,
            }
        }

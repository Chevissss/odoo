odoo.define('reserva_canchas.reservas', function (require) {
    'use strict';

    var publicWidget = require('web.public.widget');
    var ajax = require('web.ajax');

    // Widget para filtrado de canchas
    publicWidget.registry.CanchasFiltro = publicWidget.Widget.extend({
        selector: '#canchas-grid',
        events: {
            'click .btn-outline-primary': '_onFilterClick',
        },

        start: function () {
            this._super.apply(this, arguments);
            this.canchas = this.$el.find('.cancha-item');
        },

        _onFilterClick: function (ev) {
            ev.preventDefault();
            var $button = $(ev.currentTarget);
            var filter = $button.data('filter');

            // Actualizar botones activos
            $button.siblings().removeClass('active');
            $button.addClass('active');

            // Filtrar canchas
            if (filter === 'all') {
                this.canchas.fadeIn();
            } else {
                this.canchas.each(function () {
                    var $cancha = $(this);
                    if ($cancha.data('deporte') === filter) {
                        $cancha.fadeIn();
                    } else {
                        $cancha.fadeOut();
                    }
                });
            }
        },
    });

    // Widget para disponibilidad de horarios
    publicWidget.registry.DisponibilidadHorarios = publicWidget.Widget.extend({
        selector: '.oe_website_sale',
        events: {
            'change #fecha_reserva': '_onFechaChange',
            'click .horario-slot.disponible': '_onHorarioClick',
            'click #btn_reservar': '_onReservarClick',
        },

        start: function () {
            this._super.apply(this, arguments);
            
            // Cargar horarios iniciales si estamos en la página de detalle
            if ($('#fecha_reserva').length && typeof cancha_id !== 'undefined') {
                this._cargarHorarios();
            }

            this.horariosSeleccionados = [];
        },

        _onFechaChange: function () {
            this.horariosSeleccionados = [];
            $('#seleccion_info').hide();
            $('#btn_reservar').hide();
            this._cargarHorarios();
        },

        _cargarHorarios: function () {
            var self = this;
            var fecha = $('#fecha_reserva').val();
            
            if (!fecha || typeof cancha_id === 'undefined') {
                return;
            }

            // Mostrar loader
            $('#horarios_disponibles').html(
                '<div class="text-center py-4">' +
                '<div class="spinner-border text-primary" role="status"></div>' +
                '<p class="mt-2">Cargando horarios...</p>' +
                '</div>'
            );

            // Llamar al servidor
            ajax.jsonRpc('/reservas/disponibilidad', 'call', {
                cancha_id: cancha_id,
                fecha: fecha
            }).then(function (result) {
                if (result.error) {
                    $('#horarios_disponibles').html(
                        '<div class="alert alert-danger">' +
                        '<i class="fa fa-exclamation-triangle"></i> ' + result.error +
                        '</div>'
                    );
                    return;
                }

                self._renderHorarios(result.horarios);
            }).catch(function (error) {
                $('#horarios_disponibles').html(
                    '<div class="alert alert-danger">' +
                    '<i class="fa fa-exclamation-triangle"></i> Error al cargar horarios' +
                    '</div>'
                );
            });
        },

        _renderHorarios: function (horarios) {
            var html = '<div class="horarios-grid">';
            
            horarios.forEach(function (horario) {
                var clases = 'horario-slot ';
                clases += horario.disponible ? 'disponible' : 'ocupado';
                
                var horaStr = horario.hora < 10 ? '0' + horario.hora : horario.hora;
                
                html += '<div class="' + clases + '" data-hora="' + horario.hora + '">';
                html += '<span class="hora">' + horaStr + ':00</span>';
                if (horario.disponible) {
                    html += '<span class="precio">S/ ' + horario.precio.toFixed(2) + '</span>';
                } else {
                    html += '<span class="text-danger"><small>Ocupado</small></span>';
                }
                html += '</div>';
            });
            
            html += '</div>';
            
            $('#horarios_disponibles').html(html).addClass('fade-in');
        },

        _onHorarioClick: function (ev) {
            var $slot = $(ev.currentTarget);
            var hora = parseInt($slot.data('hora'));

            // Si ya está seleccionado, deseleccionar
            if ($slot.hasClass('seleccionado')) {
                this.horariosSeleccionados = this.horariosSeleccionados.filter(h => h !== hora);
                $slot.removeClass('seleccionado');
            } else {
                // Limitar a horarios consecutivos
                if (this.horariosSeleccionados.length > 0) {
                    var ultimo = Math.max(...this.horariosSeleccionados);
                    if (hora !== ultimo + 1) {
                        alert('Por favor selecciona horarios consecutivos');
                        return;
                    }
                }
                
                this.horariosSeleccionados.push(hora);
                $slot.addClass('seleccionado');
            }

            // Actualizar información
            this._actualizarSeleccion();
        },

        _actualizarSeleccion: function () {
            if (this.horariosSeleccionados.length === 0) {
                $('#seleccion_info').hide();
                $('#btn_reservar').hide();
                return;
            }

            // Ordenar horarios
            this.horariosSeleccionados.sort((a, b) => a - b);

            var horaInicio = Math.min(...this.horariosSeleccionados);
            var horaFin = Math.max(...this.horariosSeleccionados) + 1;
            var duracion = this.horariosSeleccionados.length;
            var total = duracion * (typeof precio_hora !== 'undefined' ? precio_hora : 0);

            var fecha = $('#fecha_reserva').val();
            var fechaObj = new Date(fecha + 'T00:00:00');
            var fechaStr = fechaObj.toLocaleDateString('es-PE', {
                weekday: 'long',
                year: 'numeric',
                month: 'long',
                day: 'numeric'
            });

            $('#info_fecha').text(fechaStr);
            $('#info_horario').text(
                (horaInicio < 10 ? '0' : '') + horaInicio + ':00 - ' +
                (horaFin < 10 ? '0' : '') + horaFin + ':00'
            );
            $('#info_duracion').text(duracion + ' hora' + (duracion > 1 ? 's' : ''));
            $('#info_total').text(total.toFixed(2));

            $('#seleccion_info').show().addClass('fade-in');
            $('#btn_reservar')
                .show()
                .addClass('fade-in pulse')
                .data('hora-inicio', horaInicio)
                .data('hora-fin', horaFin);
        },

        _onReservarClick: function (ev) {
            var $btn = $(ev.currentTarget);
            var canchaId = $btn.data('cancha-id');
            var horaInicio = $btn.data('hora-inicio');
            var horaFin = $btn.data('hora-fin');
            var fecha = $('#fecha_reserva').val();

            // Redirigir al formulario de reserva
            window.location.href = '/reservas/crear?' +
                'cancha_id=' + canchaId +
                '&fecha=' + fecha +
                '&hora_inicio=' + horaInicio +
                '&hora_fin=' + horaFin;
        },
    });

    // Animaciones al scroll
    $(window).on('scroll', function () {
        $('.fade-in').each(function () {
            var elementTop = $(this).offset().top;
            var elementBottom = elementTop + $(this).outerHeight();
            var viewportTop = $(window).scrollTop();
            var viewportBottom = viewportTop + $(window).height();

            if (elementBottom > viewportTop && elementTop < viewportBottom) {
                $(this).addClass('visible');
            }
        });
    });

    // Confirmación de formularios
    $('form[data-confirm]').on('submit', function (e) {
        var mensaje = $(this).data('confirm');
        if (!confirm(mensaje)) {
            e.preventDefault();
            return false;
        }
    });

    return {
        CanchasFiltro: publicWidget.registry.CanchasFiltro,
        DisponibilidadHorarios: publicWidget.registry.DisponibilidadHorarios,
    };
});

// Código adicional para páginas sin widget
$(document).ready(function () {
    // Auto-ocultar alertas después de 5 segundos
    setTimeout(function () {
        $('.alert-dismissible').fadeOut();
    }, 5000);

    // Validación de formularios
    $('form.needs-validation').on('submit', function (e) {
        if (!this.checkValidity()) {
            e.preventDefault();
            e.stopPropagation();
        }
        $(this).addClass('was-validated');
    });

    // Tooltips de Bootstrap
    $('[data-toggle="tooltip"]').tooltip();

    // Smooth scroll para enlaces internos
    $('a[href^="#"]').on('click', function (e) {
        var target = $(this.getAttribute('href'));
        if (target.length) {
            e.preventDefault();
            $('html, body').stop().animate({
                scrollTop: target.offset().top - 80
            }, 1000);
        }
    });
});

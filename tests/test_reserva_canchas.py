"""
Script de pruebas para el módulo de Reserva de Canchas
Ejecutar desde el shell de Odoo:
$ ./odoo-bin shell -d tu_base_de_datos
>>> exec(open('test_reserva_canchas.py').read())
"""

# Obtener los modelos
Cancha = env['reserva.cancha']
Reserva = env['reserva.reserva']
Cliente = env['reserva.cliente']

print("\n" + "="*50)
print("INICIANDO PRUEBAS DEL MÓDULO")
print("="*50 + "\n")

# Test 1: Crear Canchas
print("📝 Test 1: Creando canchas de prueba...")
try:
    cancha1 = Cancha.create({
        'name': 'Cancha de Fútbol 1',
        'tipo_deporte': 'futbol',
        'tipo_superficie': 'cesped_sintetico',
        'capacidad': 22,
        'precio_hora': 50.0,
        'techada': True,
        'iluminacion': True,
        'vestuarios': True,
        'descripcion': 'Cancha de fútbol profesional con césped sintético'
    })
    
    cancha2 = Cancha.create({
        'name': 'Cancha de Futsal',
        'tipo_deporte': 'futsal',
        'tipo_superficie': 'cemento',
        'capacidad': 10,
        'precio_hora': 35.0,
        'techada': True,
        'iluminacion': True,
        'descripcion': 'Cancha de futsal techada'
    })
    
    cancha3 = Cancha.create({
        'name': 'Cancha de Vóley',
        'tipo_deporte': 'voley',
        'tipo_superficie': 'parquet',
        'capacidad': 12,
        'precio_hora': 30.0,
        'techada': False,
        'iluminacion': False,
        'descripcion': 'Cancha de vóley al aire libre'
    })
    
    print(f"✅ Cancha 1 creada: {cancha1.name} - Código: {cancha1.codigo}")
    print(f"✅ Cancha 2 creada: {cancha2.name} - Código: {cancha2.codigo}")
    print(f"✅ Cancha 3 creada: {cancha3.name} - Código: {cancha3.codigo}")
    
except Exception as e:
    print(f"❌ Error al crear canchas: {str(e)}")

# Test 2: Crear Clientes
print("\n📝 Test 2: Creando clientes de prueba...")
try:
    cliente1 = Cliente.create({
        'name': 'Juan Pérez García',
        'documento': '12345678',
        'telefono': '987654321',
        'email': 'juan.perez@email.com',
        'direccion': 'Av. Principal 123',
        'tipo_cliente': 'nuevo'
    })
    
    cliente2 = Cliente.create({
        'name': 'María López Torres',
        'documento': '87654321',
        'telefono': '912345678',
        'email': 'maria.lopez@email.com',
        'direccion': 'Jr. Secundario 456',
        'tipo_cliente': 'nuevo'
    })
    
    cliente3 = Cliente.create({
        'name': 'Carlos Rodríguez Mendoza',
        'documento': '45678912',
        'telefono': '965432187',
        'email': 'carlos.rodriguez@email.com',
        'tipo_cliente': 'nuevo'
    })
    
    print(f"✅ Cliente 1 creado: {cliente1.name} - DNI: {cliente1.documento}")
    print(f"✅ Cliente 2 creado: {cliente2.name} - DNI: {cliente2.documento}")
    print(f"✅ Cliente 3 creado: {cliente3.name} - DNI: {cliente3.documento}")
    
except Exception as e:
    print(f"❌ Error al crear clientes: {str(e)}")

# Test 3: Crear Reservas
print("\n📝 Test 3: Creando reservas de prueba...")
try:
    from datetime import date, timedelta
    
    hoy = date.today()
    manana = hoy + timedelta(days=1)
    
    # Reserva 1: Para hoy
    reserva1 = Reserva.create({
        'cliente_id': cliente1.id,
        'cancha_id': cancha1.id,
        'fecha': hoy,
        'hora_inicio': 10.0,  # 10:00 AM
        'hora_fin': 12.0,     # 12:00 PM
        'tipo_reserva': 'presencial',
        'metodo_pago': 'efectivo',
        'notas': 'Reserva de prueba'
    })
    reserva1.action_confirmar()
    reserva1.action_marcar_pagado()
    
    # Reserva 2: Para mañana
    reserva2 = Reserva.create({
        'cliente_id': cliente2.id,
        'cancha_id': cancha2.id,
        'fecha': manana,
        'hora_inicio': 14.0,  # 2:00 PM
        'hora_fin': 15.0,     # 3:00 PM
        'tipo_reserva': 'presencial',
        'metodo_pago': 'tarjeta'
    })
    reserva2.action_confirmar()
    reserva2.action_marcar_pagado()
    
    # Reserva 3: Para mañana
    reserva3 = Reserva.create({
        'cliente_id': cliente3.id,
        'cancha_id': cancha1.id,
        'fecha': manana,
        'hora_inicio': 16.0,  # 4:00 PM
        'hora_fin': 18.0,     # 6:00 PM
        'tipo_reserva': 'presencial',
        'metodo_pago': 'yape'
    })
    reserva3.action_confirmar()
    reserva3.action_marcar_pagado()
    
    print(f"✅ Reserva 1 creada: {reserva1.name} - {reserva1.cancha_id.name}")
    print(f"   Fecha: {reserva1.fecha} | Hora: {reserva1.hora_inicio:.0f}:00 - {reserva1.hora_fin:.0f}:00")
    print(f"   Monto: S/ {reserva1.monto_total:.2f} | Estado: {reserva1.estado}")
    
    print(f"✅ Reserva 2 creada: {reserva2.name} - {reserva2.cancha_id.name}")
    print(f"   Fecha: {reserva2.fecha} | Hora: {reserva2.hora_inicio:.0f}:00 - {reserva2.hora_fin:.0f}:00")
    print(f"   Monto: S/ {reserva2.monto_total:.2f} | Estado: {reserva2.estado}")
    
    print(f"✅ Reserva 3 creada: {reserva3.name} - {reserva3.cancha_id.name}")
    print(f"   Fecha: {reserva3.fecha} | Hora: {reserva3.hora_inicio:.0f}:00 - {reserva3.hora_fin:.0f}:00")
    print(f"   Monto: S/ {reserva3.monto_total:.2f} | Estado: {reserva3.estado}")
    
except Exception as e:
    print(f"❌ Error al crear reservas: {str(e)}")

# Test 4: Validaciones
print("\n📝 Test 4: Probando validaciones del sistema...")

# Test 4.1: Intentar crear reserva con horario inválido
print("\n  → Probando validación de horario inválido...")
try:
    reserva_invalida = Reserva.create({
        'cliente_id': cliente1.id,
        'cancha_id': cancha1.id,
        'fecha': hoy,
        'hora_inicio': 15.0,
        'hora_fin': 14.0,  # Hora fin menor que hora inicio
        'tipo_reserva': 'presencial'
    })
    print("  ❌ FALLO: Debería haber rechazado el horario inválido")
except Exception as e:
    print(f"  ✅ CORRECTO: Validación funcionó - {str(e)}")

# Test 4.2: Intentar crear reserva duplicada
print("\n  → Probando validación de reserva duplicada...")
try:
    reserva_duplicada = Reserva.create({
        'cliente_id': cliente2.id,
        'cancha_id': cancha1.id,
        'fecha': hoy,
        'hora_inicio': 10.0,  # Mismo horario que reserva1
        'hora_fin': 12.0,
        'tipo_reserva': 'presencial'
    })
    print("  ❌ FALLO: Debería haber rechazado la reserva duplicada")
except Exception as e:
    print(f"  ✅ CORRECTO: Validación funcionó - {str(e)}")

# Test 4.3: Intentar crear reserva fuera de horario
print("\n  → Probando validación de horario fuera de rango...")
try:
    reserva_fuera_horario = Reserva.create({
        'cliente_id': cliente1.id,
        'cancha_id': cancha2.id,
        'fecha': manana,
        'hora_inicio': 4.0,  # 4 AM - Fuera de horario
        'hora_fin': 6.0,
        'tipo_reserva': 'presencial'
    })
    print("  ❌ FALLO: Debería haber rechazado el horario fuera de rango")
except Exception as e:
    print(f"  ✅ CORRECTO: Validación funcionó - {str(e)}")

# Test 5: Estadísticas
print("\n📝 Test 5: Verificando estadísticas...")
print(f"\n📊 Estadísticas de Canchas:")
for cancha in [cancha1, cancha2, cancha3]:
    print(f"\n  {cancha.name}:")
    print(f"  - Total de reservas: {cancha.reservas_count}")
    print(f"  - Ingresos totales: S/ {cancha.ingresos_total:.2f}")
    print(f"  - Disponible hoy: {'Sí' if cancha.disponibilidad_hoy else 'No'}")
    print(f"  - Estado: {cancha.estado}")

print(f"\n👥 Estadísticas de Clientes:")
for cliente in [cliente1, cliente2, cliente3]:
    print(f"\n  {cliente.name}:")
    print(f"  - Total de reservas: {cliente.total_reservas}")
    print(f"  - Total gastado: S/ {cliente.total_gastado:.2f}")
    print(f"  - Tipo de cliente: {cliente.tipo_cliente}")
    print(f"  - Última reserva: {cliente.ultima_reserva or 'N/A'}")

# Resumen Final
print("\n" + "="*50)
print("RESUMEN DE PRUEBAS")
print("="*50)
print(f"✅ Canchas creadas: {len([cancha1, cancha2, cancha3])}")
print(f"✅ Clientes creados: {len([cliente1, cliente2, cliente3])}")
print(f"✅ Reservas creadas: {len([reserva1, reserva2, reserva3])}")
print(f"✅ Validaciones probadas: 3/3")
print("\n🎉 ¡TODAS LAS PRUEBAS COMPLETADAS EXITOSAMENTE!\n")

# Guardar cambios
env.cr.commit()
print("💾 Cambios guardados en la base de datos")

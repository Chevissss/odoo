# 🏟️ Sistema de Reserva de Canchas Deportivas - Odoo Module

## 📋 Descripción

Módulo completo para la gestión de reservas de canchas deportivas, diseñado para Odoo 15/16/17. Permite gestionar reservas tanto presenciales (a través de personal administrativo) como online (a través de un portal web para clientes).

## ✨ Características Principales

### 🔐 Control de Acceso por Roles

- **Administrador**: Control total del sistema
  - Crear, editar y eliminar canchas
  - Gestión completa de reservas
  - Acceso a reportes y estadísticas
  - Configuración de precios y horarios

- **Staff/Recepcionista**: Operaciones diarias
  - Crear reservas presenciales
  - Registrar nuevos clientes
  - Consultar disponibilidad
  - Marcar pagos
  - Ver calendario de reservas

- **Clientes (Portal)**: Acceso limitado
  - Ver canchas disponibles
  - Realizar reservas online
  - Ver historial de reservas
  - Gestionar perfil

### 🏟️ Gestión de Canchas

- Registro detallado de canchas con:
  - Tipo de deporte (Fútbol, Futsal, Básquet, Vóley, Tenis, Pádel)
  - Tipo de superficie (Césped natural/sintético, Cemento, Parquet, Tierra)
  - Capacidad de jugadores
  - Precio por hora
  - Características (Techada, Iluminación, Vestuarios, Estacionamiento)
  - Imágenes
  - Estado (Disponible, Mantenimiento, Inactiva)

- Estadísticas por cancha:
  - Total de reservas
  - Ingresos generados
  - Disponibilidad en tiempo real

### 📅 Sistema de Reservas

- **Validaciones inteligentes:**
  - Prevención de reservas duplicadas
  - Validación de horarios (6:00 AM - 11:00 PM)
  - Verificación de disponibilidad en tiempo real
  - Control de fechas (no permite reservas pasadas)

- **Workflow de estados:**
  - Borrador → Confirmada → En Curso → Completada
  - Opciones de cancelación
  - Registro de no asistencias

- **Cálculo automático:**
  - Precio total según duración y tarifa
  - Duración en horas
  - Secuencias automáticas para números de reserva

- **Métodos de pago:**
  - Efectivo
  - Tarjeta
  - Transferencia
  - Yape/Plin
  - Otros

### 👥 Gestión de Clientes

- Registro completo:
  - Datos personales (Nombre, DNI, Teléfono, Email, Dirección)
  - Clasificación automática (Nuevo, Ocasional, Frecuente)
  - Historial de reservas
  - Estadísticas individuales

- Funcionalidades:
  - Creación de usuarios de portal
  - Seguimiento de actividades
  - Notas y observaciones

### 📊 Vistas y Visualización

- **Múltiples vistas disponibles:**
  - Lista (Tree view)
  - Formulario (Form view)
  - Kanban (Cards)
  - Calendario (Calendar view)

- **Búsquedas y filtros avanzados:**
  - Por fecha
  - Por estado
  - Por cancha
  - Por cliente
  - Por tipo de reserva
  - Por estado de pago

## 🛠️ Tecnologías y Arquitectura

### Stack Tecnológico
- **Framework**: Odoo 15/16/17
- **Backend**: Python 3.8+
- **ORM**: Odoo ORM
- **Base de datos**: PostgreSQL
- **Frontend**: XML, JavaScript, QWeb

### Arquitectura del Módulo

```
Capa de Presentación (Views)
    ↓
Capa de Lógica de Negocio (Models)
    ↓
Capa de Acceso a Datos (ORM)
    ↓
Base de Datos (PostgreSQL)
```

### Modelos Principales

1. **reserva.cancha** - Gestión de canchas deportivas
2. **reserva.reserva** - Sistema de reservas
3. **reserva.cliente** - Gestión de clientes

### Relaciones de Datos

```
Cliente (1) ←→ (N) Reserva (N) ←→ (1) Cancha
```

## 📦 Instalación

### Requisitos Previos

- Odoo 15, 16 o 17 instalado
- PostgreSQL 12+
- Python 3.8+

### Instalación Local

1. **Clonar o descargar el módulo:**
   ```bash
   cd /opt/odoo/addons/
   # Copiar la carpeta reserva_canchas aquí
   ```

2. **Dar permisos:**
   ```bash
   sudo chown -R odoo:odoo reserva_canchas
   ```

3. **Reiniciar Odoo:**
   ```bash
   sudo service odoo restart
   ```

4. **Activar modo desarrollador:**
   - Configuración → Activar modo desarrollador

5. **Actualizar lista de aplicaciones:**
   - Aplicaciones → Menú ⋮ → Actualizar Lista de Aplicaciones

6. **Instalar módulo:**
   - Buscar "Reserva de Canchas"
   - Clic en Instalar

### Instalación desde Código Fuente

```bash
./odoo-bin -d tu_base_de_datos -i reserva_canchas
```

## 🚀 Uso Rápido

### Primer Uso

1. **Crear usuarios:**
   - Administrador con grupo "Reserva de Canchas / Administrador"
   - Staff con grupo "Reserva de Canchas / Staff"

2. **Configurar canchas:**
   - Ir a Reserva Canchas → Configuración → Canchas
   - Crear las canchas disponibles

3. **Registrar clientes:**
   - Ir a Reserva Canchas → Configuración → Clientes
   - Agregar clientes habituales

4. **Crear reservas:**
   - Ir a Reserva Canchas → Operaciones → Nueva Reserva
   - Seleccionar cliente, cancha, fecha y horario

## 📱 Casos de Uso

### Reserva Presencial

**Actor:** Recepcionista  
**Flujo:**
1. Cliente llega al local
2. Recepcionista abre "Nueva Reserva"
3. Busca o crea el cliente
4. Selecciona cancha disponible
5. Define fecha y horario
6. Sistema calcula precio
7. Registra pago
8. Confirma reserva
9. Cliente recibe confirmación

### Gestión Administrativa

**Actor:** Administrador  
**Flujo:**
1. Revisar calendario del día
2. Verificar reservas confirmadas
3. Marcar inicio de partidos
4. Completar reservas finalizadas
5. Revisar estadísticas
6. Ajustar precios si necesario

## 📊 Reportes y Estadísticas

### Métricas Disponibles

- Total de reservas por cancha
- Ingresos por cancha
- Clientes más frecuentes
- Horarios más solicitados
- Tasa de ocupación
- Estado de pagos

## 🔒 Seguridad

### Grupos de Seguridad

- `group_reserva_admin`: Administradores del sistema
- `group_reserva_staff`: Personal operativo
- `base.group_portal`: Clientes con acceso al portal

### Reglas de Acceso

- Administradores: CRUD completo en todos los modelos
- Staff: CRUD en reservas y clientes, solo lectura en canchas
- Portal: Lectura de canchas, creación de reservas propias

## 🧪 Testing

### Ejecutar Script de Pruebas

```bash
./odoo-bin shell -d tu_base_de_datos
>>> exec(open('test_reserva_canchas.py').read())
```

### Pruebas Incluidas

- ✅ Creación de canchas
- ✅ Creación de clientes
- ✅ Creación de reservas
- ✅ Validación de horarios
- ✅ Prevención de duplicados
- ✅ Cálculo de precios
- ✅ Estadísticas

## 🐛 Solución de Problemas

### Módulo no aparece

```bash
sudo service odoo restart
# o
./odoo-bin -u all -d tu_base_de_datos
```

### Error de permisos

```bash
sudo chown -R odoo:odoo /opt/odoo/addons/reserva_canchas
```

### Error en base de datos

```bash
./odoo-bin -u reserva_canchas -d tu_base_de_datos
```

## 📝 Próximas Funcionalidades

- [ ] Portal web para reservas online
- [ ] Dashboard con gráficos estadísticos
- [ ] Notificaciones por email/SMS
- [ ] Integración con pasarelas de pago
- [ ] App móvil
- [ ] Sistema de descuentos y promociones
- [ ] Reservas recurrentes
- [ ] Lista de espera

## 🤝 Contribuciones

Este módulo fue desarrollado como proyecto académico para la materia de Desarrollo de Software con Odoo.

## 📄 Licencia

LGPL-3.0

## 👨‍💻 Autor

**Tu Nombre**  
📧 Email: tu.email@ejemplo.com  
🌐 GitHub: @tuusuario

## 📚 Documentación Adicional

Para más información sobre desarrollo en Odoo:
- [Documentación oficial de Odoo](https://www.odoo.com/documentation)
- [Guía de desarrollo](https://www.odoo.com/documentation/17.0/developer.html)

---

**Versión:** 1.0  
**Última actualización:** Diciembre 2024  
**Compatible con:** Odoo 15, 16, 17

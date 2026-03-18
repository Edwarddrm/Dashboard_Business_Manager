import pandas as pd
import numpy as np
import datetime
import os

def generate_dummy_data(output_path):
    print(f"Generating dummy data at {output_path}...")
    
    # 1. Finanzas (Ventas Mensuales y Clientes) - Lujo: menos clientes, ticket alto
    months = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 
              'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
    
    # Ventas altas
    sales = np.random.randint(50000, 250000, size=12)
    
    # Clientes más exclusivos
    monthly_clients = np.random.randint(20, 80, size=12)
    daily_clients_avg = monthly_clients / 30
    weekly_clients_avg = monthly_clients / 4
    
    df_finanzas = pd.DataFrame({
        'Mes': months,
        'Ventas ($)': sales,
        'Clientes Mensuales': monthly_clients,
        'Promedio Clientes Semanales': np.round(weekly_clients_avg, 1),
        'Promedio Clientes Diarios': np.round(daily_clients_avg, 1)
    })
    
    # 2. Procedimientos y Materiales (Clínica de Lujo)
    procedimientos_list = [
        'Lifting Facial sin Cirugía', 'Rellenos de Ácido Hialurónico Premium', 'Aplicación de Toxina Botulínica (Vistabel/Botox)', 
        'Bioestimulación con Radiesse', 'Hilos Tensores Mágicos', 'Láser CO2 Fraccionado', 
        'Peeling Químico Médico VIP', 'Rejuvenecimiento de Cuello y Escote', 'Rinoplastia Ultrasónica'
    ]
    cantidades = np.random.randint(5, 50, size=len(procedimientos_list))
    
    df_procedimientos = pd.DataFrame({
        'Procedimiento': procedimientos_list,
        'Cantidad Solicitadas': cantidades,
        'Precio Promedio ($)': np.random.randint(800, 5000, size=len(procedimientos_list))
    }).sort_values('Cantidad Solicitadas', ascending=False)
    
    # 3. Marketing General (Exclusividad)
    df_marketing = pd.DataFrame({
        'Métrica': [
            'Seguidores Instagram VIP', 
            'Clientes VIP Base de Datos', 
            'Correos Enviados (Día)', 
            'Correos Enviados (Semana)', 
            'Correos Enviados (Mes)',
            'Citas Agendadas (Email)',
            'Mensajes WA (Día)',
            'Mensajes WA (Semana)',
            'Mensajes WA (Mes)',
            'Citas Agendadas (WA)',
            'Tasa de Conversión (%)'
        ],
        'Valor': [45000, 1200, 45, 315, 1350, 28, 60, 420, 1800, 56, 15.5]
    })
    
    # 4. Campañas Vigentes (Enfocado en High-End)
    df_campanas = pd.DataFrame({
        'Campaña': ['Experiencia Rejuvenecimiento Total', 'Campaña Primavera Exclusiva', 'Retiro de Bienestar y Estética'],
        'Plataforma': ['Instagram Ads', 'Email Marketing', 'Revistas de Lujo'],
        'Estado': ['Activa', 'En Preparación', 'Activa'],
        'Inversión ($)': [5000, 1500, 8000],
        'Clics/Interacciones': [15000, 0, 300] # Revistas tiene menos "clics" pero alto impacto
    })
    
    # 5. Tareas (To-Do List y Materiales)
    df_tareas = pd.DataFrame({
        'Tarea': ['Pedir jeringas de Ácido Hialurónico Juvederm', 'Confirmar citas VIP para el viernes', 'Mantenimiento del equipo Láser CO2', 'Renovar suscripción de flores para la sala de espera', 'Revisar inventario de Botox'],
        'Responsable': ['Dra. Elena', 'Recepcionista Ana', 'Ing. Biomédico', 'Gerencia', 'Dra. Elena'],
        'Estado': ['Pendiente', 'En Progreso', 'Pendiente', 'Completada', 'Pendiente'],
        'Fecha Límite': ['2026-03-20', '2026-03-17', '2026-03-25', '2026-03-15', '2026-03-18']
    })

    # 6. Personal - Clínica Dental de Lujo
    df_personal = pd.DataFrame({
        'Nombre': ['Dra. Valeria Montes', 'Dra. Carolina Sánchez', 'Dr. Alejandro Rivas', 'Dr. Diego Fuentes',
                   'Lic. Mariana Torres', 'Ana Gómez', 'Sofía Pérez', 'Carlos Mendoza'],
        'Cargo': ['Directora Médica & Socia', 'Directora Comercial & Socia', 'Odontólogo Especialista', 'Odontólogo Especialista',
                   'Administradora', 'Recepcionista Senior', 'Asistente Dental', 'Auxiliar de Clínica'],
        'Área': ['Dirección', 'Dirección', 'Médica', 'Médica', 'Administración', 'Atención al Cliente', 'Médica', 'Operaciones'],
        'Reporta a': ['', '', 'Dra. Valeria Montes', 'Dra. Valeria Montes',
                        'Dra. Carolina Sánchez', 'Dra. Carolina Sánchez', 'Dr. Alejandro Rivas', 'Lic. Mariana Torres'],
        'Función Principal': [
            'Dirección médica, tratamientos VIP, relaciones con pacientes premium',
            'Dirección de operaciones, marketing y gestión comercial',
            'Implantes, endodoncia y estética avanzada',
            'Ortodoncia invisible y blanqueamiento láser',
            'Control financiero, RRHH y proveedores',
            'Atención y agenda de pacientes VIP',
            'Asistencia en procedimientos y esterilización',
            'Limpieza, mantenimiento y logística de la clínica'
        ]
    })

    # Save to Excel
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        df_finanzas.to_excel(writer, sheet_name='Finanzas', index=False)
        df_procedimientos.to_excel(writer, sheet_name='Procedimientos', index=False)
        df_marketing.to_excel(writer, sheet_name='Marketing_General', index=False)
        df_campanas.to_excel(writer, sheet_name='Campanas', index=False)
        df_tareas.to_excel(writer, sheet_name='Tareas', index=False)
        df_personal.to_excel(writer, sheet_name='Personal', index=False)
        
    print("Dummy data generated successfully!")

if __name__ == "__main__":
    generate_dummy_data('/home/edwarddrm/.gemini/antigravity/scratch/business_dashboard/data/dummy_data.xlsx')

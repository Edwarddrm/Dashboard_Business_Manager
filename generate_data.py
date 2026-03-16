import pandas as pd
import numpy as np
import datetime
import os

def generate_dummy_data(output_path):
    print(f"Generating dummy data at {output_path}...")
    
    # 1. Finanzas (Ventas Mensuales y Clientes)
    months = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 
              'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
    
    # Random sales between 10k and 50k
    sales = np.random.randint(10000, 50000, size=12)
    
    # Clients
    monthly_clients = np.random.randint(50, 200, size=12)
    # Estimate daily/weekly roughly from monthly and add some noise
    daily_clients_avg = monthly_clients / 30
    weekly_clients_avg = monthly_clients / 4
    
    df_finanzas = pd.DataFrame({
        'Mes': months,
        'Ventas ($)': sales,
        'Clientes Mensuales': monthly_clients,
        'Promedio Clientes Semanales': np.round(weekly_clients_avg, 1),
        'Promedio Clientes Diarios': np.round(daily_clients_avg, 1)
    })
    
    # Currently for the daily/weekly KPI, we might just want to show the "Current" month stats.
    # We will pick 'Marzo' as the current month for demo purposes inside the app.

    # 2. Procedimientos
    procedimientos_list = [
        'Limpieza Facial', 'Masaje Relajante', 'Botox', 
        'Depilación Láser', 'Manicura', 'Pedicura', 'Peeling Químico', 'Corte de Cabello'
    ]
    cantidades = np.random.randint(10, 150, size=len(procedimientos_list))
    
    df_procedimientos = pd.DataFrame({
        'Procedimiento': procedimientos_list,
        'Cantidad Solicitadas': cantidades
    }).sort_values('Cantidad Solicitadas', ascending=False)
    
    # 3. Marketing General (Followers, Emails)
    df_marketing = pd.DataFrame({
        'Métrica': ['Seguidores Instagram', 'Seguidores Facebook', 'Correos Enviados (Mes)', 'Tasa de Apertura Correos (%)'],
        'Valor': [12500, 8400, 3200, 45.2]
    })
    
    # 4. Campañas Vigentes
    df_campanas = pd.DataFrame({
        'Campaña': ['Promo Verano', 'Descuento Día de la Madre', 'Fidelización Clientes Antiguos'],
        'Plataforma': ['Instagram Ads', 'Email Marketing', 'Facebook Ads'],
        'Estado': ['Activa', 'En Preparación', 'Activa'],
        'Inversión ($)': [500, 200, 350],
        'Clics/Interacciones': [1200, 0, 850]
    })
    
    # 5. Tareas (To-Do List)
    df_tareas = pd.DataFrame({
        'Tarea': ['Llamar a proveedor de cremas', 'Revisar métricas de Instagram', 'Programar correos de promoción', 'Pagar alquiler de local'],
        'Responsable': ['María', 'Ana', 'Ana', 'Carlos'],
        'Estado': ['Pendiente', 'Completada', 'Pendiente', 'En Progreso'],
        'Fecha Límite': ['2026-03-20', '2026-03-15', '2026-03-18', '2026-03-30']
    })

    # Save to Excel
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        df_finanzas.to_excel(writer, sheet_name='Finanzas', index=False)
        df_procedimientos.to_excel(writer, sheet_name='Procedimientos', index=False)
        df_marketing.to_excel(writer, sheet_name='Marketing_General', index=False)
        df_campanas.to_excel(writer, sheet_name='Campanas', index=False)
        df_tareas.to_excel(writer, sheet_name='Tareas', index=False)
        
    print("Dummy data generated successfully!")

if __name__ == "__main__":
    generate_dummy_data('/home/edwarddrm/.gemini/antigravity/scratch/business_dashboard/data/dummy_data.xlsx')

#!/usr/bin/env python3
"""
Script para probar la carga de datos del dashboard
"""

import sys
from pathlib import Path

def test_data_loading():
    """Probar la carga de datos"""
    print("🧪 PROBANDO CARGA DE DATOS DEL DASHBOARD")
    print("=" * 50)
    
    # Configuración de datos
    crypto_to_content = {
        'Bitcoin': 'Drama',
        'Ethereum': 'Comedy', 
        'BNB': 'Action',
        'Solana': 'Documentary',
        'Tether': 'Romance'
    }

    country_to_region = {
        'US': 'North America',
        'CN': 'Asia',
        'JP': 'Asia',
        'DE': 'Europe',
        'GB': 'Europe',
        'IN': 'Asia',
        'BR': 'South America',
        'CA': 'North America',
        'AU': 'Oceania',
        'KR': 'Asia'
    }
    
    # Verificar rutas
    print("\n📁 Verificando rutas de datos:")
    integrated_path = Path('../analyst/integrated_data.csv')
    country_path = Path('../analyst/country_aggregated.csv')
    
    print(f"  integrated_path: {integrated_path.absolute()}")
    print(f"  integrated_path.exists(): {integrated_path.exists()}")
    print(f"  country_path: {country_path.absolute()}")
    print(f"  country_path.exists(): {country_path.exists()}")
    
    if not integrated_path.exists() or not country_path.exists():
        print("❌ ERROR: Archivos de datos no encontrados")
        return False
    
    # Verificar que pandas esté disponible
    try:
        import pandas as pd
        print("✅ pandas disponible")
    except ImportError:
        print("❌ ERROR: pandas no está instalado")
        print("   Ejecuta: pip install pandas")
        return False
    
    # Cargar datos
    print("\n📊 Cargando datos:")
    try:
        df_integrated = pd.read_csv(integrated_path)
        df_country = pd.read_csv(country_path)
        
        print(f"  ✅ integrated_data: {len(df_integrated)} registros")
        print(f"  ✅ country_aggregated: {len(df_country)} registros")
        
        # Aplicar mapeos
        df_integrated['content_category'] = df_integrated['crypto'].map(crypto_to_content)
        df_integrated['region'] = df_integrated['country_code'].map(country_to_region)
        df_country['content_category'] = df_country['crypto'].map(crypto_to_content)
        df_country['region'] = df_country['country_code'].map(country_to_region)
        
        print(f"  ✅ Mapeos aplicados correctamente")
        
        # Verificar datos
        print(f"\n📈 Resumen de datos:")
        print(f"  • Países únicos: {df_integrated['country_code'].nunique()}")
        print(f"  • Categorías de contenido: {df_integrated['content_category'].nunique()}")
        print(f"  • Regiones: {df_integrated['region'].nunique()}")
        print(f"  • Rango de fechas: {df_integrated['Date'].min()} a {df_integrated['Date'].max()}")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR cargando datos: {e}")
        return False

if __name__ == "__main__":
    success = test_data_loading()
    
    if success:
        print("\n🎯 RESULTADO: ✅ DATOS CARGADOS CORRECTAMENTE")
        print("🚀 El dashboard debería funcionar ahora")
        print("\n📋 Para ejecutar el dashboard:")
        print("1. pip install -r requirements.txt")
        print("2. streamlit run app.py")
        print("3. Abrir http://localhost:8501")
    else:
        print("\n🎯 RESULTADO: ❌ PROBLEMAS CON LA CARGA DE DATOS")
        print("🔧 Revisa los errores anteriores")

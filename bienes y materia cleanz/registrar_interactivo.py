import mysql.connector
from datetime import date

def registrar_activo_interactivo():
    conexion = None
    try:
        conexion = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="control_bienes"
        )
        cursor = conexion.cursor()

        print("\n" + "="*40)
        print("  FORMULARIO INTERACTIVO CLEANZ  ")
        print("="*40)
        
        # 1. ENTRADAS DE USUARIO
        nro_identificacion = input("1. Código (ej. CLEANZ-003): ").strip()
        nombre_elementos = input("2. Nombre del bien (ej. Monitor HP): ").strip()
        cantidad = int(input("3. Cantidad: "))
        valor_unitario = float(input("4. Valor unitario (Bs): "))
        
        # 2. DATOS COMPLEMENTARIOS (Sincronizados con DashboardCleanz)
        # Nota: Asegúrate de que el id_seccion e id_area existan en tus tablas
        id_seccion = 1  
        id_area = 1     
        id_responsable = 1
        id_usuario = 1
        departamento = "INFORMÁTICA" # Valor por defecto para la prueba
        cod_clasificacion = "02"    # Grupo 02: Bienes Muebles
        
        valor_total = cantidad * valor_unitario
        fecha_hoy = date.today()

        # 3. SQL CORREGIDO (Nombres exactos de tu DB y Panel)
        sql = """INSERT INTO bienes_materia 
                 (id_seccion, id_area, id_responsable, id_usuario, nro_identificacion, 
                  nombre_elementos, cantidad, valor_unitario, valor_total, fecha_ingreso,
                  departamento, cod_clasificacion) 
                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        
        valores = (id_seccion, id_area, id_responsable, id_usuario, nro_identificacion, 
                   nombre_elementos, cantidad, valor_unitario, valor_total, fecha_hoy,
                   departamento, cod_clasificacion)

        cursor.execute(sql, valores)
        conexion.commit()

        print(f"\n✅ ¡{nombre_elementos} guardado con éxito en la base de datos!")
        print(f"💰 Total calculado: {valor_total:,.2f} Bs.")

    except ValueError:
        print("❌ Error: Cantidad debe ser entero y Valor debe ser numérico (use punto para decimales).")
    except mysql.connector.Error as error:
        print(f"❌ Error de base de datos: {error}")
    finally:
        if conexion and conexion.is_connected():
            cursor.close()
            conexion.close()
            print("\n🔌 Conexión cerrada.")

if __name__ == "__main__":
    registrar_activo_interactivo()
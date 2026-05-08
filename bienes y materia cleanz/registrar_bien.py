import mysql.connector
from datetime import date

def registrar_activo():
    conexion = None # Inicializamos para evitar errores en el finally
    try:
        # 1. Conexión (Asegúrate de que las credenciales coincidan con DashboardCleanz)
        conexion = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="control_bienes" 
        )
        cursor = conexion.cursor()

        # 2. DATOS DEL BIEN (Ajustados a tu realidad técnica)
        # Nota: Estos IDs deben existir en tus tablas 'areas', 'secciones', etc.
        id_seccion = 1     
        id_area = 1        
        id_responsable = 1 
        id_usuario = 1     
        
        nro_identificacion = "CLEANZ-002" 
        nombre_elemento = "Impresora Canon imageCLASS MF3010 (Láser B/N)" # <--- Nombre preciso
        cantidad = 1
        valor_unitario = 280.00
        valor_total = cantidad * valor_unitario
        fecha_hoy = date.today()
        departamento = "ADMINISTRACIÓN" # Agregado para coincidir con tu panel
        cod_clasificacion = "02" # Ejemplo: Bienes Muebles

        # 3. SQL ACTUALIZADO (Con nombres exactos de tu phpMyAdmin)
        # Agregamos 'departamento' y 'cod_clasificacion' para que el Dashboard lo vea bien
        sql = """INSERT INTO bienes_materia 
                 (id_seccion, id_area, id_responsable, id_usuario, nro_identificacion, 
                  nombre_elemento, cantidad, valor_unitario, valor_total, fecha_ingreso,
                  departamento, cod_clasificacion) 
                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        
        valores = (id_seccion, id_area, id_responsable, id_usuario, nro_identificacion, 
                   nombre_elemento, cantidad, valor_unitario, valor_total, fecha_hoy,
                   departamento, cod_clasificacion)

        cursor.execute(sql, valores)
        conexion.commit()

        print(f"✅ ¡{nombre_elemento} registrada exitosamente!")

    except mysql.connector.Error as error:
        print(f"❌ Error de base de datos: {error}")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

    finally:
        if conexion and conexion.is_connected():
            cursor.close()
            conexion.close()
            print("🔌 Conexión cerrada.")

if __name__ == "__main__":
    registrar_activo()
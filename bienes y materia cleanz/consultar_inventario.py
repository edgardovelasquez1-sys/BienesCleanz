import mysql.connector

def mostrar_inventario_consola():
    conexion = None
    try:
        # 1. Conexión a la base de datos
        conexion = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="control_bienes"
        )
        
        cursor = conexion.cursor()

        # 2. La consulta "mágica" CORREGIDA
        # - nombre_elemento
        # - LEFT JOIN para evitar que registros con datos nulos desaparezcan
        # - 'secciones' en plural
        query = """
        SELECT 
            b.nro_identificacion, 
            b.nombre_elemento, 
            IFNULL(s.nombre_seccion, 'N/A'), 
            IFNULL(a.nombre_area, 'SIN ÁREA'), 
            b.valor_total 
        FROM bienes_materia b
        LEFT JOIN secciones s ON b.id_seccion = s.id_seccion
        LEFT JOIN areas a ON b.id_area = a.id_area
        ORDER BY b.id_item DESC
        """
        
        cursor.execute(query)
        resultados = cursor.fetchall()

        # 3. Diseño de la tabla en la terminal
        print("\n" + "="*105)
        print(" SISTEMA DE CONTROL DE BIENES - CLEANZ (INVENTARIO COMPLETO) ".center(105))
        print("="*105)
        print(f"{'CÓDIGO':<15} | {'ELEMENTO':<30} | {'SECCIÓN':<20} | {'ÁREA':<15} | {'VALOR':<10}")
        print("-"*105)
        
        for fila in resultados:
            # Formateo de precio para que se vea profesional (Bs. 00.00)
            precio = f"{float(fila[4]):,.2f}"
            print(f"{fila[0]:<15} | {fila[1]:<30} | {fila[2]:<20} | {fila[3]:<15} | {precio:<10}")
        
        print("-"*105)
        print(f"Total de bienes en inventario: {len(resultados)}".rjust(105))

    except mysql.connector.Error as e:
        print(f"❌ Error al conectar o consultar: {e}")
    except Exception as e:
        print(f"❌ Error general: {e}")

    finally:
        if conexion and conexion.is_connected():
            cursor.close()
            conexion.close()
            print("\n🔌 Conexión cerrada correctamente.")

if __name__ == "__main__":
    mostrar_inventario_consola()
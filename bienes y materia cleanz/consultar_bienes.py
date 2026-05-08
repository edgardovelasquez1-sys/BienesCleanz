import mysql.connector

def realizar_consulta_consola():
    conexion = None
    try:
        conexion = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="control_bienes"
        )
        
        cursor = conexion.cursor()
        
        # SQL Corregido: 
        # 1. nombre_elemento 
        # 2. LEFT JOIN para no perder datos
        # 3. tabla 'secciones' (en plural)
        query = """
            SELECT 
                b.nro_identificacion, 
                b.nombre_elemento, 
                IFNULL(s.nombre_seccion, 'SIN SECCIÓN'), 
                b.valor_total 
            FROM bienes_materia b
            LEFT JOIN secciones s ON b.id_seccion = s.id_seccion
        """
        
        cursor.execute(query)
        resultados = cursor.fetchall()

        print("\n--- INVENTARIO ACTUAL CLEANZ (CONSOLA) ---")
        # Ajustamos el ancho de las columnas para que se vea ordenado
        print(f"{'CÓDIGO':<15} | {'ELEMENTO':<30} | {'SECCIÓN':<20} | {'VALOR TOTAL':<12}")
        print("-" * 85)
        
        for fila in resultados:
            # Formateamos el valor para que tenga decimales bonitos
            valor_formateado = f"{float(fila[3]):,.2f} Bs"
            print(f"{fila[0]:<15} | {fila[1]:<30} | {fila[2]:<20} | {valor_formateado:<12}")

    except mysql.connector.Error as e:
        print(f"❌ Error de base de datos: {e}")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

    finally:
        if conexion and conexion.is_connected():
            cursor.close()
            conexion.close()
            print("\n🔌 Consulta finalizada y conexión cerrada.")

if __name__ == "__main__":
    realizar_consulta_consola()
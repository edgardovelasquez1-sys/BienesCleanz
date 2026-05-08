import mysql.connector

def crear_usuario():
    try:
        # 1. Establecer conexión
        conexion = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="control_bienes" # <--- CAMBIA ESTO
        )
        
        cursor = conexion.cursor()

        # 2. Definir los datos del nuevo usuario
        # No ponemos id_usuario porque es AUTO_INCREMENT
        nombre = "admin_bienes"
        clave = "12345"  # En un sistema real usaríamos hash/encriptación
        rol = "Admin"    # Debe ser 'Admin' u 'Operativo'
        estatus = "Activo"

        # 3. Preparar la consulta SQL
        sql = "INSERT INTO usuarios (nombre_usuario, password, rol, estatus) VALUES (%s, %s, %s, %s)"
        valores = (nombre, clave, rol, estatus)

        # 4. Ejecutar y guardar cambios
        cursor.execute(sql, valores)
        conexion.commit() # ¡VITAL! Sin esto los datos no se guardan en el disco

        print(f"✅ Usuario '{nombre}' creado con éxito. ID asignado: {cursor.lastrowid}")

    except mysql.connector.Error as error:
        print(f"❌ Error al insertar: {error}")

    finally:
        if conexion.is_connected():
            cursor.close()
            conexion.close()
            print("Conexión cerrada.")

# Llamar a la función
crear_usuario()
import mysql.connector

try:
    # Configuración de la conexión
    conexion = mysql.connector.connect(
        host="localhost",
        user="root",      # Usuario por defecto de XAMPP
        password="",      # Por defecto viene vacío en XAMPP
        database="control_bienes" 
    )

    if conexion.is_connected():
        print("¡Conexión exitosa al sistema de Bienes y Materias!")
        
except mysql.connector.Error as error:
    print(f"Error al conectar: {error}")

finally:
    if 'conexion' in locals() and conexion.is_connected():
        conexion.close()
        print("Conexión cerrada de forma segura.")
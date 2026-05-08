"""
MÓDULO DE DESINCORPORACIÓN DE BIENES
Gestiona la baja de bienes y su visualización en el sistema CLEANZ
"""

import mysql.connector
from tkinter import messagebox, ttk
from datetime import datetime
import customtkinter as ctk


class ModuloDesincorporar:
    """Clase que gestiona la desincorporación de bienes"""

    # ========== CONSTRUCTOR ==========
    def __init__(self, conectar_db, usuario_nombre, contenedor_principal, root):
        """
        Inicializa el módulo de desincorporación

        Args:
            conectar_db: Función para conectar a la base de datos
            usuario_nombre: Nombre del usuario actual
            contenedor_principal: Frame donde se mostrará la vista
            root: Ventana principal (para ventanas modales)
        """
        self.conectar_db = conectar_db
        self.usuario_nombre = usuario_nombre
        self.contenedor_principal = contenedor_principal
        self.root = root
        self.tabla_desincorporados = None

    # ========== PROCESAR DESINCORPORACIÓN ==========
    def procesar_desincorporacion(self, datos_bien, motivo):
        """
        Mueve un bien de la tabla activa a la de desincorporados

        Args:
            datos_bien: Tupla con los datos del bien
            motivo: Texto del motivo de desincorporación

        Returns:
            bool: True si fue exitoso, False en caso contrario
        """
        if not datos_bien or not motivo:
            messagebox.showwarning("Atención", "Datos incompletos para desincorporar.")
            return False

        # Extraer datos del bien
        item_id = datos_bien[0]
        nro_identificacion = str(datos_bien[4])
        nombre = datos_bien[5]
        grupo = str(datos_bien[1])
        subgrupo = str(datos_bien[2])
        departamento = datos_bien[6]
        area = datos_bien[7]
        cantidad = datos_bien[8]
        valor_unitario = datos_bien[9]
        valor_total = datos_bien[10]
        anio = datos_bien[11]

        conexion = self.conectar_db()
        if not conexion:
            return False

        try:
            cursor = conexion.cursor()

            # Crear tabla desincorporados si no existe
            self._crear_tabla_desincorporados(cursor)

            fecha_actual = datetime.now().strftime("%Y-%m-%d")

            # Insertar en desincorporados
            query_insert = """
                INSERT INTO desincorporados
                (id_item, nro_identificacion, nombre_elementos,
                 grupo_codigo, subgrupo_codigo, departamento, area_especifica,
                 cantidad, valor_unitario, valor_total, anio_ingreso,
                 motivo_desincorporacion, fecha_desincorporacion, usuario_desincorporo)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

            valores = (
                item_id, nro_identificacion, nombre,
                grupo, subgrupo, departamento, area,
                cantidad, valor_unitario, valor_total, anio,
                motivo, fecha_actual, self.usuario_nombre
            )

            cursor.execute(query_insert, valores)

            # Eliminar de bienes_materia
            cursor.execute("DELETE FROM bienes_materia WHERE id_item = %s", (item_id,))

            conexion.commit()

            messagebox.showinfo(
                "✅ Desincorporación Exitosa",
                f"El bien ha sido desincorporado correctamente.\n\n"
                f"📦 Bien: {nombre}\n"
                f"📝 Motivo: {motivo}\n"
                f"📅 Fecha: {fecha_actual}"
            )
            return True

        except mysql.connector.Error as e:
            conexion.rollback()
            messagebox.showerror("Error SQL", f"No se pudo desincorporar:\n{e}")
            return False

        except Exception as e:
            conexion.rollback()
            messagebox.showerror("Error", f"Detalle: {e}")
            return False

        finally:
            if cursor:
                cursor.close()
            if conexion:
                conexion.close()

    # ========== REINCORPORAR BIEN ==========
    def reincorporar_bien(self):
        """Reincorpora un bien desincorporado a la tabla activa"""
        seleccion = self.tabla_desincorporados.selection()
        if not seleccion:
            messagebox.showwarning("Atención", "Por favor, selecciona un bien para reincorporar.")
            return

        # Obtener valores del bien desincorporado
        v = self.tabla_desincorporados.item(seleccion)['values']
        id_desincorporado = v[0]
        nro_identificacion = v[1]
        nombre = v[2]
        departamento = v[3]

        # Confirmar reincorporación
        confirmar = messagebox.askyesno(
            "Confirmar Reincorporación",
            f"⚠️ ¿Está seguro que desea REINCORPORAR el siguiente bien?\n\n"
            f"📦 Bien: {nombre}\n"
            f"🔢 ID: {nro_identificacion}\n"
            f"🏢 Departamento: {departamento}\n\n"
            f"El bien volverá a estar activo en el inventario.",
            parent=self.root
        )

        if not confirmar:
            return

        conexion = self.conectar_db()
        if not conexion:
            return

        try:
            cursor = conexion.cursor()

            # Obtener todos los datos del bien desincorporado
            cursor.execute("""
                SELECT id_item, nro_identificacion, nombre_elementos,
                       grupo_codigo, subgrupo_codigo, departamento, area_especifica,
                       cantidad, valor_unitario, valor_total, anio_ingreso
                FROM desincorporados
                WHERE id_desincorporado = %s
            """, (id_desincorporado,))

            bien = cursor.fetchone()

            if not bien:
                messagebox.showerror("Error", "No se encontraron los datos del bien.")
                return

            # Obtener IDs de grupo y subgrupo
            cursor.execute("SELECT id_grupo FROM grupo WHERE cod_grupo = %s", (bien[3],))
            res_g = cursor.fetchone()
            id_grupo = res_g[0] if res_g else None

            cursor.execute("SELECT id_subgrupo FROM subgrupo WHERE cod_subgrupo = %s AND id_grupo = %s", (bien[4], id_grupo))
            res_s = cursor.fetchone()
            id_subgrupo = res_s[0] if res_s else None

            # Gestionar área
            area_texto = bien[6] if bien[6] else ""
            cursor.execute("SELECT id_area FROM areas WHERE nombre_area = %s", (area_texto,))
            res_a = cursor.fetchone()
            id_area = res_a[0] if res_a else None

            if not id_area and area_texto:
                cursor.execute("INSERT INTO areas (nombre_area) VALUES (%s)", (area_texto,))
                id_area = cursor.lastrowid

            # Gestionar sección (usamos una sección genérica)
            id_seccion = None
            if bien[3] and id_subgrupo:
                cod_seccion = f"SEC-REIN-{id_subgrupo}"
                cursor.execute("SELECT id_seccion FROM secciones WHERE cod_seccion = %s", (cod_seccion,))
                res_sec = cursor.fetchone()
                if res_sec:
                    id_seccion = res_sec[0]
                else:
                    cursor.execute(
                        "INSERT INTO secciones (cod_seccion, nombre_seccion, id_subgrupo) VALUES (%s, %s, %s)",
                        (cod_seccion, "REINCORPORADO", id_subgrupo)
                    )
                    id_seccion = cursor.lastrowid

            # Insertar nuevamente en bienes_materia
            cursor.execute("""
                INSERT INTO bienes_materia
                (id_item, nro_identificacion, nombre_elementos,
                 id_grupo, id_subgrupo, id_seccion, id_area,
                 departamento, area_especifica, cantidad,
                 valor_unitario, valor_total, anio_ingreso,
                 fecha_ingreso, id_usuario)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURDATE(), %s)
            """, (
                bien[0], bien[1], bien[2],
                id_grupo, id_subgrupo, id_seccion, id_area,
                bien[5], bien[6], bien[7],
                bien[8], bien[9], bien[10],
                1
            ))

            # Eliminar de desincorporados
            cursor.execute("DELETE FROM desincorporados WHERE id_desincorporado = %s", (id_desincorporado,))

            conexion.commit()

            messagebox.showinfo(
                "✅ Reincorporación Exitosa",
                f"El bien ha sido REINCORPORADO correctamente.\n\n"
                f"📦 Bien: {nombre}\n"
                f"🔢 ID: {nro_identificacion}\n"
                f"🏢 Departamento: {departamento}"
            )

            # Recargar la tabla de desincorporados
            self.cargar_datos()

            # Notificar al panel principal que recargue la tabla de consulta
            if hasattr(self, 'recargar_consulta_callback'):
                self.recargar_consulta_callback()

        except mysql.connector.Error as e:
            conexion.rollback()
            messagebox.showerror("Error SQL", f"No se pudo reincorporar:\n{e}")
        except Exception as e:
            conexion.rollback()
            messagebox.showerror("Error", f"Detalle: {e}")
        finally:
            if cursor:
                cursor.close()
            if conexion:
                conexion.close()

    def set_recargar_callback(self, callback):
        """Establece el callback para recargar la tabla de consulta"""
        self.recargar_consulta_callback = callback

    # ========== CREAR TABLA DESINCORPORADOS ==========
    def _crear_tabla_desincorporados(self, cursor):
        """Crea la tabla desincorporados si no existe"""
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS desincorporados (
                id_desincorporado INT(11) NOT NULL AUTO_INCREMENT,
                id_item INT(11) NOT NULL,
                nro_identificacion VARCHAR(50) DEFAULT NULL,
                nombre_elementos VARCHAR(255) NOT NULL,
                grupo_codigo VARCHAR(10) DEFAULT NULL,
                subgrupo_codigo VARCHAR(10) DEFAULT NULL,
                departamento VARCHAR(100) DEFAULT NULL,
                area_especifica VARCHAR(100) DEFAULT NULL,
                cantidad INT(10) NOT NULL,
                valor_unitario DECIMAL(15,2) NOT NULL,
                valor_total DECIMAL(15,2) NOT NULL,
                anio_ingreso VARCHAR(20) DEFAULT NULL,
                motivo_desincorporacion TEXT NOT NULL,
                fecha_desincorporacion DATE NOT NULL,
                usuario_desincorporo VARCHAR(100) DEFAULT NULL,
                PRIMARY KEY (id_desincorporado)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci
        """)

    # ========== VISTA DE DESINCORPORADOS ==========
    def mostrar_vista(self):
        """Muestra la lista de bienes desincorporados"""
        # Limpiar el contenedor principal
        for widget in self.contenedor_principal.winfo_children():
            widget.destroy()

        # Título
        titulo = ctk.CTkLabel(
            self.contenedor_principal,
            text="📋 LISTA DE BIENES DESINCORPORADOS",
            font=("Segoe UI", 24, "bold"),
            text_color="#e74c3c"
        )
        titulo.pack(pady=20)

        # Frame para la tabla
        frame_tabla = ctk.CTkFrame(
            self.contenedor_principal,
            fg_color="white",
            corner_radius=15
        )
        frame_tabla.pack(padx=20, pady=10, fill="both", expand=True)

        # Crear Treeview
        columnas = ("id", "nro_id", "nombre", "departamento", "motivo", "fecha", "usuario")
        self.tabla_desincorporados = ttk.Treeview(
            frame_tabla,
            columns=columnas,
            show="headings",
            height=20
        )

        headers = ["ID", "N° IDENTIFICACIÓN", "BIEN", "DEPARTAMENTO", "MOTIVO", "FECHA BAJA", "USUARIO"]
        anchos = [50, 130, 280, 130, 250, 100, 120]

        for col, head, ancho in zip(columnas, headers, anchos):
            self.tabla_desincorporados.heading(col, text=head)
            self.tabla_desincorporados.column(col, width=ancho, anchor="center")

        # Scrollbars
        scroll_y = ttk.Scrollbar(frame_tabla, orient="vertical", command=self.tabla_desincorporados.yview)
        scroll_x = ttk.Scrollbar(frame_tabla, orient="horizontal", command=self.tabla_desincorporados.xview)

        self.tabla_desincorporados.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

        scroll_y.pack(side="right", fill="y")
        scroll_x.pack(side="bottom", fill="x")
        self.tabla_desincorporados.pack(side="left", expand=True, fill="both")

        # Frame para botones
        btn_frame = ctk.CTkFrame(self.contenedor_principal, fg_color="transparent")
        btn_frame.pack(pady=15)

        ctk.CTkButton(
            btn_frame,
            text="🔄 ACTUALIZAR",
            fg_color="#3498db",
            hover_color="#2980b9",
            command=self.cargar_datos,
            width=140,
            height=35,
            font=("Segoe UI", 12, "bold")
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            btn_frame,
            text="📊 EXPORTAR EXCEL",
            fg_color="#27ae60",
            hover_color="#219a52",
            command=self.exportar_excel,
            width=140,
            height=35,
            font=("Segoe UI", 12, "bold")
        ).pack(side="left", padx=10)

        # Botón REINCORPORAR (color verde azulado)
        ctk.CTkButton(
            btn_frame,
            text="🔄 REINCORPORAR",
            fg_color="#16a085",
            hover_color="#1abc9c",
            command=self.reincorporar_bien,
            width=140,
            height=35,
            font=("Segoe UI", 12, "bold")
        ).pack(side="left", padx=10)

        # Cargar datos
        self.cargar_datos()

    # ========== CARGAR DATOS ==========
    def cargar_datos(self):
        """Carga la lista de bienes desincorporados desde la BD"""
        try:
            # Limpiar tabla existente
            if self.tabla_desincorporados:
                for item in self.tabla_desincorporados.get_children():
                    self.tabla_desincorporados.delete(item)

            db = self.conectar_db()
            if not db:
                return

            cursor = db.cursor()
            cursor.execute("""
                SELECT id_desincorporado, nro_identificacion, nombre_elementos,
                       departamento, motivo_desincorporacion, fecha_desincorporacion,
                       usuario_desincorporo
                FROM desincorporados
                ORDER BY fecha_desincorporacion DESC
            """)

            rows = cursor.fetchall()

            for row in rows:
                self.tabla_desincorporados.insert("", "end", values=(
                    row[0], row[1], row[2], row[3], row[4], row[5], row[6]
                ))

            total = len(rows)

            # Eliminar contador anterior si existe
            for widget in self.contenedor_principal.winfo_children():
                try:
                    if isinstance(widget, ctk.CTkLabel):
                        if "Total de bienes desincorporados" in str(widget.cget("text")):
                            widget.destroy()
                except:
                    pass

            # Mostrar total
            lbl_total = ctk.CTkLabel(
                self.contenedor_principal,
                text=f"📊 Total de bienes desincorporados: {total}",
                font=("Segoe UI", 12),
                text_color="#7f8c8d"
            )
            lbl_total.pack(pady=(0, 10))

            db.close()

        except Exception as e:
            print(f"❌ Error al cargar desincorporados: {e}")
            messagebox.showerror("Error", f"No se pudieron cargar los datos:\n{e}")

    # ========== EXPORTAR A EXCEL ==========
    def exportar_excel(self):
        """Exporta la lista de desincorporados a Excel"""
        try:
            from tkinter import filedialog
            import pandas as pd

            datos = []
            for row_id in self.tabla_desincorporados.get_children():
                datos.append(self.tabla_desincorporados.item(row_id)['values'])

            if not datos:
                messagebox.showwarning("Atención", "No hay datos para exportar.")
                return

            columnas = ["ID", "N° IDENTIFICACIÓN", "BIEN", "DEPARTAMENTO",
                        "MOTIVO", "FECHA BAJA", "USUARIO"]

            df = pd.DataFrame(datos, columns=columnas)

            archivo = filedialog.asksaveasfilename(
                initialfile="Desincorporados_CLEANZ.xlsx",
                defaultextension=".xlsx",
                filetypes=[("Libro de Excel", "*.xlsx")]
            )

            if archivo:
                df.to_excel(archivo, index=False, engine='openpyxl')
                messagebox.showinfo("Éxito", f"Archivo guardado en:\n{archivo}")

        except ImportError:
            messagebox.showerror(
                "Error",
                "Falta la librería 'openpyxl'.\nEjecuta: pip install openpyxl"
            )

        except Exception as e:
            messagebox.showerror("Error", f"Detalle: {e}")

    # ========== MÉTODOS AUXILIARES ==========
    def _limpiar_contenedor(self):
        """Limpia el contenedor principal"""
        for widget in self.contenedor_principal.winfo_children():
            widget.destroy()

    def _limpiar_tabla(self):
        """Limpia la tabla de desincorporados"""
        if self.tabla_desincorporados:
            for item in self.tabla_desincorporados.get_children():
                self.tabla_desincorporados.delete(item)

    def limpiar_tabla(self):
        """Limpia la tabla y recarga los datos"""
        self._limpiar_tabla()
        self.cargar_datos()

    # ========== CONFIRMAR ACCIÓN ==========
    def confirmar_accion(self, nombre_bien, nro_identificacion):
        """
        Muestra ventana de confirmación para desincorporar

        Args:
            nombre_bien: Nombre del bien a desincorporar
            nro_identificacion: Número de identificación del bien

        Returns:
            bool: True si el usuario confirma, False en caso contrario
        """
        respuesta = messagebox.askyesno(
            "Confirmar Desincorporación",
            f"⚠️ ¿Está seguro que desea desincorporar el siguiente bien?\n\n"
            f"📦 Bien: {nombre_bien}\n"
            f"🔢 ID: {nro_identificacion}\n\n"
            f"Esta acción NO se puede deshacer.",
            parent=self.root
        )
        return respuesta
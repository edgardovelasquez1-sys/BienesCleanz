import tkinter as tk
from tkinter import messagebox, Menu, ttk, simpledialog
from datetime import datetime
import os
from PIL import Image, ImageTk
import customtkinter as ctk
import mysql.connector
from reportlab.pdfgen import canvas
import pandas as pd
from desincorporar import ModuloDesincorporar

# =================================================================
# 1. COMPONENTES DE INTERFAZ (TOOLTIP)
# =================================================================
class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None
        self.widget.bind("<Enter>", self.show_tip)
        self.widget.bind("<Leave>", self.hide_tip)

    def show_tip(self, event=None):
        if self.tip_window or not self.text:
            return
        x, y, _cx, cy = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 25
        y = y + cy + self.widget.winfo_rooty() + 25
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, justify='left',
                         background="#2f3640", foreground="white", relief='flat',
                         border=5, font=("Segoe UI", "9", "normal"))
        label.pack(ipadx=1)

    def hide_tip(self, event=None):
        tw = self.tip_window
        self.tip_window = None
        if tw:
            tw.destroy()


# =================================================================
# 2. CLASE PRINCIPAL DEL SISTEMA
# =================================================================
class DashboardCleanz:
    def __init__(self, root):
        self.root = root
        self.root.title("SISTEMA DE CONTROL DE BIENES - CLEANZ")
        self.root.geometry("1200x850")
        self.root.configure(bg="#f5f6fa")

        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        self.usuario_nombre = "Edgardo Velasquez"
        self.Manual_usuario = "Manual_Sistema_CLEANZ.pdf"
        self.entradas = {}
        self.tabla_consulta = None

        self.configurar_menu_superior()
        self.crear_sidebar()          
        self.crear_header()  # <--- Esta línea debe existir
    
        self.actualizar_reloj()  # <--- Esta línea debe existir
        self.vista_inicio()


        # ========== CREAR CONTENEDOR PRINCIPAL PRIMERO ==========
        self.contenedor_principal = tk.Frame(self.root, bg="#f5f6fa", highlightthickness=0)
        self.contenedor_principal.pack(side="right", expand=True, fill="both", padx=30, pady=30)

        # ========== INICIALIZAR MÓDULO DE DESINCORPORACIÓN ==========
        from desincorporar import ModuloDesincorporar

        self.modulo_desincorporar = ModuloDesincorporar(
            self.conectar_db,
            self.usuario_nombre,
            self.contenedor_principal,
            self.root
        )

        self.modulo_desincorporar.set_recargar_callback(self.cargar_datos_iniciales)

        self.configurar_menu_superior()
        self.crear_sidebar()          
        self.crear_header()            

        self.actualizar_reloj()
        self.vista_inicio()


    def conectar_db(self):
        try:
            conexion = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="control_bienes"
            )
            return conexion
        except mysql.connector.Error as err:
            messagebox.showerror(
                "Error de Conexión", f"No se pudo conectar a la base de datos: {err}")
            return None

    def configurar_menu_superior(self):
        barra = Menu(self.root)
        self.root.config(menu=barra)
        m_user = Menu(barra, tearoff=0)

        barra.add_cascade(label=f"👤 Usuario", menu=m_user)
        m_user.add_command(label="Ver Perfil", command=lambda: messagebox.showinfo(
            "Perfil", f"Usuario: {self.usuario_nombre}"))
        m_user.add_separator()
        m_user.add_command(label="Cerrar Sesión", command=self.cerrar_sesion)

        m_ayuda = Menu(barra, tearoff=0)
        barra.add_cascade(label="❓ Ayuda", menu=m_ayuda)
        m_ayuda.add_command(label="Manual de Usuario", command=lambda: messagebox.showinfo(
            "manual de Usuario", f"Ayuda: {self.Manual_usuario}"))
        m_ayuda.add_separator()
        m_ayuda.add_command(label="Soporte Tecnico", command=lambda: messagebox.showinfo(
            "Soporte Tecnico", f"Contacte al soporte técnico para obtener ayuda."))

    def crear_sidebar(self):
        self.side_menu = tk.Frame(self.root, bg="#2f3640", width=260)
        self.side_menu.pack(side="left", fill="y")
        self.side_menu.pack_propagate(False)


        # Contenedor del logo
        self.contenedor_logo = tk.Frame(self.side_menu, bg="#2f3640", height=100)
        self.contenedor_logo.pack(fill="x", pady=20)
        self.contenedor_logo.pack_propagate(False)
        self.colocar_logo(self.contenedor_logo)


         # Título CLEANZ
        tk.Label(self.side_menu, text="CLEANZ", fg="#1abc9c", bg="#2f3640", font=("Segoe UI", 24, "bold")).pack(pady=(0, 30))

        # Opciones del menú
        opciones = [
            ("🏠 Inicio", self.vista_inicio),
            ("📝 Registro", self.vista_registro),
            ("🔍 Consulta", self.vista_consulta), 
            ("🗑️ Desincorporados", self.modulo_desincorporar.mostrar_vista),  # <--- CAMBIADO
            ("⚙️ Mantenimiento", lambda: messagebox.showinfo("Mantenimiento", "Módulo en desarrollo"))
        ]

        for t, cmd in opciones:
            btn = tk.Button(self.side_menu, text=f"  {t}", command=cmd, fg="#dcdde1", bg="#2f3640", font=("Segoe UI", 12), bd=0, padx=20, pady=12, anchor="w", cursor="hand2")
            btn.pack(fill="x")
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#353b48"))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg="#2f3640"))


    def colocar_logo(self, contenedor):
        try:
            ruta_logo = os.path.join(os.path.dirname(__file__), "cleanz logo.jpg")
            if os.path.exists(ruta_logo):
                img = Image.open(ruta_logo)
                img = img.resize((180, 80), Image.Resampling.LANCZOS)
                self.logo_img = ImageTk.PhotoImage(img)
                lbl_logo= tk.Label(contenedor, image=self.logo_img, bg="#2f3640")
                lbl_logo.pack(expand=True)               
        except Exception as e:
            print(f"Error al cargar logo: {e}")
        
            tk.Label(contenedor, text="CLEANZ", fg="#1abc9c", bg="#2f3640", font=("Segoe UI", 24, "bold")).pack(expand=True)

    def crear_header(self):
        self.header = tk.Frame(self.root, bg="white", height=60)
        self.header.pack(side="top", fill="x")
        self.header.pack_propagate(False)

        # Sesión (izquierda)
        tk.Label(self.header, text=f"● SESIÓN: {self.usuario_nombre}", bg="white", font=("Segoe UI", 11, "bold"), fg="#27ae60").pack(side="left", padx=25)

         # Frame para fecha y hora (derecha)
        frame_fecha_hora = tk.Frame(self.header, bg="white")
        frame_fecha_hora.pack(side="right", padx=25)

        # Fecha
        self.label_fecha = tk.Label(self.header, text="", bg="white", font=("Segoe UI", 10), fg="#718093")
        self.label_fecha.pack(side="left")

        # Separador
        tk.Label(frame_fecha_hora, text=" | ", bg="white", font=("Segoe UI", 11), fg="#bdc3c7").pack(side="left")

        # Hora
        self.label_hora = tk.Label(self.header, text="", bg="white", font=("Segoe UI", 10, "bold"), fg="#2c3e50")
        self.label_hora.pack(side="left")

    def actualizar_reloj(self):
        ahora = datetime.now()
        fecha_str = ahora.strftime("%d/%m/%Y")
        hora_str = ahora.strftime("%I:%M:%S %p")  # Formato 12 horas con AM/PM
    
        if hasattr(self, 'label_fecha'):
            self.label_fecha.config(text=fecha_str)
        if hasattr(self, 'label_hora'):
            self.label_hora.config(text=hora_str)
    
        self.root.after(1000, self.actualizar_reloj)

        

    def poner_fondo(self):
        """Agrega una imagen de fondo sutil al contenedor principal"""
        try:
            ruta_fondo = os.path.join(os.path.dirname(__file__), "fondo.png")
            if os.path.exists(ruta_fondo):
                img = Image.open(ruta_fondo)
                img = img.resize((1200, 850), Image.Resampling.LANCZOS)
                self.fondo_img = ImageTk.PhotoImage(img)
                fondo_label = tk.Label(self.contenedor_principal, image=self.fondo_img)
                fondo_label.place(x=0, y=0, relwidth=1, relheight=1)
                fondo_label.lower()
        except:
            pass

    

    def limpiar_contenedor(self):
        for widget in self.contenedor_principal.winfo_children():
            widget.destroy()


    # MODULO DE INICIO - BIENVENIDA------------------#
    def vista_inicio(self):
        self.limpiar_contenedor()

        # Frame contenedor centrado
        self.contenedor_principal.grid_rowconfigure(0, weight=1)
        self.contenedor_principal.grid_columnconfigure(0, weight=1)

        # Frame central con fondo blanco y bordes redondeados
        card = tk.Frame(self.contenedor_principal, bg="white", highlightbackground="#dcdde1", highlightthickness=1)
        card.grid(row=0, column=0, padx=50, pady=50, sticky="nsew")

        # Logo o ícono (opcional)
        try:
            ruta_logo = os.path.join(os.path.dirname(__file__), "cleanz logo.jpg")
            if os.path.exists(ruta_logo):
                img = Image.open(ruta_logo)
                img = img.resize((180, 90), Image.Resampling.LANCZOS)
                self.logo_inicio = ImageTk.PhotoImage(img)
                tk.Label(card, image=self.logo_inicio, bg="white").pack(pady=(20, 10))
        except:
            pass


        # Texto de bienvenida
        tk.Label(card, text="BIENVENIDO", font=("Segoe UI", 28, "bold"), bg="white", fg="#2f3640").pack(pady=(10, 5))
        
        tk.Label(card, text="Sistema de Control de Bienes y Materia", font=("Segoe UI", 14), bg="white", fg="#7f8c8d").pack(pady=5)

        tk.Label(card, text="CLEANZ", font=("Segoe UI", 12), bg="white", fg="#1abc9c").pack(pady=(30, 40))

    def crear_etiqueta(self, parent, texto):
        lbl = ctk.CTkLabel(parent, text=texto, font=(
            "Segoe UI", 13, "bold"), text_color="#1abc9c")
        lbl.pack(anchor="w", pady=(0, 10))
        return lbl

    def crear_entry(self, parent, label, var_name):
        ctk.CTkLabel(parent, text=label, font=(
            "Segoe UI", 11)).pack(anchor="w")
        entry = ctk.CTkEntry(parent, width=250, height=35)
        entry.pack(pady=(0, 10))
        self.entradas[var_name] = entry
        return entry

    def crear_combo(self, parent, label, opciones, comando=None):
        ctk.CTkLabel(parent, text=label, font=(
            "Segoe UI", 11)).pack(anchor="w")
        combo = ctk.CTkComboBox(parent, values=opciones,
                                width=250, height=35, command=comando)
        combo.pack(pady=(0, 10))
        return combo

    def actualizar_subgrupos(self, seleccion):
        opciones = self.datos_clasificacion.get(seleccion, [])
        self.combo_sub.configure(values=opciones)
        self.combo_sub.set(opciones[0] if opciones else "")

    def calcular_total_cleanz(self):
        try:
            c = float(self.ent_cant.get() or 0)
            v = float(self.ent_costo.get() or 0)
            self.var_total.set(f"Total: {c*v:,.2f} Bs")
        except:
            self.var_total.set("Total: 0.00 Bs")

    # =================================================================
    # 3. MÓDULO DE REGISTRO
    # =================================================================

    def vista_registro(self):
        self.limpiar_contenedor()
        titulo = ctk.CTkLabel(self.contenedor_principal, text="NUEVO REGISTRO DE BIEN",
                              font=("Segoe UI", 22, "bold"), text_color="#2c3e50")
        titulo.pack(pady=(5, 10))

        frame_form = ctk.CTkFrame(self.contenedor_principal, fg_color="white", corner_radius=15,
                                  border_width=1, border_color="#dcdde1")
        frame_form.pack(padx=20, pady=5, fill="both", expand=True)

        self.datos_clasificacion = {
            "01. Bienes Inmuebles": ["01. Terrenos o Suelos", "02. Edificaciones y Construcciones", "03. Mejoras sobre Terrenos Ajenos", "04. Bienes Inmuebles Especiales"],
            "02. Bienes Muebles": ["01. Maquinaria y Equipos", "02. Equipos de Oficina y Computación", "03. Mobiliario y Enseres", "04. Equipos de Transporte", "05. Equipos de Comunicación y Señalamiento", "06. Equipos de Seguridad y Defensa"],
            "03. Bienes Intangibles": ["01. Propiedad Intelectual", "02. Títulos Valores"]
        }

        col1 = ctk.CTkFrame(frame_form, fg_color="transparent")
        col1.grid(row=0, column=0, padx=20, pady=20, sticky="n")
        self.crear_etiqueta(col1, "1. CLASIFICACIÓN")
        self.combo_grupo = self.crear_combo(col1, "Grupo:", list(
            self.datos_clasificacion.keys()), self.actualizar_subgrupos)
        self.combo_sub = self.crear_combo(
            col1, "Sub-Grupo:", ["Seleccione Grupo..."])

        col2 = ctk.CTkFrame(frame_form, fg_color="transparent")
        col2.grid(row=0, column=1, padx=20, pady=20, sticky="n")
        self.crear_etiqueta(col2, "2. IDENTIFICACIÓN / UBICACIÓN")
        self.ent_seccion = self.crear_entry(col2, "Sección:", "ent_seccion")
        self.ent_id = self.crear_entry(col2, "Nº Identificación:", "ent_id")
        self.ent_nom = self.crear_entry(
            col2, "Nombre del Elemento:", "ent_nom")
        self.combo_dep = self.crear_combo(col2, "Departamento:", [
                                          "PRESIDENCIA", "ADMINISTRACIÓN", "INFORMÁTICA", "RRHH", "SERVICIOS"])
        self.ent_area = self.crear_entry(col2, "Área:", "ent_area")

        col3 = ctk.CTkFrame(frame_form, fg_color="transparent")
        col3.grid(row=0, column=2, padx=20, pady=20, sticky="n")
        self.crear_etiqueta(col3, "3. VALORES Y FECHA")
        self.ent_cant = self.crear_entry(col3, "Cantidad:", "ent_cant")
        self.ent_costo = self.crear_entry(
            col3, "Valor Unitario (Bs):", "ent_costo")
        self.ent_anio = self.crear_entry(col3, "Año Ingreso:", "ent_anio")

        self.var_total = ctk.StringVar(value="Total: 0.00 Bs")
        lbl_total = ctk.CTkLabel(col3, textvariable=self.var_total, font=(
            "Segoe UI", 18, "bold"), text_color="#27ae60")
        lbl_total.pack(pady=(15, 0))

        self.ent_cant.bind(
            "<KeyRelease>", lambda e: self.calcular_total_cleanz())
        self.ent_costo.bind(
            "<KeyRelease>", lambda e: self.calcular_total_cleanz())

        frame_form.columnconfigure((0, 1, 2), weight=1)

        btn_frame = ctk.CTkFrame(
            self.contenedor_principal, fg_color="transparent")
        btn_frame.pack(side="bottom", pady=20)
        ctk.CTkButton(btn_frame, text="💾 GUARDAR", fg_color="#27ae60", width=200,
                      height=45, command=self.guardar_datos).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="🗑️ LIMPIAR", fg_color="#e67e22", width=140,
                      height=45, command=self.vista_registro).pack(side="left", padx=10)

    def guardar_datos(self):
        db = None
        try:
            # 1. Captura de datos
            nro_id = self.ent_id.get().strip()
            nombre = self.ent_nom.get().strip().upper()
            texto_seccion = self.ent_seccion.get().strip().upper()
            texto_area = self.ent_area.get().strip().upper()
            departamento = self.combo_dep.get()
            anio = self.ent_anio.get().strip()
            fecha_hoy = datetime.now().strftime("%Y-%m-%d")

            if not nro_id or not nombre:
                messagebox.showwarning(
                    "Faltan Datos", "Complete los campos obligatorios.")
                return

            # Obtener el texto COMPLETO del grupo y subgrupo
            grupo_texto = self.combo_grupo.get()
            subgrupo_texto = self.combo_sub.get()

            # Extraer el número de código (01, 02, 03, etc.)
            if '.' in grupo_texto:
                cod_g = grupo_texto.split('.')[0].strip()
            elif ':' in grupo_texto:
                cod_g = grupo_texto.split(':')[0].strip()
            else:
                cod_g = grupo_texto.strip()

            if '.' in subgrupo_texto:
                cod_s = subgrupo_texto.split('.')[0].strip()
            elif ':' in subgrupo_texto:
                cod_s = subgrupo_texto.split(':')[0].strip()
            else:
                cod_s = subgrupo_texto.strip()

            # Asegurar que los códigos tengan 2 dígitos
            cod_g = cod_g.zfill(2)
            cod_s = cod_s.zfill(2)

            print(
                f"DEBUG: Código Grupo: '{cod_g}', Código Subgrupo: '{cod_s}'")

            # Validar cantidades
            try:
                cant = int(self.ent_cant.get().strip() or 1)
                costo = float(self.ent_costo.get().strip() or 0)
                total = cant * costo
            except ValueError:
                messagebox.showwarning(
                    "Error de Formato", "Cantidad y Valor deben ser números válidos.")
                return

            db = self.conectar_db()
            if not db:
                return

            cursor = db.cursor()

            # --- 2. BÚSQUEDA DEL GRUPO por código ---
            cursor.execute(
                "SELECT id_grupo FROM grupo WHERE cod_grupo = %s", (cod_g,))
            res_g = cursor.fetchone()

            if not res_g:
                messagebox.showerror(
                    "Error", f"No se encontró el GRUPO con código: {cod_g}\nGrupo seleccionado: {grupo_texto}")
                return

            id_g = res_g[0]

            # --- 3. BÚSQUEDA DEL SUBGRUPO por código y grupo ---
            cursor.execute("""
                SELECT id_subgrupo FROM subgrupo 
                WHERE cod_subgrupo = %s AND id_grupo = %s
            """, (cod_s, id_g))
            res_s = cursor.fetchone()

            if not res_s:
                # Mostrar todos los subgrupos disponibles para depuración
                cursor.execute(
                    "SELECT cod_subgrupo, nombre_subgrupo FROM subgrupo WHERE id_grupo = %s", (id_g,))
                subgrupos_disponibles = cursor.fetchall()
                lista_subs = ", ".join(
                    [f"{s[0]}: {s[1]}" for s in subgrupos_disponibles])

                messagebox.showerror("Error",
                                     f"No se encontró el SUBGRUPO con código: {cod_s} para el grupo {cod_g}\n"
                                     f"Subgrupos disponibles: {lista_subs}")
                return

            id_s = res_s[0]

            print(
                f"DEBUG: Grupo ID: {id_g}, Subgrupo ID: {id_s} (código: {cod_s})")

            # --- 4. GESTIÓN DE ÁREAS ---
            cursor.execute(
                "SELECT id_area FROM areas WHERE nombre_area = %s", (texto_area,))
            res_a = cursor.fetchone()
            id_a = res_a[0] if res_a else None

            if not id_a and texto_area:
                cursor.execute(
                    "INSERT INTO areas (nombre_area) VALUES (%s)", (texto_area,))
                id_a = cursor.lastrowid
            elif not texto_area:
                id_a = None

            # --- 5. GESTIÓN DE SECCIONES ---
            if texto_seccion:
                cursor.execute(
                    "SELECT id_seccion FROM secciones WHERE nombre_seccion = %s AND id_subgrupo = %s", (texto_seccion, id_s))
                res_sec = cursor.fetchone()
                id_sec = res_sec[0] if res_sec else None

                if not id_sec:
                    cod_sec_gen = f"SEC-{id_s}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                    cursor.execute("INSERT INTO secciones (cod_seccion, nombre_seccion, id_subgrupo) VALUES (%s, %s, %s)",
                                   (cod_sec_gen, texto_seccion, id_s))
                    id_sec = cursor.lastrowid
            else:
                id_sec = None

            # Verificar duplicado
            cursor.execute(
                "SELECT id_item FROM bienes_materia WHERE nro_identificacion = %s", (nro_id,))
            if cursor.fetchone():
                messagebox.showwarning(
                    "Duplicado", f"Ya existe un bien con el ID: {nro_id}")
                return

            # --- 6. INSERCIÓN ---
            datos_para_guardar = {
                "id_seccion": id_sec,
                "id_subgrupo": id_s,
                "id_area": id_a,
                "id_grupo": id_g,
                "nro_identificacion": nro_id,
                "nombre_elementos": nombre,
                "departamento": departamento,
                "area_especifica": texto_area or None,
                "anio_ingreso": anio,
                "cantidad": cant,
                "valor_unitario": costo,
                "valor_total": total,
                "fecha_ingreso": fecha_hoy,
                "id_usuario": 1
            }

            # Filtrar valores None para columnas que pueden ser NULL
            datos_filtrados = {
                k: v for k, v in datos_para_guardar.items() if v is not None}

            columnas = ", ".join(datos_filtrados.keys())
            marcadores = ", ".join(["%s"] * len(datos_filtrados))

            sql = f"INSERT INTO bienes_materia ({columnas}) VALUES ({marcadores})"
            valores = tuple(datos_filtrados.values())

            cursor.execute(sql, valores)
            db.commit()

            messagebox.showinfo(
                "Éxito", f"¡Bien '{nombre}' guardado exitosamente!")
            self.vista_registro()

        except mysql.connector.Error as e:
            if db:
                db.rollback()
            messagebox.showerror("Error SQL", f"Código {e.errno}: {e.msg}")
        except Exception as e:
            if db:
                db.rollback()
            messagebox.showerror("Error de Aplicación", f"Detalle: {e}")
        finally:
            if db:
                db.close()

    # =================================================================
    # 4. MÓDULO DE CONSULTA Y EDICIÓN
    # =================================================================

    def vista_consulta(self):
        """MÓDULO DE CONSULTA - Estructura con filtros, tabla y botones de acción"""
        self.limpiar_contenedor()

        # --- CONFIGURACIÓN DE ESTILO ---
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview",
                        background="white",
                        foreground="black",
                        fieldbackground="white",
                        rowheight=30,
                        borderwidth=0)
        style.configure("Treeview.Heading",
                        font=("Segoe UI", 11, "bold"),
                        background="#2f3640",
                        foreground="white")
        style.map("Treeview", background=[('selected', '#1abc9c')])

        self.jerarquia = {
            "01. Bienes Inmuebles": ["01. Terrenos o Suelos", "02. Edificaciones y Construcciones", "03. Mejoras sobre Terrenos Ajenos", "04. Bienes Inmuebles Especiales"],
            "02. Bienes Muebles": ["01. Maquinaria y Equipos", "02. Equipos de Oficina y Computación", "03. Mobiliario y Enseres", "04. Equipos de Transporte", "05. Equipos de Comunicación y Señalamiento", "06. Equipos de Seguridad y Defensa"],
            "03. Bienes Intangibles": ["01. Propiedad Intelectual", "02. Títulos Valores"]
        }

        # --- PANEL SUPERIOR DE FILTROS ---
        frame_filtros = ctk.CTkFrame(
            self.contenedor_principal, fg_color="white", corner_radius=15)
        frame_filtros.pack(padx=20, pady=10, fill="x")

        for i in range(5):
            frame_filtros.columnconfigure(i, weight=1)

        ctk.CTkLabel(frame_filtros, text="📊 FILTROS DE BÚSQUEDA", font=("Segoe UI", 13, "bold"),
                     text_color="#1abc9c").grid(row=0, column=0, columnspan=5, padx=20, pady=10, sticky="w")

        # 1. Buscador por texto
        self.f_busqueda = ctk.CTkEntry(
            frame_filtros, placeholder_text="🔍 Buscar por Nombre o ID...", height=35)
        self.f_busqueda.grid(row=1, column=0, padx=10,
                             pady=(0, 20), sticky="ew")
        self.f_busqueda.bind(
            "<KeyRelease>", lambda e: self.cargar_datos_iniciales())

        # 2. Filtro Grupo
        self.f_grupo = ctk.CTkComboBox(frame_filtros, values=["TODOS LOS GRUPOS"] + list(self.jerarquia.keys()),
                                       height=35, command=self.actualizar_subgrupos_filtro)
        self.f_grupo.grid(row=1, column=1, padx=10, pady=(0, 20), sticky="ew")

        # 3. Filtro Subgrupo
        self.f_subgrupo = ctk.CTkComboBox(frame_filtros, values=["TODOS LOS SUBGRUPOS"], height=35,
                                          command=lambda x: self.cargar_datos_iniciales())
        self.f_subgrupo.grid(row=1, column=2, padx=10,
                             pady=(0, 20), sticky="ew")

        # 4. Filtro Departamento
        self.f_depto = ctk.CTkComboBox(frame_filtros, values=["TODOS LOS DEPTOS", "PRESIDENCIA", "ADMINISTRACIÓN",
                                                              "INFORMÁTICA", "RRHH", "SERVICIOS", "SECRETARÍA"],
                                       height=35, command=lambda x: self.cargar_datos_iniciales())
        self.f_depto.grid(row=1, column=3, padx=10, pady=(0, 20), sticky="ew")

        # 5. Botón Limpiar
        btn_clean = ctk.CTkButton(frame_filtros, text="🧹 LIMPIAR", fg_color="#7f8c8d", hover_color="#95a5a6",
                                  height=35, command=self.resetear_filtros)
        btn_clean.grid(row=1, column=4, padx=10, pady=(0, 20), sticky="ew")

        # --- CONTADOR DE REGISTROS ---
        self.label_total_registros = ctk.CTkLabel(frame_filtros, text="📋 Total de bienes: 0",
                                                  font=("Segoe UI",
                                                        13, "bold"),
                                                  text_color="#1abc9c")
        self.label_total_registros.grid(
            row=2, column=0, columnspan=5, padx=20, pady=(5, 10), sticky="e")

        # --- BOTONES DE ACCIÓN ---
        frame_acciones = ctk.CTkFrame(
            self.contenedor_principal, fg_color="transparent")
        frame_acciones.pack(side="bottom", pady=20, fill="x")

        centro_btns = ctk.CTkFrame(frame_acciones, fg_color="transparent")
        centro_btns.pack(expand=True)

        # Botones con íconos y colores institucionales
        ctk.CTkButton(centro_btns, text="📝 EDITAR", fg_color="#f1c40f", text_color="black",
                      hover_color="#f39c12", font=("Segoe UI", 12, "bold"), width=140, height=40,
                      command=self.accion_editar).pack(side="left", padx=10)

        ctk.CTkButton(centro_btns, text="📄 PDF", fg_color="#e67e22",
                      hover_color="#d35400", font=("Segoe UI", 12, "bold"), width=140, height=40,
                      command=self.generar_pdf_reporte).pack(side="left", padx=10)

        ctk.CTkButton(centro_btns, text="📊 EXCEL", fg_color="#27ae60",
                      hover_color="#219150", font=("Segoe UI", 12, "bold"), width=140, height=40,
                      command=self.exportar_a_excel).pack(side="left", padx=10)

        ctk.CTkButton(centro_btns, text="🗑️ DESINCORPORAR", fg_color="#e74c3c",
                      hover_color="#c0392b", font=("Segoe UI", 12, "bold"), width=160, height=40,
                      command=self.desincorporar_item).pack(side="left", padx=10)

        # --- CONTENEDOR DE LA TABLA ---
        frame_tabla = ctk.CTkFrame(
            self.contenedor_principal, fg_color="white", corner_radius=10)
        frame_tabla.pack(padx=20, pady=10, fill="both", expand=True)

        # Crear Treeview con scrollbar
        columnas = ("id_item", "grupo", "subgrupo", "seccion", "nro_identificacion",
                    "nombre_elementos", "departamento", "area_especifica", "cantidad",
                    "valor_unitario", "valor_total", "anio_ingreso")

        self.tabla = ttk.Treeview(
            frame_tabla, columns=columnas, show="headings", height=20)

        # Reemplaza los headers y anchos por estos:
        headers = ["ID", "GRUPO", "SUB-G", "SECCIÓN", "N° IDENTIFICACIÓN",
                   "NOMBRE DEL BIEN", "DEPARTAMENTO", "ÁREA", "CANT.", "VALOR U.", "TOTAL Bs.", "AÑO"]

        # Anchos más compactos
        anchos = [40, 50, 50, 100, 130, 250, 130, 120, 70, 100, 120, 80]

        for col, head, ancho in zip(columnas, headers, anchos):
            self.tabla.heading(col, text=head)
            self.tabla.column(col, width=ancho, anchor="center" if col not in [
                              "nombre_elementos"] else "w")

        # Scrollbar vertical
        scroll_y = ttk.Scrollbar(
            frame_tabla, orient="vertical", command=self.tabla.yview)
        scroll_x = ttk.Scrollbar(
            frame_tabla, orient="horizontal", command=self.tabla.xview)
        self.tabla.configure(yscrollcommand=scroll_y.set,
                             xscrollcommand=scroll_x.set)

        scroll_y.pack(side="right", fill="y")
        scroll_x.pack(side="bottom", fill="x")
        self.tabla.pack(side="left", expand=True, fill="both")

        # Evento doble clic para editar
        self.tabla.bind("<Double-1>", self.cargar_datos_para_editar)

        # Cargar datos iniciales
        self.cargar_datos_iniciales()

    def cargar_datos_iniciales(self):
        """Carga los datos de la tabla con los filtros aplicados"""
        try:
            # Limpiar tabla
            for item in self.tabla.get_children():
                self.tabla.delete(item)

            db = self.conectar_db()
            if not db:
                return

            cursor = db.cursor()

        # Consulta SQL optimizada - MOSTRAR CÓDIGOS en lugar de nombres completos
            query = """
                SELECT 
                    b.id_item, 
                    COALESCE(g.cod_grupo, '--'),              -- CÓDIGO del grupo (01, 02, 03)
                    COALESCE(sg.cod_subgrupo, '--'),          -- CÓDIGO del subgrupo (01, 02, 03...)
                    COALESCE(s.nombre_seccion, 'SIN SECCIÓN'),
                    b.nro_identificacion, 
                    b.nombre_elementos, 
                    b.departamento, 
                    COALESCE(NULLIF(b.area_especifica, ''), 'GENERAL'), 
                    b.cantidad, 
                    b.valor_unitario, 
                    b.valor_total, 
                    b.anio_ingreso
                FROM bienes_materia b
                LEFT JOIN grupo g ON b.id_grupo = g.id_grupo
                LEFT JOIN subgrupo sg ON b.id_subgrupo = sg.id_subgrupo
                LEFT JOIN secciones s ON b.id_seccion = s.id_seccion
                WHERE 1=1
            """
            params = []

            # --- FILTROS ---
            busqueda = self.f_busqueda.get().strip() if hasattr(self, 'f_busqueda') else ""
            if busqueda:
                query += " AND (b.nombre_elementos LIKE %s OR b.nro_identificacion LIKE %s)"
                params.extend([f"%{busqueda}%", f"%{busqueda}%"])

            grupo = self.f_grupo.get() if hasattr(self, 'f_grupo') else "TODOS LOS GRUPOS"
            if grupo != "TODOS LOS GRUPOS":
                # Extraer solo el código del grupo seleccionado (ej: "01. Bienes Inmuebles" -> "01")
                cod_grupo_filtro = grupo.split('.')[0].strip()
                query += " AND g.cod_grupo = %s"
                params.append(cod_grupo_filtro)

            sub = self.f_subgrupo.get() if hasattr(
                self, 'f_subgrupo') else "TODOS LOS SUBGRUPOS"
            if sub != "TODOS LOS SUBGRUPOS":
                # Extraer solo el código del subgrupo seleccionado (ej: "02. Equipos de Oficina" -> "02")
                cod_sub_filtro = sub.split('.')[0].strip()
                query += " AND sg.cod_subgrupo = %s"
                params.append(cod_sub_filtro)

            depto = self.f_depto.get() if hasattr(self, 'f_depto') else "TODOS LOS DEPTOS"
            if depto != "TODOS LOS DEPTOS":
                query += " AND b.departamento = %s"
                params.append(depto)

            query += " ORDER BY b.id_item DESC"

            cursor.execute(query, params)
            rows = cursor.fetchall()

            # Insertar datos en la tabla
            for registro in rows:
                # Formatear valores numéricos
                v_u = f"{float(registro[9]):,.2f}" if registro[9] is not None else "0.00"
                v_t = f"{float(registro[10]):,.2f}" if registro[10] is not None else "0.00"

                self.tabla.insert("", "end", values=(
                    registro[0],  # ID
                    registro[1],  # Código Grupo (01, 02, 03)
                    registro[2],  # Código Subgrupo (01, 02, 03...)
                    registro[3],  # Sección
                    registro[4],  # N° Identificación
                    registro[5],  # Nombre
                    registro[6],  # Departamento
                    registro[7],  # Área
                    registro[8],  # Cantidad
                    v_u,          # Valor Unitario
                    v_t,          # Valor Total
                    registro[11]  # Año
                ))

            # Actualizar contador de registros
            total_registros = len(rows)
            # Ver en consola
            print(f"📊 DEBUG - Total de registros: {total_registros}")

            if hasattr(self, 'label_total_registros'):
                self.label_total_registros.configure(
                    text=f"📋 Total de bienes: {total_registros}")
            else:
                print(
                    "⚠️ ERROR: label_total_registros no existe - debes crearlo en vista_consulta")

            db.close()

        except Exception as e:
            print(f"❌ ERROR al cargar datos: {e}")
            messagebox.showerror(
                "Error", f"No se pudieron cargar los datos:\n{e}")

    def actualizar_subgrupos_filtro(self, seleccion):
        """Actualiza el combo de subgrupos según el grupo seleccionado"""
        if seleccion in self.jerarquia:
            nuevos_valores = ["TODOS LOS SUBGRUPOS"] + \
                self.jerarquia[seleccion]
            self.f_subgrupo.configure(values=nuevos_valores)
            self.f_subgrupo.set("TODOS LOS SUBGRUPOS")
        else:
            self.f_subgrupo.configure(values=["TODOS LOS SUBGRUPOS"])
            self.f_subgrupo.set("TODOS LOS SUBGRUPOS")

        self.cargar_datos_iniciales()

    def resetear_filtros(self):
        """Limpia los campos y recarga el inventario completo"""
        if hasattr(self, 'f_busqueda'):
            self.f_busqueda.delete(0, 'end')
        if hasattr(self, 'f_grupo'):
            self.f_grupo.set("TODOS LOS GRUPOS")
        if hasattr(self, 'f_subgrupo'):
            self.f_subgrupo.configure(values=["TODOS LOS SUBGRUPOS"])
            self.f_subgrupo.set("TODOS LOS SUBGRUPOS")
        if hasattr(self, 'f_depto'):
            self.f_depto.set("TODOS LOS DEPTOS")

        # Recargar datos (esto actualizará el contador automáticamente)
        self.cargar_datos_iniciales()

    def cargar_datos_para_editar(self, event):
        """Carga los datos del elemento seleccionado para su edición."""
        self.accion_editar()

    # Acción de editar: abre una ventana con los datos del registro seleccionado para su modificación #

    def accion_editar(self):
        """Abre ventana de edición con los datos del registro seleccionado."""
        from tkinter import messagebox

        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showwarning(
                "Atención", "Por favor, selecciona un registro.")
            return

        # Obtener valores de la fila seleccionada
        v = self.tabla.item(seleccion)['values']
        # v[0]=id_item | v[1]=Grupo (int: 1,2,3) | v[2]=Subgrupo (int: 1-10)
        # v[3]=Sección | v[4]=Nro Identificación | v[5]=Nombre | v[6]=Departamento
        # v[7]=Área | v[8]=Cantidad | v[9]=Valor U | v[10]=Total | v[11]=Año
        id_primario_db = v[0]
        nro_identificacion = str(v[4])  # CORREGIDO: índice 4 es el ID
        nombre_elemento = v[5]           # CORREGIDO: índice 5 es el nombre

        # Convertir códigos a string con formato de 2 dígitos
        cod_grupo_actual = str(v[1]).zfill(2)   # '01', '02', '03'
        # '01', '02', '03', '04', '05', '06'
        cod_sub_actual = str(v[2]).zfill(2)

        # Crear ventana de edición
        ventana_edit = ctk.CTkToplevel(self.root)
        ventana_edit.title(
            f"RECTIFICAR REGISTRO - CLEANZ (ID: {id_primario_db})")
        ventana_edit.geometry("900x550")
        ventana_edit.minsize(850, 500)  # Tamaño mínimo para no comprimir
        ventana_edit.configure(fg_color="#e8f0f8")
        ventana_edit.attributes("-topmost", True)
        ventana_edit.focus_force()  # Forzar foco
        ventana_edit.grab_set()
        ventana_edit.lift()  # Levantar sobre otras ventanas

        # Centrar la ventana en la pantalla
        ventana_edit.update_idletasks()
        x = (ventana_edit.winfo_screenwidth() // 2) - (900 // 2)
        y = (ventana_edit.winfo_screenheight() // 2) - (550 // 2)
        ventana_edit.geometry(f"900x550+{x}+{y}")

        # Frame principal
        main_frame = ctk.CTkFrame(
            ventana_edit, fg_color="white", corner_radius=15)
        main_frame.pack(fill="both", expand=True, padx=12, pady=15)

        # Título
        titulo_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        titulo_frame.pack(fill="x", pady=(8, 15))

        ctk.CTkLabel(titulo_frame, text="✏️ EDICIÓN INTEGRAL DE BIENES - CLEANZ",
                     font=("Segoe UI", 18, "bold"), text_color="#1a5276").pack()

        ctk.CTkLabel(titulo_frame, text=f"Registro ID: {id_primario_db}",
                     font=("Segoe UI", 10), text_color="#7f8c8d").pack()

        # Frame contenedor de 3 columnas
        cols_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        cols_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Diccionario de clasificación
        dict_categorias = {
            "01. Bienes Inmuebles": ["01. Terrenos o Suelos", "02. Edificaciones y Construcciones", "03. Mejoras sobre Terrenos Ajenos", "04. Bienes Inmuebles Especiales"],
            "02. Bienes Muebles": ["01. Maquinaria y Equipos", "02. Equipos de Oficina y Computación", "03. Mobiliario y Enseres", "04. Equipos de Transporte", "05. Equipos de Comunicación y Señalamiento", "06. Equipos de Seguridad y Defensa"],
            "03. Bienes Intangibles": ["01. Propiedad Intelectual", "02. Títulos Valores"]
        }

        # Obtener grupo actual (mapear desde código a nombre completo)
        grupo_actual = None
        for key in dict_categorias.keys():
            if key.startswith(cod_grupo_actual):
                grupo_actual = key
                break
        if not grupo_actual:
            grupo_actual = "02. Bienes Muebles"

        # ========== COLUMNA 1: CLASIFICACIÓN ==========
        col1 = ctk.CTkFrame(cols_frame, fg_color="#f0f4f8", corner_radius=10)
        col1.pack(side="left", fill="both", expand=True, padx=4, pady=4)

        ctk.CTkLabel(col1, text="📂 CLASIFICACIÓN", font=("Segoe UI", 12, "bold"),
                     text_color="#1abc9c").pack(pady=(10, 8))

        # Combo Grupo
        ctk.CTkLabel(col1, text="Grupo:", font=("Segoe UI", 10, "bold")).pack(
            anchor="w", padx=12, pady=(4, 2))
        combo_grupo = ctk.CTkComboBox(col1, width=250, height=32, font=(
            "Segoe UI", 10), values=list(dict_categorias.keys()))
        combo_grupo.set(grupo_actual)
        combo_grupo.pack(padx=12, pady=2)

        # Combo Subgrupo
        ctk.CTkLabel(col1, text="Sub-Grupo:", font=("Segoe UI", 10,
                     "bold")).pack(anchor="w", padx=12, pady=(8, 2))
        combo_sub = ctk.CTkComboBox(
            col1, width=250, height=32, font=("Segoe UI", 10), values=[])
        combo_sub.pack(padx=12, pady=2)

        # Función para actualizar subgrupos
        def actualizar_subs(grupo_seleccionado):
            subs = dict_categorias.get(grupo_seleccionado, [])
            combo_sub.configure(values=subs)
            if subs:
                sub_encontrado = None
                for sub_item in subs:
                    if sub_item.startswith(cod_sub_actual):
                        sub_encontrado = sub_item
                        break
                combo_sub.set(sub_encontrado if sub_encontrado else subs[0])

        # Conectar el comando del combo_grupo
        combo_grupo.configure(command=actualizar_subs)
        actualizar_subs(grupo_actual)

        # ========== COLUMNA 2: IDENTIFICACIÓN / UBICACIÓN ==========
        col2 = ctk.CTkFrame(cols_frame, fg_color="#f0f4f8", corner_radius=10)
        col2.pack(side="left", fill="both", expand=True, padx=4, pady=4)

        ctk.CTkLabel(col2, text="📍 IDENTIFICACIÓN / UBICACIÓN", font=("Segoe UI", 10, "bold"),
                     text_color="#1abc9c").pack(pady=(8, 2))

        # Sección
        ctk.CTkLabel(col2, text="Sección / Ubicación:", font=("Segoe UI",
                     10, "bold")).pack(anchor="w", padx=12, pady=(8, 2))
        ent_seccion = ctk.CTkEntry(
            col2, width=280, height=32, font=("Segoe UI", 10))
        ent_seccion.insert(0, v[3] if v[3] != "SIN SECCIÓN" else "")
        ent_seccion.pack(padx=12, pady=2)

        # N° Identificación
        ctk.CTkLabel(col2, text="N° Identificación:", font=(
            "Segoe UI", 10, "bold")).pack(anchor="w", padx=12, pady=(8, 2))
        ent_nro_id = ctk.CTkEntry(
            col2, width=280, height=35, font=("Segoe UI", 10))
        ent_nro_id.insert(0, nro_identificacion)
        ent_nro_id.pack(padx=12, pady=2)

        # Nombre del Elemento
        ctk.CTkLabel(col2, text="Nombre del Elemento:", font=(
            "Segoe UI", 10, "bold")).pack(anchor="w", padx=12, pady=(8, 2))
        ent_nombre = ctk.CTkEntry(
            col2, width=280, height=35, font=("Segoe UI", 10))
        ent_nombre.insert(0, nombre_elemento)
        ent_nombre.pack(padx=12, pady=2)

        # Departamento
        ctk.CTkLabel(col2, text="Departamento:", font=(
            "Segoe UI", 11, "bold")).pack(anchor="w", padx=15, pady=(8, 2))
        combo_depto = ctk.CTkComboBox(col2, width=280, height=35, font=("Segoe UI", 10), values=[
                                      "PRESIDENCIA", "ADMINISTRACIÓN", "INFORMÁTICA", "RRHH", "SERVICIOS", "SECRETARÍA", "OFICINA"])
        combo_depto.set(v[6])
        combo_depto.pack(padx=12, pady=2)

        # Área Específica
        ctk.CTkLabel(col2, text="Área Específica:", font=(
            "Segoe UI", 10, "bold")).pack(anchor="w", padx=12, pady=(8, 2))
        ent_area = ctk.CTkEntry(
            col2, width=280, height=32, font=("Segoe UI", 10))
        ent_area.insert(0, v[7] if v[7] != "GENERAL" else "")
        ent_area.pack(padx=12, pady=2)

        # ========== COLUMNA 3: VALORES Y FECHA ==========
        col3 = ctk.CTkFrame(cols_frame, fg_color="#f0f4f8", corner_radius=10)
        col3.pack(side="left", fill="both", expand=True, padx=4, pady=4)

        ctk.CTkLabel(col3, text="💰 VALORES", font=("Segoe UI", 12,
                     "bold"), text_color="#1abc9c").pack(pady=(10, 8))

        # Cantidad
        ctk.CTkLabel(col3, text="Cantidad:", font=("Segoe UI", 10, "bold")).pack(
            anchor="w", padx=12, pady=(8, 2))
        ent_cant = ctk.CTkEntry(
            col3, width=280, height=32, font=("Segoe UI", 10))
        ent_cant.insert(0, str(v[8]))
        ent_cant.pack(padx=12, pady=2)

        # Valor Unitario
        ctk.CTkLabel(col3, text="Valor Unitario (Bs):", font=(
            "Segoe UI", 10, "bold")).pack(anchor="w", padx=12, pady=(8, 2))
        ent_valor = ctk.CTkEntry(
            col3, width=240, height=32, font=("Segoe UI", 10))
        valor_limpio = str(v[9]).replace(",", "").replace("Bs", "").strip()
        ent_valor.insert(0, valor_limpio)
        ent_valor.pack(padx=12, pady=2)

        # Año Ingreso
        ctk.CTkLabel(col3, text="Año Ingreso:", font=("Segoe UI", 10, "bold")).pack(
            anchor="w", padx=12, pady=(8, 2))
        ent_anio = ctk.CTkEntry(
            col3, width=240, height=32, font=("Segoe UI", 10))
        ent_anio.insert(0, str(v[11]))
        ent_anio.pack(padx=12, pady=2)

        # Total
        total_frame = ctk.CTkFrame(col3, fg_color="#d4f1f9", corner_radius=8)
        total_frame.pack(fill="x", padx=12, pady=(15, 10))

        ctk.CTkLabel(total_frame, text="TOTAL (Bs)", font=(
            "Segoe UI", 11, "bold"), text_color="#1a5276").pack(pady=(6, 2))
        lbl_total = ctk.CTkLabel(total_frame, text="0.00", font=(
            "Segoe UI", 18, "bold"), text_color="#27ae60")
        lbl_total.pack(pady=(0, 6))

        def calcular_total(*args):
            try:
                cant = float(ent_cant.get() or 0)
                valor = float(ent_valor.get() or 0)
                total = cant * valor
                lbl_total.configure(text=f"Bs. {total:,.2f}")
            except:
                lbl_total.configure(text="Bs. 0.00")

        ent_cant.bind("<KeyRelease>", calcular_total)
        ent_valor.bind("<KeyRelease>", calcular_total)
        calcular_total()

        # ========== BOTONES ==========
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(pady=12)

        btn_guardar = ctk.CTkButton(btn_frame, text="💾 GUARDAR CAMBIOS", fg_color="#27ae60",
                                    hover_color="#219a52", width=170, height=35,
                                    font=("Segoe UI", 11, "bold"),
                                    command=lambda: self.guardar_cambios_db(ventana_edit, combo_grupo, combo_sub,
                                                                            ent_seccion, ent_nro_id, ent_nombre,
                                                                            combo_depto, ent_area, ent_cant,
                                                                            ent_valor, ent_anio, id_primario_db))
        btn_guardar.pack(side="left", padx=8)

        btn_cancelar = ctk.CTkButton(btn_frame, text="❌ CANCELAR", fg_color="#e74c3c",
                                     hover_color="#c0392b", width=170, height=35,
                                     font=("Segoe UI", 11, "bold"),
                                     command=ventana_edit.destroy)
        btn_cancelar.pack(side="left", padx=8)

    def guardar_cambios_db(self, ventana, c_grupo, c_sub, e_sec, e_id, e_nom, c_dep, e_area, e_cant, e_val, e_anio, id_item):
        """Procesa la actualización de datos en la DB tras la edición"""
        from tkinter import messagebox
        db = None
        try:
            # Capturar datos
            n_id = e_id.get().strip()
            nom = e_nom.get().strip().upper()
            dep = c_dep.get()
            area = e_area.get().strip().upper()
            cant = int(e_cant.get().strip() or 0)
            # Reemplazar coma por punto si es necesario
            valor_str = e_val.get().strip().replace(",", ".")
            val_u = float(valor_str or 0)
            total = cant * val_u
            anio = e_anio.get().strip()
            texto_seccion = e_sec.get().strip().upper()

            # Validar que el número de identificación no esté vacío
            if not n_id:
                messagebox.showwarning(
                    "Advertencia", "El número de identificación no puede estar vacío.")
                return

            # Extraer códigos
            grupo_texto = c_grupo.get()
            subgrupo_texto = c_sub.get()

            if '.' in grupo_texto:
                cod_grupo = grupo_texto.split('.')[0].strip()
            else:
                cod_grupo = grupo_texto.split(':')[0].strip()

            if '.' in subgrupo_texto:
                cod_sub = subgrupo_texto.split('.')[0].strip()
            else:
                cod_sub = subgrupo_texto.split(':')[0].strip()

            cod_grupo = cod_grupo.zfill(2)
            cod_sub = cod_sub.zfill(2)

            print(f"DEBUG - ID Item: {id_item}, Nuevo Nro ID: {n_id}")

            db = self.conectar_db()
            if not db:
                messagebox.showerror(
                    "Error", "No se pudo conectar a la base de datos")
                return

            cursor = db.cursor()

            # Verificar si el número de identificación ya existe en OTRO registro
            cursor.execute(
                "SELECT id_item FROM bienes_materia WHERE nro_identificacion = %s AND id_item != %s", (n_id, id_item))
            if cursor.fetchone():
                messagebox.showwarning(
                    "Duplicado", f"El número de identificación '{n_id}' ya existe en otro registro.\nPor favor, usa un número único.")
                return

            # Buscar ID del grupo
            cursor.execute(
                "SELECT id_grupo FROM grupo WHERE cod_grupo = %s", (cod_grupo,))
            res_g = cursor.fetchone()
            if not res_g:
                messagebox.showerror(
                    "Error", f"No se encontró el grupo con código: {cod_grupo}")
                return
            id_g_real = res_g[0]

            # Buscar ID del subgrupo
            cursor.execute("SELECT id_subgrupo FROM subgrupo WHERE cod_subgrupo = %s AND id_grupo = %s",
                           (cod_sub, id_g_real))
            res_s = cursor.fetchone()
            if not res_s:
                messagebox.showerror(
                    "Error", f"No se encontró el subgrupo con código: {cod_sub}")
                return
            id_s_real = res_s[0]

            # Gestionar sección
            id_sec_final = None
            if texto_seccion:
                cursor.execute("SELECT id_seccion FROM secciones WHERE nombre_seccion = %s AND id_subgrupo = %s",
                               (texto_seccion, id_s_real))
            res_sec = cursor.fetchone()
            if res_sec:
                id_sec_final = res_sec[0]
            else:
                cod_seccion = f"SEC-{id_s_real}-{anio}" if anio else f"SEC-{id_s_real}"
                cursor.execute("INSERT INTO secciones (cod_seccion, nombre_seccion, id_subgrupo) VALUES (%s, %s, %s)",
                               (cod_seccion, texto_seccion, id_s_real))
                id_sec_final = cursor.lastrowid

            # Actualizar el registro
            sql = """UPDATE bienes_materia SET 
                 id_grupo = %s, 
                 id_subgrupo = %s, 
                 id_seccion = %s, 
                 nro_identificacion = %s, 
                 nombre_elementos = %s, 
                 departamento = %s, 
                 area_especifica = %s, 
                 cantidad = %s, 
                 valor_unitario = %s, 
                 valor_total = %s, 
                 anio_ingreso = %s 
                 WHERE id_item = %s"""

            valores = (id_g_real, id_s_real, id_sec_final, n_id, nom, dep, area,
                       cant, val_u, total, anio, id_item)

            cursor.execute(sql, valores)
            db.commit()

            # Crear messagebox que salga al frente
            msg_box = messagebox.showinfo(
                "Éxito", "Registro actualizado correctamente.", parent=ventana)
            ventana.destroy()
            self.cargar_datos_iniciales()

        except Exception as e:
            print(f"❌ Error: {e}")
            if db:
                db.rollback()
            # Mostrar mensaje más amigable
            if "Duplicate entry" in str(e):
                messagebox.showerror(
                    "Error", "El número de identificación ya existe en otro registro.\nPor favor, usa un número único.")
            else:
                messagebox.showerror(
                    "Error", f"No se pudo actualizar el registro:\n{e}")
        finally:
            if db:
                db.close()

    def exportar_a_excel(self):
        """Exporta los datos de la tabla a un archivo Excel (.xlsx)"""
        try:
            from tkinter import filedialog, messagebox

            # 1. Extraemos los datos de la tabla
            datos = []
            for row_id in self.tabla.get_children():
                datos.append(self.tabla.item(row_id)['values'])

            if not datos:
                messagebox.showwarning(
                    "Atención", "No hay datos en la tabla para exportar.")
                return

            # Definimos las columnas exactas de tu sistema CLEANZ
            columnas = ["Item", "GRUPO", "SUB-GRUPO", "SECCIÓN", "ID",
                        "NOMBRE", "DEPTO", "ÁREA", "CANT.", "VALOR U.", "TOTAL", "AÑO"]
            df = pd.DataFrame(datos, columns=columnas)

            # 2. Cuadro de diálogo de guardado con nombre por defecto
            archivo = filedialog.asksaveasfilename(
                initialfile="Reporte_Inventario_CLEANZ.xlsx",
                defaultextension=".xlsx",
                filetypes=[("Libro de Excel", "*.xlsx")]
            )

            # pandas ya importado globalmente
            if archivo:
                # Especificamos el motor 'openpyxl' explícitamente para evitar errores
                df.to_excel(archivo, index=False, engine='openpyxl')
                messagebox.showinfo(
                    "Éxito", f"El archivo Excel se ha guardado en:\n{archivo}")

        except ImportError:
            messagebox.showerror(
                "Error de Librería", "Falta la librería 'openpyxl'.\nPor favor ejecuta: pip install openpyxl")
        except Exception as e:
            messagebox.showerror("Error Inesperado", f"Detalle del error: {e}")

    def generar_pdf_reporte(self):  # Mover esta función dentro de la clase
        """Genera un reporte PDF con la tabla de bienes completa"""
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.lib import colors
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet
        from tkinter import filedialog, messagebox
        import datetime

        # 1. Configurar nombre de archivo
        archivo = filedialog.asksaveasfilename(
            initialfile=f"Reporte_CLEANZ_{datetime.datetime.now().strftime('%d_%m_%Y')}.pdf",
            defaultextension=".pdf",
            filetypes=[("Documento PDF", "*.pdf")]
        )

        if not archivo:
            return

        try:
            # Configuración del documento en horizontal para que quepa la tabla
            doc = SimpleDocTemplate(archivo, pagesize=landscape(A4))
            elementos = []
            estilos = getSampleStyleSheet()

            # Encabezado institucional
            titulo = Paragraph(
                "<b>CONSEJO LEGISLATIVO DEL ESTADO ANZOÁTEGUI (CLEANZ)</b>", estilos['Title'])
            subtitulo = Paragraph(
                "Departamento de Bienes y Materia - Reporte de Inventario", estilos['Heading2'])
            fecha = Paragraph(
                f"Fecha de generación: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}", estilos['Normal'])

            elementos.extend([titulo, subtitulo, fecha, Spacer(1, 20)])

            # 2. Recolectar datos de la tabla para el PDF
            encabezados = ["ID", "NOMBRE", "DEPTO", "ÁREA", "CANT", "TOTAL"]
            data_pdf = [encabezados]

            for row_id in self.tabla.get_children():
                v = self.tabla.item(row_id)['values']
                # Seleccionamos las columnas más importantes para que quepan bien (ID, Nombre, Depto, Área, Cant, Total)
                data_pdf.append([v[4], v[5], v[6], v[7], v[8], v[10]])

            # 3. Crear y dar estilo a la tabla del PDF
            tabla_pdf = Table(data_pdf)
            estilo_tabla = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.teal),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ])
            tabla_pdf.setStyle(estilo_tabla)
            elementos.append(tabla_pdf)

            # Generar el archivo final
            doc.build(elementos)
            messagebox.showinfo(
                "PDF Creado", "El reporte con los datos de bienes ha sido generado.")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo generar el PDF: {e}")

    # =================================================================
    # 5. MÓDULO DE DESINCORPORACIÓN DE BIENES
    # =================================================================

    def desincorporar_item(self):
        """Desincorpora un bien usando el módulo especializado"""
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showwarning("Atención", "Por favor, selecciona un bien para desincorporar.")
            return

        # Obtener valores de la fila seleccionada
        v = self.tabla.item(seleccion)['values']

        # Usar el módulo para confirmar
        if not self.modulo_desincorporar.confirmar_accion(v[5], v[4]):
            return

        # Solicitar motivo
        motivo = self._pedir_motivo_desincorporacion(v[5], v[4])
        if not motivo:
            return

        # Procesar desincorporación
        exito = self.modulo_desincorporar.procesar_desincorporacion(v, motivo)

        if exito:
            self.cargar_datos_iniciales()


    def _pedir_motivo_desincorporacion(self, nombre_bien, nro_id):
        """Solicita el motivo de desincorporación"""
        import tkinter as tk

        motivo_ventana = ctk.CTkToplevel(self.root)
        motivo_ventana.title("Motivo de Desincorporación")
        motivo_ventana.geometry("500x350")
        motivo_ventana.configure(fg_color="#e8f0f8")
        motivo_ventana.attributes("-topmost", True)
        motivo_ventana.grab_set()

        # Centrar ventana
        motivo_ventana.update_idletasks()
        x = (motivo_ventana.winfo_screenwidth() // 2) - (500 // 2)
        y = (motivo_ventana.winfo_screenheight() // 2) - (350 // 2)
        motivo_ventana.geometry(f"500x350+{x}+{y}")

        # Frame principal
        main_frame = ctk.CTkFrame(motivo_ventana, fg_color="white", corner_radius=15)
        main_frame.pack(fill="both", expand=True, padx=15, pady=15)

        # Título
        ctk.CTkLabel(main_frame, text="✏️ Motivo de Desincorporación",
                 font=("Segoe UI", 18, "bold"), text_color="#c0392b").pack(pady=(15, 10))

        # Información del bien
        info_frame = ctk.CTkFrame(main_frame, fg_color="#f8f9fa", corner_radius=10)
        info_frame.pack(fill="x", padx=15, pady=10)

        ctk.CTkLabel(info_frame, text=f"📦 Bien: {nombre_bien}",
                 font=("Segoe UI", 12), text_color="#2c3e50").pack(anchor="w", padx=15, pady=(10, 5))

        ctk.CTkLabel(info_frame, text=f"🔢 ID: {nro_id}",
                 font=("Segoe UI", 12), text_color="#2c3e50").pack(anchor="w", padx=15, pady=(0, 10))

        # Área de texto para motivo
        ctk.CTkLabel(main_frame, text="Describa el motivo:",
                 font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=15, pady=(10, 5))

        text_motivo = tk.Text(main_frame, height=5, width=50, font=("Segoe UI", 11),
                          wrap=tk.WORD, relief="flat", borderwidth=1)
        text_motivo.pack(padx=15, pady=5)
        text_motivo.focus_set()

        # Ejemplos
        ctk.CTkLabel(main_frame, text="💡 Ejemplo: Deterioro | Robo | Daño | Obsolescencia | Donación | Venta",
                 font=("Segoe UI", 9), text_color="#95a5a6").pack(pady=(5, 10))

        motivo_resultado = [None]

        def confirmar():
            motivo = text_motivo.get("1.0", tk.END).strip()
            if motivo:
                motivo_resultado[0] = motivo
                motivo_ventana.destroy()
            else:
                messagebox.showwarning("Atención", "Debes ingresar un motivo.", parent=motivo_ventana)

        def cancelar():
            motivo_ventana.destroy()

        # Botones
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(pady=15)

        ctk.CTkButton(btn_frame, text="✅ Confirmar", fg_color="#27ae60",
                  command=confirmar, width=120).pack(side="left", padx=10)

        ctk.CTkButton(btn_frame, text="❌ Cancelar", fg_color="#95a5a6",
                  command=cancelar, width=120).pack(side="left", padx=10)

        motivo_ventana.wait_window()
        return motivo_resultado[0]

    # =================================================================
    # 6. MÓDULO DE MANTENIMIENTO DE SESIÓN
    # =================================================================

    # =================================================================
    # 6. MÓDULO DE CIERRE DE SESIÓN
    # =================================================================

    def cerrar_sesion(self):
        if messagebox.askyesno("Cerrar Sesión", "¿Salir del sistema?"):
            self.root.destroy()


if __name__ == "__main__":
    root = ctk.CTk()
    app = DashboardCleanz(root)
    root.mainloop()

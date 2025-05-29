import pyodbc
from fpdf import FPDF
from src.conexion_sqlS import conexiondb  # Función que devuelve la conexión pyodbc
from io import BytesIO
from PIL import Image
import tempfile
import os


def _fmt(val, prec):
    """
    Intenta convertir val a float y formatearlo con 'prec' decimales.
    Si falla, devuelve cadena vacía.
    """
    try:
        return f"{float(val):.{prec}f}"
    except (TypeError, ValueError):
        return ""

class PDFReport(FPDF):
    def __init__(self, logo_path=None, watermark_path=None):
        super().__init__()
        self.logo_path = logo_path
        self.watermark_path = watermark_path
        self.set_left_margin(15)
        self.set_right_margin(15)
        self.set_top_margin(20)
        self.set_auto_page_break(auto=True, margin=20)

    def header(self):
        # Logo a la derecha en el header, si existe
        if self.logo_path and os.path.exists(self.logo_path):
            # Colocamos el logo a 15 mm desde el borde derecho y 10 mm desde arriba
            logo_width = 25
            self.image(self.logo_path, x=self.w - self.r_margin - logo_width, y=10, w=logo_width)

        # Título centrado
        self.set_y(10)
        self.set_font("Arial", 'B', 16)
        self.set_text_color(0, 0, 0)
        self.cell(0, 15, "Reporte de Resultados", ln=True, align='C')
        self.ln(5)  # un pequeño espacio después del título

    def footer(self):
        # Pie de página con número de página centrado
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(100, 100, 100)
        self.cell(0, 10, f'Página {self.page_no()}', align='C')
            
##comente el add watermark porque da problema el opacity porque FPDF NO soporta ese parametro 
    '''def add_watermark(self):
        if self.watermark_path and os.path.exists(self.watermark_path):
            # Calcular ancho efectivo (ancho total menos márgenes)
            epw = self.w - self.l_margin - self.r_margin
            # Ancho de la marca de agua: la mitad del ancho efectivo
            w_wm = epw * 0.5
            # Centrar horizontalmente dentro del margen
            x_wm = self.l_margin + (epw - w_wm) / 2
            # Centrar verticalmente en la página
            y_wm = (self.h - w_wm) / 2
            self.image(self.watermark_path, x=x_wm, y=y_wm, w=w_wm, opacity=0.1)  # si tu fpdf soporta opacity
'''
def Greporte(nombre_usuario=None, resultado_id=None, fecha=None, nombre_metodo=None,
             logo_path='static/img/Logo_mariano.png'):
    conn = conexiondb()
    cursor = conn.cursor()

    sql = """
        SELECT 
            r.ResultadoId AS ID,
            r.NombreUsuario,
            m.Nombre    AS Metodo,
            r.Funcion,
            r.X0,
            r.X1,
            r.X2,
            r.Resultado,
            r.Iteraciones,
            r.ErrorRelativo,
            r.Fecha,
            r.Grafica
        FROM ResultadosMetodos r
        JOIN Metodos m ON r.MetodoId = m.MetodoId
    """

    params = []
    condiciones = []
    if resultado_id:
        condiciones.append("r.ResultadoId = ?")
        params.append(resultado_id)
    if nombre_usuario:
        condiciones.append("r.NombreUsuario = ?")
        params.append(nombre_usuario)
    if fecha:
        condiciones.append("CONVERT(date, r.Fecha) = ?")
        params.append(fecha)
    if nombre_metodo:
        condiciones.append("m.Nombre = ?")
        params.append(nombre_metodo)
    if condiciones:
        sql += " WHERE " + " AND ".join(condiciones)

    sql += " ORDER BY r.Fecha ASC"

    cursor.execute(sql, params)
    filas = cursor.fetchall()
    conn.close()

    if not filas:
        return None

    pdf = PDFReport(logo_path=logo_path)
    fila = filas[0]

    pdf.add_page()
  

    pdf.set_text_color(0)
    pdf.set_font("Arial", '', 12)
    info_lines = [
        f"Usuario: {fila.NombreUsuario}",
        f"Método: {fila.Metodo}",
        f"Fecha: {fila.Fecha.strftime('%Y-%m-%d')}",
        f"Función: f(x) = {fila.Funcion}"
    ]

    y_start = pdf.get_y() + 10
    for i, line in enumerate(info_lines):
        pdf.set_xy(pdf.l_margin, y_start + (i * 8))
        pdf.cell(0, 8, line, ln=True, align='L')

    pdf.ln(4)

    headers = ["ID", "X0", "X1", "X2", "Resultado", "Iter.", "Error Rel."]
    widths  = [20, 25, 25, 25, 35, 25, 35]

    table_width = sum(widths)
    start_x = (pdf.w - table_width) / 2
    pdf.set_x(start_x)

    pdf.set_fill_color(75, 0, 125)
    pdf.set_text_color(255)
    pdf.set_font("Arial", 'B', 10)
    for i, h in enumerate(headers):
        pdf.cell(widths[i], 7, h, border=1, align='C', fill=True)
    pdf.ln()

    cur2 = conexiondb().cursor()
    cur2.execute(
        """
        SELECT Iteracion AS NumeroIteracion,
               X0,
               X1,
               X2,
               ErrorRelativo
          FROM IteracionesDetalle
         WHERE ResultadoId = ?
         ORDER BY Iteracion
        """, (fila.ID,)
    )
    detalle = cur2.fetchall()
    cur2.connection.close()

    pdf.set_text_color(0)
    pdf.set_font("Arial", '', 9)

    if detalle:
        primera = detalle[0]
        pdf.set_x(start_x)
        pdf.cell(widths[0], 6, str(fila.ID), border=1, align='C')
        pdf.cell(widths[1], 6, _fmt(fila.X0, 6), border=1, align='C')
        pdf.cell(widths[2], 6, _fmt(fila.X1, 6), border=1, align='C')
        pdf.cell(widths[3], 6, _fmt(fila.X2, 6), border=1, align='C')
        pdf.cell(widths[4], 6, _fmt(primera.X2, 8), border=1, align='C')
        pdf.cell(widths[5], 6, str(primera.NumeroIteracion), border=1, align='C')
        pdf.cell(widths[6], 6, _fmt(primera.ErrorRelativo, 8), border=1, align='C')
        pdf.ln()

        for it in detalle[1:]:
            pdf.set_x(start_x)
            pdf.cell(widths[0], 6, "", border=1, align='C')
            pdf.cell(widths[1], 6, _fmt(it.X0, 6), border=1, align='C')
            pdf.cell(widths[2], 6, _fmt(it.X1, 6), border=1, align='C')
            pdf.cell(widths[3], 6, _fmt(it.X2, 6), border=1, align='C')
            pdf.cell(widths[4], 6, _fmt(it.X2, 8), border=1, align='C')
            pdf.cell(widths[5], 6, str(it.NumeroIteracion), border=1, align='C')
            pdf.cell(widths[6], 6, _fmt(it.ErrorRelativo, 8), border=1, align='C')
            pdf.ln()
    else:
        pdf.set_x(start_x)
        pdf.cell(widths[0], 6, str(fila.ID), border=1, align='C')
        pdf.cell(widths[1], 6, _fmt(fila.X0, 6), border=1, align='C')
        pdf.cell(widths[2], 6, _fmt(fila.X1, 6), border=1, align='C')
        pdf.cell(widths[3], 6, _fmt(fila.X2, 6), border=1, align='C')
        pdf.cell(widths[4], 6, _fmt(fila.Resultado, 8), border=1, align='C')
        pdf.cell(widths[5], 6, str(fila.Iteraciones), border=1, align='C')
        pdf.cell(widths[6], 6, _fmt(fila.ErrorRelativo, 8), border=1, align='C')
        pdf.ln()

    pdf.ln(6)

    if fila.Grafica:
        graf_bytes = bytes(fila.Grafica)
        img = Image.open(BytesIO(graf_bytes))
        tmp_img_path = tempfile.NamedTemporaryFile(delete=False, suffix=".png").name
        img.save(tmp_img_path)

        w_img = pdf.w - pdf.l_margin - pdf.r_margin
        pdf.image(tmp_img_path, x=pdf.l_margin, w=w_img)
        os.remove(tmp_img_path)

    pdf_bytes = pdf.output(dest='S').encode('latin1')
    return BytesIO(pdf_bytes)

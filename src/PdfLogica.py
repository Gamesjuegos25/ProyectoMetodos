import pyodbc
from fpdf import FPDF
from src.conexion_sqlS import conexiondb
from io import BytesIO
from PIL import Image
import tempfile
import os

def _fmt(val, prec):
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
        if self.logo_path and os.path.exists(self.logo_path):
            logo_width = 25
            self.image(self.logo_path, x=self.w - self.r_margin - logo_width, y=10, w=logo_width)
        self.set_y(10)
        self.set_font("Arial", 'B', 16)
        self.set_text_color(0, 0, 0)
        self.cell(0, 15, "Reporte de Resultados", ln=True, align='C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(100, 100, 100)
        self.cell(0, 10, f'Página {self.page_no()}', align='C')


def Greporte(nombre_usuario=None, resultado_id=None, fecha=None, nombre_metodo=None,
             logo_path='static/img/Logo_mariano.png'):

    print("DEBUG: Parámetros recibidos")
    print(f"nombre_usuario={nombre_usuario}, resultado_id={resultado_id}, fecha={fecha}, nombre_metodo={nombre_metodo}")

    conn = conexiondb()
    cursor = conn.cursor()

    sql = """
        SELECT 
            r.ResultadoId AS ID,
            r.NombreUsuario,
            m.Nombre AS Metodo,
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
        condiciones.append("CAST(r.Fecha AS DATE) = ?")
        params.append(fecha)
    if nombre_metodo:
        condiciones.append("m.Nombre = ?")
        params.append(nombre_metodo)
    if condiciones:
        sql += " WHERE " + " AND ".join(condiciones)

    sql += " ORDER BY r.Fecha ASC"

    print("DEBUG: Consulta SQL que se ejecutará:")
    print(sql)
    print("DEBUG: Parámetros de la consulta:")
    print(params)

    cursor.execute(sql, params)
    filas = cursor.fetchall()
    conn.close()

    print(f"DEBUG: Número de filas obtenidas: {len(filas)}")
    if not filas:
        print("DEBUG: No se encontraron resultados con esos filtros.")
        return None

    pdf = PDFReport(logo_path=logo_path)

    for fila in filas:
        print(f"DEBUG: Procesando ResultadoId={fila.ID}, Usuario={fila.NombreUsuario}, Metodo={fila.Metodo}, Fecha={fila.Fecha}")

        pdf.add_page()
        pdf.set_text_color(0)
        pdf.set_font("Arial", '', 12)
        info_lines = [
            f"Usuario: {fila.NombreUsuario}",
            f"Método: {fila.Metodo}",
            f"Fecha: {fila.Fecha.strftime('%Y-%m-%d') if hasattr(fila.Fecha, 'strftime') else fila.Fecha}",
            f"Función: f(x) = {fila.Funcion}"
        ]

        y_start = pdf.get_y() + 10
        for i, line in enumerate(info_lines):
            pdf.set_xy(pdf.l_margin, y_start + (i * 8))
            pdf.cell(0, 8, line, ln=True, align='L')

        pdf.ln(4)

        metodo = fila.Metodo.lower()

        # Definir columnas según método
        if "newton" in metodo:
            headers = ["ID", "X0", "Resultado", "Iter.", "Error Rel."]
            widths = [20, 40, 40, 25, 40]
        elif "secante" in metodo:
            headers = ["ID", "X0", "X1", "Resultado", "Iter.", "Error Rel."]
            widths = [15, 25, 25, 35, 25, 35]
        else:  # Muller u otro
            headers = ["ID", "X0", "X1", "X2", "Resultado", "Iter.", "Error Rel."]
            widths = [20, 25, 25, 25, 35, 25, 35]

        table_width = sum(widths)
        start_x = (pdf.w - table_width) / 2
        pdf.set_x(start_x)

        pdf.set_fill_color(75, 0, 125)
        pdf.set_text_color(255)
        pdf.set_font("Arial", 'B', 10)
        for i, h in enumerate(headers):
            pdf.cell(widths[i], 7, h, border=1, align='C', fill=True)
        pdf.ln()

        # Cargar detalle de iteraciones
        cur2 = conexiondb().cursor()
        cur2.execute("""
            SELECT Iteracion AS NumeroIteracion, X0, X1, X2, ErrorRelativo
            FROM IteracionesDetalle
            WHERE ResultadoId = ?
            ORDER BY Iteracion
        """, (fila.ID,))
        detalle = cur2.fetchall()
        cur2.connection.close()

        print(f"DEBUG: Número de iteraciones detalle para ResultadoId={fila.ID}: {len(detalle)}")

        pdf.set_text_color(0)
        pdf.set_font("Arial", '', 9)

        if detalle:
            for i, it in enumerate(detalle):
                pdf.set_x(start_x)
                pdf.cell(widths[0], 6, str(fila.ID if i == 0 else ""), border=1, align='C')

                if "newton" in metodo:
                    pdf.cell(widths[1], 6, _fmt(it.X0, 6), border=1, align='C')
                    pdf.cell(widths[2], 6, _fmt(fila.Resultado, 8), border=1, align='C')
                    pdf.cell(widths[3], 6, str(it.NumeroIteracion), border=1, align='C')
                    pdf.cell(widths[4], 6, _fmt(it.ErrorRelativo, 8), border=1, align='C')

                elif "secante" in metodo:
                    pdf.cell(widths[1], 6, _fmt(it.X0, 6), border=1, align='C')
                    pdf.cell(widths[2], 6, _fmt(it.X1, 6), border=1, align='C')
                    pdf.cell(widths[3], 6, _fmt(fila.Resultado, 8), border=1, align='C')
                    pdf.cell(widths[4], 6, str(it.NumeroIteracion), border=1, align='C')
                    pdf.cell(widths[5], 6, _fmt(it.ErrorRelativo, 8), border=1, align='C')

                else:  # Muller u otro
                    pdf.cell(widths[1], 6, _fmt(it.X0, 6), border=1, align='C')
                    pdf.cell(widths[2], 6, _fmt(it.X1, 6), border=1, align='C')
                    pdf.cell(widths[3], 6, _fmt(it.X2, 6), border=1, align='C')
                    pdf.cell(widths[4], 6, _fmt(fila.Resultado, 8), border=1, align='C')
                    pdf.cell(widths[5], 6, str(it.NumeroIteracion), border=1, align='C')
                    pdf.cell(widths[6], 6, _fmt(it.ErrorRelativo, 8), border=1, align='C')
                pdf.ln()
        else:
            # Fila sin detalle
            pdf.set_x(start_x)
            row = []
            if "newton" in metodo:
                row = [
                    str(fila.ID),
                    _fmt(fila.X0, 6),
                    _fmt(fila.Resultado, 8),
                    str(fila.Iteraciones),
                    _fmt(fila.ErrorRelativo, 8)
                ]
            elif "secante" in metodo:
                row = [
                    str(fila.ID),
                    _fmt(fila.X0, 6),
                    _fmt(fila.X1, 6),
                    _fmt(fila.Resultado, 8),
                    str(fila.Iteraciones),
                    _fmt(fila.ErrorRelativo, 8)
                ]
            else:  # Muller u otro
                row = [
                    str(fila.ID),
                    _fmt(fila.X0, 6),
                    _fmt(fila.X1, 6),
                    _fmt(fila.X2, 6),
                    _fmt(fila.Resultado, 8),
                    str(fila.Iteraciones),
                    _fmt(fila.ErrorRelativo, 8)
                ]

            for i in range(len(headers)):
                pdf.cell(widths[i], 6, row[i] if i < len(row) else "", border=1, align='C')
            pdf.ln()

        pdf.ln(6)

        # Insertar imagen si existe
        if fila.Grafica:
            try:
                img_data = fila.Grafica
                print("DEBUG: Tamaño de la imagen (bytes):", len(img_data))
                image = Image.open(BytesIO(img_data))
                with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmpfile:
                    temp_img_path = tmpfile.name
                    image.save(temp_img_path)
                    pdf.image(temp_img_path, x=(pdf.w - 150)/2, w=150)
                os.unlink(temp_img_path)
            except Exception as e:
                print("ERROR: No se pudo insertar la imagen en el PDF:", e)

    pdf_bytes = pdf.output(dest='S').encode('latin1')
    return BytesIO(pdf_bytes)

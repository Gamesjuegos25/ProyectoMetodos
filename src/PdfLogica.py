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

    conn = conexiondb()
    cursor = conn.cursor()

    sql = """
        SELECT 
            r.ResultadoId AS ID,
            r.NombreUsuario,
            m.Nombre AS Metodo,
            r.Funcion,
            r.X0, r.X1, r.X2,
            r.Resultado,
            r.Iteraciones,
            r.ErrorRelativo,
            r.Fecha,
            r.Grafica,
            r.ValorX, r.ValorY, r.ValorZ
        FROM ResultadosMetodos r
        JOIN Metodos m ON r.MetodoId = m.MetodoId
    """
    condiciones = []
    params = []

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
        condiciones.append("LOWER(m.Nombre) = LOWER(?)")
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

    for fila in filas:
        pdf.add_page()
        pdf.set_text_color(0)
        pdf.set_font("Arial", '', 12)

        # Información general
        info = [
            f"Usuario: {fila.NombreUsuario}",
            f"Método: {fila.Metodo}",
            f"Fecha: {fila.Fecha.strftime('%Y-%m-%d') if hasattr(fila.Fecha, 'strftime') else fila.Fecha}",
            f"Función: f(x) = {fila.Funcion}"
        ]
        for line in info:
            pdf.cell(0, 8, line, ln=True)
        pdf.ln(4)

        metodo = fila.Metodo.lower()

        if "gauss-jordan" in metodo:
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 10, "Solución:", ln=True)

            solucion_str = f"X = {_fmt(fila.ValorX, 8)}, Y = {_fmt(fila.ValorY, 8)}, Z = {_fmt(fila.ValorZ, 8)}"
            pdf.set_font("Arial", '', 11)
            pdf.set_fill_color(255, 255, 255)
            pdf.set_text_color(0)
            pdf.multi_cell(0, 8, solucion_str, border=0, align='C', fill=True)
            pdf.ln(6)

            headers = ["Fila", "X", "Y", "Z"]
            widths = [25, 40, 40, 40]
            start_x = (pdf.w - sum(widths)) / 2
            pdf.set_x(start_x)

            pdf.set_fill_color(75, 0, 125)
            pdf.set_text_color(255)
            pdf.set_font("Arial", 'B', 10)
            for i, h in enumerate(headers):
                pdf.cell(widths[i], 7, h, border=1, align='C', fill=True)
            pdf.ln()

            cur2 = conexiondb().cursor()
            cur2.execute("""
                SELECT Iteracion, X0, X1, X2
                FROM IteracionesDetalle
                WHERE ResultadoId = ?
                ORDER BY Iteracion
            """, (fila.ID,))
            detalle = cur2.fetchall()
            cur2.connection.close()

            pdf.set_text_color(0)
            pdf.set_font("Arial", '', 9)
            for it in detalle:
                pdf.set_x(start_x)
                pdf.cell(widths[0], 6, str(it.Iteracion), border=1, align='C')
                pdf.cell(widths[1], 6, _fmt(it.X0, 6), border=1, align='C')
                pdf.cell(widths[2], 6, _fmt(it.X1, 6), border=1, align='C')
                pdf.cell(widths[3], 6, _fmt(it.X2, 6), border=1, align='C')
                pdf.ln()
            pdf.ln(10)

        else:
            if "newton" in metodo:
                headers = ["ID", "X0", "Resultado", "Iter.", "Error Rel."]
                widths = [20, 40, 40, 25, 40]
            elif "secante" in metodo:
                headers = ["ID", "X0", "X1", "Resultado", "Iter.", "Error Rel."]
                widths = [15, 25, 25, 35, 25, 35]
            else:
                headers = ["ID", "X0", "X1", "X2", "Resultado", "Iter.", "Error Rel."]
                widths = [20, 25, 25, 25, 35, 25, 35]

            start_x = (pdf.w - sum(widths)) / 2
            pdf.set_x(start_x)

            pdf.set_fill_color(75, 0, 125)
            pdf.set_text_color(255)
            pdf.set_font("Arial", 'B', 10)
            for i, h in enumerate(headers):
                pdf.cell(widths[i], 7, h, border=1, align='C', fill=True)
            pdf.ln()

            cur2 = conexiondb().cursor()
            cur2.execute("""
                SELECT Iteracion, X0, X1, X2, ErrorRelativo
                FROM IteracionesDetalle
                WHERE ResultadoId = ?
                ORDER BY Iteracion
            """, (fila.ID,))
            detalle = cur2.fetchall()
            cur2.connection.close()

            pdf.set_text_color(0)
            pdf.set_font("Arial", '', 9)
            for i, it in enumerate(detalle):
                pdf.set_x(start_x)
                pdf.cell(widths[0], 6, str(fila.ID if i == 0 else ""), border=1, align='C')

                if "newton" in metodo:
                    fila_datos = [it.X0, fila.Resultado, it.Iteracion, it.ErrorRelativo]
                elif "secante" in metodo:
                    fila_datos = [it.X0, it.X1, fila.Resultado, it.Iteracion, it.ErrorRelativo]
                else:
                    fila_datos = [it.X0, it.X1, it.X2, fila.Resultado, it.Iteracion, it.ErrorRelativo]

                for j, val in enumerate(fila_datos):
                    pdf.cell(widths[j + 1], 6, _fmt(val, 6), border=1, align='C')
                pdf.ln()
            pdf.ln(10)

        # Agregar imagen
        if fila.Grafica:
            try:
                pdf.ln(8)
                imgdata = BytesIO(fila.Grafica)
                img = Image.open(imgdata)
                with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmpfile:
                    img.save(tmpfile.name, format="PNG")
                    img_width = pdf.w * 0.65
                    pdf.image(tmpfile.name, w=img_width, x=(pdf.w - img_width) / 2)
                    os.unlink(tmpfile.name)
            except Exception as e:
                print(f"Error al procesar imagen: {e}")

        pdf.ln(15)

    output = BytesIO()
    pdf.output(output)
    output.seek(0)
    return output

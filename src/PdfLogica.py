import pyodbc
from fpdf import FPDF
from src.conexion_sqlS import conexiondb
from io import BytesIO
from PIL import Image
import tempfile
import os

def Greporte(nombre_usuario=None, resultado_id=None, fecha=None, nombre_metodo=None):
    conn = conexiondb()
    cursor = conn.cursor()

    sql = """
        SELECT 
        r.ResultadoId,
        r.NombreUsuario,
        r.Funcion,
        r.X0,
        r.X1,
        r.X2,
        r.Resultado,
        r.Iteraciones,
        r.ErrorRelativo,
        r.Fecha,
        m.Nombre AS Metodo,
        r.Grafica
    FROM ResultadosMetodos r
    JOIN Usuarios u ON r.NombreUsuario = u.NombreUsuario
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

    if condiciones:
        sql += " WHERE " + " AND ".join(condiciones)

    sql += " ORDER BY r.Fecha ASC"

    cursor.execute(sql, params)
    datos = cursor.fetchall()

    if not datos:
        conn.close()
        return None

    pdf = FPDF()
    encabezados = ["ID", "Método", "Función", "X0", "X1", "X2", "Resultado", "Iter.", "Error Relativo"]

    def formatear_valor(fila, idx):
        if idx == 0:
            return str(fila.ResultadoId)
        elif idx == 1:
            return fila.Metodo if fila.Metodo else ""
        elif idx == 2:
            return fila.Funcion if fila.Funcion else ""
        elif idx == 3:
            return f"{fila.X0:.4f}" if fila.X0 is not None else ""
        elif idx == 4:
            return f"{fila.X1:.4f}" if fila.X1 is not None else ""
        elif idx == 5:
            return f"{fila.X2:.4f}" if fila.X2 is not None else ""
        elif idx == 6:
            return f"{fila.Resultado:.6f}" if fila.Resultado is not None else ""
        elif idx == 7:
            return str(fila.Iteraciones)
        elif idx == 8:
            return f"{fila.ErrorRelativo:.8f}" if fila.ErrorRelativo is not None else ""
        return ""

    for fila in datos:
        pdf.add_page()
        pdf.set_font("Arial", 'B', 14)
        titulo = f"Reporte de Resultados - Usuario: {fila.NombreUsuario or 'N/A'}"
        pdf.cell(0, 12, titulo, ln=True, align='C')
        pdf.ln(5)

        # Tabla encabezados
        pdf.set_font("Arial", 'B', 11)
        pdf.set_fill_color(220, 220, 220)
        col_widths = [12, 30, 30, 15, 15, 15, 28, 15, 35]
        for i, encabezado in enumerate(encabezados):
            pdf.cell(col_widths[i], 10, encabezado, border=1, align='C', fill=True)
        pdf.ln()

        # Fila de datos
        pdf.set_font("Arial", '', 10)
        pdf.set_fill_color(245, 245, 245)
        for i in range(len(encabezados)):
            valor = formatear_valor(fila, i)
            if i == 2 and len(valor) > 45:
                valor = valor[:42] + "..."
            pdf.cell(col_widths[i], 9, valor, border=1, fill=True)
        pdf.ln(15)

        # Si hay gráfica, agregarla centrada y con buen ancho
        if fila.Grafica:
            grafica_bytes = bytes(fila.Grafica)
            try:
                img = Image.open(BytesIO(grafica_bytes))
                img_buffer = BytesIO()
                img.save(img_buffer, format='PNG')
                img_buffer.seek(0)

                with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_img_file:
                    tmp_img_file.write(img_buffer.read())
                    tmp_img_file.flush()
                    temp_filename = tmp_img_file.name

                max_width = pdf.w - 40
                x_pos = (pdf.w - max_width) / 2
                pdf.image(temp_filename, x=x_pos, w=max_width)
                pdf.ln(10)

                os.remove(temp_filename)
            except Exception:
                pass

    conn.close()

    pdf_bytes = bytes(pdf.output(dest='S'))
    pdf_buffer = BytesIO(pdf_bytes)
    pdf_buffer.seek(0)
    return pdf_buffer

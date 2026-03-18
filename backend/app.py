from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS
from db import get_connection
import os
from docxtpl import DocxTemplate
from flask import send_file
from io import BytesIO
from datetime import datetime, timedelta

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

app = Flask(
    __name__,
    static_folder=os.path.join(BASE_DIR, "frontend"),
    static_url_path=""
)

CORS(app)


# SERVIR FRONTEND

@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


# REGISTRAR BENEFICIARIO
@app.route("/api/beneficiarios", methods=["POST"])
def registrar_beneficiario():
    data = request.json
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO beneficiarios
    (ci,nombre,cite,nudecud,tipo_codigo,fecha_inicio,carga_horaria,periodo_meses,telefono)
    VALUES (?,?,?,?,?,?,?,?,?)
    """,(

        data["ci"],
        data["nombre"],
        data["cite"],
        data["nudecud"],
        data["tipo_codigo"],
        data["fecha_inicio"],
        data["carga_horaria"],
        data["periodo_meses"],
        data["telefono"]

    ))
    conn.commit()
    conn.close()

    return jsonify({"mensaje":"registrado"})


# LISTAR BENEFICIARIOS
@app.route("/api/beneficiarios", methods=["GET"])
def obtener_beneficiarios():

    conn = get_connection()
    cursor = conn.cursor()
    query = """
    SELECT 
        ci,
        nombre,
        carga_horaria,
        fecha_inicio,
        periodo_meses
    FROM beneficiarios
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    beneficiarios = []
    for r in rows:
        fecha_inicio = datetime.strptime(r["fecha_inicio"], "%Y-%m-%d")
        fecha_fin = fecha_inicio + timedelta(days=30 * r["periodo_meses"])
        hoy = datetime.now()
        semanas_restantes = int((fecha_fin - hoy).days / 7)
        beneficiarios.append({
            "ci": r["ci"],
            "nombre": r["nombre"],
            "carga": r["carga_horaria"],
            "inicio": r["fecha_inicio"],
            "periodo": r["periodo_meses"],
            "semanas_restantes": semanas_restantes
        })
    conn.close()
    return jsonify(beneficiarios)


#Cronograma Actividades
@app.route("/api/cronograma", methods=["POST"])
def registrar_actividad():

    data=request.json

    conn=get_connection()
    cursor=conn.cursor()

    cursor.execute("""
    INSERT INTO actividades_mensuales
    (fecha,descripcion)
    VALUES (?,?)
    """,(data["fecha"],data["descripcion"]))

    conn.commit()
    conn.close()

    return jsonify({"ok":True})


# Obtener cronograma
@app.route("/api/cronograma/<anio>/<mes>")
def obtener_cronograma(anio,mes):
    conn=get_connection()
    cursor=conn.cursor()
    cursor.execute("""
    SELECT *
    FROM actividades_mensuales
    WHERE strftime('%Y',fecha)=?
    AND strftime('%m',fecha)=?
    ORDER BY fecha
    """,(anio,mes.zfill(2)))
    data=[dict(r) for r in cursor.fetchall()]
    conn.close()
    return jsonify(data)


# Obtener actividad 
@app.route("/api/actividad_hoy")
def actividad_hoy():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT descripcion
    FROM actividades_mensuales
    WHERE fecha = DATE('now')
    """)
    r = cursor.fetchone()
    conn.close()
    if r:
        return jsonify({"actividad": r["descripcion"]})
    else:
        return jsonify({"actividad": "Sin actividad registrada para hoy"})
    


# Guardar asistencia
@app.route("/api/registrar_asistencia", methods=["POST"])
def registrar_asistencia():

    registros = request.json

    conn = get_connection()
    cursor = conn.cursor()

    for r in registros:
        ci = r["ci"]
        fecha = r["fecha"]
        dia = r["dia"]

        cursor.execute("""
        SELECT id FROM asistencias
        WHERE ci = ? AND fecha = ? AND dia = ?
        """,(ci,fecha,dia))

        existe = cursor.fetchone()

        if existe:
            # Si ya existe, no registrar de nuevo
            continue

        hora_inicio = datetime.strptime(r["hora_ingreso"], "%H:%M")
        hora_fin = datetime.strptime(r["hora_salida"], "%H:%M")
        horas = (hora_fin - hora_inicio).seconds / 3600

        cursor.execute("""
        INSERT INTO asistencias
        (ci,fecha,dia,hora_ingreso,hora_salida,horas)
        VALUES (?,?,?,?,?,?)
        """,(
        ci,
        fecha,
        dia,
        r["hora_ingreso"],
        r["hora_salida"],
        horas

        ))

    conn.commit()
    conn.close()

    return jsonify({"mensaje":"ok"})


# Cargar cronograma lista
@app.route("/api/cronograma_lista")
def cronograma_lista():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT fecha, descripcion
    FROM actividades_mensuales
    ORDER BY fecha DESC
    """)
    data=[dict(r) for r in cursor.fetchall()]
    conn.close()
    return jsonify(data)


#Cargar historial de asistencias
@app.route("/api/cronograma/<anio>/<mes>")
def cronograma_mes(anio, mes):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT fecha, descripcion
    FROM cronograma
    WHERE strftime('%Y', fecha)=?
    AND strftime('%m', fecha)=?
    """,(anio, mes.zfill(2)))
    datos = cursor.fetchall()
    conn.close()
    resultado=[]
    for d in datos:
        resultado.append({
        "fecha":d[0],
        "descripcion":d[1]
        })
    return jsonify(resultado)


# Cargar tabla de historial de asistencias
@app.route("/api/asistencia_historial/<fecha>")
def asistencia_historial(fecha):

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT 
    b.ci,
    b.nombre,
    b.carga_horaria,
    a.fecha,
    a.hora_ingreso,
    a.hora_salida,
    a.horas
    FROM asistencias a
    JOIN beneficiarios b
    ON a.ci = b.ci
    WHERE a.fecha = ?
    """,(fecha,))
    datos = cursor.fetchall()
    conn.close()
    resultado=[]

    for d in datos:

        resultado.append({
        "ci":d[0],
        "nombre":d[1],
        "carga":d[2],
        "fecha":d[3],
        "hora_ingreso":d[4],
        "hora_salida":d[5],
        "horas":d[6]

        })

    return jsonify(resultado)


# Beneficiario View
@app.route("/api/beneficiario/<ci>")
def obtener_beneficiario(ci):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT ci,nombre,telefono,cite,nudecud,tipo_codigo,
           fecha_inicio,carga_horaria,periodo_meses
    FROM beneficiarios
    WHERE ci = ?
    """,(ci,))
    b = cursor.fetchone()
    conn.close()
    if not b:
        return jsonify({})
    return jsonify({
        "ci":b[0],
        "nombre":b[1],
        "telefono":b[2],
        "cite":b[3],
        "codigo":b[4],
        "tipo":b[5],
        "fecha_inicio":b[6],
        "carga":b[7],
        "periodo":b[8]
    })


# Historial de beneficiarios
@app.route("/api/historial_beneficiario/<ci>")
def historial_beneficiario(ci):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT a.fecha, c.descripcion
    FROM asistencias a
    JOIN actividades_mensuales c ON a.fecha = c.fecha
    WHERE a.ci = ?
    ORDER BY a.fecha
    """,(ci,))
    datos = cursor.fetchall()
    conn.close()
    resultado=[]

    for d in datos:
        resultado.append({
        "fecha":d[0],
        "actividad":d[1]
        })

    return jsonify(resultado)


# Generar imforme
@app.route("/api/generar_informe/<ci>/<anio>/<mes>")
def generar_informe(ci, anio, mes):

    conn = get_connection()
    cursor = conn.cursor()
    # 🔹 1. Datos beneficiario
    cursor.execute("""
    SELECT nombre, ci, carga_horaria, fecha_inicio
    FROM beneficiarios
    WHERE ci = ?
    """,(ci,))
    b = cursor.fetchone()
    # 🔹 2. Asistencias del mes
    cursor.execute("""
    SELECT a.fecha, c.descripcion
    FROM asistencias a
    LEFT JOIN actividades_mensuales c ON a.fecha = c.fecha
    WHERE a.ci = ?
    AND strftime('%Y', a.fecha) = ?
    AND strftime('%m', a.fecha) = ?
    """,(ci, anio, mes.zfill(2)))
    asistencias = cursor.fetchall()
    conn.close()
    # 🔹 3. Formatear fechas
    def fecha_literal(f):
        meses = ["enero","febrero","marzo","abril","mayo","junio",
                 "julio","agosto","septiembre","octubre","noviembre","diciembre"]

        fecha = datetime.strptime(f, "%Y-%m-%d")
        return f"{fecha.day} de {meses[fecha.month-1]} de {fecha.year}"
    
    def mes_literal(mes):
        meses = ["enero","febrero","marzo","abril","mayo","junio",
                "julio","agosto","septiembre","octubre","noviembre","diciembre"]
        return meses[int(mes)-1]

    def fecha_completa_literal(f):
        dias = ["lunes","martes","miércoles","jueves","viernes","sábado","domingo"]
        meses = ["enero","febrero","marzo","abril","mayo","junio",
                "julio","agosto","septiembre","octubre","noviembre","diciembre"]

        fecha = datetime.strptime(f, "%Y-%m-%d")
        dia_semana = dias[fecha.weekday()]
        
        return f"{dia_semana} {fecha.day:02d} de {meses[fecha.month-1]} de {fecha.year}"
    from docx import Document

    def limpiar_parrafos_vacios(ruta_docx):
        doc = Document(ruta_docx)

        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    paragraphs = cell.paragraphs
                    for p in paragraphs:
                        if not p.text.strip():
                            p._element.getparent().remove(p._element)

        doc.save(ruta_docx)


    lista = []
    for a in asistencias:
        lista.append({
            "fecha": fecha_literal(a[0]),
            "actividad": a[1] if a[1] else "Actividad",
            "asistencia": "SI"  # porque si existe registro, asistió
        })
    # 🔹 4. Cargar plantilla
    doc = DocxTemplate("../templates_word/INF. MENSUAL PLANTILLA.docx")
    nombre = b[0]

    mes_texto = mes_literal(mes)

    mes_anio_minus = f"{mes_texto} de {anio}"
    mes_anio_mayus_bold = f"{mes_texto.upper()} DE {anio}"

    nombre_titulo = nombre.title()
    nombre_mayus = nombre.upper()

    fecha_inicio_literal = fecha_completa_literal(b[3])

    # 🔹 ejemplo de periodo (puedes ajustarlo luego)
    if asistencias:
        fecha_inicio_periodo = asistencias[0][0]
        fecha_fin_periodo = asistencias[-1][0]

        periodo_literal = f"{fecha_completa_literal(fecha_inicio_periodo)} hasta el {fecha_completa_literal(fecha_fin_periodo)}"
    else:
        periodo_literal = "No registrado"

    context = {
        "nombre": nombre,
        "ci": b[1],
        "carga_horaria": b[2],

        # NUEVOS
        "mes_anio_mayus_bold": mes_anio_mayus_bold,
        "mes_anio_minus": mes_anio_minus,
        "nombre_titulo": nombre_titulo,
        "nombre_mayus": nombre_mayus,
        "fecha_inicio": fecha_inicio_literal,
        "periodo_literal": periodo_literal,

        "asistencias": lista,
        "mes": mes,
        "anio": anio
    }

    doc.render(context)
    # 🔹 5. Guardar en memoria (no archivo físico)
    file_stream = BytesIO()
    doc.save(file_stream)
    limpiar_parrafos_vacios(file_stream)
    file_stream.seek(0)
    return send_file(
        file_stream,
        as_attachment=True,
        download_name=f"informe_{ci}_{anio}_{mes}.docx",
        mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )


# EJECUTAR APP
if __name__ == "__main__":
    app.run(debug=True)
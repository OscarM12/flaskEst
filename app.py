from flask import Flask, request, jsonify, render_template, send_file
import mysql.connector
import xml.etree.ElementTree as ET
from xml.dom.minidom import parseString
from xml.sax.saxutils import escape  # Para manejar caracteres especiales
import io  # Para manejar descargas de archivos

app = Flask(__name__)

# Configuración de la base de datos
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Morenoram12',
    'database': 'gestion_estudiantes'
}

def get_db_connection():
    return mysql.connector.connect(**db_config)

@app.route('/')
def index():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        query = "SELECT id, nombre, edad, curso FROM estudiantes"
        cursor.execute(query)
        estudiantes = cursor.fetchall()
        return render_template('index.html', estudiantes=estudiantes)
    except mysql.connector.Error as err:
        return f"Error: {str(err)}"
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

@app.route('/guardar', methods=['POST'])
def guardar_estudiante():
    data = request.json
    
    # Validación de campos
    if not all(key in data for key in ('nombre', 'edad', 'curso')):
        return jsonify({'error': 'Faltan campos en los datos enviados'}), 400
    
    # Validación de campos vacíos
    if not data['nombre'] or not data['edad'] or not data['curso']:
        return jsonify({'error': 'Todos los campos deben estar completos'}), 400

    # Generación del XML con escape de caracteres especiales
    estudiante = ET.Element('estudiante')
    ET.SubElement(estudiante, 'nombre').text = escape(data['nombre'])  # Escapar caracteres especiales
    ET.SubElement(estudiante, 'edad').text = str(data['edad'])
    ET.SubElement(estudiante, 'curso').text = escape(data['curso'])  # Escapar caracteres especiales
    
    xml_data = parseString(ET.tostring(estudiante, encoding='unicode')).toprettyxml()

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = """
            INSERT INTO estudiantes (nombre, edad, curso, xml_data)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(query, (data['nombre'], data['edad'], data['curso'], xml_data))
        conn.commit()
        return jsonify({'message': 'Estudiante guardado exitosamente'}), 200
    except mysql.connector.Error as err:
        return jsonify({'error': str(err)}), 500
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

@app.route('/ver_xml/<int:estudiante_id>', methods=['GET'])
def ver_xml(estudiante_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        query = "SELECT xml_data FROM estudiantes WHERE id = %s"
        cursor.execute(query, (estudiante_id,))
        estudiante = cursor.fetchone()
        if estudiante:
            return jsonify({'xml_data': estudiante['xml_data']}), 200
        else:
            return jsonify({'error': 'Estudiante no encontrado'}), 404
    except mysql.connector.Error as err:
        return jsonify({'error': str(err)}), 500
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

@app.route('/eliminar/<int:estudiante_id>', methods=['DELETE'])
def eliminar_estudiante(estudiante_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # Eliminar el estudiante de la base de datos por su ID
        query = "DELETE FROM estudiantes WHERE id = %s"
        cursor.execute(query, (estudiante_id,))
        conn.commit()
        
        if cursor.rowcount == 0:
            return jsonify({'error': 'Estudiante no encontrado'}), 404
        
        return jsonify({'message': 'Estudiante eliminado exitosamente'}), 200
    except mysql.connector.Error as err:
        return jsonify({'error': str(err)}), 500
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

@app.route('/actualizar/<int:estudiante_id>', methods=['PUT'])
def actualizar_estudiante(estudiante_id):
    data = request.json
    if not all(key in data for key in ('nombre', 'edad', 'curso')):
        return jsonify({'error': 'Faltan campos en los datos enviados'}), 400

    # Actualizamos el estudiante en la base de datos
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = """
            UPDATE estudiantes
            SET nombre = %s, edad = %s, curso = %s
            WHERE id = %s
        """
        cursor.execute(query, (data['nombre'], data['edad'], data['curso'], estudiante_id))
        conn.commit()

        # Crear el XML actualizado
        estudiante = ET.Element('estudiante')
        ET.SubElement(estudiante, 'id').text = str(estudiante_id)
        ET.SubElement(estudiante, 'nombre').text = escape(data['nombre'])  # Escapar caracteres especiales
        ET.SubElement(estudiante, 'edad').text = str(data['edad'])
        ET.SubElement(estudiante, 'curso').text = escape(data['curso'])  # Escapar caracteres especiales
        xml_data = parseString(ET.tostring(estudiante, encoding='unicode')).toprettyxml()

        # Actualizar el campo xml_data en la base de datos
        query_xml = """
            UPDATE estudiantes
            SET xml_data = %s
            WHERE id = %s
        """
        cursor.execute(query_xml, (xml_data, estudiante_id))
        conn.commit()

        return jsonify({'message': 'Estudiante actualizado exitosamente'}), 200
    except mysql.connector.Error as err:
        return jsonify({'error': str(err)}), 500
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

@app.route('/descargar_xml/<int:estudiante_id>', methods=['GET'])
def descargar_xml(estudiante_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Modificamos la consulta para seleccionar todos los campos relevantes
        query = "SELECT id, nombre, edad, curso, xml_data FROM estudiantes WHERE id = %s"
        cursor.execute(query, (estudiante_id,))
        estudiante = cursor.fetchone()

        if estudiante:
            xml_data = estudiante['xml_data']
            nombre_estudiante = estudiante['nombre']
            edad_estudiante = estudiante['edad']
            curso_estudiante = estudiante['curso']

            if xml_data:  # Verifica si xml_data no está vacío
                # Prepara el archivo XML para la descarga
                nombre_archivo = f"{nombre_estudiante}_datos.xml"
                
                # Enviar el archivo XML como descarga
                return send_file(
                    io.BytesIO(xml_data.encode('utf-8')),  # Codifica el XML en UTF-8
                    as_attachment=True,
                    download_name=nombre_archivo,
                    mimetype='application/xml'
                )
            else:
                return jsonify({'error': 'El estudiante no tiene datos XML disponibles'}), 404
        else:
            return jsonify({'error': 'Estudiante no encontrado'}), 404

    except mysql.connector.Error as err:
        return jsonify({'error': str(err)}), 500
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()




if __name__ == '__main__':
    app.run(debug=True)

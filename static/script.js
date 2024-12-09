// Función para validar los datos del formulario
function validarFormulario() {
    const nombre = document.getElementById('nombre').value.trim();
    const edad = document.getElementById('edad').value.trim();
    const curso = document.getElementById('curso').value.trim();
 
    if (!nombre || !edad || !curso) {
        alert('Por favor, completa todos los campos.');
        return false;
    }
    if (isNaN(edad) || edad <= 0) {
        alert('La edad debe ser un número positivo.');
        return false;
    }
    return true;
}
 
// Función para manejar la edición de un estudiante
function modificarEstudiante(id, nombre, edad, curso) {
    document.getElementById('hidden-id').value = id; // ID oculto para editar
    document.getElementById('nombre').value = nombre;
    document.getElementById('edad').value = edad;
    document.getElementById('curso').value = curso;
 
    document.getElementById('accept-btn').style.display = 'block'; // Mostrar botón "Aceptar Cambios"
    document.getElementById('save-btn').style.display = 'none'; // Ocultar botón "Guardar"
}
 
// Función para manejar la eliminación de un estudiante
function eliminarEstudiante(id, row) {
    fetch(`/eliminar/${id}`, { method: 'DELETE' })
        .then(response => response.json())
        .then(data => {
            if (data.message) {
                alert(data.message);
                row.remove();
            } else {
                alert(data.error || 'Error al eliminar estudiante');
            }
        })
        .catch(error => console.error('Error:', error));
}
 
// Función para abrir el modal y mostrar el XML
function verXML(estudianteId) {
    fetch(`/ver_xml/${estudianteId}`)
        .then(response => response.json())
        .then(data => {
            if (data.xml_data) {
                const modal = document.getElementById('xml-modal');
                const modalContent = document.getElementById('xml-content');
                modalContent.textContent = data.xml_data;
                modal.style.display = 'block';
            } else {
                alert('Error: No se pudo obtener el XML');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Ocurrió un error al obtener el XML');
        });
}
 
// Función para cerrar el modal
function cerrarXML() {
    document.getElementById('xml-modal').style.display = 'none';
}
 
// Función para descargar el XML
function descargarXML(estudianteId) {
    window.location.href = `/descargar_xml/${estudianteId}`;
}
 
// Función para manejar el envío del formulario
document.getElementById('student-form').addEventListener('submit', function (event) {
    event.preventDefault();
 
    if (!validarFormulario()) return;
 
    const id = document.getElementById('hidden-id').value; // Obtener el ID del campo oculto
    const nombre = document.getElementById('nombre').value;
    const edad = document.getElementById('edad').value;
    const curso = document.getElementById('curso').value;
 
    const studentData = { nombre, edad, curso };
 
    // Determinar si es un nuevo registro o una actualización
    const url = id ? `/actualizar/${id}` : '/guardar';
    const method = id ? 'PUT' : 'POST';
 
    fetch(url, {
        method: method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(studentData)
    })
        .then(response => response.json())
        .then(data => {
            if (data.message) {
                alert(data.message);
 
                if (id) {
                    // Actualizar la fila en la tabla
                    const updatedStudent = data.data; // Datos del estudiante actualizado
                    const row = document.getElementById(`row-${id}`);
                    row.children[1].textContent = updatedStudent.nombre;
                    row.children[2].textContent = updatedStudent.edad;
                    row.children[3].textContent = updatedStudent.curso;
                } else {
                    // Agregar nueva fila si es un nuevo registro
                    actualizarTabla(studentData);
                }
 
                // Resetear formulario
                document.getElementById('student-form').reset();
                document.getElementById('accept-btn').style.display = 'none';
                document.getElementById('save-btn').style.display = 'block';
            } else {
                alert(data.error || 'Error al guardar el estudiante.');
            }
        })
        .catch(error => console.error('Error:', error));
});
 
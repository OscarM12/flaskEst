// Función para validar los datos del formulario
function validarFormulario() {
    
    const nombre = document.getElementById('nombre').value.trim();
    const edad = document.getElementById('edad').value.trim();
    const curso = document.getElementById('curso').value.trim();

    if (!id || !nombre || !edad || !curso) {
        alert('Por favor, completa todos los campos.');
        return false;
    }
    if (isNaN(edad) || edad <= 0) {
        alert('La edad debe ser un número positivo.');
        return false;
    }
    return true;
}

// Función para enviar los datos del formulario y guardar un estudiante
document.getElementById('student-form').addEventListener('submit', function (event) {
    event.preventDefault();

    if (!validarFormulario()) return;

    const id = document.getElementById('id').value;
    const nombre = document.getElementById('nombre').value;
    const edad = document.getElementById('edad').value;
    const curso = document.getElementById('curso').value;

    const studentData = { id, nombre, edad, curso };

    fetch('/guardar', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(studentData)
    })
        .then(response => response.json())
        .then(data => {
            if (data.message) {
                alert(data.message);
                actualizarTabla(studentData);
                document.getElementById('student-form').reset();
            } else {
                alert('Hubo un error al guardar el estudiante.');
            }
        })
        .catch(error => console.error('Error:', error));
});

// Función para agregar una fila a la tabla de estudiantes
function actualizarTabla(estudiante) {
    const tableBody = document.querySelector('#results-table tbody');
    const newRow = document.createElement('tr');
    newRow.id = `row-${estudiante.id}`;
    newRow.innerHTML = `
        <td>${estudiante.id}</td>
        <td>${estudiante.nombre}</td>
        <td>${estudiante.edad}</td>
        <td>${estudiante.curso}</td>
        <td class="actions">
            <button class="modify-btn" onclick="modificarEstudiante(${estudiante.id})">Modificar</button>
            <button class="delete-btn" onclick="eliminarEstudiante(${estudiante.id}, this)">Eliminar</button>
            <button class="view-xml-btn" onclick="verXML(${estudiante.id})">Ver XML</button>
        </td>
    `;
    tableBody.appendChild(newRow);
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

                // Crear el botón de descarga
                const downloadBtn = document.createElement('button');
                downloadBtn.textContent = 'Descargar XML';
                downloadBtn.classList.add('download-btn');
                downloadBtn.onclick = () => descargarXML(data.xml_data, estudianteId);

                // Agregar el botón de descarga al modal
                const modalFooter = document.getElementById('xml-modal-footer');
                modalFooter.innerHTML = '';  // Limpiar cualquier contenido previo
                modalFooter.appendChild(downloadBtn);

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

// Función para descargar el XML
function descargarXML(xmlData, estudianteId) {
    // Crear un blob con los datos XML
    const blob = new Blob([xmlData], { type: 'application/xml' });

    // Crear un enlace para la descarga
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `estudiante_${estudianteId}.xml`;  // El nombre del archivo será el ID del estudiante

    // Simular el clic en el enlace para descargar el archivo
    link.click();
}

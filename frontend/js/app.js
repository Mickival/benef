document.addEventListener("DOMContentLoaded", function () {

mostrarFecha();
cargarBeneficiarios();
cargarActividadDia();
cargarActividadesAsistencia();
cargarAnios();
cargarAniosHistorial()
cargarDatosBeneficiario()
cargarHistorialBeneficiario()

})


/* MOSTRAR FECHA */
function mostrarFecha(){
let cont = document.getElementById("fecha")
if(!cont) return
const hoy = new Date()
cont.innerText = hoy.toLocaleDateString("es-BO")
}


/* LISTAR BENEFICIARIOS (TABLA PRINCIPAL) */

async function cargarBeneficiarios(){

let tabla = document.getElementById("tabla_beneficiarios")

if(!tabla) return

let res = await fetch("/api/beneficiarios")
let data = await res.json()

tabla.innerHTML=""

data.forEach(b=>{

tabla.innerHTML += `
<tr>
<td>${b.ci}</td>
<td>
<span class="nombre_link" onclick="abrirBeneficiario('${b.ci}')">
${b.nombre}
</span>
</td>
<td>${b.carga}</td>
<td>${b.inicio}</td>
<td>${b.periodo} meses</td>
<td>${b.semanas_restantes}</td>
</tr>
`
})
}


function abrirBeneficiario(ci){
window.location = `beneficiario.html?ci=${ci}`
}
function obtenerCI(){
let params = new URLSearchParams(window.location.search)
return params.get("ci")
}

/* REGISTRAR BENEFICIARIO */
async function registrarBeneficiario(){

let data = {

ci: document.getElementById("ci").value,
nombre: document.getElementById("nombre").value,
telefono: document.getElementById("telefono").value,
cite: document.getElementById("cite").value,

tipo_codigo: document.getElementById("tipo_codigo").value,
nudecud: document.getElementById("codigo").value,

carga_horaria: document.getElementById("carga").value,
fecha_inicio: document.getElementById("fecha").value,
periodo_meses: document.getElementById("periodo").value

}

let res = await fetch("/api/beneficiarios",{

method:"POST",
headers:{ "Content-Type":"application/json"},
body:JSON.stringify(data)

})

await res.json()

alert("Beneficiario registrado")

window.location="index.html"

}


/* ACTIVIDAD DEL DIA */

async function cargarActividadDia(){

let cont = document.getElementById("actividad_dia_texto")

if(!cont) return

let res = await fetch("/api/actividad_hoy")

let data = await res.json()

cont.innerText = data.actividad

}


/* TABLA DE ASISTENCIA */

async function cargarTablaAsistencia(){

let tabla = document.getElementById("tabla_asistencia")

if(!tabla) return

let res = await fetch("/api/beneficiarios")
let data = await res.json()

tabla.innerHTML=""
data.forEach(b=>{
let selectorDia=""
if(b.carga == 16){
selectorDia = `
<select disabled>
<option>Sabado y Lunes</option>
</select>
`
}else{
selectorDia = `
<select>
<option>Sabado</option>
<option>Lunes</option>
</select>
`
}

tabla.innerHTML += `

<tr>
<td>
<input type="checkbox" class="checkAsistencia">
</td>
<td class="ci">${b.ci}</td>
<td>${b.nombre}</td>
<td>${b.carga}</td>
<td>${selectorDia}</td>
<td><input type="time" class="ingreso" disabled></td>
<td><input type="time" class="salida" disabled></td>
</tr>
`
})
activarCheckboxes()
}


/* GUARDAR ASISTENCIA */

async function guardarAsistencia(){

let filas = document.querySelectorAll("#tabla_asistencia tr")

let actividad = document.getElementById("actividad_dia").value

if(actividad == ""){

alert("Seleccione una actividad")

return

}

let registros=[]

filas.forEach(f=>{

let ci = f.children[1].innerText

let dia = f.children[4].querySelector("select").value

let ingreso = f.children[5].querySelector("input").value

let salida = f.children[6].querySelector("input").value

if(ingreso && salida){

registros.push({

ci:ci,
fecha:actividad,
dia:dia,
hora_ingreso:ingreso,
hora_salida:salida

})

}

})

if(registros.length==0){

alert("No hay asistencias para guardar")

return

}

let res = await fetch("/api/registrar_asistencia",{

method:"POST",
headers:{ "Content-Type":"application/json"},
body:JSON.stringify(registros)

})

let r = await res.json()

alert("Asistencia registrada correctamente")

}


/* CRONOGRAMA */

async function registrarActividad(){

if(!validarFecha()) return

let fecha = document.getElementById("fecha").value
let actividad = document.getElementById("actividad").value

await fetch("/api/cronograma",{

method:"POST",
headers:{ "Content-Type":"application/json"},
body:JSON.stringify({

fecha:fecha,
descripcion:actividad

})

})

cargarActividades()

}


/* CARGAR CRONOGRAMA */

async function cargarActividades(){

let tabla = document.getElementById("tabla_actividades")

if(!tabla) return

let mes = document.getElementById("mes").value
let anio = document.getElementById("anio").value
let res = await fetch(`/api/cronograma/${anio}/${mes}`)
let data = await res.json()
tabla.innerHTML=""
data.forEach(a=>{
tabla.innerHTML +=`

<tr>
<td>${a.fecha}</td>
<td>${a.descripcion}</td>
</tr>
`
})

}


/* ACTIVIDADES EN ASISTENCIA */

async function cargarActividadesAsistencia(){

let select = document.getElementById("actividad_dia")

if(!select) return

let res = await fetch("/api/cronograma_lista")

let data = await res.json()

select.innerHTML = '<option value="">Seleccione actividad</option>'

data.forEach(a=>{

let op = document.createElement("option")

op.value = a.fecha

op.textContent = a.fecha + " - " + a.descripcion

select.appendChild(op)

})

}


/* CAMBIAR ACTIVIDAD */

function cargarAsistencia(){
let actividad = document.getElementById("actividad_dia").value
if(actividad=="") return
cargarTablaAsistencia()
}


/* CARGAR AÑOS */

function cargarAnios(){
let select = document.getElementById("anio")
if(!select) return
let actual = new Date().getFullYear()
for(let i=actual-2;i<=actual+2;i++){
let op = document.createElement("option")
op.value=i
op.text=i
select.appendChild(op)
}
}


/* VALIDACION FECHA */

function validarFecha(){
let valor = document.getElementById("fecha").value
if(!valor){
alert("Seleccione una fecha")
return false
}
let partes = valor.split("-")
let anio = parseInt(partes[0])
let mes = parseInt(partes[1]) - 1
let diaMes = parseInt(partes[2])
let fecha = new Date(anio, mes, diaMes)
let mesSeleccionado = parseInt(document.getElementById("mes").value)
let anioSeleccionado = parseInt(document.getElementById("anio").value)
if((mes + 1) !== mesSeleccionado || anio !== anioSeleccionado){
alert("La fecha debe pertenecer al mes seleccionado")
return false
}
let dia = fecha.getDay()
if(dia !== 1 && dia !== 6){
alert("Solo se permiten lunes o sábados")
return false
}
return true
}


// Activador de checkbox
function activarCheckboxes(){
let checks = document.querySelectorAll(".checkAsistencia")
checks.forEach(check=>{
check.addEventListener("change",function(){
let fila = this.closest("tr")
let ingreso = fila.querySelector(".ingreso")
let salida = fila.querySelector(".salida")
if(this.checked){
ingreso.disabled = false
salida.disabled = false

ingreso.value = "08:00"
salida.value = "16:00"

}else{
ingreso.disabled = true
salida.disabled = true

ingreso.value = ""
salida.value = ""
}
})

})

}


// Cargar historial (años)
function cargarAniosHistorial(){

let select = document.getElementById("anio_historial")

if(!select) return

let actual = new Date().getFullYear()

select.innerHTML = '<option value="">Año</option>'

for(let i=actual-2;i<=actual+2;i++){

let op = document.createElement("option")

op.value = i
op.text = i

select.appendChild(op)

}

}


// Cargar historial (actividades)
async function cargarActividadesHistorial(){

let mes = document.getElementById("mes_historial").value
let anio = document.getElementById("anio_historial").value

if(!mes || !anio) return

let res = await fetch(`/api/cronograma/${anio}/${mes}`)
let data = await res.json()
let select = document.getElementById("actividad_historial")

select.innerHTML = '<option value="">Seleccione actividad</option>'

data.forEach(a=>{

let op=document.createElement("option")

op.value = a.fecha
op.text = a.fecha + " - " + a.descripcion

select.appendChild(op)
})
}

document.getElementById("mes_historial")?.addEventListener("change",cargarActividadesHistorial)
document.getElementById("anio_historial")?.addEventListener("change",cargarActividadesHistorial)



// Cargar historial
async function cargarHistorial(){
let fecha = document.getElementById("actividad_historial").value
if(!fecha) return
let res = await fetch(`/api/asistencia_historial/${fecha}`)
let data = await res.json()
let tabla = document.getElementById("tabla_historial")

tabla.innerHTML=""

data.forEach(b=>{

tabla.innerHTML +=`

<tr>

<td>${b.ci}</td>
<td>${b.nombre}</td>
<td>${b.carga}</td>
<td>${b.fecha}</td>
<td>${b.hora_ingreso}</td>
<td>${b.hora_salida}</td>
<td>${b.horas}</td>

</tr>
`
})
}

document.getElementById("actividad_historial")?.addEventListener("change",cargarHistorial)


// cargar datos beneficiario
async function cargarDatosBeneficiario(){
let ci = obtenerCI()
if(!ci) return
let res = await fetch(`/api/beneficiario/${ci}`)
let b = await res.json()
let cont = document.getElementById("datos_beneficiario")
if(!cont) return

cont.innerHTML = `
<p><b>CI:</b> ${b.ci}</p>
<p><b>Nombre:</b> ${b.nombre}</p>
<p><b>Teléfono:</b> ${b.telefono}</p>
<p><b>CITE:</b> ${b.cite}</p>
<p><b>${b.tipo}:</b> ${b.codigo}</p>
<p><b>Fecha inicio:</b> ${b.fecha_inicio}</p>
<p><b>Carga horaria:</b> ${b.carga}</p>
<p><b>Periodo:</b> ${b.periodo} meses</p>
`
}


// cargar historial del beneficiario
async function cargarHistorialBeneficiario(){
let ci = obtenerCI()
if(!ci) return
let res = await fetch(`/api/historial_beneficiario/${ci}`)
let data = await res.json()
let cont = document.getElementById("historial_beneficiario")
if(!cont) return
cont.innerHTML = ""
let grupos = {}
data.forEach(r=>{
let fecha = new Date(r.fecha)
let anio = fecha.getFullYear()
let mes = fecha.getMonth()+1
let clave = `${anio}-${mes}`
if(!grupos[clave]){
grupos[clave] = []
}
grupos[clave].push(r)
})
for(let clave in grupos){
let [anio, mes] = clave.split("-")
cont.innerHTML += `
<div style="display:flex; justify-content:space-between; align-items:center; gap:8px;">
<h3>${mes}/${anio}</h3>
<div style="display:flex; gap:8px;">
  <button onclick="generarInforme('${anio}','${mes}')">Generar Informe</button>
  <button onclick="generarPlanillaAsistencia('${anio}','${mes}')">Generar Planilla de Asistencia</button>
</div>
</div>
`
grupos[clave].forEach(r=>{
cont.innerHTML += `<p>• ${r.fecha} → ${r.actividad}</p>`
})
}
}


// Generar informe mensual
function generarInforme(anio, mes){
let ci = obtenerCI()
window.open(`/api/generar_informe/${ci}/${anio}/${mes}`, "_blank")
}


// Generar informe de conclusión de penitencia
function generarInformeConclusion(){
let ci = obtenerCI()
window.open(`/api/generar_informe_conclusion/${ci}`, "_blank")
}


// Generar planilla de asistencia mensual (pendiente de implementar)
function generarPlanillaAsistencia(anio, mes){
let ci = obtenerCI()
window.open(`/api/generar_planilla/${ci}/${anio}/${mes}`, "_blank")
}
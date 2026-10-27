let entidadSeleccionada = { sec_ejec: '301086', ejecutora_nombre: 'MUNICIPALIDAD PROVINCIAL DE JUNIN' };
let moduloActual = 'inicio';
let chartPrincipal = null;
let chartSecundario = null;

// Variables de Sesión para Control de Seguridad (DCL) - Sesión 6
let usuarioAutenticado = 'us_operador_lima';
let passwordAutenticado = 'OperadorMef2026!';

const CONFIG_MODULOS = {
    inicio: {
        titulo: "Dashboard General",
        subtitulo: "Resumen consolidado de la información financiera y proyectos del MEF",
        kpi1: { label: "INGRESOS TOTALES", sub: "<i class='fa-solid fa-arrow-trend-up mr-1'></i> Recaudación constante" },
        kpi2: { label: "GASTO SOCIAL", sub: "<i class='fa-solid fa-circle-check mr-1'></i> Devengado verificado" },
        kpi3: { label: "TRANSFERENCIAS", sub: "<i class='fa-solid fa-clock-history mr-1'></i> Fondos acreditados" },
        kpi4: { label: "PROYECTOS", sub: "<i class='fa-solid fa-bolt mr-1'></i> Inversión pública activa" },
        chartTitle1: "<i class='fa-solid fa-chart-column text-sky-500'></i> Evolución General del Periodo",
        chartTitle2: "<i class='fa-solid fa-chart-pie text-cyan-500'></i> Distribución Presupuestal General"
    },
    ingresos: {
        titulo: "Consulta de Ingresos",
        subtitulo: "Analice el presupuesto PIA, PIM y la recaudación efectiva de las entidades",
        kpi1: { label: "PIA (PRESUPUESTO INICIAL)", sub: "<i class='fa-solid fa-calculator mr-1'></i> Presupuesto Aprobado" },
        kpi2: { label: "PIM (PRESUPUESTO MODIFICADO)", sub: "<i class='fa-solid fa-pen-to-square mr-1'></i> Presupuesto Actualizado" },
        kpi3: { label: "RECAUDACIÓN EFECTIVA", sub: "<i class='fa-solid fa-sack-dollar mr-1'></i> Ingreso Captado" },
        kpi4: { label: "% EFICIENCIA RECAUDACIÓN", sub: "<i class='fa-solid fa-percent mr-1'></i> Cumplimiento meta" },
        chartTitle1: "<i class='fa-solid fa-chart-line text-sky-500'></i> Evolución de Ingresos",
        chartTitle2: "<i class='fa-solid fa-chart-pie text-cyan-500'></i> Ingresos por Fuente de Financiamiento"
    },
    gasto: {
        titulo: "Consulta de Gasto Social",
        subtitulo: "Monitoreo de la ejecución presupuestaria orientada a programas sociales e inversión",
        kpi1: { label: "PIA GASTO SOCIAL", sub: "<i class='fa-solid fa-wallet mr-1'></i> Asignación Inicial" },
        kpi2: { label: "PIM GASTO SOCIAL", sub: "<i class='fa-solid fa-arrow-trend-up mr-1'></i> Monto Vigente" },
        kpi3: { label: "GASTO DEVENGADO", sub: "<i class='fa-solid fa-file-invoice-dollar mr-1'></i> Ejecutado Real" },
        kpi4: { label: "% EJECUCIÓN GASTO", sub: "<i class='fa-solid fa-chart-line mr-1'></i> Avance de Ejecución" },
        chartTitle1: "<i class='fa-solid fa-chart-column text-sky-500'></i> Devengado vs PIM del Periodo",
        chartTitle2: "<i class='fa-solid fa-chart-pie text-cyan-500'></i> Distribución por Rubros Sociales"
    },
    transferencias: {
        titulo: "Consulta de Transferencias",
        subtitulo: "Seguimiento de fondos autorizados y acreditados entre gobiernos y sectores",
        kpi1: { label: "MONTO AUTORIZADO", sub: "<i class='fa-solid fa-file-signature mr-1'></i> Aprobado por Decreto" },
        kpi2: { label: "MONTO ACREDITADO", sub: "<i class='fa-solid fa-check-double mr-1'></i> Depositado en Cuenta" },
        kpi3: { label: "DIFERENCIA / SALDO", sub: "<i class='fa-solid fa-scale-balanced mr-1'></i> Pendiente de Giro" },
        kpi4: { label: "% EFECTIVIDAD", sub: "<i class='fa-solid fa-circle-check mr-1'></i> Tasa de Acreditación" },
        chartTitle1: "<i class='fa-solid fa-chart-bar text-sky-500'></i> Autorizado vs Acreditado",
        chartTitle2: "<i class='fa-solid fa-chart-pie text-cyan-500'></i> Transferencias por Canon / Regalias"
    },
    proyectos: {
        titulo: "Seguimiento de Proyectos de Inversión",
        subtitulo: "Monitoreo del avance financiero e inversión en obras públicas del país",
        kpi1: { label: "PROYECTOS REGISTRADOS", sub: "<i class='fa-solid fa-folder-open mr-1'></i> Obras Registradas" },
        kpi2: { label: "PIM INVERSIÓN", sub: "<i class='fa-solid fa-coins mr-1'></i> Presupuesto Asignado" },
        kpi3: { label: "DEVENGADO EN OBRAS", sub: "<i class='fa-solid fa-helmet-safety mr-1'></i> Inversión Ejecutada" },
        kpi4: { label: "% AVANCE FÍSICO / FINANCIERO", sub: "<i class='fa-solid fa-list-check mr-1'></i> Avance Promedio" },
        chartTitle1: "<i class='fa-solid fa-chart-line text-sky-500'></i> Avance de Proyectos en el Periodo",
        chartTitle2: "<i class='fa-solid fa-chart-pie text-cyan-500'></i> Top Proyectos por Monto Devengado"
    }
};

document.addEventListener('DOMContentLoaded', () => {
    configurarBuscador();
    inicializarGraficos();
});

// -----------------------------------------------------------------------------
// GESTIÓN DE ROLES Y AUTENTICACIÓN (SESIÓN 6)
// -----------------------------------------------------------------------------

function accesoCiudadano() {
    usuarioAutenticado = 'us_web_publico';
    passwordAutenticado = 'Consulta2026!';
    document.getElementById('modal-login').classList.add('hidden');
    document.getElementById('badge-rol-activo').textContent = 'Rol: Ciudadano Consulta';
    document.getElementById('panel-operador-csv').classList.add('hidden');
    
    cargarAniosDinamicos();
}

async function autenticarUsuario(event) {
    if (event) event.preventDefault();
    const usInput = document.getElementById('login-usuario');
    const passInput = document.getElementById('login-password');
    const errDiv = document.getElementById('login-mensaje-error');

    const us = usInput ? usInput.value.trim() : 'us_operador_lima';
    const pass = passInput ? passInput.value.trim() : 'OperadorMef2026!';

    if (errDiv) errDiv.classList.add('hidden');

    try {
        const res = await fetch('/api/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ usuario: us, password: pass })
        });
        const data = await res.json();

        if (res.ok && data.exito) {
            usuarioAutenticado = us;
            passwordAutenticado = pass;
            if (document.getElementById('modal-login')) {
                document.getElementById('modal-login').classList.add('hidden');
            }
            if (document.getElementById('badge-rol-activo')) {
                document.getElementById('badge-rol-activo').textContent = `Rol: ${us}`;
            }

            if (us === 'us_operador_lima' && document.getElementById('panel-operador-csv')) {
                document.getElementById('panel-operador-csv').classList.remove('hidden');
            }

            cargarAniosDinamicos();
        } else {
            if (errDiv) {
                errDiv.textContent = data.mensaje || "Error al autenticar con la BD.";
                errDiv.classList.remove('hidden');
            }
        }
    } catch (err) {
        if (errDiv) {
            errDiv.textContent = "Error de conexión con el servidor Flask/MySQL.";
            errDiv.classList.remove('hidden');
        }
    }
}

function cerrarSesion() {
    usuarioAutenticado = 'us_web_publico';
    passwordAutenticado = 'Consulta2026!';
    if (document.getElementById('modal-login')) {
        document.getElementById('modal-login').classList.remove('hidden');
    }
    if (document.getElementById('panel-operador-csv')) {
        document.getElementById('panel-operador-csv').classList.add('hidden');
    }
}

// Carga Dinámica de Años desde MySQL para actualizar filtros
async function cargarAniosDinamicos() {
    try {
        const res = await fetch('/api/anios');
        const anios = await res.json();

        const selectInicio = document.getElementById('select-ano-inicio');
        const selectFin = document.getElementById('select-ano-fin');

        if (selectInicio && selectFin && Array.isArray(anios) && anios.length > 0) {
            selectInicio.innerHTML = '';
            selectFin.innerHTML = '';

            anios.forEach(ano => {
                selectInicio.innerHTML += `<option value="${ano}">${ano}</option>`;
                selectFin.innerHTML += `<option value="${ano}">${ano}</option>`;
            });

            selectInicio.value = anios[0];
            selectFin.value = anios[anios.length - 1];

            ejecutarConsulta();
        }
    } catch (err) {
        console.error('Error al obtener años dinámicos:', err);
    }
}

// Subida de Datasets CSV con Permisos de Operador y Ejecución de Trigger
async function subirDatasetCSV(event) {
    if (event) event.preventDefault();
    const fileInput = document.getElementById('input-archivo-csv');
    const msgDiv = document.getElementById('msg-subida-csv');

    if (!fileInput || !fileInput.files[0]) {
        alert("Por favor seleccione un archivo CSV.");
        return;
    }

    const formData = new FormData();
    formData.append('archivo', fileInput.files[0]);
    formData.append('usuario', usuarioAutenticado || 'us_operador_lima');
    formData.append('password', passwordAutenticado || 'OperadorMef2026!');

    if (msgDiv) {
        msgDiv.className = "mt-3 p-2.5 rounded-lg text-xs font-semibold bg-sky-900/40 text-sky-200 border border-sky-500/50";
        msgDiv.textContent = "Procesando dataset en MySQL y registrando auditoría...";
        msgDiv.classList.remove('hidden');
    }

    try {
        const res = await fetch('/api/subir-csv', {
            method: 'POST',
            body: formData
        });
        const data = await res.json();

        if (res.ok && data.exito) {
            if (msgDiv) {
                msgDiv.className = "mt-3 p-2.5 rounded-lg text-xs font-semibold bg-emerald-900/40 text-emerald-200 border border-emerald-500/50";
                msgDiv.textContent = `✔ ${data.mensaje}`;
            }
            fileInput.value = '';
            cargarAniosDinamicos();
        } else {
            if (msgDiv) {
                msgDiv.className = "mt-3 p-2.5 rounded-lg text-xs font-semibold bg-red-900/40 text-red-200 border border-red-500/50";
                msgDiv.textContent = `✖ Denegado por MySQL / Error: ${data.mensaje}`;
            }
        }
    } catch (err) {
        if (msgDiv) {
            msgDiv.className = "mt-3 p-2.5 rounded-lg text-xs font-semibold bg-red-900/40 text-red-200 border border-red-500/50";
            msgDiv.textContent = "Error al comunicarse con la API de carga: " + err.message;
        }
    }
}

// -----------------------------------------------------------------------------
// BÚSQUEDA Y AUTOCOMPLETADO
// -----------------------------------------------------------------------------

function configurarBuscador() {
    const inputBusqueda = document.getElementById('input-busqueda');
    const listaAutocompletado = document.getElementById('lista-autocompletado');

    if (!inputBusqueda || !listaAutocompletado) return;

    inputBusqueda.addEventListener('input', async (e) => {
        const query = e.target.value.trim();
        if (query.length < 2) {
            listaAutocompletado.classList.add('hidden');
            return;
        }

        try {
            const res = await fetch(`/api/buscar_entidades?q=${encodeURIComponent(query)}`);
            const entidades = await res.json();

            listaAutocompletado.innerHTML = '';
            if (!entidades || entidades.length === 0) {
                listaAutocompletado.classList.add('hidden');
                return;
            }

            entidades.forEach(ent => {
                const li = document.createElement('li');
                li.className = 'px-4 py-2.5 hover:bg-sky-50 cursor-pointer text-xs flex justify-between items-center transition';
                li.innerHTML = `<div>
                                    <span class="font-bold text-slate-800">${ent.ejecutora_nombre}</span>
                                </div>
                                <span class="font-mono text-[10px] bg-slate-100 text-slate-600 px-2 py-0.5 rounded font-bold">SEC: ${ent.sec_ejec}</span>`;
                
                li.addEventListener('click', () => {
                    entidadSeleccionada = ent;
                    inputBusqueda.value = ent.ejecutora_nombre;
                    listaAutocompletado.classList.add('hidden');
                    ejecutarConsulta();
                });

                listaAutocompletado.appendChild(li);
            });

            listaAutocompletado.classList.remove('hidden');

        } catch (err) {
            console.error('Error buscando entidades:', err);
        }
    });

    document.addEventListener('click', (e) => {
        if (!inputBusqueda.contains(e.target) && !listaAutocompletado.contains(e.target)) {
            listaAutocompletado.classList.add('hidden');
        }
    });
}

// Cambio entre Módulos/Pestañas
function cambiarModulo(nombreModulo) {
    moduloActual = nombreModulo;
    const config = CONFIG_MODULOS[nombreModulo];

    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.className = "nav-btn px-4 py-2 rounded-lg text-slate-300 hover:text-white hover:bg-slate-800/60 transition-all flex items-center gap-2";
    });
    
    const btnActivo = document.getElementById(`btn-${nombreModulo}`);
    if (btnActivo) {
        btnActivo.className = "nav-btn px-4 py-2 rounded-lg bg-gradient-to-r from-sky-500 to-cyan-500 text-white font-bold shadow-md shadow-sky-500/20 transition-all flex items-center gap-2";
    }

    if (document.getElementById('modulo-titulo')) {
        document.getElementById('modulo-titulo').innerHTML = `<span class="w-2 h-6 bg-sky-500 rounded-full inline-block"></span> ${config.titulo}`;
    }
    if (document.getElementById('modulo-subtitulo')) {
        document.getElementById('modulo-subtitulo').textContent = config.subtitulo;
    }

    if (document.getElementById('kpi-label-1')) document.getElementById('kpi-label-1').textContent = config.kpi1.label;
    if (document.getElementById('kpi-sub-1')) document.getElementById('kpi-sub-1').innerHTML = config.kpi1.sub;

    if (document.getElementById('kpi-label-2')) document.getElementById('kpi-label-2').textContent = config.kpi2.label;
    if (document.getElementById('kpi-sub-2')) document.getElementById('kpi-sub-2').innerHTML = config.kpi2.sub;

    if (document.getElementById('kpi-label-3')) document.getElementById('kpi-label-3').textContent = config.kpi3.label;
    if (document.getElementById('kpi-sub-3')) document.getElementById('kpi-sub-3').innerHTML = config.kpi3.sub;

    if (document.getElementById('kpi-label-4')) document.getElementById('kpi-label-4').textContent = config.kpi4.label;
    if (document.getElementById('kpi-sub-4')) document.getElementById('kpi-sub-4').innerHTML = config.kpi4.sub;

    if (document.getElementById('chart-title-1')) document.getElementById('chart-title-1').innerHTML = config.chartTitle1;
    if (document.getElementById('chart-title-2')) document.getElementById('chart-title-2').innerHTML = config.chartTitle2;

    ejecutarConsulta();
}

// Ejecutar Consulta con Filtros de Periodo y Mensajes de Carga
async function ejecutarConsulta() {
    const secEjec = entidadSeleccionada ? entidadSeleccionada.sec_ejec : '301086';
    const selectInicio = document.getElementById('select-ano-inicio');
    const selectFin = document.getElementById('select-ano-fin');

    if (!selectInicio || !selectFin || !selectInicio.value || !selectFin.value) {
        return;
    }

    const anoInicio = selectInicio.value;
    const anoFin = selectFin.value;

    if (parseInt(anoInicio) > parseInt(anoFin)) {
        alert("El año inicial no puede ser mayor al año final.");
        return;
    }

    mostrarEstadoCarga(true);

    try {
        const res = await fetch(`/api/consultar_integrado?sec_ejec=${secEjec}&ano_inicio=${anoInicio}&ano_fin=${anoFin}`);
        const data = await res.json();

        if (res.status === 200) {
            actualizarBannerEntidad(data.entidad, anoInicio, anoFin);
            actualizarInterfaz(data, anoInicio, anoFin);
        }
    } catch (err) {
        console.error("Error al consultar la API:", err);
    } finally {
        mostrarEstadoCarga(false);
    }
}

function mostrarEstadoCarga(cargando) {
    const overlay = document.getElementById('loading-overlay');
    const iconBtn = document.getElementById('icon-btn-consultar');
    const txtBtn = document.getElementById('txt-btn-consultar');

    if (overlay) {
        if (cargando) overlay.classList.remove('hidden');
        else overlay.classList.add('hidden');
    }
    if (iconBtn) {
        iconBtn.className = cargando ? "fa-solid fa-circle-notch fa-spin text-[10px]" : "fa-solid fa-filter text-[10px]";
    }
    if (txtBtn) {
        txtBtn.textContent = cargando ? "CARGANDO..." : "CONSULTAR";
    }
}

function actualizarBannerEntidad(entidad, anoInicio, anoFin) {
    if (entidad && document.getElementById('entidad-nombre-grande')) {
        document.getElementById('entidad-nombre-grande').textContent = entidad.ejecutora_nombre;
        document.getElementById('entidad-sec-ejec').textContent = entidad.sec_ejec;
    }
    if (document.getElementById('entidad-periodo')) {
        document.getElementById('entidad-periodo').textContent = `${anoInicio} — ${anoFin}`;
    }
}

function actualizarInterfaz(data, anoInicio, anoFin) {
    const ind = data.indicadores || {};

    if (moduloActual === 'ingresos') {
        if (document.getElementById('kpi-val-1')) document.getElementById('kpi-val-1').textContent = formatearSoles((ind.total_ingresos_recaudados || 0) * 0.9);
        if (document.getElementById('kpi-val-2')) document.getElementById('kpi-val-2').textContent = formatearSoles((ind.total_ingresos_recaudados || 0) * 1.05);
        if (document.getElementById('kpi-val-3')) document.getElementById('kpi-val-3').textContent = formatearSoles(ind.total_ingresos_recaudados || 0);
        if (document.getElementById('kpi-val-4')) document.getElementById('kpi-val-4').textContent = `${ind.porcentaje_ejecucion_gasto || 0}%`;
    } else if (moduloActual === 'gasto') {
        if (document.getElementById('kpi-val-1')) document.getElementById('kpi-val-1').textContent = formatearSoles((ind.total_gasto_social_devengado || 0) * 1.1);
        if (document.getElementById('kpi-val-2')) document.getElementById('kpi-val-2').textContent = formatearSoles((ind.total_gasto_social_devengado || 0) * 1.15);
        if (document.getElementById('kpi-val-3')) document.getElementById('kpi-val-3').textContent = formatearSoles(ind.total_gasto_social_devengado || 0);
        if (document.getElementById('kpi-val-4')) document.getElementById('kpi-val-4').textContent = `${ind.porcentaje_ejecucion_gasto || 0}%`;
    } else {
        if (document.getElementById('kpi-val-1')) document.getElementById('kpi-val-1').textContent = formatearSoles(ind.total_ingresos_recaudados || 0);
        if (document.getElementById('kpi-val-2')) document.getElementById('kpi-val-2').textContent = formatearSoles(ind.total_gasto_social_devengado || 0);
        if (document.getElementById('kpi-val-3')) document.getElementById('kpi-val-3').textContent = formatearSoles(ind.total_transferencias_acreditadas || 0);
        if (document.getElementById('kpi-val-4')) document.getElementById('kpi-val-4').textContent = `${data.detalle && data.detalle.proyectos ? data.detalle.proyectos.length : 0} Activos`;
    }

    renderizarTablaResultados(data, anoInicio, anoFin);
    renderizarGraficosDinamicos(data, anoInicio, anoFin);
}

function renderizarTablaResultados(data, anoInicio, anoFin) {
    const tbody = document.getElementById('tabla-resultados-body');
    if (!tbody) return;
    tbody.innerHTML = '';

    const nombreEntidad = data.entidad ? data.entidad.ejecutora_nombre : "ENTIDAD CONSULTADA";
    const ind = data.indicadores || {};

    const filas = [
        { entidad: nombreEntidad, periodo: `${anoInicio} - ${anoFin}`, ind: "Ingresos Recaudados Totales", monto: formatearSoles(ind.total_ingresos_recaudados || 0) },
        { entidad: nombreEntidad, periodo: `${anoInicio} - ${anoFin}`, ind: "Gasto Social Devengado", monto: formatearSoles(ind.total_gasto_social_devengado || 0) },
        { entidad: nombreEntidad, periodo: `${anoInicio} - ${anoFin}`, ind: "Transferencias Acreditadas", monto: formatearSoles(ind.total_transferencias_acreditadas || 0) }
    ];

    filas.forEach(item => {
        const tr = document.createElement('tr');
        tr.className = "hover:bg-sky-50/50 transition-colors";
        tr.innerHTML = `
            <td class="py-3 px-4 text-slate-900 font-bold flex items-center gap-2">
                <i class="fa-solid fa-building text-slate-400 text-xs"></i> ${item.entidad}
            </td>
            <td class="py-3 px-4"><span class="bg-slate-100 text-slate-700 px-2 py-0.5 rounded font-mono text-[11px]">${item.periodo}</span></td>
            <td class="py-3 px-4 text-slate-600">${item.ind}</td>
            <td class="py-3 px-4 text-right font-mono font-bold text-slate-900">${item.monto}</td>
        `;
        tbody.appendChild(tr);
    });
}

function inicializarGraficos() {
    const c1 = document.getElementById('chartPrincipal');
    if (c1) {
        chartPrincipal = new Chart(c1.getContext('2d'), {
            type: 'bar',
            data: {
                labels: ['2021', '2022', '2023'],
                datasets: [{
                    label: 'Monto Devengado (S/)',
                    data: [0, 0, 0],
                    backgroundColor: '#0284c7',
                    borderRadius: 6
                }]
            },
            options: { responsive: true, maintainAspectRatio: false }
        });
    }

    const c2 = document.getElementById('chartSecundario');
    if (c2) {
        chartSecundario = new Chart(c2.getContext('2d'), {
            type: 'doughnut',
            data: {
                labels: ['Recursos Ordinarios', 'Canon y Sobrecanon', 'Donaciones'],
                datasets: [{
                    data: [60, 30, 10],
                    backgroundColor: ['#0284c7', '#06b6d4', '#38bdf8']
                }]
            },
            options: { responsive: true, maintainAspectRatio: false }
        });
    }
}

function renderizarGraficosDinamicos(data, anoInicio, anoFin) {
    if (chartPrincipal) {
        chartPrincipal.data.labels = [anoInicio, anoFin];
        const val = data.indicadores ? (data.indicadores.total_gasto_social_devengado || 0) : 0;
        chartPrincipal.data.datasets[0].data = [val * 0.8, val];
        chartPrincipal.update();
    }
}

function formatearSoles(monto) {
    return new Intl.NumberFormat('es-PE', { style: 'currency', currency: 'PEN' }).format(monto || 0);
}

function exportarDatos(tipo) {
    alert(`Exportando reporte en formato ${tipo.toUpperCase()}...`);
}
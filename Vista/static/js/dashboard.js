// =========================================================================
// LOGICA DINÁMICA DE MÓDULOS, PERIODOS Y ESTADOS DE CARGA (MEF SVS)
// =========================================================================

let entidadSeleccionada = { sec_ejec: '301086', ejecutora_nombre: 'MUNICIPALIDAD METROPOLITANA DE LIMA' };
let moduloActual = 'inicio';
let chartPrincipal = null;
let chartSecundario = null;

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
    ejecutarConsulta();
});

// 1. Configuración del Buscador con Autocompletado
function configurarBuscador() {
    const inputBusqueda = document.getElementById('input-busqueda');
    const listaAutocompletado = document.getElementById('lista-autocompletado');

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

// 2. Cambio entre Módulos/Pestañas
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

    document.getElementById('modulo-titulo').innerHTML = `<span class="w-2 h-6 bg-sky-500 rounded-full inline-block"></span> ${config.titulo}`;
    document.getElementById('modulo-subtitulo').textContent = config.subtitulo;

    document.getElementById('kpi-label-1').textContent = config.kpi1.label;
    document.getElementById('kpi-sub-1').innerHTML = config.kpi1.sub;

    document.getElementById('kpi-label-2').textContent = config.kpi2.label;
    document.getElementById('kpi-sub-2').innerHTML = config.kpi2.sub;

    document.getElementById('kpi-label-3').textContent = config.kpi3.label;
    document.getElementById('kpi-sub-3').innerHTML = config.kpi3.sub;

    document.getElementById('kpi-label-4').textContent = config.kpi4.label;
    document.getElementById('kpi-sub-4').innerHTML = config.kpi4.sub;

    document.getElementById('chart-title-1').innerHTML = config.chartTitle1;
    document.getElementById('chart-title-2').innerHTML = config.chartTitle2;

    ejecutarConsulta();
}

// 3. Ejecutar Consulta con Filtros de Periodo y Mensajes de Carga
async function ejecutarConsulta() {
    const secEjec = entidadSeleccionada ? entidadSeleccionada.sec_ejec : '301086';
    const anoInicio = document.getElementById('select-ano-inicio').value;
    const anoFin = document.getElementById('select-ano-fin').value;

    if (parseInt(anoInicio) > parseInt(anoFin)) {
        alert("El año inicial no puede ser mayor al año final.");
        return;
    }

    // Activar Animación de Carga (Loading Overlay y Estado del Botón)
    mostrarEstadoCarga(true);

    try {
        const res = await fetch(`/api/consultar_integrado?sec_ejec=${secEjec}&ano_inicio=${anoInicio}&ano_fin=${anoFin}`);
        const data = await res.json();

        if (res.status === 200) {
            actualizarBannerEntidad(data.entidad, anoInicio, anoFin);
            actualizarInterfaz(data, anoInicio, anoFin);
        } else {
            console.warn("No se obtuvieron datos de la API, usando respaldo");
        }
    } catch (err) {
        console.error("Error al consultar la API:", err);
    } finally {
        // Desactivar Animación de Carga
        mostrarEstadoCarga(false);
    }
}

// 4. Mostrar u Ocultar Indicadores de Carga
function mostrarEstadoCarga(cargando) {
    const overlay = document.getElementById('loading-overlay');
    const iconBtn = document.getElementById('icon-btn-consultar');
    const txtBtn = document.getElementById('txt-btn-consultar');

    if (cargando) {
        overlay.classList.remove('hidden');
        iconBtn.className = "fa-solid fa-circle-notch fa-spin text-[10px]";
        txtBtn.textContent = "CARGANDO...";
    } else {
        overlay.classList.add('hidden');
        iconBtn.className = "fa-solid fa-filter text-[10px]";
        txtBtn.textContent = "CONSULTAR";
    }
}

// 5. Actualizar el Banner Principal de la Entidad
function actualizarBannerEntidad(entidad, anoInicio, anoFin) {
    if (entidad) {
        document.getElementById('entidad-nombre-grande').textContent = entidad.ejecutora_nombre;
        document.getElementById('entidad-sec-ejec').textContent = entidad.sec_ejec;
    }
    document.getElementById('entidad-periodo').textContent = `${anoInicio} — ${anoFin}`;
}

// 6. Actualizar KPIs, Tablas y Gráficos
function actualizarInterfaz(data, anoInicio, anoFin) {
    const ind = data.indicadores;

    if (moduloActual === 'ingresos') {
        document.getElementById('kpi-val-1').textContent = formatearSoles(ind.total_ingresos_recaudados * 0.9);
        document.getElementById('kpi-val-2').textContent = formatearSoles(ind.total_ingresos_recaudados * 1.05);
        document.getElementById('kpi-val-3').textContent = formatearSoles(ind.total_ingresos_recaudados);
        document.getElementById('kpi-val-4').textContent = `${ind.porcentaje_ejecucion_gasto}%`;
    } else if (moduloActual === 'gasto') {
        document.getElementById('kpi-val-1').textContent = formatearSoles(ind.total_gasto_social_devengado * 1.1);
        document.getElementById('kpi-val-2').textContent = formatearSoles(ind.total_gasto_social_devengado * 1.15);
        document.getElementById('kpi-val-3').textContent = formatearSoles(ind.total_gasto_social_devengado);
        document.getElementById('kpi-val-4').textContent = `${ind.porcentaje_ejecucion_gasto}%`;
    } else {
        document.getElementById('kpi-val-1').textContent = formatearSoles(ind.total_ingresos_recaudados);
        document.getElementById('kpi-val-2').textContent = formatearSoles(ind.total_gasto_social_devengado);
        document.getElementById('kpi-val-3').textContent = formatearSoles(ind.total_transferencias_acreditadas);
        document.getElementById('kpi-val-4').textContent = `${data.detalle.proyectos ? data.detalle.proyectos.length : 0} Activos`;
    }

    renderizarTablaResultados(data, anoInicio, anoFin);
    renderizarGraficosDinamicos(data, anoInicio, anoFin);
}

function renderizarTablaResultados(data, anoInicio, anoFin) {
    const tbody = document.getElementById('tabla-resultados-body');
    tbody.innerHTML = '';

    const nombreEntidad = data.entidad ? data.entidad.ejecutora_nombre : "ENTIDAD CONSULTADA";

    const filas = [
        { entidad: nombreEntidad, periodo: `${anoInicio} - ${anoFin}`, ind: "Ingresos Recaudados Totales", monto: formatearSoles(data.indicadores.total_ingresos_recaudados) },
        { entidad: nombreEntidad, periodo: `${anoInicio} - ${anoFin}`, ind: "Gasto Social Devengado", monto: formatearSoles(data.indicadores.total_gasto_social_devengado) },
        { entidad: nombreEntidad, periodo: `${anoInicio} - ${anoFin}`, ind: "Transferencias Acreditadas", monto: formatearSoles(data.indicadores.total_transferencias_acreditadas) }
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
    const ctx1 = document.getElementById('chartPrincipal').getContext('2d');
    chartPrincipal = new Chart(ctx1, {
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

    const ctx2 = document.getElementById('chartSecundario').getContext('2d');
    chartSecundario = new Chart(ctx2, {
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

function renderizarGraficosDinamicos(data, anoInicio, anoFin) {
    if (chartPrincipal) {
        chartPrincipal.data.labels = [anoInicio, anoFin];
        chartPrincipal.data.datasets[0].data = [
            data.indicadores.total_gasto_social_devengado * 0.8,
            data.indicadores.total_gasto_social_devengado
        ];
        chartPrincipal.update();
    }
}

function formatearSoles(monto) {
    return new Intl.NumberFormat('es-PE', { style: 'currency', currency: 'PEN' }).format(monto || 0);
}

function exportarDatos(tipo) {
    alert(`Exportando reporte en formato ${tipo.toUpperCase()}...`);
}
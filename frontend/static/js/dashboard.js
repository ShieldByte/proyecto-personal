const API = 'http://localhost:8000';
let maquinas = [];
let chartBarras = null;
let chartHistorial = [];

// Inicializar cuando cargue la pagina
document.addEventListener('DOMContentLoaded', () => {
    cargarDashboard();
    cargarOrdenes();
    cargarMaquinas();
    
    // Recargar datos cada 15 segundos
    setInterval(() => {
        cargarDashboard();
        cargarOrdenes();
    }, 15000);
});

// Funcion para traer los datos del dashboard y KPIs
async function cargarDashboard() {
    try {
        const res = await fetch(`${API}/dashboard/resumen`);
        const data = await res.json();

        document.getElementById('kpi-total').textContent = data.ordenes.total;
        document.getElementById('kpi-proceso').textContent = data.ordenes.en_proceso;
        document.getElementById('kpi-completadas').textContent = data.ordenes.completadas;

        document.getElementById('kpi-producidas').textContent = data.produccion.unidades_producidas.toLocaleString();
        document.getElementById('kpi-buenas').textContent = data.produccion.unidades_buenas.toLocaleString();
        document.getElementById('kpi-defectos').textContent = data.produccion.unidades_defectuosas.toLocaleString();

        const oee = data.oee;
        document.getElementById('oee-valor').textContent = oee.oee + '%';
        document.getElementById('oee-disponibilidad').textContent = oee.disponibilidad + '%';
        document.getElementById('oee-rendimiento').textContent = oee.rendimiento + '%';
        document.getElementById('oee-calidad').textContent = oee.calidad + '%';

        const badge = document.getElementById('oee-badge');
        const clases = {
            'Clase Mundial': 'badge-mundial',
            'Aceptable': 'badge-aceptable',
            'Regular': 'badge-regular',
            'Crítico': 'badge-critico'
        };
        badge.textContent = oee.clasificacion;
        badge.className = 'oee-badge ' + (clases[oee.clasificacion] || '');

        actualizarGauge(oee.oee);

        // Guardar en el historial para la grafica de lineas
        const hora = new Date().toLocaleTimeString('es-MX', { hour: '2-digit', minute: '2-digit' });
        chartHistorial.push({ hora, oee: oee.oee });
        if (chartHistorial.length > 12) chartHistorial.shift();
        actualizarGraficaLinea();

        document.getElementById('last-update').textContent =
            'Actualizado: ' + new Date().toLocaleTimeString('es-MX');

    } catch (e) {
        console.error('Error cargando dashboard:', e);
    }
}

// Dibujar el gauge del OEE con canvas
function actualizarGauge(valor) {
    const canvas = document.getElementById('gauge-canvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const cx = 100, cy = 90, r = 70;

    ctx.clearRect(0, 0, 200, 110);

    // Fondo gris
    ctx.beginPath();
    ctx.arc(cx, cy, r, Math.PI, 0);
    ctx.lineWidth = 14;
    ctx.strokeStyle = 'rgba(255,255,255,0.08)';
    ctx.stroke();

    // Color segun el porcentaje de OEE
    let color;
    if (valor >= 85) color = '#00d4aa';
    else if (valor >= 65) color = '#f4a261';
    else color = '#e63946';

    // Dibujar el avance
    const angulo = Math.PI + (valor / 100) * Math.PI;
    ctx.beginPath();
    ctx.arc(cx, cy, r, Math.PI, angulo);
    ctx.lineWidth = 14;
    ctx.strokeStyle = color;
    ctx.lineCap = 'round';
    ctx.stroke();
}

// Grafica de linea del historial de OEE
function actualizarGraficaLinea() {
    const canvas = document.getElementById('chart-linea');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const w = canvas.width, h = canvas.height;
    const pad = { top: 20, right: 20, bottom: 30, left: 40 };

    ctx.clearRect(0, 0, w, h);

    if (chartHistorial.length < 2) return;

    const valores = chartHistorial.map(d => d.oee);
    const minVal = Math.max(0, Math.min(...valores) - 10);
    const maxVal = Math.min(100, Math.max(...valores) + 10);
    const rangeY = maxVal - minVal || 1;

    const toX = i => pad.left + (i / (chartHistorial.length - 1)) * (w - pad.left - pad.right);
    const toY = v => pad.top + ((maxVal - v) / rangeY) * (h - pad.top - pad.bottom);

    // Linea de referencia del 85%
    const y85 = toY(85);
    if (y85 >= pad.top && y85 <= h - pad.bottom) {
        ctx.beginPath();
        ctx.setLineDash([4, 4]);
        ctx.strokeStyle = 'rgba(0,212,170,0.3)';
        ctx.lineWidth = 1;
        ctx.moveTo(pad.left, y85);
        ctx.lineTo(w - pad.right, y85);
        ctx.stroke();
        ctx.setLineDash([]);
        ctx.fillStyle = 'rgba(0,212,170,0.5)';
        ctx.font = '10px Segoe UI';
        ctx.fillText('85%', pad.left + 4, y85 - 4);
    }

    // Rellenar area debajo de la linea
    ctx.beginPath();
    ctx.moveTo(toX(0), toY(valores[0]));
    valores.forEach((v, i) => { if (i > 0) ctx.lineTo(toX(i), toY(v)); });
    ctx.lineTo(toX(valores.length - 1), h - pad.bottom);
    ctx.lineTo(toX(0), h - pad.bottom);
    ctx.closePath();
    ctx.fillStyle = 'rgba(204,0,0,0.1)';
    ctx.fill();

    // Dibujar la linea del grafico
    ctx.beginPath();
    ctx.moveTo(toX(0), toY(valores[0]));
    valores.forEach((v, i) => { if (i > 0) ctx.lineTo(toX(i), toY(v)); });
    ctx.strokeStyle = '#CC0000';
    ctx.lineWidth = 2.5;
    ctx.lineJoin = 'round';
    ctx.stroke();

    // Dibujar los puntos
    valores.forEach((v, i) => {
        ctx.beginPath();
        ctx.arc(toX(i), toY(v), 4, 0, Math.PI * 2);
        ctx.fillStyle = '#CC0000';
        ctx.fill();
        ctx.strokeStyle = '#1a1a2e';
        ctx.lineWidth = 2;
        ctx.stroke();
    });

    // Fechas en el eje X
    ctx.fillStyle = 'rgba(160,160,176,0.8)';
    ctx.font = '10px Segoe UI';
    ctx.textAlign = 'center';
    chartHistorial.forEach((d, i) => {
        if (i % 2 === 0 || i === chartHistorial.length - 1) {
            ctx.fillText(d.hora, toX(i), h - 8);
        }
    });
}

// Grafica de barras de produccion por maquina
async function cargarGraficaBarras() {
    const res = await fetch(`${API}/ordenes/`);
    const ordenes = await res.json();

    // Agrupar los datos por maquina
    const porMaquina = {};
    ordenes.forEach(o => {
        const key = `M-${o.maquina_id}`;
        if (!porMaquina[key]) porMaquina[key] = { buenas: 0, defectuosas: 0 };
        porMaquina[key].buenas += (o.unidades_producidas - o.unidades_defectuosas);
        porMaquina[key].defectuosas += o.unidades_defectuosas;
    });

    const canvas = document.getElementById('chart-barras');
    if (!canvas || Object.keys(porMaquina).length === 0) return;

    const ctx = canvas.getContext('2d');
    const w = canvas.width, h = canvas.height;
    const pad = { top: 20, right: 20, bottom: 40, left: 50 };
    const labels = Object.keys(porMaquina);
    const maxVal = Math.max(...labels.map(k => porMaquina[k].buenas + porMaquina[k].defectuosas));

    ctx.clearRect(0, 0, w, h);

    const barWidth = (w - pad.left - pad.right) / labels.length * 0.5;
    const gap = (w - pad.left - pad.right) / labels.length;

    labels.forEach((key, i) => {
        const x = pad.left + i * gap + gap * 0.25;
        const { buenas, defectuosas } = porMaquina[key];
        const total = buenas + defectuosas;
        const hBuenas = ((buenas / maxVal) * (h - pad.top - pad.bottom)) || 0;
        const hDef = ((defectuosas / maxVal) * (h - pad.top - pad.bottom)) || 0;
        const base = h - pad.bottom;

        // Barra de buenas
        ctx.fillStyle = '#00d4aa';
        ctx.beginPath();
        ctx.roundRect(x, base - hBuenas, barWidth / 2 - 2, hBuenas, [4, 4, 0, 0]);
        ctx.fill();

        // Barra de defectuosas
        ctx.fillStyle = '#e63946';
        ctx.beginPath();
        ctx.roundRect(x + barWidth / 2, base - hDef, barWidth / 2 - 2, hDef, [4, 4, 0, 0]);
        ctx.fill();

        ctx.fillStyle = 'rgba(160,160,176,0.8)';
        ctx.font = '10px Segoe UI';
        ctx.textAlign = 'center';
        ctx.fillText(key, x + barWidth / 2, h - 10);
    });

    // Dibujar la leyenda de la grafica
    ctx.font = '10px Segoe UI';
    ctx.fillStyle = '#00d4aa';
    ctx.fillRect(pad.left, 5, 10, 10);
    ctx.fillStyle = 'rgba(160,160,176,0.8)';
    ctx.fillText('Buenas', pad.left + 14, 14);
    ctx.fillStyle = '#e63946';
    ctx.fillRect(pad.left + 70, 5, 10, 10);
    ctx.fillStyle = 'rgba(160,160,176,0.8)';
    ctx.fillText('Defectuosas', pad.left + 84, 14);
}

// Cargar ordenes en la tabla
async function cargarOrdenes() {
    const res = await fetch(`${API}/ordenes/`);
    const ordenes = await res.json();
    const tbody = document.getElementById('tabla-ordenes');

    if (ordenes.length === 0) {
        tbody.innerHTML = `<tr><td colspan="7" style="text-align:center;color:var(--text-secondary);padding:2rem">
            No hay órdenes registradas. Crea la primera usando el botón "Nueva Orden".
           </td></tr>`;
    } else {
        tbody.innerHTML = ordenes.map(o => {
            const pct = o.unidades_objetivo > 0
                ? Math.min(100, Math.round((o.unidades_producidas / o.unidades_objetivo) * 100))
                : 0;
            const color = pct >= 90 ? '#00d4aa' : pct >= 60 ? '#f4a261' : '#e63946';
            return `
            <tr>
                <td><strong>${o.numero_orden}</strong></td>
                <td>${o.producto}</td>
                <td>${o.turno}</td>
                <td>
                    <div style="display:flex;align-items:center;gap:8px">
                        <div class="progress-bar" style="width:80px">
                            <div class="progress-fill" style="width:${pct}%;background:${color}"></div>
                        </div>
                        <span style="font-size:0.8rem">${o.unidades_producidas}/${o.unidades_objetivo}</span>
                    </div>
                </td>
                <td style="color:var(--danger)">${o.unidades_defectuosas}</td>
                <td><span class="badge badge-${o.estado}">${o.estado.replace('_',' ')}</span></td>
                <td>
                    <button onclick="abrirModalActualizar(${o.id}, ${o.unidades_producidas}, ${o.unidades_defectuosas}, '${o.estado}')"
                        style="background:none;border:1px solid var(--border);color:var(--text-secondary);
                               padding:4px 10px;border-radius:4px;cursor:pointer;font-size:0.75rem">
                        Actualizar
                    </button>
                </td>
            </tr>`;
        }).join('');
    }

    cargarGraficaBarras();
    cargarMaquinas();
}

// Cargar maquinas en el select
async function cargarMaquinas() {
    const res = await fetch(`${API}/maquinas/`);
    maquinas = await res.json();
    const sel = document.getElementById('select-maquina');
    if (!sel) return;
    sel.innerHTML = maquinas.map(m =>
        `<option value="${m.id}">${m.codigo} — ${m.nombre}</option>`
    ).join('');
}

// Funciones para el modal de nueva orden
function abrirModalOrden() {
    document.getElementById('modal-orden').classList.add('active');
}

function cerrarModalOrden() {
    document.getElementById('modal-orden').classList.remove('active');
    document.getElementById('form-orden').reset();
}

async function crearOrden() {
    const datos = {
        numero_orden: document.getElementById('inp-numero').value.trim(),
        producto: document.getElementById('inp-producto').value.trim(),
        unidades_objetivo: parseInt(document.getElementById('inp-objetivo').value),
        turno: document.getElementById('inp-turno').value,
        maquina_id: parseInt(document.getElementById('select-maquina').value)
    };

    if (!datos.numero_orden || !datos.producto || isNaN(datos.unidades_objetivo)) {
        mostrarToast('Completa todos los campos', 'error');
        return;
    }

    try {
        const res = await fetch(`${API}/ordenes/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(datos)
        });
        if (res.ok) {
            cerrarModalOrden();
            mostrarToast('Orden creada exitosamente');
            cargarOrdenes();
            cargarDashboard();
        } else {
            const err = await res.json();
            mostrarToast(err.detail || 'Error al crear orden', 'error');
        }
    } catch (e) {
        mostrarToast('Error de conexión', 'error');
    }
}

// Funciones para el modal de actualizar orden
let ordenActualId = null;

function abrirModalActualizar(id, producidas, defectuosas, estado) {
    ordenActualId = id;
    document.getElementById('upd-producidas').value = producidas;
    document.getElementById('upd-defectuosas').value = defectuosas;
    document.getElementById('upd-estado').value = estado;
    document.getElementById('modal-actualizar').classList.add('active');
}

function cerrarModalActualizar() {
    document.getElementById('modal-actualizar').classList.remove('active');
    ordenActualId = null;
}

async function actualizarOrden() {
    if (!ordenActualId) return;
    const datos = {
        unidades_producidas: parseInt(document.getElementById('upd-producidas').value),
        unidades_defectuosas: parseInt(document.getElementById('upd-defectuosas').value),
        estado: document.getElementById('upd-estado').value
    };

    const res = await fetch(`${API}/ordenes/${ordenActualId}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(datos)
    });

    if (res.ok) {
        cerrarModalActualizar();
        mostrarToast('Orden actualizada');
        cargarOrdenes();
        cargarDashboard();
    } else {
        mostrarToast('Error al actualizar', 'error');
    }
}

// Mostrar avisos en pantalla (toast)
function mostrarToast(msg, tipo = 'success') {
    const toast = document.getElementById('toast');
    toast.textContent = msg;
    toast.style.borderLeftColor = tipo === 'error' ? 'var(--danger)' : 'var(--success)';
    toast.classList.add('show');
    setTimeout(() => toast.classList.remove('show'), 3000);
}

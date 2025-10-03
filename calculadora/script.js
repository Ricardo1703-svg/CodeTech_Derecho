function toNumber(v) {
    if (typeof v === 'number') return v;
    if (!v) return NaN;
    v = String(v).replace(',', '.').replace(/[^0-9\.\-]/g, '');
    return parseFloat(v);
}

// Mostrar u ocultar campos proporcionales
const tipoVacaciones = document.getElementById('tipoVacaciones');
tipoVacaciones.addEventListener('change', () => {
    document.getElementById('tiempoProporcional').style.display =
        tipoVacaciones.value === 'proporcionales' ? 'block' : 'none';
});

document.getElementById('calcular').addEventListener('click', () => {
    const salarioRaw = document.getElementById('salario').value.trim();
    const salario = toNumber(salarioRaw);
    const tipo = document.getElementById('tipoVacaciones').value;
    const meses = parseInt(document.getElementById('meses')?.value, 10) || 0;
    const diasExtra = parseInt(document.getElementById('dias')?.value, 10) || 0;
    const diasSemana = parseInt(document.getElementById('diasSemana').value, 10);
    const salarioTipo = document.getElementById('salarioTipo').value;
    const out = document.getElementById('resultado');
    const resumen = document.getElementById('resumen');
    const formulaEl = document.getElementById('formula');
    const articuloEl = document.getElementById('articulo');

    // Validaciones
    if (isNaN(salario) || salario <= 0) {
        resumen.innerHTML = '<span class="error">Introduce un salario válido.</span>';
        out.style.display = 'block'; formulaEl.textContent = ''; articuloEl.textContent = ''; return;
    }
    if (tipo === 'proporcionales' && (meses <= 0 && diasExtra <= 0)) {
        resumen.innerHTML = '<span class="error">Introduce al menos meses o días trabajados.</span>';
        out.style.display = 'block'; formulaEl.textContent = ''; articuloEl.textContent = ''; return;
    }

    const diasVacacionesCompleto = 15;
    let diasVacaciones;
    let detalleTiempo = "";

    if (tipo === 'integras') {
        diasVacaciones = diasVacacionesCompleto;
        detalleTiempo = "(>= 1 año de trabajo)";
    } else {
        const proporcion = Math.min((meses + (diasExtra / 30)), 12) / 12;
        diasVacaciones = Math.round((diasVacacionesCompleto * proporcion) * 100) / 100;
        detalleTiempo = `${meses} meses y ${diasExtra} días`;
    }

    // Calcular salario diario
    const salarioDiario = salario / 30;

    const pagoBase = salarioDiario * diasVacaciones;
    const recargo = pagoBase * 0.30;
    const totalVacaciones = Math.round((pagoBase + recargo) * 100) / 100;

    resumen.innerHTML = `
        Tipo: <strong>${tipo === 'integras' ? 'Íntegras' : 'Proporcionales'}</strong> ${detalleTiempo}<br>
        Días: <strong>${diasVacaciones}</strong><br>
        Salario diario: <strong>$${salarioDiario.toFixed(2)}</strong><br>
        Pago base: <strong>$${pagoBase.toFixed(2)}</strong><br>
        Recargo (30%): <strong>$${recargo.toFixed(2)}</strong><br><br>
        <strong>Total: $${totalVacaciones.toFixed(2)}</strong>`;

    formulaEl.textContent = `1) Días = 15 ${tipo === 'proporcionales' ? '* ((meses + dias/30)/12)' : ''}\n2) Salario diario = salario / 30\n3) Pago base = salario_diario * dias\n4) Recargo = 30% * Pago base\n5) Total = Pago base + Recargo`;

    articuloEl.textContent = `Art. 177: Derecho a 15 días de vacaciones remuneradas con +30%.\nArt. 183: Cálculo según salario básico o promedio de 6 meses previos.`;

    out.style.display = 'block';
});

document.getElementById('year').textContent = new Date().getFullYear();
// Convierte a número (acepta punto o coma)
function toNumber(v) {
    if (typeof v === 'number') return v;
    if (!v) return NaN;
    v = String(v).replace(',', '.').replace(/[^0-9\.\-]/g, '');
    return parseFloat(v);
}

// 🔒 Restringir solo números, punto o coma en el campo salario
const salarioInput = document.getElementById('salario');
salarioInput.addEventListener('input', (e) => {
    e.target.value = e.target.value
        .replace(/[^\d.,]/g, '')  // permite solo números, punto o coma
        .replace(/(\..*)\./g, '$1'); // evita escribir más de un punto
});

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
        out.style.display = 'block';
        formulaEl.textContent = '';
        articuloEl.textContent = '';
        return;
    }

    if (tipo === 'proporcionales' && (meses <= 0 && diasExtra <= 0)) {
        resumen.innerHTML = '<span class="error">Introduce al menos meses o días trabajados.</span>';
        out.style.display = 'block';
        formulaEl.textContent = '';
        articuloEl.textContent = '';
        return;
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

    formulaEl.textContent = `1) Días = 15 ${tipo === 'proporcionales' ? '* ((meses + dias/30)/12)' : ''}
2) Salario diario = salario / 30
3) Pago base = salario_diario * días
4) Recargo = 30% * Pago base
5) Total = Pago base + Recargo`;

    articuloEl.textContent = `Art. 177.- Después de un año de trabajo continuo en la misma empresa o establecimiento o bajo la
dependencia de un mismo patrono, los trabajadores tendrán derecho a un período de vacaciones cuya duración
será de quince días, los cuales serán remunerados con una prestación equivalente al salario ordinario
correspondiente a dicho lapso más un 30% del mismo.

Art. 183.- Para calcular la remuneración que el trabajador debe recibir en concepto de prestación por
vacaciones, se tomará en cuenta:

1º) El salario básico que devengue a la fecha en que deba gozar de ellas, cuando el salario hubiere sido
estipulado por unidad de tiempo;

2º) El salario básico que resulte de dividir los salarios ordinarios que el trabajador haya devengado durante
los seis meses anteriores a la fecha en que deba gozar de ellas, entre el número de días laborables
comprendidos en dicho período, cuando se trate de cualquier otra forma de estipulación del salario.`;

    out.style.display = 'block';
});

document.getElementById('year').textContent = new Date().getFullYear();

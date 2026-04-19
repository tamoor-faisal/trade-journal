'use strict';

function renderEquityChart(canvasId, data) {
    const canvas = document.getElementById(canvasId);
    if (!canvas || !data || data.length === 0) return;

    const ctx = canvas.getContext('2d');
    const dpr = window.devicePixelRatio || 1;
    const W = canvas.offsetWidth;
    const H = canvas.offsetHeight || 200;
    canvas.width  = W * dpr;
    canvas.height = H * dpr;
    ctx.scale(dpr, dpr);

    const values = data.map(d => d.pnl);
    const labels = data.map(d => d.date);
    const minV   = Math.min(0, ...values);
    const maxV   = Math.max(0, ...values);
    const range  = maxV - minV || 1;

    const PAD = { top: 16, right: 16, bottom: 36, left: 58 };
    const gW  = W - PAD.left - PAD.right;
    const gH  = H - PAD.top  - PAD.bottom;

    // Clear
    ctx.clearRect(0, 0, W, H);

    // Zero line
    const zeroY = PAD.top + gH - ((0 - minV) / range) * gH;
    ctx.beginPath();
    ctx.strokeStyle = 'rgba(232,228,217,0.1)';
    ctx.lineWidth = 1;
    ctx.setLineDash([4, 4]);
    ctx.moveTo(PAD.left, zeroY);
    ctx.lineTo(PAD.left + gW, zeroY);
    ctx.stroke();
    ctx.setLineDash([]);

    // Y-axis labels
    ctx.fillStyle = '#5c5a55';
    ctx.font = '10px Space Mono, monospace';
    ctx.textAlign = 'right';
    const yTicks = 4;
    for (let i = 0; i <= yTicks; i++) {
        const v = minV + (range / yTicks) * i;
        const y = PAD.top + gH - ((v - minV) / range) * gH;
        ctx.fillText((v >= 0 ? '+$' : '-$') + Math.abs(Math.round(v)), PAD.left - 6, y + 4);
    }

    if (data.length < 2) return;

    const xStep = gW / (data.length - 1);
    const getX  = i => PAD.left + i * xStep;
    const getY  = v  => PAD.top + gH - ((v - minV) / range) * gH;

    // Fill gradient
    const lastVal = values[values.length - 1];
    const isPositive = lastVal >= 0;
    const grad = ctx.createLinearGradient(0, PAD.top, 0, PAD.top + gH);
    if (isPositive) {
        grad.addColorStop(0,   'rgba(61,240,160,0.20)');
        grad.addColorStop(1,   'rgba(61,240,160,0)');
    } else {
        grad.addColorStop(0,   'rgba(240,69,69,0)');
        grad.addColorStop(1,   'rgba(240,69,69,0.20)');
    }

    ctx.beginPath();
    ctx.moveTo(getX(0), getY(values[0]));
    for (let i = 1; i < values.length; i++) ctx.lineTo(getX(i), getY(values[i]));
    ctx.lineTo(getX(values.length - 1), PAD.top + gH);
    ctx.lineTo(getX(0), PAD.top + gH);
    ctx.closePath();
    ctx.fillStyle = grad;
    ctx.fill();

    // Line
    ctx.beginPath();
    ctx.moveTo(getX(0), getY(values[0]));
    for (let i = 1; i < values.length; i++) ctx.lineTo(getX(i), getY(values[i]));
    ctx.strokeStyle = isPositive ? '#3df0a0' : '#f04545';
    ctx.lineWidth = 1.5;
    ctx.stroke();

    // X labels (show at most 8)
    ctx.fillStyle = '#5c5a55';
    ctx.font = '9px Space Mono, monospace';
    ctx.textAlign = 'center';
    const step = Math.ceil(data.length / 8);
    for (let i = 0; i < data.length; i += step) {
        ctx.fillText(labels[i], getX(i), H - PAD.bottom + 18);
    }

    // End dot
    const lastX = getX(values.length - 1);
    const lastY = getY(values[values.length - 1]);
    ctx.beginPath();
    ctx.arc(lastX, lastY, 4, 0, Math.PI * 2);
    ctx.fillStyle = isPositive ? '#3df0a0' : '#f04545';
    ctx.fill();
}
document.addEventListener('DOMContentLoaded', (event) => {
    const container = document.getElementById('canvas-container');
    const canvas = document.createElement('canvas');
    canvas.width = 600;
    canvas.height = 600;

    // Setting up the context for drawing
    const ctx = canvas.getContext('2d');

    function drawHexagon(x, y, size) {
        ctx.beginPath();
        for (let i = 0; i < 6; i++) {
            let angle = Math.PI / 3 * i;
            ctx.lineTo(
                x + size * Math.cos(angle),
                y - size * Math.sin(angle)
            );
        }
        ctx.closePath();
        ctx.stroke();
    }

    function animate() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        drawHexagon(canvas.width / 2, canvas.height / 2, 150);
        requestAnimationFrame(animate);
    }

    // Drawing the initial hexagon
    drawHexagon(canvas.width / 2, canvas.height / 2, 150);

    container.appendChild(canvas);

    animate();
});
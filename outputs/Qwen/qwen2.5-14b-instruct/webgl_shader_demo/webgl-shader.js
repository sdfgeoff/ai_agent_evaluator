// webgl-shader.js
const canvas = document.getElementById('gl-canvas');
const gl = canvas.getContext('webgl');
if (!gl) {
    console.error('WebGL is not supported!');
}

// Vertex shader source code
var vertexShaderSource = """
attribute vec4 a_position;
varying vec4 v_color;
void main() {
  gl_Position = a_position;
  v_color = vec4(1.0, 1.0, 1.0, 1.0);
}""";

// Fragment shader source code
var fragmentShaderSource = """
varying vec4 v_color;
void main() {
  gl_FragColor = v_color;
}""";

function createShader(gl, type, source) {
    var shader = gl.createShader(type);
    gl.shaderSource(shader, source);
    gl.compileShader(shader);
    if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
        console.error(gl.getShaderInfoLog(shader));
        gl.deleteShader(shader);
        return null;
    }
    return shader;
}

function createProgram(gl, vertexShader, fragmentShader) {
    var program = gl.createProgram();
    gl.attachShader(program, vertexShader);
    gl.attachShader(program, fragmentShader);
    gl.linkProgram(program);
    if (!gl.getProgramParameter(program, gl.LINK_STATUS)) {
        console.error(gl.getProgramInfoLog(program));
        return null;
    }
    gl.useProgram(program);
    gl.viewport(0, 0, gl.canvas.width, gl.canvas.height);
    // Set up vertex data
    var vertices = new Float32Array([
        -0.5, -0.5,
         0.5,  -0.5,
         0.5,   0.5,
        -0.5,   0.5
    ]);
    var buffer = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, buffer);
    gl.bufferData(gl.ARRAY_BUFFER, vertices, gl.STATIC_DRAW);
    // Get attribute location and enable it
    var positionLocation = gl.getAttribLocation(program, 'a_position');
    gl.enableVertexAttribArray(positionLocation);
    gl.vertexAttribPointer(positionLocation, 2, gl.FLOAT, false, 0, 0);
    // Draw the triangle!
    gl.drawArrays(gl.TRIANGLE_FAN, 0, vertices.length / 2);
}

// Create shaders
var vertexShader = createShader(gl, gl.VERTEX_SHADER, vertexShaderSource);
if (!vertexShader) {
    throw new Error('Vertex shader failed to compile');
}
var fragmentShader = createShader(gl, gl.FRAGMENT_SHADER, fragmentShaderSource);
if (!fragmentShader) {
    throw new Error('Fragment shader failed to compile');
}
// Create program
createProgram(gl, vertexShader, fragmentShader);
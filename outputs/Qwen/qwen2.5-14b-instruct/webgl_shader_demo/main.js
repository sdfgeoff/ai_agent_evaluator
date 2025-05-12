const webglUtils = require('webgl-utils');
const canvas = document.querySelector('#gl-canvas');

// Initialize WebGL
const gl = webglUtils.create3DContext(canvas);
if (!gl) {
    console.error("Failed to setup WebGL context");
}

function createProgramFromSources(gl, vertexShaderSource, fragmentShaderSource) {
  const vertShader = loadShader(gl, gl.VERTEX_SHADER, vertexShaderSource);
  const fragShader = loadShader(gl, gl.FRAGMENT_SHADER, fragmentShaderSource);

  // Create the shader program
  const prog = webglUtils.createProgramFromSources(gl, [vertShader, fragShader]);
  
  return prog;
}

function createSquareVertexPositions() {
  const posBuffer = gl.createBuffer();
  gl.bindBuffer(gl.ARRAY_BUFFER, posBuffer);
  gl.bufferData(gl.ARRAY_BUFFER,
      new Float32Array([
          -0.5, -0.5,
           0.5, -0.5,
           0.5,  0.5,
           0.5,  0.5,
          -0.5,  0.5,
          -0.5, -0.5,
      ]),
      gl.STATIC_DRAW);

  // Set up the position attribute
  const numComponents = 2;
  const type = gl.FLOAT;
  const normalize = false;
  const stride = 0;
  const offset = 0;

  const posLoc = gl.getAttribLocation(gl.program, 'a_position');
  gl.vertexAttribPointer(posLoc, numComponents, type, normalize, stride, offset);
  gl.enableVertexAttribArray(posLoc);

  return [posBuffer];
}

function loadShader(gl, type, source) {
    const shader = gl.createShader(type);
    gl.shaderSource(shader, source);
    gl.compileShader(shader);
    if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
        console.error('An error occurred while compiling the shaders:', gl.getShaderInfoLog(shader));
        gl.deleteShader(shader);
        return null;
    }
    return shader;
}

function main() {
  const vertexShaderSource = document.querySelector('#vertex-shader').textContent;
  const fragmentShaderSource = document.querySelector('#fragment-shader').textContent;

  // Create a program object and attach our vertex shader and fragment shader
  gl.program = createProgramFromSources(gl, vertexShaderSource, fragmentShaderSource);

  const squareVertexPositions = createSquareVertexPositions();

  // Clear the canvas before we start drawing on it.
  gl.clearColor(0, 0, 0, 1);
  gl.clearDepth(1.0);
  gl.enable(gl.DEPTH_TEST);

  // Draw a clear color screen
  gl.viewport(0, 0, gl.canvas.width, gl.canvas.height);
  gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT);

  // Set the drawing position to the "center" of the canvas.
  gl.uniform2f(webglUtils.locateUniform(gl.program, 'u_resolution'), gl.canvas.width, gl.canvas.height);

  // Draw a rectangle
  const u_color = webglUtils.locateUniform(gl.program, 'u_color');
  gl.uniform4f(u_color, 1.0, 1.0, 0.0, 1.0); 
  gl.drawArrays(gl.TRIANGLES, 0, squareVertexPositions.length * 3);
}

main();
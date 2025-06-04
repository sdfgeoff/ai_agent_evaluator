// main.js
(function() {
  // Vertex shader program
  const vsSource = `#version 300 es
  in vec4 aVertexPosition;
  uniform mat4 uModelViewMatrix;
  void main(void) {
    gl_Position = uModelViewMatrix * aVertexPosition;
  }
  `;

  // Fragment shader program
  const fsSource = `#version 300 es
  precision highp float;
  out vec4 fragColor;
  void main(void) {
    fragColor = vec4(0.2, 0.6, 0.8, 1.0);
  }
  `;

  // Initialize WebGL context
  const canvas = document.getElementById('glcanvas');
  const gl = canvas.getContext('webgl2');
  if (!gl) {
    alert('WebGL 2 not available, falling back on WebGL.');
    gl = canvas.getContext('webgl');
  }
  if (!gl) {
    alert('Your browser does not support WebGL.');
    return;
  }

  // Compile shader
  function loadShader(type, source) {
    const shader = gl.createShader(type);
    gl.shaderSource(shader, source);
    gl.compileShader(shader);

    if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
      const info = gl.getShaderInfoLog(shader);
      console.error('Could not compile shader:', info);
      gl.deleteShader(shader);
      return null;
    }
    return shader;
  }

  // Create shader program
  function initShaderProgram(vsSource, fsSource) {
    const vertexShader = loadShader(gl.VERTEX_SHADER, vsSource);
    const fragmentShader = loadShader(gl.FRAGMENT_SHADER, fsSource);

    const shaderProgram = gl.createProgram();
    gl.attachShader(shaderProgram, vertexShader);
    gl.attachShader(shaderProgram, fragmentShader);
    gl.linkProgram(shaderProgram);

    if (!gl.getProgramParameter(shaderProgram, gl.LINK_STATUS)) {
      console.error('Unable to initialize the shader program:', gl.getProgramInfoLog(shaderProgram));
      return null;
    }
    return shaderProgram;
  }

  const shaderProgram = initShaderProgram(vsSource, fsSource);
  const programInfo = {
    program: shaderProgram,
    attribLocations: {
      vertexPosition: gl.getAttribLocation(shaderProgram, 'aVertexPosition'),
    },
    uniformLocations: {
      modelViewMatrix: gl.getUniformLocation(shaderProgram, 'uModelViewMatrix'),
    },
  };

  // Triangle positions
  const positions = [
    0.0,  0.5,
   -0.5, -0.5,
    0.5, -0.5,
  ];

  // Create buffer
  const positionBuffer = gl.createBuffer();
  gl.bindBuffer(gl.ARRAY_BUFFER, positionBuffer);
  gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(positions), gl.STATIC_DRAW);

  let then = 0;
  let rotation = 0;

  function render(now) {
    now *= 0.001; // convert to seconds
    const deltaTime = now - then;
    then = now;

    rotation += deltaTime;

    drawScene(gl, programInfo, positionBuffer, rotation);
    requestAnimationFrame(render);
  }
  requestAnimationFrame(render);

  function drawScene(gl, programInfo, buffer, rotation) {
    gl.clearColor(0.0, 0.0, 0.0, 1.0);
    gl.clearDepth(1.0);
    gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT);

    gl.useProgram(programInfo.program);

    // Bind position buffer
    gl.bindBuffer(gl.ARRAY_BUFFER, buffer);
    gl.enableVertexAttribArray(programInfo.attribLocations.vertexPosition);
    gl.vertexAttribPointer(
      programInfo.attribLocations.vertexPosition,
      2, // num components
      gl.FLOAT,
      false,
      0,
      0
    );

    // Set the matrix
    let modelViewMatrix = mat4.create();
    mat4.rotateZ(modelViewMatrix, modelViewMatrix, rotation);

    gl.uniformMatrix4fv(
      programInfo.uniformLocations.modelViewMatrix,
      false,
      modelViewMatrix
    );

    gl.drawArrays(gl.TRIANGLES, 0, 3);
  }
})();

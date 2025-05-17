// Vertex Shader Code
attribute vec4 aVertexPosition;
uniform mat4 uMVMatrix;
void main(void) {
	gl_Position = uMVMatrix * aVertexPosition;
}
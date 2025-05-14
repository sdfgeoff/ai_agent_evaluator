use serde::{Deserialize, Serialize};
use std::collections::HashMap;

#[derive(Debug, Serialize, Deserialize, PartialEq, Clone)]
#[serde(rename_all = "lowercase")]
pub enum Role {
    User,
    Assistant,
    Tool,
}

#[derive(Debug, Serialize, Deserialize, PartialEq, Clone)]
#[serde(rename_all = "lowercase")]
pub enum ToolFunctionType {
    Function,
}

#[derive(Debug, Serialize, Deserialize, PartialEq, Clone)]
pub struct ToolFunctionCall {
    pub name: String,
    pub arguments: String,
}

#[derive(Debug, Serialize, Deserialize, PartialEq, Clone)]
pub struct ToolCall {
    pub id: String,
    #[serde(rename = "type")]
    pub type_: ToolFunctionType,
    pub function: ToolFunctionCall,
}

#[derive(Debug, Serialize, Deserialize, PartialEq, Clone)]
pub struct TextMessage {
    pub role: Role,
    pub content: String,
    pub images: Option<Vec<String>>,
}

#[derive(Debug, Serialize, Deserialize, PartialEq, Clone)]
pub struct ToolRequestMessage {
    pub role: Role,
    pub tool_calls: Vec<ToolCall>,
}

#[derive(Debug, Serialize, Deserialize, PartialEq, Clone)]
pub struct ToolResponseMessage {
    pub tool_call_id: String,
    pub role: Role,
    pub name: String,
    pub content: serde_json::Value, // Use serde_json::Value for dynamic content types
}

#[derive(Debug, Serialize, Deserialize, PartialEq, Clone)]
pub struct ToolFunction {
    pub name: String,
    pub description: Option<String>,
    pub parameters: HashMap<String, serde_json::Value>,
}

#[derive(Debug, Serialize, Deserialize, PartialEq, Clone)]
pub struct ToolDefinition {
    #[serde(rename = "type")]
    pub type_: ToolFunctionType,
    pub function: ToolFunction,
}

#[derive(Debug, Serialize, Deserialize, PartialEq, Clone)]
#[serde(untagged)]
pub enum Message {
    TextMessage(TextMessage),
    ToolRequestMessage(ToolRequestMessage),
    ToolResponseMessage(ToolResponseMessage),
}

#[derive(Debug, Serialize, Deserialize, PartialEq, Clone)]
pub struct ChatParameters {
    pub model: String,
    pub messages: Vec<Message>,
    pub tools: Option<Vec<ToolDefinition>>,
    pub stream: Option<bool>,
}

#[derive(Debug, Serialize, Deserialize, PartialEq, Clone)]
pub struct MessageChoice {
    pub index: usize,
    pub message: Message,
    pub finish_reason: Option<String>,
}

#[derive(Debug, Serialize, Deserialize, PartialEq, Clone)]
pub struct ChatResponse {
    pub choices: Vec<MessageChoice>,
}

#[derive(Debug, Serialize, Deserialize, PartialEq, Clone)]
#[serde(rename_all = "lowercase")]
pub enum FinishReasonType {
    Stop,
}

#[derive(Debug, Serialize, Deserialize, PartialEq, Clone)]
pub struct MessageChoicePartial {
    pub index: usize,
    pub delta: Message,
    pub logprobs: Option<()>,
    pub finish_reason: Option<FinishReasonType>,
}

#[derive(Debug, Serialize, Deserialize, PartialEq, Clone)]
pub struct PartialChatCompletion {
    pub id: String,
    pub object: String,
    pub created: i64,
    pub model: String,
    pub system_fingerprint: String,
    pub choices: Vec<MessageChoicePartial>,
}

#[cfg(test)]
mod tests {
    // Note this useful idiom: importing names from outer (for mod tests) scope.
    use super::*;

    #[test]
    fn test_validate_partial_chat_completion() {
        let json = r#"{
        "id":"chatcmpl-160c39e6qb3fdo4yj0rm7",
        "object":"chat.completion.chunk",
        "created":1744024035,
        "model":"qwen2.5-7b-instruct-1m",
        "system_fingerprint":"qwen2.5-7b-instruct-1m",
        "choices":[
            {
                "index":0,
                "delta":{
                    "role":"assistant","content":"It"
                },
                "logprobs":null,
                "finish_reason":null
            }
        ]
    }"#;

        let parsed: PartialChatCompletion = serde_json::from_str(json).unwrap();
        assert_eq!(parsed.id, "chatcmpl-160c39e6qb3fdo4yj0rm7");
        assert_eq!(
            parsed.choices[0].delta,
            Message::TextMessage(TextMessage {
                role: Role::Assistant,
                content: "It".to_string(),
                images: None,
            })
        );
    }

    #[test]
    fn test_validate_messages() {
        // This assert would fire and test will fail.
        // Please note, that private functions can be tested too!
        let json = r#"[
        {
            "role": "user",
            "content": "Make a 3d web based game of racing gocarts. Pick a standard rendering technology (Eg balylonjs, playcanvas, three.js). Make sure the result is available in index.html",
            "images": null
        },
        {
            "role": "assistant",
            "tool_calls": [
                {
                    "id": "call_nxMtpB2FMLYgeK40SficYHL8",
                    "type": "function",
                    "function": {
                        "name": "create_file",
                        "arguments": "{\n  \"filename\": \"index.html\",\n  \"content\": \"<!DOCTYPE html>\\n<html lang=\\\"en\\\">\\n<head>\\n  <meta charset=\\\"UTF-8\\\">\\n  <meta name=\\\"viewport\\\" content=\\\"width=device-width, initial-scale=1.0\\\">\\n  <title>3D Go-Cart Racing Game</title>\\n  <style>\\n    body { margin: 0; overflow: hidden; }\\n    canvas { display: block; }\\n    #hud {\\n      position: absolute;\\n      top: 10px;\\n      left: 10px;\\n      color: white;\\n      font-family: Arial, sans-serif;\\n      z-index: 100;\\n    }\\n  </style>\\n</head>\\n<body>\\n  <div id=\\\"hud\\\">Use arrow keys to drive the go-cart</div>\\n  <!-- Include Three.js from CDN -->\\n  <script src=\\\"https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js\\\"></script>\\n  <script>\\n    // Scene, Camera, Renderer\\n    const scene = new THREE.Scene();\\n    scene.background = new THREE.Color(0x87ceeb);  // Sky blue sky\\n\\n    const camera = new THREE.PerspectiveCamera(75, window.innerWidth/window.innerHeight, 0.1, 1000);\\n    camera.position.set(0, 5, -10);\\n    camera.lookAt(0, 0, 0);\\n\\n    const renderer = new THREE.WebGLRenderer({ antialias: true });\\n    renderer.setSize(window.innerWidth, window.innerHeight);\\n    document.body.appendChild(renderer.domElement);\\n\\n    // Resize handler\\n    window.addEventListener('resize', () => {\\n      camera.aspect = window.innerWidth/window.innerHeight;\\n      camera.updateProjectionMatrix();\\n      renderer.setSize(window.innerWidth, window.innerHeight);\\n    });\\n\\n    // Lights\\n    const ambientLight = new THREE.AmbientLight(0xffffff, 0.4);\\n    scene.add(ambientLight);\\n    \\n    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);\\n    directionalLight.position.set(5, 10, 7.5);\\n    scene.add(directionalLight);\\n\\n    // Ground (Track)\\n    const groundGeometry = new THREE.PlaneGeometry(200, 200, 10, 10);\\n    const groundMaterial = new THREE.MeshLambertMaterial({ color: 0x228B22 });  // green grass\\n    const ground = new THREE.Mesh(groundGeometry, groundMaterial);\\n    ground.rotation.x = -Math.PI / 2;\\n    scene.add(ground);\\n\\n    // Simple track (darker patch) - just an example section of a track\\n    const trackGeometry = new THREE.PlaneGeometry(50, 200);\\n    const trackMaterial = new THREE.MeshLambertMaterial({ color: 0x555555 });\\n    const track = new THREE.Mesh(trackGeometry, trackMaterial);\\n    track.rotation.x = -Math.PI / 2;\\n    track.position.y = 0.01;  // slightly above ground to avoid z-fighting\\n    scene.add(track);\\n\\n    // Go-cart (represented by a box geometry)\\n    const cartGeometry = new THREE.BoxGeometry(1, 0.5, 2);\\n    const cartMaterial = new THREE.MeshLambertMaterial({ color: 0xff0000 });\\n    const cart = new THREE.Mesh(cartGeometry, cartMaterial);\\n    cart.position.y = 0.25; // Half of its height\\n    scene.add(cart);\\n\\n    // Variables for controlling the go-cart movement\\n    let speed = 0;\\n    let maxSpeed = 0.5;\\n    let acceleration = 0.01;\\n    let deceleration = 0.02;\\n    let rotationSpeed = 0.03;\\n    let keysPressed = {};\\n\\n    // Event listeners for key press\\n    document.addEventListener('keydown', (event) => {\\n      keysPressed[event.code] = true;\\n    });\\n\\n    document.addEventListener('keyup', (event) => {\\n      keysPressed[event.code] = false;\\n    });\\n\\n    // Game loop\\n    function animate() {\\n      requestAnimationFrame(animate);\\n\\n      // Simple controls: Up arrow to accelerate, Down arrow to decelerate, Left and Right to turn\\n      if(keysPressed['ArrowUp']) {\\n        speed = Math.min(speed + acceleration, maxSpeed);\\n      } else if(keysPressed['ArrowDown']) {\\n        speed = Math.max(speed - acceleration, -maxSpeed/2);  // allow reverse, but slower\\n      } else {\\n        // Natural deceleration when not pressing forward/backward\\n        if(speed > 0) {\\n          speed = Math.max(speed - deceleration, 0);\\n        } else if(speed < 0) {\\n          speed = Math.min(speed + deceleration, 0);\\n        }\\n      }\\n\\n      // Turning\\n      if(keysPressed['ArrowLeft']) {\\n        cart.rotation.y += rotationSpeed * (speed !== 0 ? Math.sign(speed) : 1);\\n      }\\n      if(keysPressed['ArrowRight']) {\\n        cart.rotation.y -= rotationSpeed * (speed !== 0 ? Math.sign(speed) : 1);\\n      }\\n\\n      // Update cart position based on speed and rotation\\n      cart.position.x -= Math.sin(cart.rotation.y) * speed;\\n      cart.position.z -= Math.cos(cart.rotation.y) * speed;\\n\\n      // Camera follows the cart\\n      const cameraOffset = new THREE.Vector3(0, 5, -10);\\n      const rotatedOffset = cameraOffset.clone().applyAxisAngle(new THREE.Vector3(0,1,0), cart.rotation.y);\\n      camera.position.copy(cart.position).add(rotatedOffset);\\n      camera.lookAt(cart.position);\\n\\n      renderer.render(scene, camera);\\n    }\\n\\n    animate();\\n  </script>\\n</body>\\n</html>\\n\"\n}"
                    }
                }
            ]
        },
        {
            "tool_call_id": "call_nxMtpB2FMLYgeK40SficYHL8",
            "role": "tool",
            "name": "create_file",
            "content": [
                {
                    "type": "text",
                    "text": "{\"message\": \"File index.html created successfully\"}",
                    "annotations": null
                }
            ]
        },
        {
            "role": "assistant",
            "tool_calls": [
                {
                    "id": "call_wlI7QTehwxExN6C5MNxeci8u",
                    "type": "function",
                    "function": {
                        "name": "task_complete",
                        "arguments": "{}"
                    }
                }
            ]
        }
    ]"#;

        let parsed: Vec<Message> = serde_json::from_str(json).unwrap();
        assert_eq!(parsed.len(), 4);
        assert_eq!(parsed[0], Message::TextMessage(TextMessage {
            role: Role::User,
            content: "Make a 3d web based game of racing gocarts. Pick a standard rendering technology (Eg balylonjs, playcanvas, three.js). Make sure the result is available in index.html".to_string(),
            images: None,
        }));
        assert_eq!(
            parsed[2],
            Message::ToolResponseMessage(ToolResponseMessage {
                tool_call_id: "call_nxMtpB2FMLYgeK40SficYHL8".to_string(),
                role: Role::Tool,
                name: "create_file".to_string(),
                content: serde_json::json!([{
                    "type": "text",
                    "text": "{\"message\": \"File index.html created successfully\"}",
                    "annotations": null
                }]),
            })
        );
        assert_eq!(
            parsed[3],
            Message::ToolRequestMessage(ToolRequestMessage {
                role: Role::Assistant,
                tool_calls: vec![ToolCall {
                    id: "call_wlI7QTehwxExN6C5MNxeci8u".to_string(),
                    type_: ToolFunctionType::Function,
                    function: ToolFunctionCall {
                        name: "task_complete".to_string(),
                        arguments: "{}".to_string(),
                    },
                }],
            })
        );
    }
}

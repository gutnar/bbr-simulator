const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer();

camera.up = new THREE.Vector3(0, 0, 1);

renderer.autoClear = false;
renderer.shadowMap.enabled = false;
renderer.shadowMap.autoUpdate = false;
renderer.setSize(window.innerWidth, window.innerHeight);

document.body.appendChild(renderer.domElement);

const controls = new THREE.OrbitControls(camera, renderer.domElement);
controls.minPolarAngle = 0;
controls.maxPolarAngle = Math.PI / 2 - 0.05;
controls.target = new THREE.Vector3(0,0,0); // set the center
controls.minDistance = 1; // the minimum distance the camera must have from center
controls.maxDistance = 10; // the maximum distance the camera must have from center
controls.zoomSpeed = 1; // control the zoomIn and zoomOut speed
controls.rotateSpeed = 0.5; // control the rotate speed

const scene = new CompetitionScene();

function connect() {
  const ws = new WebSocket(`ws://${window.location.host}/ws`);

  ws.onmessage = (event) => {
    const { type, payload } = JSON.parse(event.data);
  
    if (type === 'constants') {
      console.log(payload);
      camera.position.z = payload.COMPETITION_AREA_HEIGHT;
      camera.position.y = -payload.COMPETITION_AREA_HEIGHT;
      scene.setup(payload);
    } else if (type === 'state') {
      scene.setState(payload);
    }
  };

  ws.onclose = () => {
    scene.clear();
    console.log('Connection lost! Reconnecting in 1 second...');

    setTimeout(() => {
      connect();
      console.log('Reconnecting...');
    }, 1000);
  };
}

const renderLoop = () => {
  requestAnimationFrame(renderLoop);

  // Render user-controlled camera
  controls.update();
  renderer.clear();

  renderer.setViewport(0, 0, window.innerWidth, window.innerHeight);
  renderer.render(scene, camera);

  // Render robot cameras
  const robotViewportWidth = 200;
  const robotViewportHeight = robotViewportWidth / scene.ROBOT_CAMERA_ASPECT;
  const robotIds = Object.keys(scene.robots);

  for (let i = 0; i < robotIds.length; ++i) {
    const robot = scene.robots[robotIds[i]];

    renderer.clearDepth();
    renderer.setScissorTest(true);
    renderer.setScissor(
      16 + i * (robotViewportWidth + 16),
      window.innerHeight - robotViewportHeight - 16,
      robotViewportWidth, robotViewportHeight
    );
    renderer.setViewport(
      16 + i * (robotViewportWidth + 16),
      window.innerHeight - robotViewportHeight - 16,
      robotViewportWidth, robotViewportHeight
    );
    renderer.render(scene, robot.camera);
    renderer.setScissorTest(false);
  }
};

renderLoop();
connect();

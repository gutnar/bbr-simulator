// Materials
const CARPET_ORANGE_MATERIAL = new THREE.MeshLambertMaterial( { color: 0xDD6743 });
const CARPET_BLACK_MATERIAL = new THREE.MeshLambertMaterial( { color: 0x2D2C28 });
const CARPET_WHITE_MATERIAL = new THREE.MeshLambertMaterial( { color: 0xC0BDB6 });
const BACKBOARD_MATERIAL = new THREE.MeshLambertMaterial({ color: 0xCFCFC5 });
const MAGENTA_MATERIAL = new THREE.MeshLambertMaterial({ color: 0xA33357 });
const BLUE_MATERIAL = new THREE.MeshLambertMaterial({ color: 0x114266 });
const BALL_MATERIAL = new THREE.MeshLambertMaterial({ color: 0x589252 });
const ROBOT_MATERIAL = new THREE.MeshLambertMaterial({ color: 0x444444, side: THREE.DoubleSide });

function getPlane(width, height, material) {
  const geometry = new THREE.PlaneGeometry(width, height);
  const plane = new THREE.Mesh(geometry, material);

  plane.receiveShadow = true;

  return plane;
}

function getHollowPlane(outerWidth, outerHeight, innerWidth, innerHeight, material) {
  const group = new THREE.Group();

  for (const side of [1, -1]) {
    const verticalMesh = new THREE.Mesh(new THREE.PlaneGeometry(
      (outerWidth - innerWidth) / 2, outerHeight
    ), material);

    const horizontalMesh = new THREE.Mesh(new THREE.PlaneGeometry(
      outerWidth - (outerWidth - innerWidth), (outerHeight - innerHeight) / 2
    ), material);

    verticalMesh.position.x = side * (outerWidth + innerWidth) / 4;
    horizontalMesh.position.y = side * (outerHeight + innerHeight) / 4;

    verticalMesh.receiveShadow = true;
    horizontalMesh.receiveShadow = true;

    group.add(verticalMesh);
    group.add(horizontalMesh);
  }

  return group;
}

class CarpetObject3D extends THREE.Group {
  constructor({
    AREA_WIDTH, AREA_HEIGHT,
    PLAY_AREA_WIDTH, PLAY_AREA_HEIGHT,
    COMPETITION_AREA_WIDTH, COMPETITION_AREA_HEIGHT,
    LINE_WIDTH
  }) {
    super();

    // Black carpet
    this.add(getHollowPlane(
      AREA_WIDTH,
      AREA_HEIGHT,
      PLAY_AREA_WIDTH,
      PLAY_AREA_HEIGHT,
      CARPET_BLACK_MATERIAL
    ));

    // Orange carpet outside borders
    this.add(getHollowPlane(
      PLAY_AREA_WIDTH,
      PLAY_AREA_HEIGHT,
      COMPETITION_AREA_WIDTH,
      COMPETITION_AREA_HEIGHT,
      CARPET_ORANGE_MATERIAL
    ));

    // Black borders
    this.add(getHollowPlane(
      COMPETITION_AREA_WIDTH,
      COMPETITION_AREA_HEIGHT,
      COMPETITION_AREA_WIDTH - LINE_WIDTH * 2,
      COMPETITION_AREA_HEIGHT - LINE_WIDTH * 2,
      CARPET_BLACK_MATERIAL
    ));

    // White borders
    this.add(getHollowPlane(
      COMPETITION_AREA_WIDTH - LINE_WIDTH * 2,
      COMPETITION_AREA_HEIGHT - LINE_WIDTH * 2,
      COMPETITION_AREA_WIDTH - LINE_WIDTH * 4,
      COMPETITION_AREA_HEIGHT - LINE_WIDTH * 4,
      CARPET_WHITE_MATERIAL
    ));

    // White middle line
    this.add(getPlane(
      LINE_WIDTH,
      COMPETITION_AREA_HEIGHT - LINE_WIDTH * 4,
      CARPET_WHITE_MATERIAL
    ));

    // Orange carpet inside borders
    for (const side of [-1, 1]) {
      const plane = getPlane(
        (COMPETITION_AREA_WIDTH - LINE_WIDTH * 5) / 2,
        COMPETITION_AREA_HEIGHT - LINE_WIDTH * 4,
        CARPET_ORANGE_MATERIAL
      );

      plane.position.x = side * (COMPETITION_AREA_WIDTH / 4 - LINE_WIDTH * 3 / 4);
      this.add(plane);
    }
  }
}

class BasketObject3D extends THREE.Group {
  constructor({
    BACKBOARD_WIDTH, BACKBOARD_HEIGHT, BACKBOARD_DEPTH,
    BASKET_OUTER_RADIUS, BASKET_INNER_RADIUS, BASKET_HEIGHT
  }, material) {
    super();

    // Backboard
    const backboardGeom = new THREE.BoxGeometry(BACKBOARD_WIDTH, BACKBOARD_HEIGHT, BACKBOARD_DEPTH);
    const backboard = new THREE.Mesh(backboardGeom, BACKBOARD_MATERIAL);

    backboard.castShadow = true;
    backboard.rotation.x = Math.PI / 2;
    backboard.rotation.y = Math.PI / 2;
    backboard.position.x = -BACKBOARD_DEPTH / 2;
    backboard.position.z = BACKBOARD_HEIGHT / 2;

    this.add(backboard);

    // Tube
    const innerCylinderGeom = new THREE.CylinderGeometry(
      BASKET_INNER_RADIUS, BASKET_INNER_RADIUS, BASKET_HEIGHT, 32, 1, true
    );

    const outerCylinderGeom = new THREE.CylinderGeometry(
      BASKET_OUTER_RADIUS, BASKET_OUTER_RADIUS, BASKET_HEIGHT, 32, 1, true
    );

    const innerCylinderBSP = new ThreeBSP(innerCylinderGeom);
    const outerCylinderBSP = new ThreeBSP(outerCylinderGeom);
    const intersectionBSP = outerCylinderBSP.subtract(innerCylinderBSP);
    const tube = intersectionBSP.toMesh(material);

    tube.castShadow = true;
    tube.rotation.x = Math.PI / 2;
    tube.position.x = BASKET_OUTER_RADIUS;
    tube.position.z = BASKET_HEIGHT / 2;

    this.add(tube);
  }
}

class RobotObject3D extends THREE.Group {
  constructor({
    ROBOT_RADIUS,
    ROBOT_HEIGHT,
    ROBOT_CAMERA_X,
    ROBOT_CAMERA_Y,
    ROBOT_CAMERA_Z,
    ROBOT_CAMERA_R,
    ROBOT_CAMERA_FOV,
    ROBOT_CAMERA_ASPECT,
    ROBOT_CAMERA_NEAR,
    ROBOT_CAMERA_FAR
  }) {
    super();

    const geometry = new THREE.CylinderGeometry(
      ROBOT_RADIUS, ROBOT_RADIUS, ROBOT_HEIGHT,
      32, 32, false, 0, Math.PI * 2
    );

    this.mesh = new THREE.Mesh(geometry, ROBOT_MATERIAL);
    this.mesh.rotation.x = Math.PI / 2;
    this.mesh.position.z = ROBOT_HEIGHT / 2;
    this.add(this.mesh);

    this.ROBOT_HEIGHT = ROBOT_HEIGHT;
    this.camera = new THREE.PerspectiveCamera(
      ROBOT_CAMERA_FOV, ROBOT_CAMERA_ASPECT, ROBOT_CAMERA_NEAR, ROBOT_CAMERA_FAR
    );
    this.camera.position.z = ROBOT_CAMERA_Z;
    this.camera.rotation.x = ROBOT_CAMERA_R;
    this.add(this.camera);
  }

  setState({ x, y, z, r }) {
    this.position.x = x;
    this.position.y = y;
    this.position.z = z;
    this.rotation.z = r;
  }
}

class BallObject3D extends THREE.Mesh {
  constructor({ BALL_RADIUS }, id) {
    super(new THREE.SphereGeometry(BALL_RADIUS, 32, 32), BALL_MATERIAL);

    this.castShadow = true;
    this.simulationId = id;
    this.position.z = BALL_RADIUS;
  }

  setState({ x, y, z }) {
    this.position.x = x;
    this.position.y = y;
    this.position.z = z;
  }
}

class CompetitionScene extends THREE.Scene {
  robots = {};
  balls = {};

  clear() {
    this.robots = {};
    this.balls = {};

    while (this.children.length > 0) {
      this.remove(scene.children[0]); 
    }
  }

  setup(constants) {
    for (const key in constants) {
      this[key] = constants[key];
    }

    // Lights
    const spotLight = new THREE.SpotLight(0xFFFFFF);
    spotLight.position.set(0, 0, this.BACKBOARD_HEIGHT * 5);
    spotLight.castShadow = true;
    this.add(spotLight);

    this.add(new THREE.AmbientLight(0x626262));

    // Carpet
    this.add(new CarpetObject3D(constants));

    // Baskets
    const magentaBasket = new BasketObject3D(constants, MAGENTA_MATERIAL);
    magentaBasket.position.x = -this.COMPETITION_AREA_WIDTH / 2;
    this.add(magentaBasket);

    const blueBasket = new BasketObject3D(constants, BLUE_MATERIAL);
    blueBasket.position.x = this.COMPETITION_AREA_WIDTH / 2;
    blueBasket.rotation.z = Math.PI;
    this.add(blueBasket);
  }

  setState({ robots, balls }) {
    for (const robotState of robots) {
      if (!(robotState.id in this.robots)) {
        this.robots[robotState.id] = new RobotObject3D(this, robotState.id);
        this.add(this.robots[robotState.id]);
        this.add(new THREE.CameraHelper(this.robots[robotState.id].camera));
      }

      this.robots[robotState.id].setState(robotState);
    }

    for (const ballState of balls) {
      if (!(ballState.id in this.balls)) {
        this.balls[ballState.id] = new BallObject3D(this, ballState.id);
        this.add(this.balls[ballState.id]);
      }

      this.balls[ballState.id].setState(ballState);
    }
  }
}

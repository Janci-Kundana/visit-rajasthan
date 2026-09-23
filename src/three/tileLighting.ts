import * as THREE from "three";

/** A small HDR sky supplies outdoor reflections without another network asset. */
export function lightTile(renderer: THREE.WebGLRenderer, scene: THREE.Scene, radius: number) {
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.AgXToneMapping;
  renderer.toneMappingExposure = 1.05;
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;

  const width = 128,
    height = 64;
  const pixels = new Float32Array(width * height * 4);
  const sky = new THREE.Color(0xb9d3ed);
  const horizon = new THREE.Color(0xf2e8d5);
  const ground = new THREE.Color(0x5e5140);
  const color = new THREE.Color();
  for (let y = 0; y < height; y++) {
    const elevation = Math.cos((y / (height - 1)) * Math.PI);
    color.copy(elevation > 0 ? horizon : ground);
    if (elevation > 0) color.lerp(sky, Math.pow(elevation, 0.45));
    for (let x = 0; x < width; x++) {
      const offset = (y * width + x) * 4;
      pixels[offset] = color.r;
      pixels[offset + 1] = color.g;
      pixels[offset + 2] = color.b;
      pixels[offset + 3] = 1;
    }
  }
  const skyTexture = new THREE.DataTexture(
    pixels,
    width,
    height,
    THREE.RGBAFormat,
    THREE.FloatType,
  );
  skyTexture.mapping = THREE.EquirectangularReflectionMapping;
  skyTexture.needsUpdate = true;
  const generator = new THREE.PMREMGenerator(renderer);
  const environment = generator.fromEquirectangular(skyTexture);
  scene.environment = environment.texture;
  scene.environmentIntensity = 0.65;
  generator.dispose();
  skyTexture.dispose();

  scene.add(new THREE.HemisphereLight(0xcbdff5, 0x827055, 0.65));
  const sun = new THREE.DirectionalLight(0xffe5c1, 2.7);
  sun.position.set(radius * 0.8, radius * 1.8, radius * 1.2);
  sun.castShadow = true;
  sun.shadow.mapSize.set(2048, 2048);
  const span = radius * 1.2;
  Object.assign(sun.shadow.camera, {
    left: -span,
    right: span,
    top: span,
    bottom: -span,
    near: 0.1,
    far: radius * 6,
  });
  sun.shadow.bias = -0.00015;
  sun.shadow.normalBias = 0.012;
  scene.add(sun);
  const fill = new THREE.DirectionalLight(0xc2d8ee, 0.45);
  fill.position.set(-radius, radius * 0.7, -radius);
  scene.add(fill);
  return () => {
    scene.environment = null;
    environment.dispose();
    sun.shadow.map?.dispose();
  };
}

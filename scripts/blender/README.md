# Destination models

The site loads `public/models/{city}_tile.glb` and uses
`public/images/tiles/{city}.png` while loading or when WebGL is unavailable.
All four models have embedded albedo, roughness and tangent-space normal maps.
Geometry uses `EXT_meshopt_compression`, decoded by Three.js's bundled
`MeshoptDecoder`; there are no external texture or decoder URLs.
Attribute compression is lossless: the export helper bypasses Blender 5.2's
12-bit filter to preserve thin relief and accurate bounds. Tangents are exported
explicitly so normal maps have the same basis across renderers.

## Rebuild

Requires Blender 5.2 or later and Python 3. Blender supplies NumPy.

```sh
python scripts/blender/build_tiles.py
python scripts/blender/build_tiles.py jaipur
python scripts/blender/build_tiles.py --blender "/path/to/blender"
```

`BLENDER_PATH` can also point to the executable. Builds use fixed seeds, save
logs under `blender-output/`, and stop on a Blender failure.

Each build writes:

- An embedded, compressed GLB in `public/models/`.
- A transparent landscape poster in `public/images/tiles/`.
- An 1100px Cycles preview in `blender-output/tiles/`.
- A packed, editable scene in `blender-output/scenes/{city}.blend` (generated,
  excluded from Git).

In the `.blend`, hide the joined `{city}_tile` object and enable the **Editable
landmarks** collection to work on individual parts. The camera and lighting are
included. Texture images are packed into the scene.

## Structure

- `tile_kit.py`: geometry, assembly, compression and rendering.
- `tile_surfaces.py`: seamless PBR images and world-scale UV projection.
- `tile_details.py`: balustrades, street furniture, wildlife, boats and dunes.
- `{city}_tile.py`: landmark composition and destination-specific details.

These remain artist-built architectural interpretations, not surveyed replicas.
The earlier `*_iso.py` and other standalone landmark scripts are legacy experiments.

## Homepage: Hawa Mahal

`hawa_mahal_home.py` builds the homepage's separate, detailed facade from a frontal
Hawa Mahal photo: five stepped storeys, projecting polygonal jharokhas, cusped
arches, dense diamond jali, nested mouldings, corbels, green shutters, side wings,
terrace railings and rooftop chhatris. Limewash has embedded PBR texture maps.
The palace stands on its street: the Pink City wall runs off either side (shopfront
arcade, latticed windows, kangura parapet, in the palace's own plasters), and a
footway, kerbs and a marked road with a zebra crossing run along the front.

```sh
python scripts/blender/build_home.py
```

This requires Node.js/npm as well as Blender. After rendering, the builder uses
pinned `gltfpack@1.2.0` with 16-bit positions, 14-bit UVs and meshopt compression.
It preserves the geometry while reducing the file and GPU buffer sizes. Outputs:

- `public/models/hawa_mahal_home.glb`: the homepage's live model.
- `public/images/home/hawa-mahal.webp`: matching transparent fallback render.
- `blender-output/scenes/hawa_mahal_home.blend`: packed editable source.
- `blender-output/hawa_mahal_home.raw.glb`: intermediate export, excluded from Git.

`--pack-only` repacks the existing intermediate without running Blender again.
The homepage loads the model on its first visit. Its resting camera is a level
perspective camera with a shifted lens, and the fallback still is rendered from
exactly that camera; `DISTANCE`, `EYE` and the still's frame must stay in step with
`src/three/HomeScene.ts`. Moving the pointer eases the camera up to 9° around the
facade and up or down, and it stops rendering once the view settles or the page is
inactive. Reduced motion keeps the resting view. A failed model load or unavailable
WebGL leaves the matching still visible.

## Check in the browser

```sh
npm ci
npm run dev
npm run build
```

Visit `/#/places` for the integrated cards, or `/tools/viewer.html` for a larger
inspection grid with the same PBR lighting. The inspection grid also accepts
`?models=jaipur&cell=900`.

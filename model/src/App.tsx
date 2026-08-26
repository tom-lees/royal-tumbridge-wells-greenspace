import { Canvas } from "@react-three/fiber";
import { Suspense, useEffect, useState } from "react";
import { Scene } from "./components/Scene";
import type { TileManifestEntry } from "./types";

function App() {
  const [tiles, setTiles] = useState<TileManifestEntry[]>([]);

  useEffect(() => {
    fetch("/tiles/manifest.json")
      .then((res) => res.json())
      .then(setTiles);
  }, []);

  return (
    <Canvas camera={{ position: [800, 600, 800], fov: 50, near: 1, far: 20000 }}>
      <Suspense fallback={null}>
        <Scene tiles={tiles} />
      </Suspense>
    </Canvas>
  );
}

export default App;

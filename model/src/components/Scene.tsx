import { Grid, OrbitControls } from "@react-three/drei";
import type { TileManifestEntry } from "../types";
import { Tile } from "./Tile";

export function Scene({ tiles }: { tiles: TileManifestEntry[] }) {
  return (
    <>
      <ambientLight intensity={0.6} />
      <directionalLight position={[500, 800, 300]} intensity={1} />
      <Grid
        args={[10000, 10000]}
        cellSize={100}
        sectionSize={1000}
        fadeDistance={8000}
        infiniteGrid
      />
      {tiles.map((tile) => (
        <Tile key={tile.name} tile={tile} />
      ))}
      <OrbitControls target={[0, 0, 0]} />
    </>
  );
}

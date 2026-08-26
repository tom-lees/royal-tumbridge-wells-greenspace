import { useGLTF } from "@react-three/drei";
import type { TileManifestEntry } from "../types";

export function Tile({ tile }: { tile: TileManifestEntry }) {
  const { scene } = useGLTF(`/${tile.file}`);
  return <primitive object={scene} position={[tile.offsetX, 0, tile.offsetZ]} />;
}

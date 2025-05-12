interface SectorModel {
  id: number;
  warps: number[];
  portId: string | null;
  planetId: string | null; // LEGACY: Only supports one planet per sector. Consider replacing with planets: string[] for multi-planet support.
  fighters: number;
  fighterOwnerId: string | null;
  ships: string[]; // player IDs
}
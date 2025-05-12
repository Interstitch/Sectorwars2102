// Sector Wars 2102 Ship Data Model

export interface ShipModel {
  id: string;
  name: string;
  type: string; // ShipType, see ship types doc
  ownerId: string;
  ownerName?: string;
  sectorId: number;
  fighters: number;
  shields: number;
  holds: number;
  commodities: number[];
  // Colonist transport
  colonists: number; // Current number of colonists on board
  maxColonists: number; // Maximum colonist capacity
  // Genesis Device support (for planet creation)
  genesis: number; // Current Genesis Device count
  maxGenesis: number; // Maximum Genesis Devices this ship can carry
  // Other equipment fields as needed
}

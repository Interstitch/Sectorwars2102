interface PortModel {
  id: string;
  name: string;
  class: number;
  commodities: number[];
  production: number[];
  priceVariance: number[];
  lastUpdate: Date;
  occupiedBy: string | null;
  sector: number;
}
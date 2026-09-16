// Must stay in the same order as JetsonExample/labels.txt.
export enum Element {
  Blue = 0,
  BlueYellow = 1,
  Cup = 2,
  Red = 3,
  RedBlue = 4,
  RedYellow = 5,
  Yellow = 6,
  YellowYellow = 7,
}

export enum Direction {
  X = 0,
  Y = 1,
}

export interface Theme {
  id: string;
  componentBackground: string;
  font: string;
  control: string;
  controlHover: string;
}

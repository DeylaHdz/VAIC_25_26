import { Element } from "../lib/types";
import { images } from "./images";

/**
 * General configuration for the application
 */
export const config = {
  socketIP: "10.42.0.1",
  socketPort: "3030",

  /**
   * Default image width captured by the camera on the robot
   */
  SCALE_X: 640,

  /**
   * Default image height captured by the camera on the robot
   */
  SCALE_Y: 480,

  /**
   * Rate at which the data services polls for data (ms)
   */
  pollingInterval: 60,
  logDataResponse: false,
  detectOutOfBoundsElements: true,
  colors: {
    red: "#D22630",
    darkRed: "#971c22",
    gray: "#939597",
    darkGray: "#58585B",
    darkerGray: "#111111",
    blue: "#0077C8",
    darkBlue: "#004d80",
    black: "#000000",
    white: "#F4F2FF",
    orange: "#fca503",
    darkOrange: "#bf7e04",
    purple: "#7466F1",
    darkPurple: "#433b87",
    grayPurple: "#293045",
  },
  field: {
    dimension: 3.6576, // meters
    oov: 0.1,
    texture: images.field,
    scale: 1.5,
    compass: {
      texture: images.map.compass,
      scale: 0.23,
      ringPositionCorrectionX: 0.1,
      lineScale: 0.03,
      numberOffset: 0.045,
      numberScale: 0.017,
    },
    fog: {
      opacity: 0.75,
    },
    ruler: {
      texture: images.map.ruler,
      xySidebarOffset: 0.26,
      xySidebarMarkersOffset: 0.22,
      xySidebarArrowOffset: 0.22,
      xySidebarSizeMultiplier: 0.025,
      arrowScale: 0.1,
    },
    robot: {
      length: 0.4191, // meters
      width: 0.3175, // meters
      scale: 1.5,
      texture: images.robot,
      textureWidth: 1024, // pixels
      textureHeight: 1024, // pixels
      fov: 50,
    },
  },
  elements: {
    // 2026-27 Override game elements. Pins are ~40mm (0.04m) diameter, 6.5" (0.1651m) tall;
    // Cups are ~3.15" (0.08m) diameter, 6.5" (0.1651m) tall. Using diameter for the top-down
    // field view size, same convention the previous Push Back ball sizes used.
    textures: {
      [Element.Blue]: images.elements.blue,
      [Element.BlueYellow]: images.elements.blueYellow,
      [Element.Cup]: images.elements.cup,
      [Element.Red]: images.elements.red,
      [Element.RedBlue]: images.elements.redBlue,
      [Element.RedYellow]: images.elements.redYellow,
      [Element.Yellow]: images.elements.yellow,
      [Element.YellowYellow]: images.elements.yellowYellow,
    },
    size: {
      [Element.Blue]: { height: 0.04, width: 0.04, scale: 2.0 },
      [Element.BlueYellow]: { height: 0.04, width: 0.04, scale: 2.0 },
      [Element.Cup]: { height: 0.08, width: 0.08, scale: 2.0 },
      [Element.Red]: { height: 0.04, width: 0.04, scale: 2.0 },
      [Element.RedBlue]: { height: 0.04, width: 0.04, scale: 2.0 },
      [Element.RedYellow]: { height: 0.04, width: 0.04, scale: 2.0 },
      [Element.Yellow]: { height: 0.04, width: 0.04, scale: 2.0 },
      [Element.YellowYellow]: { height: 0.04, width: 0.04, scale: 2.0 },
    },
    borderColors: {
      [Element.Blue]: "rgba(0, 119, 200, .8)",
      [Element.BlueYellow]: "rgba(0, 119, 200, .8)",
      [Element.Cup]: "rgba(150, 150, 150, .8)",
      [Element.Red]: "rgba(210, 38, 48, .8)",
      [Element.RedBlue]: "rgba(210, 38, 48, .8)",
      [Element.RedYellow]: "rgba(210, 38, 48, .8)",
      [Element.Yellow]: "rgba(255, 212, 0, .8)",
      [Element.YellowYellow]: "rgba(255, 212, 0, .8)",
    },
    backgroundColors: {
      [Element.Blue]: "rgba(0, 119, 200, .3)",
      [Element.BlueYellow]: "rgba(0, 119, 200, .3)",
      [Element.Cup]: "rgba(150, 150, 150, .3)",
      [Element.Red]: "rgba(210, 38, 48, .3)",
      [Element.RedBlue]: "rgba(210, 38, 48, .3)",
      [Element.RedYellow]: "rgba(210, 38, 48, .3)",
      [Element.Yellow]: "rgba(255, 212, 0, .3)",
      [Element.YellowYellow]: "rgba(255, 212, 0, .3)",
    },
    label: {
      textColors: {
        white: "rgba(255, 255, 255, 1)",
        black: "rgba(0, 0, 0, 1)",
      },
      text: {
        [Element.Blue]: "Blue Pin",
        [Element.BlueYellow]: "Blue/Yellow Pin",
        [Element.Cup]: "Cup",
        [Element.Red]: "Red Pin",
        [Element.RedBlue]: "Red/Blue Pin",
        [Element.RedYellow]: "Red/Yellow Pin",
        [Element.Yellow]: "Yellow Pin",
        [Element.YellowYellow]: "Yellow/Yellow Pin",
      },
    },
  },
};

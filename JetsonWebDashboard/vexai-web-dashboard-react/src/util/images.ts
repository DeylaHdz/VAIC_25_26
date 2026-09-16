import VexAILogoBlack from "../images/vex_ai_logo_black.png";
import VexAILogoWhite from "../images/vex_ai_logo_white.png";
import Robot from "../images/HeroBot-Top.png";
import Field from "../images/FieldTopDown-Cleared.png";
import Compass from "../images/compass.png";
import Ruler from "../images/ruler.png";

/**
 * Generates a simple placeholder icon for an Override Pin as a data URI: a circle split
 * into its two color halves, matching the real game piece's two-tone appearance.
 * There is no official token art bundled with this repo yet - swap these for real
 * top-down photos/renders of the game elements when available.
 */
const pinIcon = (topColor: string, bottomColor: string) => {
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
    <defs>
      <clipPath id="circle"><circle cx="50" cy="50" r="48" /></clipPath>
    </defs>
    <g clip-path="url(#circle)">
      <rect x="0" y="0" width="100" height="50" fill="${topColor}" />
      <rect x="0" y="50" width="100" height="50" fill="${bottomColor}" />
    </g>
    <circle cx="50" cy="50" r="48" fill="none" stroke="#000000" stroke-width="3" />
  </svg>`;
  return `data:image/svg+xml;utf8,${encodeURIComponent(svg)}`;
};

/** Placeholder icon for an Override Cup: a simple hourglass silhouette. */
const cupIcon = () => {
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
    <circle cx="50" cy="50" r="48" fill="#e5e5e5" stroke="#000000" stroke-width="3" />
    <path d="M30 22 H70 L58 50 L70 78 H30 L42 50 Z" fill="#ffffff" stroke="#000000" stroke-width="3" />
  </svg>`;
  return `data:image/svg+xml;utf8,${encodeURIComponent(svg)}`;
};

const BLUE = "#0077C8";
const RED = "#D22630";
const YELLOW = "#FFD400";

export const images = {
  icons: {},
  logos: {
    vexAILogoBlack: VexAILogoBlack,
    vexAILogoWhite: VexAILogoWhite,
  },
  map: {
    compass: Compass,
    ruler: Ruler,
  },
  // 2026-27 Override game elements. See labels.txt / Element enum in lib/types.ts for the
  // authoritative class list - these are placeholder vector icons, not real token art.
  elements: {
    blue: pinIcon(BLUE, BLUE),
    blueYellow: pinIcon(BLUE, YELLOW),
    cup: cupIcon(),
    red: pinIcon(RED, RED),
    redBlue: pinIcon(RED, BLUE),
    redYellow: pinIcon(RED, YELLOW),
    yellow: pinIcon(YELLOW, YELLOW),
    yellowYellow: pinIcon(YELLOW, YELLOW),
  },
  robot: Robot,
  field: Field,
};

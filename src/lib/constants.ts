export const WOW = {
  amber: "#c47b2b",
  amberLight: "#d4923f",
  amberGlow: "#e8a94e",
  oak: "#3b2314",
  oakLight: "#5c3a24",
  parchment: "#faf6ee",
  parchmentDark: "#f0e8d4",
  copper: "#b35e2a",
  charcoal: "#2a2520",
  muted: "#8a7e6e",
  white: "#ffffff",
};

export const FORMSPREE_SUBMIT_ID = "mjgpywkp";

export type Region = "all" | "ireland" | "scotland" | "usa" | "europe" | "asia" | "rest";

export const regionViews: Record<Region, { center: [number, number]; zoom: number }> = {
  all: { center: [0, 30], zoom: 2 },
  ireland: { center: [-7.5, 53.5], zoom: 6.5 },
  scotland: { center: [-4.5, 57], zoom: 5.8 },
  usa: { center: [-98, 39], zoom: 3.8 },
  europe: { center: [10, 50], zoom: 3.8 },
  asia: { center: [105, 35], zoom: 3 },
  rest: { center: [0, 30], zoom: 2 },
};

export const regionLabels: Record<Region, string> = {
  all: "All",
  ireland: "Ireland",
  scotland: "Scotland",
  usa: "USA",
  europe: "Europe",
  asia: "Asia",
  rest: "World",
};

export type RouteResolution =
  { type: "home" } | { type: "places" } | { type: "about" } | { type: "place"; id: string };

/** Resolve the location hash to one of the app's known route surfaces. */
export function resolveRoute(hash: string, placeIds: readonly string[]): RouteResolution {
  const rawPath = hash.replace(/^#\/?/, "");
  if (rawPath === "") return { type: "home" };

  // A single trailing slash is a harmless URL variation; nested paths remain unknown.
  const path = rawPath.endsWith("/") ? rawPath.slice(0, -1) : rawPath;
  if (path === "") return { type: "places" };
  if (path === "places") return { type: "places" };
  if (path === "about") return { type: "about" };
  if (placeIds.includes(path)) return { type: "place", id: path };
  return { type: "places" };
}

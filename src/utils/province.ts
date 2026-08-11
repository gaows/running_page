import type { Activity } from '@/types';
import { extractProvince } from '@/core/hooks/useActivities';
import * as polyline from '@mapbox/polyline';

export type GeoFeature = {
  type: 'Feature';
  properties: { name: string; adcode: number };
  geometry: {
    type: 'Polygon' | 'MultiPolygon';
    coordinates: number[][][][];
  };
};

// Cache the China province GeoJSON so multiple consumers share one load.
let featuresCache: GeoFeature[] | null = null;

export async function loadChinaFeatures(): Promise<GeoFeature[]> {
  if (featuresCache) return featuresCache;
  const mod = (await import('../assets/china-provinces.json')) as unknown as {
    default: { features: GeoFeature[] };
  };
  featuresCache = mod.default.features;
  return featuresCache;
}

function pointInRing(ring: number[][], x: number, y: number): boolean {
  let inside = false;
  const n = ring.length;
  let j = n - 1;
  for (let i = 0; i < n; i++) {
    const xi = ring[i][0];
    const yi = ring[i][1];
    const xj = ring[j][0];
    const yj = ring[j][1];
    if ((yi > y) !== (yj > y) && x < ((xj - xi) * (y - yi)) / (yj - yi) + xi) {
      inside = !inside;
    }
    j = i;
  }
  return inside;
}

// Point-in-polygon against province boundaries. Returns the province name or null.
export function pointInProvince(
  lng: number,
  lat: number,
  features: GeoFeature[]
): string | null {
  for (const f of features) {
    const g = f.geometry;
    const polys = g.type === 'MultiPolygon' ? g.coordinates : [g.coordinates];
    for (const poly of polys) {
      if (pointInRing(poly[0], lng, lat)) {
        let inHole = false;
        for (let h = 1; h < poly.length; h++) {
          if (pointInRing(poly[h], lng, lat)) {
            inHole = true;
            break;
          }
        }
        if (!inHole) return f.properties.name;
      }
    }
  }
  return null;
}

/**
 * Resolve the Chinese province an activity took place in.
 * Prefers the stored `location_country` (reverse-geocoded address); when that
 * is missing (the common case here — Nominatim geocoding failed in CI), it
 * falls back to the GPS track's start coordinate via point-in-polygon.
 * This makes the footprint map work fully offline and survive data regen.
 */
export function getActivityProvince(
  a: Activity,
  features?: GeoFeature[] | null
): string | null {
  const fromLoc = extractProvince(a.location_country);
  if (fromLoc) return fromLoc;
  if (!features || !a.summary_polyline) return null;
  try {
    const pts = polyline.decode(a.summary_polyline);
    if (pts.length) {
      const [lat, lng] = pts[0];
      return pointInProvince(lng, lat, features);
    }
  } catch {
    /* malformed polyline — ignore */
  }
  return null;
}

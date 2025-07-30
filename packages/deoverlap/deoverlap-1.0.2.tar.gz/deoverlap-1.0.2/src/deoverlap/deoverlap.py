"""
This module provides high-level functions for de-overlapping a set of Shapely
geometric objects. It intelligently removes portions of geometries that are
within a specified tolerance of geometries earlier in the processing order.

This version is specifically adapted for compatibility with Shapely < 2.0.
"""

from typing import List, Union, Iterable, Tuple, Dict, Any
from shapely.ops import unary_union
from shapely.strtree import STRtree
from tqdm import tqdm
from shapely.geometry import (
    LineString, Point, MultiLineString, MultiPoint,
    Polygon, MultiPolygon, GeometryCollection
)
from shapely.geometry.base import BaseGeometry

# =============================================================================
#  Type Aliases
# =============================================================================
# Using type aliases for better readability and maintainability of type hints.
GeomInput = Union[BaseGeometry, Iterable['GeomInput']]
FlatGeomOutput = List[Union[LineString, Point]]

# =============================================================================
#  Helper Function
# =============================================================================

def flatten_geometries(geoms: GeomInput) -> FlatGeomOutput:
    """
    Recursively flattens any geometry input into a flat list of non-empty
    LineStrings and Points.

    This utility is used to decompose complex geometries into a simple,
    standardized format that the de-overlapping engines can process.

    Args:
        geoms: A Shapely geometry or a nested iterable of geometries.

    Returns:
        A flat list of simple Point and LineString geometries. Polygons are
        converted to their exterior and interior boundary LineStrings.
    """
    out = []
    if geoms is None: return out

    # Use pattern matching for clear, type-safe dispatching.
    match geoms:
        case LineString() | Point():
            if not geoms.is_empty: out.append(geoms)
        case MultiLineString() | MultiPoint() | GeometryCollection():
            # Recursively flatten all geometries within a collection.
            for g in geoms.geoms: out.extend(flatten_geometries(g))
        case Polygon():
            # Convert Polygons to their constituent rings (LineStrings).
            if not geoms.is_empty:
                out.append(LineString(geoms.exterior.coords))
                for ring in geoms.interiors: out.append(LineString(ring.coords))
        case MultiPolygon():
            # Handle MultiPolygons by flattening each Polygon individually.
            for poly in geoms.geoms: out.extend(flatten_geometries(poly))
        case list() | tuple() | set():
            # Handle standard iterable types.
            for g in geoms: out.extend(flatten_geometries(g))
        case _:
            # Fallback for any other type that is a valid Shapely geometry
            # but not explicitly listed above. This provides some future-proofing.
            if not isinstance(geoms, BaseGeometry):
                 raise TypeError(f"Unsupported geometry type: {type(geoms)}")
    return out

# =============================================================================
#  Internal Engine Functions
# =============================================================================

def _deoverlap_flat_engine(
    geometries: GeomInput,
    tolerance: float,
    progress_bar: bool,
    mask: List[Polygon] = None
) -> Tuple[FlatGeomOutput, FlatGeomOutput, list]:
    """
    Internal engine for fast, flat de-overlapping.

    This function prioritizes performance by working with a flattened list of
    simple geometries. It always computes both the kept and removed portions.

    Args:
        geometries: The input geometries to de-overlap.
        tolerance: The buffer distance to define the overlap area.
        progress_bar: Whether to display a tqdm progress bar.
        mask (optional): An existing list of mask polygons to start with.

    Returns:
        A tuple containing:
            - A flat list of the kept (non-overlapping) geometries.
            - A flat list of the removed (overlapping) geometries.
            - The list of mask polygons used for clipping.
    """
    # Initialize the mask, using a copy of the provided mask if it exists.
    current_mask = [] if mask is None else mask[:]
    flat_geoms, kept_geoms, removed_geoms = flatten_geometries(geometries), [], []

    # A tiny buffer used to resolve floating-point ambiguities. When geometries
    # are perfectly aligned, a simple `.difference()` can be inconsistent.
    # Buffering the clipping mask ensures robust results.
    ROBUSTNESS_BUFFER = 1e-9

    iterable = tqdm(flat_geoms, desc="De-overlapping (flat)", disable=not progress_bar)

    for geom in iterable:
        kept_portion = geom

        # Only perform clipping if a mask has been built up.
        if current_mask:
            # Use an STRtree for efficient spatial querying of nearby mask polygons.
            tree = STRtree(current_mask)
            # In Shapely 1.8, query() returns a list/array of GEOMETRIES.
            # Must check for emptiness by checking its length.
            nearby_geoms = tree.query(geom)
            if len(nearby_geoms) > 0:
                # Create a local mask from the returned nearby geometries.
                local_mask = unary_union(nearby_geoms)
                # The core operation: clip the geometry by the buffered local mask.
                kept_portion = geom.difference(local_mask.buffer(ROBUSTNESS_BUFFER))

        # Add the kept portion to the results and update the master mask for the next iteration.
        if not kept_portion.is_empty:
            kept_geoms.append(kept_portion)
            current_mask.append(kept_portion.buffer(tolerance))

        # The removed portion is simply what's left of the original after the difference.
        if not (removed_portion := geom.difference(kept_portion)).is_empty:
            removed_geoms.append(removed_portion)

    # Return flattened lists, as difference operations can create multi-part geometries.
    return flatten_geometries(kept_geoms), flatten_geometries(removed_geoms), current_mask

def _deoverlap_structured_engine(
    geometries: Iterable[BaseGeometry],
    tolerance: float,
    progress_bar: bool,
    mask: List[Polygon] = None,
) -> Tuple[List[BaseGeometry], Dict[int, List[BaseGeometry]], Dict[int, List[BaseGeometry]], List[int], List[Polygon]]:
    """
    Internal engine for structure-preserving de-overlapping with origin tracking.
    This version uses a type-aware approach to correctly handle clipping for
    both polygons (areas) and linestrings/points.
    """
    current_mask = [] if mask is None else mask[:]
    kept_results, kept_parts_map, removed_parts_map, wholly_removed_indices = [], {}, {}, []
    ROBUSTNESS_BUFFER = 1e-9

    iterable = tqdm(list(geometries), desc="De-overlapping (structured)", disable=not progress_bar)

    for i, geom in enumerate(iterable):
        if geom.is_empty:
            continue

        # Build a local mask from relevant geometries for efficiency
        local_mask = None
        if current_mask:
            tree = STRtree(current_mask)
            # In Shapely 1.8, query() returns a list/array of GEOMETRIES.
            # Must check for emptiness by checking its length.
            nearby_geoms = tree.query(geom)
            if len(nearby_geoms) > 0:
                local_mask = unary_union(nearby_geoms)

        kept_portion = None

        # =====================================================================
        #  TYPE-AWARE LOGIC
        # =====================================================================
        # If geometry is a Polygon or MultiPolygon, operate on its area directly.
        if isinstance(geom, (Polygon, MultiPolygon)):
            if local_mask:
                kept_portion = geom.difference(local_mask.buffer(ROBUSTNESS_BUFFER))
            else:
                kept_portion = geom  # No mask means we keep the whole geometry.

        # For all other types, use the flatten-and-reassemble strategy.
        else:
            parts_to_process = flatten_geometries(geom)
            if not parts_to_process:
                continue

            kept_sub_parts = []
            if not local_mask:
                kept_sub_parts = parts_to_process
            else:
                # Clip each primitive part (LineString, Point)
                buffered_local_mask = local_mask.buffer(ROBUSTNESS_BUFFER)
                for part in parts_to_process:
                    if not (kept_part := part.difference(buffered_local_mask)).is_empty:
                        kept_sub_parts.append(kept_part)

            if kept_sub_parts:
                kept_portion = unary_union(kept_sub_parts)

        # --- Process results after applying the correct logic ---

        if kept_portion is None or kept_portion.is_empty:
            wholly_removed_indices.append(i)
            removed_parts_map.setdefault(i, []).append(geom)
            continue

        # The result is the final kept geometry
        final_kept_geom = kept_portion
        kept_results.append(final_kept_geom)
        kept_parts_map.setdefault(i, []).append(final_kept_geom)

        # The removed portion is simply the difference between the original and what was kept.
        if not (removed_portion := geom.difference(final_kept_geom)).is_empty:
            removed_parts_map.setdefault(i, []).append(removed_portion)

        # Update the master mask with the buffer of the geometry that was *actually kept*.
        current_mask.append(final_kept_geom.buffer(tolerance))

    return kept_results, kept_parts_map, removed_parts_map, wholly_removed_indices, current_mask


# =============================================================================
#  Single Public-Facing Function
# =============================================================================

def deoverlap(
    geometries: GeomInput,
    tolerance: float,
    preserve_types: bool = False,
    keep_duplicates: bool = False,
    track_origins: bool = False,
    progress_bar: bool = False,
    mask: List[Polygon] = None
) -> Any:
    """De-overlaps a list of geometries, with extensive options for output format.

    This is the main public-facing function that acts as a dispatcher to the
    internal engines based on user-selected flags.

    Args:
        geometries: An iterable of shapely geometries.
        tolerance: The buffer distance to consider geometries as overlapping.
        preserve_types (bool, optional):
            - `False` (Default): Fast mode. Returns a flat list of simple
              LineStrings and Points.
            - `True`: Powerful mode. Returns structured geometries
              (e.g., MultiLineString). Slower but more informative.
        keep_duplicates (bool, optional):
            If `True`, the removed/overlapping portions are also returned.
            Defaults to False.
        track_origins (bool, optional):
            Only applies when `preserve_types=True`. If `True`, returns a
            detailed dictionary with full origin tracking. Defaults to False.
        progress_bar (bool, optional):
            If `True`, displays a tqdm progress bar during processing.
            Defaults to False.
        mask (List[Polygon], optional):
            An optional, pre-existing list of polygon masks. If provided,
            geometries will be de-overlapped against this mask first. This is
            useful for iterative processing or for ensuring consistency across
            multiple, separate calls. The returned mask will include these
            initial polygons. Defaults to None.

    Returns:
        The return type is dynamic and depends on the flags:
        - `preserve_types=False`:
          A tuple `(kept_geoms, {}, removed_geoms, mask)`.
        - `preserve_types=True` and `track_origins=False`:
          A tuple `(kept_geoms, kept_map, removed_geoms, mask)`.
        - `preserve_types=True` and `track_origins=True`:
          A dictionary with keys `("kept", "kept_parts", "removed_parts",
          "wholly_removed_indices", "mask")`.
    """
    # --- Mode 1: Fast, Flat Output ---
    if not preserve_types:
        kept, removed, final_mask = _deoverlap_flat_engine(
            geometries, tolerance, progress_bar, mask=mask
        )
        return kept, {}, (removed if keep_duplicates else []), final_mask

    # --- Mode 2: Structure-Preserving Output ---
    # Ensure geoms is a list for repeatable iteration, which is crucial.
    geom_list = list(geometries)
    kept, kept_map, removed_map, wholly_removed, final_mask = _deoverlap_structured_engine(
        geom_list, tolerance, progress_bar, mask=mask
    )

    # Sub-mode: Return the detailed dictionary with full origin tracking.
    if track_origins:
        return {
            "kept": kept,
            "kept_parts": kept_map,
            "removed_parts": (removed_map if keep_duplicates else {}),
            "wholly_removed_indices": wholly_removed,
            "mask": final_mask
        }
    else:
        # Sub-mode: Return a simplified tuple for compatibility.
        removed_list = []
        if keep_duplicates:
            for parts in removed_map.values():
                removed_list.extend(parts)
        return kept, kept_map, removed_list, final_mask
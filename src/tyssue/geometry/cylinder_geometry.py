"""Geometry of an open tube of cells around the z axis."""

import math
import warnings

import numpy as np

from .planar_geometry import update_boundary_index
from .sheet_geometry import SheetGeometry


class CylinderGeometry(SheetGeometry):
    """Sheet geometry for an open tube around the z axis.

    On top of :class:`SheetGeometry`, `update_all` computes the azimuthal
    tangent of each vertex (`tx, ty, tz`), its distance to the z axis
    (`distance_z_axis`), its deviation from its neighbours (`dx, dy, dz`,
    `dev_length`, read by
    :class:`~tyssue.dynamics.effectors.SurfaceElasticity`) and the lumen volume
    (`settings["lumen_vol"]`), closed by two cones at the open ends.
    """

    @staticmethod
    def update_boundary_index(sheet):
        """Updates the vertex and edge `boundary` columns.

        The face `boundary` column is left unchanged.
        """
        update_boundary_index(sheet, with_faces=False)

    @staticmethod
    def update_tangents(sheet):
        """Writes the unit azimuthal tangent, (x, y, 0) x z, in `tx, ty, tz`."""
        tx = sheet.vert_df["y"].to_numpy(dtype=float)
        ty = -sheet.vert_df["x"].to_numpy(dtype=float)
        with np.errstate(divide="ignore", invalid="ignore"):
            inv_length = 1.0 / np.hypot(tx, ty)
        sheet.vert_df["tx"] = tx * inv_length
        sheet.vert_df["ty"] = ty * inv_length
        sheet.vert_df["tz"] = 0.0

    @staticmethod
    def update_vert_distance(sheet):
        """Writes the distance of each vertex to the z axis in `distance_z_axis`."""
        sheet.vert_df["distance_z_axis"] = np.hypot(
            sheet.vert_df["x"].to_numpy(dtype=float),
            sheet.vert_df["y"].to_numpy(dtype=float),
        )

    @staticmethod
    def update_vert_deviation(sheet):
        """Writes in `vert_df` the deviation of each vertex from the mean
        position of its neighbours: its length in `dev_length` and the unit
        vector from that mean to the vertex in `dx, dy, dz`, as read by
        `SurfaceElasticity`.

        Neighbours linked by an edge in either direction are counted. A vertex
        without neighbours gets a zero deviation.
        """
        vert_df, edge_df = sheet.vert_df, sheet.edge_df
        pos = vert_df[["x", "y", "z"]].to_numpy(dtype=float)
        n_verts = len(pos)
        srce = vert_df.index.get_indexer(edge_df["srce"].to_numpy())
        trgt = vert_df.index.get_indexer(edge_df["trgt"].to_numpy())

        # each (vertex, neighbour) pair once, whichever way the edge runs
        linked = (srce >= 0) & (trgt >= 0) & (srce != trgt)
        s, t = srce[linked].astype(np.int64), trgt[linked].astype(np.int64)
        pairs = np.unique(np.concatenate([s * n_verts + t, t * n_verts + s]))
        vert, neighbor = pairs // n_verts, pairs % n_verts

        neighbor_sum = np.zeros_like(pos)
        np.add.at(neighbor_sum, vert, pos[neighbor])
        degree = np.bincount(vert, minlength=n_verts)
        has_neighbors = degree > 0

        deviation = np.zeros_like(pos)
        deviation[has_neighbors] = (
            pos[has_neighbors] - neighbor_sum[has_neighbors] / degree[has_neighbors, None]
        )
        dev_length = np.linalg.norm(deviation, axis=1)
        grad = np.zeros_like(pos)
        nonzero = dev_length > 0
        grad[nonzero] = deviation[nonzero] / dev_length[nonzero, None]

        vert_df[["dx", "dy", "dz"]] = grad
        vert_df["dev_length"] = dev_length

    @staticmethod
    def update_lumen_vol(sheet):
        """Stores the lumen volume in `settings["lumen_vol"]`.

        The volume enclosed by the faces is closed at each open end by a cone
        whose base is the mean radius of the border vertices on that side
        (z > 0 or z < 0) and whose apex is the origin.
        """
        lumen_pos_faces = sheet.edge_df[["f" + c for c in sheet.coords]].to_numpy()
        lumen_sub_vol = (
            np.sum(lumen_pos_faces * sheet.edge_df[sheet.ncoords].to_numpy(), axis=1) / 6
        )
        lumen_volume_gross = sum(lumen_sub_vol)

        border = sheet.vert_df["boundary"] == 1
        top_verts = sheet.vert_df.loc[border & (sheet.vert_df["z"] > 0)]
        top_radius = top_verts["distance_z_axis"].to_numpy().mean()
        top_height = top_verts["z"].to_numpy().mean()
        top_volume = (1 / 3) * math.pi * top_radius**2 * top_height

        bot_verts = sheet.vert_df.loc[border & (sheet.vert_df["z"] < 0)]
        bot_radius = bot_verts["distance_z_axis"].to_numpy().mean()
        bot_height = -bot_verts["z"].to_numpy().mean()
        bot_volume = (1 / 3) * math.pi * bot_radius**2 * bot_height

        sheet.settings["lumen_vol"] = top_volume + bot_volume + lumen_volume_gross

    @classmethod
    def update_all(cls, sheet):
        super().update_all(sheet)
        cls.update_tangents(sheet)
        cls.update_vert_distance(sheet)
        cls.update_vert_deviation(sheet)
        cls.update_lumen_vol(sheet)


class CylinderGeometryInit(CylinderGeometry):
    """Deprecated alias of :class:`CylinderGeometry`."""

    @classmethod
    def update_all(cls, sheet):
        warnings.warn(
            "CylinderGeometryInit is deprecated, use CylinderGeometry instead.",
            FutureWarning,
            stacklevel=2,
        )
        super().update_all(sheet)

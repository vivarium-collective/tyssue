"""Geometry of a tube of cells around an arbitrary coordinate axis."""

import numpy as np

from .sheet_geometry import SheetGeometry, face_svd_  # noqa: F401


class VesselGeometry(SheetGeometry):
    """Sheet geometry for a vessel (an open tube).

    On top of :class:`SheetGeometry`, `update_all` computes the azimuthal
    tangent of each vertex (`tx, ty, tz`) and its distance to the vessel axis
    (`distance_origin`), with the unit radial vector in the two other
    coordinates (e.g. `ox, oy` for the z axis), as read by
    :class:`~tyssue.dynamics.effectors.VesselSurfaceElasticity`.

    The axis is `settings["axis"]` (one of "x", "y", "z"), "z" by default.
    """

    @staticmethod
    def update_tangents(sheet):
        """Writes the unit tangent (x, y, 0) x z in `tx, ty, tz`.

        This tangent is always computed around the z axis.
        """
        x = sheet.vert_df["x"].to_numpy()
        y = sheet.vert_df["y"].to_numpy()

        # tangent: (x, y, 0) x z
        tx = y
        ty = -x

        length = np.hypot(tx, ty)

        with np.errstate(divide="ignore", invalid="ignore"):
            inv_length = 1.0 / length

        sheet.vert_df["tx"] = tx * inv_length
        sheet.vert_df["ty"] = ty * inv_length
        sheet.vert_df["tz"] = 0.0

    @staticmethod
    def update_vert_distance(sheet):
        """Writes the distance to the vessel axis in `distance_origin` and the
        unit radial vector in `o<u>, o<v>`, u and v being the two other axes."""
        coords = ["x", "y", "z"]
        if "axis" in sheet.settings.keys():
            axis = sheet.settings["axis"]
        else:
            axis = "z"
        coords.remove(axis)
        distances = np.sqrt(
            sheet.vert_df[coords[0]].to_numpy() ** 2
            + sheet.vert_df[coords[1]].to_numpy() ** 2
        )
        sheet.vert_df["distance_origin"] = distances
        sheet.vert_df["o" + f"{coords[0]}"] = sheet.vert_df[f"{coords[0]}"] / distances
        sheet.vert_df["o" + f"{coords[1]}"] = sheet.vert_df[f"{coords[1]}"] / distances

    @classmethod
    def update_all(cls, sheet):
        super().update_all(sheet)
        cls.update_tangents(sheet)
        cls.update_vert_distance(sheet)

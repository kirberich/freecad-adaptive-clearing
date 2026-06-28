"""Test adaptive clearing with a star-shaped pocket to exercise complex pathing."""

import math
import time

from freecad_adaptive_clearing import Adaptive2d, MotionType, OperationType


def star_polygon(cx: float, cy: float, outer_r: float, inner_r: float, points: int):
    """Generate a star-shaped polygon with alternating outer/inner radii."""
    vertices: list[tuple[float, float]] = []
    for i in range(points * 2):
        angle = math.pi / 2 + i * math.pi / points  # start at top
        r = outer_r if i % 2 == 0 else inner_r
        x = cx + r * math.cos(angle)
        y = cy + r * math.sin(angle)
        vertices.append((x, y))
    return vertices


def main() -> None:
    # 5-pointed star inside 100x100mm stock
    star: list[tuple[float, float]] = star_polygon(50, 50, 40, 18, 5)
    stock: list[list[tuple[float, float]]] = [[(0, 0), (100, 0), (100, 100), (0, 100)]]

    a2d = Adaptive2d(
        tool_diameter=5.0,
        step_over_factor=0.15,
        tolerance=0.1,
        stock_to_leave=0,
        force_inside_out=True,
        finishing_profile=True,
        op_type=OperationType.ClearingInside,
    )

    last_progress = [time.time()]

    def progress_cb(paths):
        now = time.time()
        if now - last_progress[0] > 2.0:
            pts = sum(len(p[1]) for p in paths if len(p) > 1)
            print(f"  [{now - last_progress[0]:.0f}s] paths={len(paths)} pts~{pts}")
            last_progress[0] = now
        return False

    print("Star-shaped pocket: 5-point star, 100x100 stock, 5mm tool")
    print(f"Star vertices: {len(star)}")
    t0 = time.time()
    results = a2d.execute(stock, [star], progress_callback=progress_cb)
    elapsed = time.time() - t0
    print(f"Done in {elapsed:.1f}s")

    for i, r in enumerate(results):
        print(
            f"\nRegion {i}: {len(r.adaptive_paths)} segments, area={r.cleared_area:.1f} mm²"
        )
        print(
            f"  Helix: ({r.helix_center_point[0]:.1f}, {r.helix_center_point[1]:.1f})"
        )
        print(f"  Start: ({r.start_point[0]:.1f}, {r.start_point[1]:.1f})")
        cutting_pts = sum(
            len(pts) for mt, pts in r.adaptive_paths if mt == MotionType.Cutting
        )
        link_pts = sum(
            len(pts) for mt, pts in r.adaptive_paths if mt != MotionType.Cutting
        )
        print(f"  Cutting: {cutting_pts} pts, Link: {link_pts} pts")
        print(
            f"  Errors: start={r.start_point_not_found} lead={r.lead_path_failed} "
            f"uncleared={r.uncleared_area_remains} engage={r.too_many_failed_engagements} "
            f"finish_setup={r.failed_to_set_up_finishing_pass} finish_lead={r.finishing_lead_in_failed}"
        )


if __name__ == "__main__":
    main()

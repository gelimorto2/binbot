"""Writes demo/anti_slide_3d.html: interactive three.js demo of the anti-slide / anti-spin systems.
Dimensions are injected from params.py so the demo matches the drawings."""
import json
import params as P

keys = ["TRACK_LEN", "TRACK_H", "TRACK_W", "TRACK_Y", "TRACK_OUTER_W", "BASE_BODY", "BASE_CLEARANCE", "BASE_TOP", "BASE_PLATE",
        "FRAME_LEN", "FRAME_Z0", "FRAME_Z1", "RAIL_Y", "RHS_B", "LIFT_BAR", "LIFT_BAR_Z0", "CELL", "CELL_X", "DECK_LX", "DECK_LY",
        "DECK_H", "DECK_TOP_LOW", "BIN", "BIN_WALL", "EBOX", "EBOX_X0", "EBOX_Z0", "MAST_Y", "ANT_TOP", "ANT", "BEACON",
        "FRONT_BAR", "FRONT_BAR_X0", "FRONT_BAR_Z0", "LIDAR", "ESTOP_BOX", "SPRAG_L", "SPRAG_PIVOT", "SPRAG_Y", "SPRAG_DEPLOY",
        "SPRAG_ARM", "ANCHOR_Y", "ANCHOR_CHAIN", "ANCHOR_CLAW", "ANCHOR_Z0", "SLOPE_MAX", "STEEP_OLIVES", "M_OLIVES"]
params = {k: getattr(P, k) for k in keys}
html = open("demo/template.html").read().replace("__PARAMS__", json.dumps(params))
open("demo/anti_slide_3d.html", "w").write(html)
print("written", len(html), "bytes")

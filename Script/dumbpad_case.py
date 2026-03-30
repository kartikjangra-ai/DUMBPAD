"""
dumbpad_case.py
Parametric build123d model of the Dumbpad macropad case.
"""

from build123d import (
    BuildPart, BuildSketch,
    Box, Cylinder, RectangleRounded, Circle, Polygon,
    Plane, Locations,
    add, extrude, fillet, offset,
    Axis, Mode, Align, MM, export_stl
)
import os

# ─────────────────────────────────────────────────────────

OUTER_W       = 105.0 * MM
OUTER_D       = 86.5 * MM
OUTER_H_TALL  = 18.0 * MM
OUTER_H_SHORT = 8.0 * MM
CORNER_R      = 7.0 * MM
WALL_T        = 3.0 * MM
FLOOR_T       = 1.0 * MM

# Standoff dimensions and asymmetric layout
STANDOFF_R    = 3.0 * MM
STANDOFF_H    = 2.0 * MM   # From floor up
SCREW_R       = 1.0 * MM

MOUNT_X_L     = 9.925 * MM
MOUNT_X_R     = 30.075 * MM
MOUNT_Y       = 19.825 * MM

# Right-based Step cut (if keeping centered layout)
STEP_WIDTH    = 25.647 * MM
CUT_X_POS     = -(OUTER_W / 2) + (STEP_WIDTH / 2)

# Back Wall Rectangular Cutout parameters
SIDE_CUT_L     = 9.5 * MM
SIDE_CUT_DEPTH = 3.0 * MM
SIDE_CUT_OFF   = 9.0 * MM # from the left face

# ─────────────────────────────────────────────────────────
# Model Build
# ─────────────────────────────────────────────────────────

with BuildPart() as case:
    # 1. Base solid block (Centered)
    with BuildSketch() as base_sk:
        RectangleRounded(OUTER_W, OUTER_D, CORNER_R)
    extrude(amount=OUTER_H_TALL)
    
    # 2. Hollow out interior
    with BuildSketch(Plane.XY.offset(OUTER_H_TALL)):
        offset(base_sk.sketch, amount=-WALL_T)
    extrude(amount=-(OUTER_H_TALL - FLOOR_T), mode=Mode.SUBTRACT)
    
    # 3. Step-down through cut on the left side
    with Locations((CUT_X_POS, 0, OUTER_H_SHORT + (OUTER_H_TALL - OUTER_H_SHORT)/2)):
        Box(STEP_WIDTH, OUTER_D + 2.0, OUTER_H_TALL - OUTER_H_SHORT, mode=Mode.SUBTRACT)

    # 4. Standoffs for PCB
    with BuildSketch(Plane.XY.offset(FLOOR_T)):
        with Locations(
            (-MOUNT_X_L,  MOUNT_Y),
            (-MOUNT_X_L, -MOUNT_Y),
            ( MOUNT_X_R,  MOUNT_Y),
            ( MOUNT_X_R, -MOUNT_Y)
        ):
            Circle(STANDOFF_R)
    extrude(amount=STANDOFF_H)

    # 5. M2 screw pilot holes
    with BuildSketch(Plane.XY.offset(FLOOR_T + STANDOFF_H)):
        with Locations(
            (-MOUNT_X_L,  MOUNT_Y),
            (-MOUNT_X_L, -MOUNT_Y),
            ( MOUNT_X_R,  MOUNT_Y),
            ( MOUNT_X_R, -MOUNT_Y)
        ):
            Circle(SCREW_R)
    extrude(amount=-STANDOFF_H, mode=Mode.SUBTRACT)

    # 6. Back wall rectangular cutout
    # Starts 9mm away from the left face. Left face is at X = -(OUTER_W / 2)
    cut_x = -(OUTER_W / 2) + SIDE_CUT_OFF + (SIDE_CUT_L / 2)
    cut_y = (OUTER_D / 2) - (WALL_T / 2)
    cut_z = OUTER_H_SHORT - (SIDE_CUT_DEPTH / 2)
    
    with Locations((cut_x, cut_y, cut_z)):
        # Make the cutter slightly wider than the wall thickness to ensure a clean through-cut
        Box(SIDE_CUT_L, WALL_T + 2.0, SIDE_CUT_DEPTH, mode=Mode.SUBTRACT)

    # 7. Triangular corner steps
    int_w = OUTER_W - 2*WALL_T
    int_d = OUTER_D - 2*WALL_T
    int_r = max(0, CORNER_R - WALL_T)
    leg = 10.0 * MM
    
    with BuildSketch(Plane.XY.offset(FLOOR_T)) as corner_steps:
        with BuildSketch() as inner_profile:
            RectangleRounded(int_w, int_d, int_r)
        
        with BuildSketch() as wedges:
            with Locations(( int_w/2,  int_d/2)):
                Polygon([(0,0), (-leg,0), (0,-leg)], align=None)
            with Locations((-int_w/2,  int_d/2)):
                Polygon([(0,0), ( leg,0), (0,-leg)], align=None)
            with Locations(( int_w/2, -int_d/2)):
                Polygon([(0,0), (-leg,0), (0, leg)], align=None)
            with Locations((-int_w/2, -int_d/2)):
                Polygon([(0,0), ( leg,0), (0, leg)], align=None)
                
        add(inner_profile.sketch)
        add(wedges.sketch, mode=Mode.INTERSECT)
        
    extrude(amount=2.0 * MM)

    # 8. Fillets - Creating the curved "S" profile and pill-shaped cutout
    split_x = -(OUTER_W / 2) + STEP_WIDTH
    
    # A. S-Curve Transition (Horizontal edges at the step)
    # These are the horizontal edges parallel to Y at the top and bottom of the step wall
    trans_h_edges = case.edges().filter_by(Axis.Y).filter_by(lambda e: abs(e.center().X - split_x) < 0.2)
    
    if trans_h_edges:
        try:
            # Large 4.7mm radius for the sweeping curved profile
            fillet(trans_h_edges, radius=4.7)
        except:
            pass

    # B. Side cutout edges (Pill-shaped slot + Top/Bot rims)
    cut_x_center = -(OUTER_W / 2) + SIDE_CUT_OFF + (SIDE_CUT_L / 2)
    
    # 1. Vertical corners (pill-shape)
    c_v = case.edges().filter_by(Axis.Z) \
                      .filter_by(lambda e: abs(e.center().X - cut_x_center) < (SIDE_CUT_L / 2 + 0.5)) \
                      .filter_by(lambda e: abs(e.center().Y - (OUTER_D / 2)) < WALL_T + 1.0)
    if c_v:
        try: fillet(c_v, radius=3.0)
        except: pass

    # 2. Horizontal rims (top at Z=8, bot at Z=5)
    # Filtering for edges near the cutout's X-center and Y-wall plane
    c_h = case.edges().filter_by(Axis.X) \
                      .filter_by(lambda e: abs(e.center().X - cut_x_center) < (SIDE_CUT_L / 2 + 0.5)) \
                      .filter_by(lambda e: abs(e.center().Y - (OUTER_D / 2)) < WALL_T + 1.0) \
                      .filter_by(lambda e: abs(e.center().Z - 8.0) < 0.1 or abs(e.center().Z - 5.0) < 0.1)
    
    if c_h:
        try: fillet(c_h, radius=0.8)
        except: pass

    # C. Top rims (Horizontal edges at Z=18 and Z=8)
    top_rims = case.edges().filter_by(lambda e: abs(e.center().Z - OUTER_H_TALL) < 0.1 or abs(e.center().Z - OUTER_H_SHORT) < 0.1)
    if top_rims:
        try:
            fillet(top_rims, radius=2.5)
        except:
            pass

    # D. Bottom exterior perimeter
    bot_edges = case.faces().sort_by(Axis.Z)[0].edges()
    if bot_edges:
        try: fillet(bot_edges, radius=2.5)
        except: pass

# ─────────────────────────────────────────────────────────

script_dir = os.path.dirname(os.path.abspath(__file__))
output_file = os.path.join(script_dir, "dumbpad_case.s" + "tl")

export_stl(
    case.part, 
    output_file, 
    ascii_format=True,
    tolerance=0.08,
    angular_tolerance=0.3
)

if "show" in globals():
    show(case, names=["Dumbpad Case"])

"""Downtown core: Central Market House, Continental Square and the commercial blocks inside the
creek elbow (x=54..159, y=48..123, excluding the creek walk and rail lane).

Layout follows design/downtown_brief.md section 3.3 with one deliberate change: Beaver St now ends
at Philadelphia St so that it dead-ends on the Market House's front stair (the hall is 30 tiles wide
and the T-junction gives the landmark a street axis, like the George St -> cemetery gate axis).
"""
import random

from PIL import Image, ImageDraw

import buildings as B
import decals as DC
import dress as D
import facades as F
import synth as SY

REGION = (54, 48, 159, 123)
T = 16
OUT = (0x3D, 0x3D, 0x52, 255)


# ------------------------------------------------------------------ helpers
def put_building(L, lib, pid, img, x, y_bottom, depth, solid="all", doors=None):
    """Register `img` as a building whose bottom `depth` rows are its solid footprint; any rows above
    spill north as overhead (tall tops occlude what is behind them, 3/4-view style)."""
    h = img.size[1] // T
    over = max(0, h - depth)
    p = lib.add_img(pid, img, "building", solid, over, doors or [])
    L.place(pid, x, y_bottom - h + 1)
    return p


def place_at_solid(L, pid, tx, ty):
    """Place a prop so that its (first) solid base cell lands on (tx,ty)."""
    p = L.lib[pid]
    sx, sy = sorted(p.solid, key=lambda c: (c[1], c[0]))[0] if p.solid else (0, p.h - 1)
    L.place(pid, tx - sx, ty - sy)


def try_at_solid(L, pid, tx, ty, **kw):
    p = L.lib[pid]
    sx, sy = sorted(p.solid, key=lambda c: (c[1], c[0]))[0] if p.solid else (0, p.h - 1)
    return D.try_place(L, pid, tx - sx, ty - sy, **kw)


def marquee(w=7):
    """Movie-theatre marquee: wedge canopy with chaser bulbs and a blank cream letter board."""
    W, H = w * T, 2 * T
    img = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(img)
    d.polygon([(0, 8), (W - 1, 8), (W - 5, H - 3), (4, H - 3)], fill=(0xB8, 0x2C, 0x2C, 255), outline=OUT)
    d.rectangle([6, 11, W - 7, H - 7], fill=(0xF4, 0xEC, 0xD4, 255), outline=OUT)
    for y in (14, 19):
        for x in range(10, W - 10, 6):
            d.line([x, y, x + 3, y], fill=(0x3A, 0x3A, 0x46, 255))   # unreadable title letters
    for x in range(2, W - 1, 3):
        d.point((x, 8), fill=(0xFF, 0xE8, 0x7A, 255))
        d.point((min(W - 1, x + 1), H - 3), fill=(0xFF, 0xE8, 0x7A, 255))
    d.rectangle([0, 3, W - 1, 8], fill=(0xD8, 0x9C, 0x2C, 255), outline=OUT)
    return img


def blade_sign(h=5):
    """Tall vertical theatre blade sign with bulbs (no lettering)."""
    W, H = T, h * T
    img = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(img)
    d.rectangle([3, 2, 12, H - 4], fill=(0xC8, 0x30, 0x2C, 255), outline=OUT)
    d.rectangle([5, 5, 10, H - 7], fill=(0xF0, 0xC0, 0x3A, 255))
    for y in range(8, H - 9, 6):
        d.rectangle([6, y, 9, y + 3], fill=(0xC8, 0x30, 0x2C, 255))
    for y in range(3, H - 4, 3):
        d.point((3, y), fill=(0xFF, 0xF4, 0xB0, 255))
        d.point((12, y), fill=(0xFF, 0xF4, 0xB0, 255))
    d.polygon([(4, 2), (11, 2), (7, -1 + 1)], fill=(0xF0, 0xC0, 0x3A, 255), outline=OUT)
    return img


def roof_sign(w=8):
    """Hotel rooftop sign: steel frame with a bulb-studded blank board (no lettering)."""
    W, H = w * T, 22
    img = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(img)
    for x in (6, W // 2, W - 8):
        d.line([x, 12, x, H - 1], fill=OUT, width=2)
    d.rectangle([0, 0, W - 1, 13], fill=(0x2A, 0x3A, 0x6A, 255), outline=OUT)
    d.rectangle([3, 3, W - 4, 10], fill=(0xC8, 0x30, 0x2C, 255))
    for x in range(2, W - 1, 3):
        d.point((x, 1), fill=(0xFF, 0xF0, 0xA8, 255))
        d.point((x, 12), fill=(0xFF, 0xF0, 0xA8, 255))
    return img


def parking_stalls(L, x0, x1, y0, y1):
    for x in range(x0, x1 + 1, 3):
        for y in range(y0, y1 + 1):
            L.put("Decals", x, y, DC.parking_tick_v(x, y))


# ------------------------------------------------------------------ ground edits
def build_ground(L, lib):
    # Market House forecourt (brick) + farmers' curb-market wings
    L.fill("plaza", 62, 48, 103, 59)
    # Beaver St no longer runs north of Philadelphia: the old roadbed is part of the forecourt
    # parking lot behind the diner (B-1)
    L.fill("road", 62, 100, 71, 103)
    # alleys behind the King St blocks (brick)
    for (x0, x1) in ((60, 79), (88, 95), (122, 131), (140, 155)):
        L.fill("plaza", x0, 91, x1, 92)
    # back strips: cinders/grass
    for (x0, x1) in ((60, 79), (88, 95), (122, 131), (140, 155)):
        L.fill("grass", x0, 88, x1, 90)
    # depot platform + baggage area
    L.fill("plaza", 112, 120, 133, 121)
    # lawns around the churches
    L.fill("grass", 140, 48, 155, 59)
    # hotel flanks are paved forecourt, not lawn
    L.fill("sidewalk", 114, 48, 115, 59)
    L.fill("sidewalk", 130, 131 - 1, 131, 59) if False else L.fill("sidewalk", 130, 48, 131, 59)
    L.fill("grass", 88, 112, 103, 121)
    # service alley A-1
    L.fill("plaza", 78, 68, 79, 77)


# ------------------------------------------------------------------ build
def build(L, lib):
    rng = random.Random(1962)
    market_house(L, lib)
    block_n0(L, lib)
    block_a(L, lib)
    plazas(L, lib)
    block_b(L, lib)
    block_c(L, lib)
    street_dressing(L, lib, rng)


def market_house(L, lib):
    """Central Market House: the twin-tower Victorian hall re-bricked to York red, with a new central
    pedimented gable, big arched window and round-arched entrance replacing the pack's balcony stair.
    Hall x=69..98 so the gable (cols 13..16) sits exactly on Beaver St's roadway (x=82..85) and the
    2-wide door (x=83..84) closes the street axis."""
    src = lib["cv_vic_twin_tower_hall"]
    img = B.warm_brick(src.img, 0.7).copy()
    brick = (0x77, 0x52, 0x44, 255)
    img.paste((0, 0, 0, 0), (13 * T, 3 * T, 17 * T, 16 * T))
    img.alpha_composite(F.market_gable(brick, 16), (13 * T, 0))
    # green-and-white striped awnings over the ground-floor arched windows
    for cx in F.glass_runs(img, 13 * T + 8, 0, img.size[0]):
        if 13 * T <= cx < 17 * T:
            continue
        aw = F.striped_awning(22)
        img.alpha_composite(aw, (cx - 11, 12 * T + 2))
    put_building(L, lib, "dt_market_house", img, 69, 57, 10, doors=[[14, 15], [15, 15]])
    L.marker("door", 83, 57, building="central_market")
    L.marker("door", 84, 57, building="central_market")
    # curb market on the brick wings: canvas stalls, produce crates, flower buckets (no beach umbrellas)
    west = [("cf_slat_roof_stall", 62, 48), ("cf_slat_roof_stall_drinks", 65, 48), ("sp_market_stand_wood", 62, 53),
            ("sp_crate_open_fruit", 65, 53), ("sp_stand_flowers_tall", 62, 56), ("sp_crate_open_produce_b", 66, 57)]
    east = [("cf_slat_roof_stall", 100, 48), ("sp_market_table_goods", 100, 53), ("sp_crate_open_fruit", 101, 56),
            ("sp_cart_flowers", 99, 56)]
    for pid, x, y in west + east:
        if pid in lib:
            D.try_place(L, pid, x, y, pad=0)
    for x in (64, 68, 99, 103):
        D.try_place(L, "sp_bucket_flowers_red_small" if x % 2 else "sp_bucket_flowers_teal", x, 59, pad=0)
    L.marker("npc", 64, 52, role="farmer_vendor")
    L.marker("npc", 101, 52, role="flower_seller")


def block_n0(L, lib):
    # Hotel Yorktowne stand-in: ONE symmetric 14-wide brick front (bay + mirrored bay), 4 storeys,
    # central entrance, rooftop bulb-frame sign; the tallest building downtown (top spills over the creek)
    bay = B.building(lib, "dt_hotel_bay", ["sf_brick_upper_8windows", "sf_brick_upper_ornate_3windows",
                                           "sf_brick_upper_4tall_windows", "sf_brick_ground_teal_entrance"], 17, "gravel", 5)
    hotel = B.hcat([bay.img, bay.img.transpose(Image.FLIP_LEFT_RIGHT)])
    hotel.alpha_composite(roof_sign(8), (3 * T, 2))
    hotel.alpha_composite(F.striped_awning(2 * T + 8, ((0xB8, 0x2C, 0x2C), (0xF2, 0xEE, 0xE4))), (6 * T - 4, 14 * T + 4))
    put_building(L, lib, "dt_hotel", hotel, 116, 59, 12, doors=[[3, 16], [10, 16]])
    for x in (115, 130):
        D.try_place(L, "rr_potted_plant_tall", x, 58, pad=0)
    if "cv_flagpoles_pair" in lib:
        D.try_place(L, "cv_flagpoles_pair", 114, 50, pad=0)
    # Stone church (St. John's-like): matching stone bell tower + gable-end nave with rose window
    put_building(L, lib, "dt_church1_body", F.church_front(7, 12, "stone"), 145, 59, 12, doors=[[3, 11]])
    put_building(L, lib, "dt_church1_tower", B.stone_steeple(14), 142, 59, 12, doors=[[1, 13]])
    # churchyard: a few old stones + iron fence along the street
    for (pid, x, y) in (("cf_headstone_round_marble", 152, 52), ("cf_headstone_tall_marble_plain", 154, 55),
                        ("cf_headstone_cross_marble", 152, 56), ("nt_s26_tree_medium", 152, 48)):
        if pid in lib:
            D.try_place(L, pid, x, y, pad=0)
    SY.paint_fence(L, [(x, 59) for x in range(152, 156)], "iron")


def block_a(L, lib):
    # A-1 department store (Bon-Ton-like): one symmetric 14-wide, 3-storey front, continuous awning band
    bay = B.building(lib, "dt_dept_bay", ["sf_brick_upper_ornate_3windows", "sf_brick_upper_4tall_windows",
                                          "sf_brick_ground_smallpane_glassdoor"], 12, "tar", 3)
    dept = B.hcat([bay.img, bay.img.transpose(Image.FLIP_LEFT_RIGHT)])
    dept.alpha_composite(F.striped_awning(14 * T, ((0xB8, 0x2C, 0x2C), (0xF2, 0xEE, 0xE4)), 10), (0, 9 * T - 2))
    put_building(L, lib, "dt_dept", dept, 62, 77, 10, doors=[[5, 11], [8, 11]])
    # A-2 five-and-dime: red fascia with gold border over a plain display front (no lettering)
    dime = B.building(lib, "dt_dime", ["sf_brick_upper_teal_bay", "sf_music_store_front"], 10, "tar_red", 4)
    dimg = dime.img.copy()
    dimg.alpha_composite(F.fascia(7), (0, 7 * T - 2))
    put_building(L, lib, "dt_dime_b", dimg, 88, 77, 10, doors=[[3, 9]])
    # A-3 bank on the square: classical granite, 4 columns, pediment, bronze doors (distinct from the courthouse)
    put_building(L, lib, "dt_bank", F.bank_facade(10, 12), 122, 77, 10, doors=[[4, 11], [5, 11]])
    # A-4 county courthouse: full stone/teal front, central copper dome + two small domes
    ch = B.cut_rows(lib["cv_stone_teal_civic_facade"].img, 3, 4)
    ch = ch.copy()
    ch.alpha_composite(B.dome(4, 4), (6 * T, 0))
    small = B.dome(3, 3, drum=False)
    ch.alpha_composite(small, (0 * T + 2, 1 * T))
    ch.alpha_composite(small, (13 * T - 2, 1 * T))
    put_building(L, lib, "dt_courthouse", ch, 140, 77, 10, doors=[[7, 10], [8, 10]])
    for x in (138, 156):
        pass
    # alley A-1 dressing
    for (pid, x, y) in (("sp_trashcan_metal", 78, 69), ("sp_barrel_metal_empty", 79, 71), ("sp_trashcan_green_lid", 78, 74)):
        D.try_place(L, pid, x, y, pad=0)
    # gap between dept store and alley: small newsstand kiosk
    D.try_place(L, "sp_newsbox_tall_a", 76, 75, pad=0)


def plaza(L, lib, x0, y0, north_strip, south_strip, seed, extra=()):
    """1962 quadrant plaza: flower-hedge strips with a walk-through gap, a raised tree planter,
    benches, lamp, bin. x0..x0+7 wide, 10 rows from y0."""
    if north_strip:
        for x in (x0, x0 + 6):
            D.try_place(L, "nt_s17_flower_hedge_box_pink" if seed % 2 else "nt_s17_flower_hedge_box_blue", x, y0, pad=0)
    if south_strip:
        for x in (x0, x0 + 6):
            D.try_place(L, "nt_s17_flower_hedge_box_blue", x, y0 + 8, pad=0)
    D.try_place(L, "sf_tree_round_planter", x0 + 3, y0 + 2, pad=0)
    D.try_place(L, "sf_bench_wood_long", x0, y0 + 4, pad=0)
    D.try_place(L, "sf_bench_wood_long", x0 + 5, y0 + 4, pad=0)
    D.try_place(L, "sy_lamp_iron", x0 + 1, y0 + 6, pad=0)
    D.try_place(L, "sp_trashcan_metal", x0 + 6, y0 + 6, pad=0)
    for pid, rx, ry in extra:
        D.try_place(L, pid, x0 + rx, y0 + ry, pad=0)


def plazas(L, lib):
    plaza(L, lib, 96, 68, True, False, 1, extra=[("sp_newsbox_short_a", 3, 7)])
    plaza(L, lib, 114, 68, True, False, 2, extra=[("sy_phone_booth", 4, 6)])
    plaza(L, lib, 96, 88, False, True, 3, extra=[("sp_mailbox_blue", 3, 6)])
    plaza(L, lib, 114, 88, False, True, 4, extra=[("sf_bench_side_wood", 3, 6)])
    # traffic signals on the four corners of Continental Square
    for pid, tx, ty in (("sp_traffic_signal_right_amber", 104, 79), ("sp_traffic_signal_left_green", 113, 79),
                        ("sp_traffic_signal_diag_right_green", 104, 86), ("sp_traffic_signal_diag_left_red", 113, 86)):
        if pid in lib:
            try_at_solid(L, pid, tx, ty, pad=0)
    L.marker("npc", 108, 82, role="traffic_cop")


def block_b(L, lib):
    # back strips: garages, fences, ash cans, laundry
    SY.paint_fence(L, [(x, 88) for x in range(60, 80) if x not in (66, 67)], "wood")
    SY.paint_fence(L, [(x, 88) for x in range(140, 156) if x not in (147, 148)], "picket")
    for (pid, x, y) in (("sp_laundry_line_clothes_a", 141, 89), ("sp_laundry_line_sheet_b", 150, 89),
                        ("sp_trashcan_green_lid", 62, 90), ("sp_trashcan_green_overflow", 63, 90),
                        ("sp_barrel_rust_trash", 75, 89), ("sp_dumpster_closed", 89, 89),
                        ("sp_trashcan_metal_overflow", 124, 89), ("sp_trashcan_metal", 126, 89),
                        ("sp_laundry_line_clothes_c", 90, 88)):
        D.try_place(L, pid, x, y, pad=0)
    L.marker("secret", 154, 89, id="S7")
    # B-1: diner (1 storey with blue-striped awnings), parking lot, hardware store
    # (shop fronts are cropped below their lettered signs: pictures and awnings stay, words go)
    diner = B.building(lib, "dt_diner_b", ["sf_brick_ground_smallpane_glassdoor"], 6, "tin_green", 7)
    dimg = diner.img.copy()
    dimg.alpha_composite(F.striped_awning(7 * T, ((0x3A, 0x6A, 0xB4), (0xF2, 0xEE, 0xE4)), 10), (0, 3 * T - 2))
    put_building(L, lib, "dt_diner", dimg, 63, 98, 6, doors=[[5, 5]])
    parking_stalls(L, 62, 71, 100, 103)
    for pid, x, y in (("sp_car_sedan_mint_up", 62, 99), ("sp_car_sedan_beige_up", 68, 99)):
        D.try_place(L, pid, x, y, pad=0)
    hw = B.building(lib, "dt_hardware_b", ["sf_brick_upper_4tall_windows", "sf_brick_ground_smallpane_glassdoor"], 9, "tar", 8)
    hwi = hw.img.copy()
    hwi.alpha_composite(F.striped_awning(7 * T, ((0xC8, 0x3A, 0x2C), (0xF2, 0xEE, 0xE4)), 10), (0, 6 * T - 2))
    put_building(L, lib, "dt_hardware", hwi, 72, 103, 9, doors=[[5, 8]])
    for (pid, x, y) in (("sp_wheelbarrow_tools", 72, 104), ("sp_ladder_wood", 79, 102)):
        pass
    # B-2 barber + apartments (3 storeys)
    barber = B.building(lib, "dt_barber_b", ["sf_brick_upper_balcony", "sf_brick_upper_4tall_windows",
                                              "sf_brick_ground_smallpane_glassdoor"], 12, "tar", 9)
    put_building(L, lib, "dt_barber", barber.img, 88, 103, 11, doors=[[5, 11]])
    # SW corner: newsstand + cigar shop (2 storeys) with kiosk out front on the plaza
    news = B.building(lib, "dt_news_b", ["sf_brick_upper_8windows", "sf_shop_vacant_blank_sign_7"], 8, "tar", 10) \
        if "sf_shop_vacant_blank_sign_7" in lib else \
        B.building(lib, "dt_news_b", ["sf_brick_upper_8windows", "sf_brick_ground_arched_door"], 8, "tar", 10)
    put_building(L, lib, "dt_news", news.img, 97, 103, 8, doors=[[3, 7]])
    # SE corner: drugstore with soda fountain (bakery-style sign front reads as a sweet shop)
    drug = B.building(lib, "dt_drug_b", ["sf_brick_upper_ornate_3windows", "sf_brick_ground_teal_entrance"], 8, "tar_red", 11)
    _dimg = drug.img.copy()
    _dimg.alpha_composite(F.striped_awning(7 * T, ((0xE8, 0x9C, 0xB4), (0xF2, 0xEE, 0xE4)), 10), (0, 5 * T - 2))
    drug = lib.add_img("dt_drug_b2", _dimg, "building", "all")
    put_building(L, lib, "dt_drug", drug.img, 114, 103, 8, doors=[[5, 7]])
    # B-3 movie theatre: grand arched upper floor, marquee + blade sign
    th_pieces = ["sf_brick_arched_window_floor", "sf_brick_ground_teal_entrance"]
    th = B.building(lib, "dt_theatre_b", th_pieces, 11, "tar", 12)
    img = th.img.copy()
    img.alpha_composite(marquee(7), (0, 7 * T))
    put_building(L, lib, "dt_theatre", img, 123, 103, 11, doors=[[3, 10]])
    lib.add_img("dt_blade", blade_sign(5), "sign", [[0, 4]], 4)
    L.place("dt_blade", 130, 99)
    D.try_place(L, "cf_wood_kiosk_booth", 122, 101, pad=0)
    # B-4: a full row of brick rowhouses facing King St
    rows, rdoors = B.rowhouse_row(lib, 4, 11, 21)
    rows = F.rowhouse_doors(rows, 4, 11, 21)
    put_building(L, lib, "dt_rows_b4", rows, 140, 103, 11, doors=rdoors)
    # B-3 back lot: a parked sedan and a board fence instead of bare lawn
    D.try_place(L, "sp_car_sedan_silver_left", 125, 88, pad=0)
    SY.paint_fence(L, [(x, 88) for x in range(122, 132) if not 124 <= x <= 130], "wood")


def block_c(L, lib):
    # C-1 / C-4 rowhouses: York red-brick rows with white stoops, facing the rail lane
    def rowhouses(pid, x, n, seed):
        img, doors = B.rowhouse_row(lib, n, 10, seed)
        img = F.rowhouse_doors(img, n, 10, seed)
        put_building(L, lib, pid, img, x, 121, 10, doors=doors)
    rowhouses("dt_rows_c1", 62, 4, 11)
    rowhouses("dt_rows_c1b", 78, 0, 12) if False else None
    rowhouses("dt_rows_c4", 140, 4, 13)
    for x in range(63, 80, 3):
        D.try_place(L, "rr_potted_plant_small", x, 121, pad=0) if (x // 3) % 2 else None
    # C-2 white-steepled Lutheran-type church
    put_building(L, lib, "dt_church2_body", F.church_front(7, 12, "brick"), 93, 121, 10, doors=[[3, 11]])
    put_building(L, lib, "dt_church2_tower", B.white_steeple(12), 90, 121, 10, doors=[[1, 11]])
    for (pid, x, y) in (("nt_s26_tree_medium", 100, 113), ("nt_s26_tree_small", 88, 118), ("sf_bench_wood_small", 101, 119)):
        D.try_place(L, pid, x, y, pad=0)
    # C-3 railroad depot: brick, red tile roof, clock, platform benches and baggage carts
    dep = B.stack([B.gable_roof(14, 5, "red")], lib)
    face = B.hcat([lib["sf_brick_ground_arched_door"].img, lib["sf_brick_ground_teal_entrance"].img])
    depot = Image.new("RGBA", (14 * T, 8 * T))
    depot.alpha_composite(dep, (0, 0))
    depot.alpha_composite(face, (0, 5 * T))
    depot.alpha_composite(F.clock_dormer(4, 3), (5 * T, 0))
    put_building(L, lib, "dt_depot", depot, 115, 119, 8, doors=[[3, 7], [10, 7]])
    # platform canopy on cast-iron posts over the platform (walk-under, drawn above characters)
    can = F.platform_canopy(18, 2)
    for ty in range(2):
        for tx in range(18):
            t = can.crop((tx * T, ty * T, tx * T + T, ty * T + T))
            if t.getchannel("A").getbbox():
                L.put("Overhead", 114 + tx, 120 + ty, t, False)
    for (pid, x, y) in (("sf_bench_wood_long", 113, 120), ("sf_bench_wood_long", 130, 120), ("sp_cart_wood_empty", 128, 113),
                        ("sp_boxes_on_pallet_a", 131, 113), ("sy_lamp_iron", 114, 113)):
        D.try_place(L, pid, x, y, pad=0)
    L.marker("spawn", 121, 122, facing="up")
    L.marker("npc", 118, 122, role="newsboy")


PAVE = {"sidewalk", "plaza", "plaza_grey"}
ROAD = {"road"}


def street_dressing(L, lib, rng):
    # cast-iron lamps along Market St and George St (curb row), hydrants at corners, meters, mailboxes
    for x in range(64, 156, 9):
        for y in (79, 86):
            D.try_place(L, "sy_lamp_iron", x, y - 2, pad=0, kinds=PAVE)
    for y in range(52, 122, 9):
        for x in (105, 112):
            D.try_place(L, "sy_lamp_iron", x, y - 2, pad=0, kinds=PAVE)
    for (x, y) in ((60, 66), (87, 66), (113, 79), (132, 86), (80, 104), (139, 111), (61, 111), (103, 61)):
        D.try_place(L, "sy_hydrant", x, y - 1, pad=0, kinds=PAVE)
    for x in range(66, 102, 4):
        D.try_place(L, "sy_parking_meter", x, 86 - 1, pad=0, kinds=PAVE) if x % 8 == 2 else None
    for (pid, x, y) in (("sp_mailbox_blue", 88, 66), ("sp_newsbox_tall_b", 120, 66), ("sp_mailbox_red", 133, 110),
                        ("sp_trashcan_metal", 112, 104), ("sp_newsbox_short_b", 61, 77)):
        D.try_place(L, pid, x, y - 1, pad=0, kinds=PAVE)
    # wooden utility poles on the side streets (Water, Duke) and the rail lane
    for y in range(70, 120, 12):
        D.try_place(L, "sp_utility_pole_crossarm", 61, y, pad=0, kinds=PAVE)
        D.try_place(L, "sp_utility_pole_crossarm_b", 132, y, pad=0, kinds=PAVE)
    # parked 1960s-ish sedans along the curbs + a bus on Market St
    # parked sedans only in the curb lanes of the 6-lane streets, facing with traffic
    # (Market St: north lane westbound y=80, south lane eastbound y=83; George St: west lane
    # southbound x=106, east lane northbound x=109), well clear of intersections
    for (pid, x, y) in (("sp_car_sedan_beige_left", 64, 80), ("sp_car_sedan_lilac_left", 122, 80),
                        ("sp_car_sedan_mint_right", 89, 83), ("sp_car_sedan_green_right", 145, 83),
                        ("sp_car_sedan_silver_down", 106, 90), ("sp_car_sedan_beige_up", 109, 50)):
        D.try_place(L, pid, x, y, pad=0, kinds=ROAD)
    # sawhorse roadblocks at the east edge
    for y in (62, 81, 84, 107):
        D.try_place(L, "sp_sawhorse_plain", 158, y, pad=0, kinds=ROAD)
    for y in range(62, 66):
        L.extra_solid.add((159, y))
    for y in range(80, 86):
        L.extra_solid.add((159, y))
    for y in range(106, 110):
        L.extra_solid.add((159, y))
    # east border: trees + stone wall
    for y in range(48, 122, 4):
        if not any(a <= y <= b for a, b in ((60, 67), (78, 87), (104, 111))):
            D.try_place(L, "nt_s26_tree_small", 156, y, pad=0, kinds={"grass", "sidewalk"})
    for y in range(46, 124):
        if not any(a <= y <= b for a, b in ((60, 67), (78, 87), (104, 111))):
            L.extra_solid.add((159, y))

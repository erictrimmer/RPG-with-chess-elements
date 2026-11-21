# Downtown Yorktowne: Master Design Brief and Tile Layout

**Level:** Downtown Yorktowne, the first overworld level of *Pawn's Journey*. It is a fictionalized York, Pennsylvania, around 1962-1966.
**Tileset:** LimeZu Modern Exteriors 16x16. Characters are 16x32 and the camera is a 3/4 top-down view, as in Earthbound.
**Map:** 160 x 128 tiles, in 20 chunks of 32x32 (5 columns x 4 rows). The viewport is 480x270, about 30 x 17 tiles.
**Coordinates:** all are inclusive tile coordinates, `x` = column 0..159 and `y` = row 0..127, with (0,0) at top-left. "x=40..55" means columns 40 through 55.
**Status:** this replaces all earlier blockouts and LDtk files. Ignore those.

> 3/4-view rule used everywhere in this brief: **every building shows its SOUTH facade, and doors are on its bottom row.** On an east-west street, the buildings that face the street therefore stand on its **north** side. On the south side the player sees the backs and roofs of the next block, which face the street further south. Each block is planned so that its fronts open onto the street to its south.

---

## 1. Landmark visual signatures (research)

### 1.1 Central Market House (1888, J.A. Dempwolf)
Research findings:
- The building is a large two-storey brick building in the **Romanesque Revival** style. It stands at **Philadelphia and Beaver Streets** on a lot of about 1.3 acres. Its plan is L-shaped, and some sources count five towers in total.
- **Main facade:** two **three-storey square towers with pyramidal roofs** flank the main entrance. Between them is a **central, window-filled gable**. SAH Archipedia notes that this scheme of "great towers either side of a central gable" was later copied by Lancaster's Central Market.
- **Roof:** a hipped roof with **steep gable dormers** and projecting front pieces.
- **Use:** in the 1960s it was a working farmers' market of produce, meats, baked goods and flowers. Interior stalls were still run by county farm families.

Visual signatures for the tile artist:
1. **Two square brick towers**, each 3 tiles wide, run the full height of the building. Each has a **steep pyramidal slate cap** with a small iron finial. Paired round-arched windows sit on each tower stage, with light sandstone belt courses between the stages.
2. A **central front gable**, 4 tiles wide, rises above the main roof between the towers. It has one large **round-arched, multi-pane window** that reads as a fan or rose window.
3. A **round-arched main entrance**, 2 tiles wide, sits on the centre line under the gable. It has dark-green double doors and an arch of light sandstone voussoirs.
4. A **blue-grey slate hipped roof** has 2 steep gable dormers on each side of the central gable.
5. The walls are **warm red brick** with sandstone trim. Ground-floor round-arched windows have **green-and-white striped awnings**.
6. Outside the front are **curb-market stalls**: produce crates, flower buckets, bushel baskets and a farm pickup at the curb. The space reads as busy and agricultural.

Build it from the Victorian brick and slate tower pieces (sheets 159-167), the red-brick hall with arched doorway (39-40) and the market awnings (10-12, 118). Do not use the "MARKET" text signs on sheets 10-12. Take only their awnings and stall fronts.

### 1.2 Codorus Creek through downtown
Research findings:
- After the **1933 flood**, Civil Works Administration crews **straightened, widened and deepened** about 2.25 miles of the creek through York.
- The Army Corps of Engineers then built **flood walls, levees, bank protection and six storm-water pump stations**. The project was authorized by the Flood Control Act of 1936. Walls between Penn St and Tyler Run date from the 1930s-40s, and the Indian Rock Dam upstream was finished in 1942.
- By the 1960s the creek was therefore a **hard-edged flood channel** with high banks and almost no public access.
- It was badly polluted and locally nicknamed **"Inky Stinky"**. In the 1960s, **22 of 40 industrial sites dumped directly into it**.
- There was **no greenway trail** then. The present-day trail is a much later plan. Any 1960s path is a utilitarian levee or maintenance walk.
- Bridges: the **Market St bridge was built in 1951** and the **W Philadelphia St bridge in 1954**. Both were new, plain concrete spans in the 1960s. Market Street has had a crossing since 1743.
- The 1972 Agnes flood is **after** our era, so the town is pre-Agnes.

Visual signatures:
1. A **straight, sunken channel** with **hard grey stone-and-concrete walls**. On east-west stretches the south-facing wall shows its face, 2 tiles tall. On north-south stretches only a concrete coping lip shows.
2. **Dark, murky slate-teal water**, never bright blue. Use subtle dark streaks and a scum line along the walls.
3. **Rusty outfall pipes** in the wall face, each with a dark stain below it.
4. **Low concrete bridges** with plain parapets and 1950s lamp standards on Market St (the main bridge, with a wider deck) and King St. There is also a **riveted steel footbridge**, painted rust-red, at Philadelphia St, and a **black steel railroad trestle** at the south edge.
5. **Levee walks** on top of the walls are concrete or gravel strips behind **pipe railing or chain-link**, with a scrubby grass verge. A small **concrete pump house** has a grated door.
6. A **gravel shoal** sits inside the channel just south of the Market St bridge. It is a hidden spot, reached by service stairs.

### 1.3 York Fairgrounds (York Interstate Fair), Carlisle Ave
Research findings:
- The fair claims to be "America's first fair" (1765). It began on the town commons, today's **Penn Park**.
- It moved in **1888** to a 73-acre site on **Carlisle Avenue**, today 334 Carlisle Ave.
- A **Grandstand was built in 1926**, and **auto racing ran on the track from the 1930s**. Horse racing was also held. The "half-mile" figure comes from the art direction and was not confirmed in sources; treat it as a dirt oval.
- **Memorial Hall** was built in the 1950s, about 1955, as the fair's first all-weather exhibition building, so it was brand-new in the 1960s.
- There are livestock and horse barns. The 1930s-60s midways were lined with sideshows and game and food stands.
- The fair was held in September from 1942 onwards.

Visual signatures:
1. A **main gate**: two square brick pillars carry a wooden or iron arch hung with bunting and pennant strings, with no text. **Ticket booths** stand just inside.
2. The **covered grandstand** is long and roofed, with tiers of wooden bench seats facing the track, steel posts and a pennant on every roof bay.
3. The **dirt oval track** has white wooden rails on both its inner and outer edges. The infield is grass, with a small judges' stand and flagpole.
4. **Memorial Hall** is a 1950s exhibition hall: long and low, with a flat roof, tan brick or block walls, a strip of high windows and wide double doors.
5. **Red gambrel or gable barns** have white trim, with wooden-fence pens, hay bales and a windmill.
6. **The midway** is a packed-dirt avenue. Striped canvas tents line it, along with candy-apple, popcorn and hot-dog stands, ring-toss booths and one large **"big top" tent**. Overhead are strings of light bulbs, and the ground has sawdust, litter and balloons.

### 1.4 Prospect Hill Cemetery, 700 North George St
Research findings:
- The cemetery was chartered in **1849** and the first burial was in 1851. It was laid out as a **Victorian "rural cemetery"**, with curving pathways, irregularly shaped sections, generous lawns and a hillside setting outside the old town.
- It covers more than 100 acres and holds more than 90,000 burials.
- The **main entrance gates are on North George St**, on the west side of the road.
- The **Soldiers' Lot**, from 1862, is a **circular lot on the western slope** about 500 ft NNW of the entrance. It holds 163 Union graves. At its centre is a **15-foot bronze soldier by Martin Milmore (1874)** on a square granite base with **four cannons**. The names are cut into **concentric stone curbs**, and **stone bollards linked by chain** surround the lot.
- Five unknown Confederate soldiers are also buried there.
- One of the cemetery's buildings is among Dempwolf's oldest works.
- The famous **Soldiers & Sailors Monument**, a tall column, is in **Penn Park**, not in the cemetery. We use it there (section 2) so the brief's "Soldiers & Sailors?" note is honoured.

Visual signatures:
1. A **gateway on the George St axis**: two stone piers with a pointed Gothic arch and black iron gates, with **iron fence on a low stone wall** running left and right of it. Use sheet 84.
2. A small **stone gatehouse or office** stands just inside, Gothic with a slate roof. It is our nod to the Dempwolf building, and is artistic licence.
3. The **hillside** has two terraces split by a rocky, grass-topped bank, which uses the cliff autotile. **Stone steps** and **curving gravel carriage roads** climb it.
4. The **Soldiers' Circle** is a round lawn ringed by stone curbs and chain-and-bollard fence. A **green-bronze soldier statue** stands on a grey granite base at the centre, with four small cannons. Use the sheet 77 bronze statue.
5. **Varied monuments**: rounded and square headstones, **white obelisks**, praying angels and urns (sheets 71, 77, 81, 82). A small **Gothic chapel or receiving vault** stands on the upper terrace (84).
6. **Mature trees** (sheets 26-27): broad oaks and dark evergreens give deep shade and fallen leaves. The mood is quiet, not spooky.

### 1.5 Continental Square and downtown character
Research findings:
- Continental Square is the George St x Market St crossing. It was called Centre Square until 1925, and the colonial courthouse and market sheds once stood in it.
- It was a **traffic circle until after WWII**, then traffic ran straight through. In **1962 corner "quadrants" with planters and trees were built**, giving four small plazas, so they are brand-new in our era.
- Buildings around it span several eras: the **Colonial Hotel (1893, Dempwolf)** at 18 S George and **1 N George (1929)**.
- West Market had the **Bon-Ton flagship (1911-12, 100 W Market)**, **Woolworth's**, W.T. Grant's and Kinney Shoes.
- On East Market are the **Hotel Yorktowne (1925)**, about 8 storeys and the tallest landmark, and the domed **York County Courthouse**.
- The 1960s were downtown's last boom. The York Mall opened in 1968 and drew trade away.
- York's look overall: **red-brick rowhouses with stoops**, **2-4 storey brick commercial blocks** with cornices, narrow **brick alleys**, and **church steeples** rising above the roofs.

### Sources
- [York Central Market, Wikipedia](https://en.wikipedia.org/wiki/York_Central_Market)
- [SAH Archipedia, Central Market House](https://sah-archipedia.org/buildings/PA-02-YO20) (facade-scheme quote via search snippet)
- [York Town Square blog, Market House no. 4](https://yorkblog.com/yorktownsquare/2006/04/market-house-no-4-central-mark) (L-shape, five towers)
- [NPS NRHP record](https://npgallery.nps.gov/AssetDetail/NRIS/74001292)
- [York History Center, flooding and the Corps project](https://www.yorkhistorycenter.org/will-new-history-center-impacted-flooding/)
- [DVIDS, Penn St floodwall (1930s-40s walls)](https://www.dvidshub.net/news/391263/army-corps-engineers-awards-contract-replace-floodwall-near-penn-street)
- [Army.mil, Indian Rock Dam 75 years](https://www.army.mil/article/196349/community_celebrates_75_years_of_indian_rock_dam_reducing_flood_risks)
- [Witnessing York, Codorus "Inky Stinky" and greenway](https://www.witnessingyork.com/mapping-meaning/some-see-it-as-a-foul-canal-but-codorus-greenway-will-turn-creek-into-park/)
- [Bridge records: Market St 1951](https://bridgecondition.com/bridge/pennsylvania/pa-000000000038279) and [W Philadelphia St 1954](https://bridgecondition.com/bridge/pennsylvania/pa-000000000038271)
- [York State Fair, Our History](https://www.yorkstatefair.com/p/our-history)
- [Prospect Hill Cemetery, About](https://prospecthill.org/about-us/)
- [Prospect Hill Cemetery, Wikipedia](https://en.wikipedia.org/wiki/Prospect_Hill_Cemetery_(York,_Pennsylvania))
- [NPS, Prospect Hill Soldiers' Lot](https://www.nps.gov/nr/travel/national_cemeteries/pennsylvania/Prospect_Hill_Cemetery_Soldiers_Lot.html)
- [Witnessing York, Continental Square](https://www.witnessingyork.com/mapping-meaning/yorks-continental-square-makeover-to-invite-folks-to-come-there-and-stay-a-while/)
- [SAH Archipedia, Bon-Ton building](https://sah-archipedia.org/node/18849) and [Hotel Yorktowne](https://sah-archipedia.org/buildings/PA-02-YO13)
- [Yorktowne Hotel and 1960s retail flight](https://www.aol.com/yorktowne-hotel-resilience-leads-longevity-080602023.html)

Some details were not verified: the Penn Park Soldiers & Sailors column, the half-mile length of the track, and the cemetery gate design. They are treated as art direction, not fact.

---

## 2. Overall composition

### 2.1 The big idea
**Codorus Creek forms a big reversed "L".** It runs north-south down the west third of the map (x=42..53), turns at an elbow at (42..53, 36..45), and then runs east along the north (y=36..45) to the east edge. The creek cuts the map into two regions:

- **Inside the elbow (south-east, about 100 x 80 tiles): Downtown.** It holds the depot (spawn), Continental Square, Central Market, the commercial blocks, churches, rowhouses and the courthouse. It is warm brick-red.
- **Outside the elbow, an inverted "L" around it.** On the west, across the creek, are the **Fairgrounds** (north) and **Penn Park** (south). Along the north edge, across the creek, are a **candy and barbell factory**, **Prospect Hill Cemetery** on its hill, and **Victorian hilltop houses**.

This geography follows reality, compressed. In York the creek runs north through the west side of downtown, Central Market is NW of the square, the fairgrounds are west across the creek on Carlisle Ave, and North George St runs straight north to Prospect Hill Cemetery.

### 2.2 Player flow
The routes below form a loop, with the bridges as chokepoints.

1. **Spawn** at the **railroad depot platform**, tile (121,122), facing north. The player arrives by train, which suits a "journey".
2. **George St** is the town's spine. It runs straight north from the depot (y=123) to the **cemetery gate** (y=18..23). Walking north, the player passes the theatre and drugstore and reaches **Continental Square** (George x Market, centre at (108.5, 82.5)). That is the first big "town" screen, with four corner plazas, traffic lights, the bank and the crowd.
3. **West on Market St** past the department store and five-and-dime. **North on Beaver St** to **Central Market House** (x=62..79, y=48..57). The market is the hub for the first quest and shops.
4. **Water St and the creek walk.** Cross the wide **Market St bridge** (x=42..53, y=78..87) to **Carlisle Ave**. The **Fair main gate** (x=14..21, y=72..77) is the first gated chokepoint, opened by story. **Penn Park** lies south across Carlisle Ave.
5. **Back loop.** The **west bank path** (x=38..41) runs north to **Parkway Blvd** (y=24..31). Head east along Parkway past the **factory** to the **cemetery gate**, the second gated chokepoint, for example night-only or after a key. Return downtown over the **George St bridge** (x=104..113, y=36..45).
6. The **Philadelphia St steel footbridge** (y=62..65) links Water St to the fair's locked **back gate** (x=36..37, y=63..64). It is a late shortcut.

### 2.3 Sight lines and "far" landmarks
With a 30 x 17 viewport, the reveals are short-range.

- The **George St axis** is the master sight line. As the player walks north, the square appears, then the hotel tower and church steeple framing George St at y=48..59, then the bridge, then the **cemetery gate dead-ending the axis**. The gate is deliberately placed on the axis, which is a liberty: the real gate is beside N George St.
- **Tall elements** are allowed to overhang one or two rows into the sidewalk behind them as *overhead* rows: steeples, the Market towers, the courthouse domes, the hotel's roof sign frame, the factory smokestack and the grandstand roof pennants. Because of the overhang, they peek into view before the player reaches their block.
- From the **Market St bridge** the player sees the fair gate's bunting to the west and the creek's long straight channel north and south.
- From the **NE overlook** (x=140..155, y=2..9) the player looks down over the cemetery wall and the creek. It is a reward spot.

### 2.4 Chunk seams
Seams fall at x = 32, 64, 96, 128 and y = 32, 64, 96. Focal points are kept off them:

| Landmark | Focal point (x,y) | Chunk (cx,cy) |
|---|---|---|
| Continental Square centre | 108.5, 82.5 | (3,2) |
| Market House entrance arch | 70-71, 56-57 | (2,1); the seam x=64 only clips the west tower's outer column, which is acceptable |
| Cemetery gate arch | 107-110, 18-23 | (3,0) |
| Soldiers' Circle statue | 81-82, 3-6 | (2,0) |
| Cemetery chapel | 116-125, 1-7 | (3,0) |
| Grandstand centre | 17.5, 25 | (0,0) |
| Fair main gate | 16-19, 72-77 | (0,2) |
| Courthouse | 140-155, 68-77 | (4,2) |
| Depot / spawn | 114-129, 112-121 | (3,3) |
| Penn Park monument | 16-19, 102-106 | (0,3) |
| Church 1 steeple (east end) | x=99..101 | (3,1); keep the steeple off x=96 |
| Church 2 steeple (west end) | x=90..92 | (2,3) |

### 2.5 Neighbourhood variety
Each area should feel distinct, in the Earthbound way:

- **Downtown core:** dense, warm, busy, with lots of awnings and signs.
- **Rowhouse lanes:** repetitive brick with stoops, laundry and kids' chalk.
- **Creek:** cold, grey, industrial and empty.
- **Fair:** festive colour, canvas and dirt.
- **Penn Park:** soft green and civic.
- **Factory:** soot and corrugated metal.
- **Cemetery:** hushed greens and greys, with height and shade.
- **Hilltop:** a Victorian, slightly well-to-do lookout.

### 2.6 Secrets and rewards
All of them were verified reachable from the spawn by a flood-fill of the layout below.

| # | Where | Tiles | Access |
|---|---|---|---|
| S1 | Gravel shoal in the creek | x=44..46, y=88..99 | Service stairs cut into the west lip at x=42..43, y=92..93 |
| S2 | Grove glade (NW) | glade x=39..40, y=8..9 | 1-tile trail x=40, y=10..21, hidden under tree canopy (overhead) from the factory yard |
| S3 | Factory back corner | x=42..43, y=2..4 | Behind crates in the factory yard |
| S4 | Cemetery receiving vault | door in cliff face x=90..93, y=10..11 | From the lower carriage road |
| S5 | Forgotten mausoleum, cemetery NW | x=66..69, y=2..3 | Upper terrace via the west stairs |
| S6 | NE overlook bench and telescope | item at x=152..153, y=3..4 | Stairs x=146..147, y=10..11 |
| S7 | SE alley dead-end | x=154..155, y=88..90 | East end of the B-4 alley (y=91..92) |
| S8 | Hobo camp by the trestle | x=2..7, y=114..120 (item 4..5, 116..117) | Gap x=6..7, y=116..117 from Penn Park |
| S9 | Track infield judges' stand | x=16..19, y=40..44 | Through the rail gap x=16..19, y=50..55 |

---

## 3. Street grid and blocks (exact coordinates)

Conventions:
- **Sidewalks** are concrete with curbs and are walkable.
- **Roads** are asphalt with dashed centre lines and are walkable. Crosswalks go at every intersection.
- The main streets, Market and George, are 10 wide: 2 sidewalk + 6 road + 2 sidewalk.
- Secondary streets are 8 wide: 2 + 4 + 2.

### 3.1 Roads and walks

| Street | Full rect (incl. sidewalks) | Road surface | Notes |
|---|---|---|---|
| **Market St** (east of creek) / **Carlisle Ave** (west of creek) | x=0..159, y=78..87 | y=80..85 | Main E-W axis. Sidewalks y=78..79 and y=86..87. Sawhorse roadblocks (no text) at x=0..1 and x=158..159. |
| **George St** | x=104..113, y=24..123 | x=106..111, y=26..123 | Main N-S axis. Sidewalks x=104..105 and x=112..113. North end tees into Parkway; the cemetery gate is on its axis. South end: crossbucks at (105,122) and (112,122). The rails are not crossable. |
| **Philadelphia St** | x=54..159, y=60..67 | x=56..159, y=62..65 | Roadblock at x=158..159. West end meets Water St and the footbridge. |
| **King St** | x=38..159, y=104..111 | x=42..159, y=106..109 | Crosses the creek on the King St bridge. Roadblock at x=158..159. |
| **Parkway Blvd** | x=38..159, y=24..31 | x=42..159, y=26..29 | North E-W road along the cemetery front and factory. Roadblock at x=158..159. |
| **Water St** | x=54..61, y=46..123 | x=56..59, y=48..123 | Creek-side street. Its west sidewalk is the inner creek walk (x=54..55). |
| **Beaver St** | x=80..87, y=46..123 | x=82..85, y=48..123 | Dead-ends north at the creek walk (railing). |
| **Duke St** | x=132..139, y=46..123 | x=134..137, y=48..123 | Dead-ends north at the creek walk. |
| Rail-side lane / depot platform | x=54..155, y=122..123 | none | Cobble lane. Brick platform paving at x=114..131. Spawn at (121..122, 122..123). |
| West bank path | x=38..41, y=22..123 | none | x=38..39 gravel, x=40..41 concrete levee top. Chain-link on the fair side. |
| Outer (north) creek walk | x=38..155, y=34..35 | none | Pipe railing drawn on the wall's top edge. |
| Grass verge with street trees | x=42..155, y=32..33 | none | Trees every 6 tiles; trunks are solid. |
| Inner creek walk | x=54..55, y=46..123 and x=54..155, y=46..47 | none | Concrete walk with pipe railing. |
| Brick service alleys (row B) | y=91..92 within x=60..79, 88..95, 140..155 | none | York-style alleys behind the King St buildings. Garages, ash cans and fences sit at y=88..90. |
| Service alley (A-1) | x=78..79, y=68..77 | none | Narrow N-S alley between the department store and Beaver St. |

### 3.2 Codorus Creek (sunken channel)
Use the **concrete-top cliff autotile** so the bed reads as lower ground, and the **water autotile** for the water itself.

| Part | Rect | Collision |
|---|---|---|
| North wall face (south-facing stone, 2 rows visible) | x=42..159, y=36..37 | solid |
| West lip / coping | x=42..43, y=36..127 | solid |
| Water, vertical arm | x=44..51, y=38..127 | solid |
| Water, horizontal arm (exits the east edge) | x=44..159, y=38..43 | solid |
| East lip (inner bank) | x=52..53, y=44..127 | solid |
| South lip (inner bank) | x=52..159, y=44..45 | solid |
| Elbow | outer corner at (42..43, 36..37), inner corner at (52..53, 44..45) | Round both with the autotile corner pieces |
| Gravel shoal (secret S1, lower level, walkable) | x=44..46, y=88..99, stairs x=42..43, y=92..93 | walkable |

**Bridges.** Each deck is at street level. Parapets sit on the outer rows/columns of the deck and are solid.

| Bridge | Rect | Walkable deck | Style |
|---|---|---|---|
| **Market St** | x=42..53, y=78..87 | y=79..86 | Wide 1951 concrete bridge. Plain parapets y=78 and y=87, a 1950s lamp standard at each end (x=42, x=53 on both parapets), sidewalks continuous. |
| **King St** | x=42..53, y=104..111 | y=105..110 | Concrete with iron pipe railings. |
| **George St** | x=104..113, y=36..45 | x=105..112 | Concrete. Parapets x=104 and x=113. Lamp standards at the four corners. |
| **Philadelphia St footbridge** | x=42..53, y=62..65 | y=63..64 | Riveted steel truss, rust-red, pedestrians only. Rails y=62 and y=65. |
| Rail trestle | x=42..53, y=124..126 | not walkable | Black steel girders over the water. |

### 3.3 Downtown blocks (inside the elbow)
The rows are:
- **N0**: y=48..59, fronts face Philadelphia St.
- **A**: y=68..77, fronts face Market St.
- **B**: y=88..103, fronts face King St, with an alley behind.
- **C**: y=112..121, fronts face the rail lane.

The columns are:
- **1**: x=60..79, Water St to Beaver St.
- **2**: x=88..103, Beaver St to George St.
- **3**: x=114..131, George St to Duke St.
- **4**: x=140..155, Duke St to the east edge. The east border is x=156..159 (trees and a stone wall).

| Block | Rect | Contents |
|---|---|---|
| **N0-1** | x=60..79, y=48..59 | **Central Market House**, x=62..79, y=48..57 (18x10). West tower x=62..64, east tower x=77..79, both full height with pyramidal slate caps at y=48..50. Centre section x=65..76: slate hipped roof y=50..53 with gable dormers at x=66..67 and x=74..75; central gable x=69..72 rising to y=49 with a big arched window; entrance arch doors at **(70..71, 56..57)**. Front apron y=58..59 (brick): stalls, crates, flower buckets. x=60..61 is sidewalk. |
| **N0-2** | x=88..103, y=48..59 | **Church 1** (St. John's-type stone Episcopal): body x=90..98, **steeple tower x=99..101** (spire overhangs into the creek walk as overhead rows). Grass churchyard at x=88..89 and x=102..103 with a few old headstones and an iron fence. Door on the south. |
| **N0-3** | x=114..131, y=48..59 | **Hotel Yorktowne-type tall brick hotel**, x=116..129 (14 wide, about 8 storeys compressed to 12 rows). Stacked brick floors (sheets 44-45), stone base, flag poles, revolving or double door at x=122..123, y=59. A rooftop sign frame with lights only, no lettering. |
| **N0-4** | x=140..155, y=48..59 | **Fire station**, x=142..153, y=50..57 (red brick, 2 bays, sheet 79). Concrete apron y=58..59 with a 1960s red fire engine. Lawn and flagpole around it. |
| **A-1** | x=60..79, y=68..77 | **Department store** (Bon-Ton-like), x=62..77, 4 storeys: brick, big display windows at street level, a striped awning band, and a cornice. N-S service alley x=78..79. |
| **A-2** | x=88..95, y=68..77 | **Five-and-dime** (Woolworth's-like): red fascia band, gold trim, deep display windows, 2-3 storeys of brick above. |
| **NW plaza** | x=96..103, y=68..77 | 1962 quadrant plaza. Planter and hedge strip at y=68..69 with a walk-through gap at x=98..101. Paving y=70..77, one raised tree planter (2x2, solid) at x=99..100, y=72..73, two benches, a lamp, a trash can and a newspaper box. |
| **NE plaza** | x=114..121, y=68..77 | Mirror of the NW plaza. Strip gap x=116..119, planter x=117..118, y=72..73, plus a phone booth. |
| **A-3** | x=122..131, y=68..77 | **Bank on the square**: stone, 4 columns, pediment, bronze doors at x=126..127 (from sheet 41's classical facade, cropped to 10 wide). |
| **A-4** | x=140..155, y=68..77 | **County Courthouse**: buff stone, a 6-column portico at the centre (x=144..151), green copper domes at x=141..143 and x=152..154, and a central cupola. The domes overhang 2 rows into the Philadelphia St sidewalk as overhead rows. Wide steps down to the Market sidewalk. |
| **B-1** | x=60..79, y=88..103 | y=88..90: garages, fences, ash cans; y=91..92: brick alley. **Diner** (stainless or red-and-cream railcar style, sheet 89), x=62..71, y=93..99. **Parking lot** x=62..71, y=100..103 with 3 classic cars. **Hardware store** x=72..79, y=93..103 (sheet 116 striped awning, using the hammer pictogram). x=60..61 is a grass strip. |
| **B-2** | x=88..95, y=88..103 | Same back strip and alley. **Barber shop and apartments**, x=88..95, y=93..103 (3-storey brick, barber pole). |
| **SW plaza** | x=96..103, y=88..95 | Quadrant plaza (the alley y=91..92 runs into it): bus-stop bench, mailbox, planter tree at x=99..100, y=90..91. |
| **SW corner shop** | x=96..103, y=96..103 | **Newsstand and cigar shop**: 2-storey brick, magazine racks at the front. |
| **SE plaza** | x=114..121, y=88..95 | Quadrant plaza: planter tree, benches, traffic-signal pole, drinking fountain. |
| **SE corner shop** | x=114..121, y=96..103 | **Drugstore with soda fountain**: pastel awning, mortar-and-pestle pictogram. |
| **B-3** | x=122..131, y=88..103 | Back strip y=88..90, alley y=91..92 (it dead-ends at the theatre). **Movie theatre**, x=122..131, y=93..103: tall vertical blade sign with bulbs (no lettering), a triangular marquee with chasing bulbs, poster cases and a ticket booth. |
| **B-4** | x=140..155, y=88..103 | Back yards y=88..90 with laundry lines and secret S7 at x=154..155. Alley y=91..92. **Rowhouses**, x=140..155, y=93..103 (4 houses of 4 wide, or 2 doubles of 8): red brick, white stoops, 2.5 storeys. |
| **C-1** | x=60..79, y=112..121 | **Rowhouses**, x=62..79 (3 houses of 6 wide), facing the rail lane. Stoops, porch awnings, a milk crate at each door. x=60..61 is grass. |
| **C-2** | x=88..103, y=112..121 | **Church 2** (Christ Lutheran-type): brick body x=93..101 with **white wooden steeple x=90..92**, which overhangs King St's south sidewalk as overhead rows. Lawn x=88..89 and x=102..103. |
| **C-3** | x=114..131, y=112..121 | **Railroad depot**, x=114..129: brick, a deep platform canopy on the south, a bay window, and a clock. Doors at **x=121..122, y=121**. Lawn x=130..131 with a baggage cart. |
| **C-4** | x=140..155, y=112..121 | **Rowhouses**, 2 doubles of 8 wide, facing the rail lane. |
| Rails | x=0..159, y=124..126 | Solid. Map border y=127 (ballast and fence). |

### 3.4 West of the creek: Fairgrounds (x=0..37, y=0..77)
- **Border:** trees at x=0..1 and y=0..1.
- **East fence:** x=36..37, y=2..77, chain-link painted green. The **back gate** is at x=36..37, y=63..64, locked.
- **South fence:** y=76..77, x=2..35, picket fence with an ornamental top.
- **Main gate**, centred on the midway: pillars x=14..15 and x=20..21 (y=72..77, solid). The walkable opening is x=16..19. Its arch and bunting form overhead rows y=72..74.

| Zone | Rect | Contents |
|---|---|---|
| Barns | x=2..15, y=3..15 | Two **red barns** facing south (x=2..8 and x=9..15; sheets 73/168/169), hay bales, windmill. |
| Pens and barnyard | x=2..7, y=16..19 (fenced pens); x=8..15, y=16..19 (dirt yard) | Wooden fences (sheet 170), troughs, a tractor. |
| **Memorial Hall** | x=18..33, y=5..15 | 1950s exhibition hall: low, flat roof, tan brick, double doors at x=25..26, y=15, flagpole. |
| **Grandstand** | x=6..29, y=20..29 | Covered grandstand facing south onto the track. Bench tiers use sheet 55 rows, the roof uses sheet 105 truss pieces, and pennants run along the roof. The front rail row is y=29. |
| **Track** | ellipse ring centred (17.5, 42.5), outer radii 16 x 13, inner radii 12 x 9 (about x=2..33, y=30..55) | Packed-dirt band (walkable) with white rails on the inner and outer edges (solid). The rail gap at x=16..19 on the south straight is the midway crossing. |
| Infield | inside the ring, about x=6..29, y=34..51 | Grass, **judges' stand and flagpole** at x=16..19, y=40..44 (secret S9). |
| **Midway** | x=2..35, y=56..75 | Packed dirt. **Avenue** x=16..19 from the gate north to the track crossing. West stands at x=3..13, y=58..61, 64..67 and 70..71: food stands (sheet 31) and game booths. **Big top tent** x=23..34, y=58..68 (sheet 130 recoloured to red/white stripes). East stands x=22..34, y=71..73. Ice-cream truck (sheet 32) and a ticket booth by the gate. Light-bulb strings overhead. |

### 3.5 West of the creek: Penn Park (x=0..37, y=88..123)

| Item | Rect |
|---|---|
| North hedge (gap x=16..19) | x=2..37, y=88..89 |
| East hedge (gap y=106..109 to the King St bridge path) | x=36..37, y=88..121 |
| South fence (rails beyond) | x=0..37, y=122..123 |
| N-S gravel path | x=16..19, y=90..121 |
| E-W gravel path | x=2..35, y=104..107 |
| Round paved plaza | x=13..22, y=100..109 |
| **Soldiers & Sailors column** (tall column on a plinth with a statue on top, sheet 71 column + 77 statue, overhead top) | x=16..19, y=102..106 |
| Duck pond (flat water autotile) | x=4..11, y=92..99 |
| Bandstand / gazebo (white, octagonal feel) | x=24..31, y=92..98 |
| Flood pump house (concrete, grated door, faces south) | x=30..35, y=113..119 |
| Hobo camp (S8): campfire, crates, bedroll | trees x=2..7, y=114..120 |

### 3.6 North band (across the horizontal creek arm)

| Zone | Rect | Contents |
|---|---|---|
| Grove + glade (S2) | x=38..41, y=2..21 | Dense trees; hidden trail x=40, y=10..21. |
| **Factory yard** | x=42..63, y=2..23 | Concrete yard, crates, drums, pallets, a 1960s delivery truck at the y=22..23 loading dock. |
| **Factory** (candy and barbell works, a "Muscletown"/peppermint-pattie nod) | x=44..61, y=10..21 | Brick mill, sawtooth roof, loading doors at y=21. **Smokestack** at x=58..59 rises over the yard as overhead rows. Wooden **water tanks** x=54..61, y=3..8 (sheet 56). |
| **Cemetery** | x=64..135, y=2..23 | See the sub-table below. |
| Hilltop houses | x=136..155, y=2..23 | Cliff face y=10..11 with stairs at x=146..147. **Victorian house 1** x=137..145, y=12..21 and **house 2** x=148..155, y=13..21 (sheets 141/167). Path x=146..147, y=12..23. **Overlook** paved x=140..155, y=2..9: bench, coin telescope, S6 item at x=152..153, y=3..4. |

**Prospect Hill Cemetery detail:**
- **Walls:** stone wall with iron fence at x=64..65 and x=134..135 (y=2..23), and along the south at y=22..23 (x=64..135). The **gate opening** is x=107..110.
- **Gate structure:** x=105..112, y=18..23. The piers at x=105..106 and x=111..112 are solid. The Gothic arch forms overhead rows y=18..20.
- **Terraces:** the lower terrace is y=12..21. The cliff face (grass-top rocky wall) is y=10..11, x=66..133. The upper terrace is y=2..9.
- **Stairs:** x=70..73, x=106..111 (grand axial stair) and x=126..129, all at y=10..11.
- **Carriage roads (gravel):**
  - Axis: x=107..110, y=12..21.
  - Lower loop: y=12..13, x=70..129.
  - Upper loop: y=8..9, x=70..129.
  - The implementer should wiggle the loops by about 1 tile with curved path pieces, but keep them continuous.
- **Gatehouse:** x=114..121, y=14..19, door on the south at about (117, 19).
- **Soldiers' Circle:** x=76..87, y=2..7. A gravel ring with a lawn inside (x=78..85, y=3..6). The **bronze soldier on its granite base** is at x=81..82, y=3..6, and four cannons sit at the ring's diagonal points. Stone bollards with chain run around the outside.
- **Chapel:** x=116..125, y=1..7, door at about (120,7), opening onto the upper loop.
- **Receiving vault (S4):** an iron door in the cliff face at x=90..93, y=10..11.
- **Mausoleum (S5):** x=66..69, y=2..3.
- **Monument fill:** the remaining grass areas get irregular clusters of 6-15 headstones in loose curved rows that follow the roads. Add 4-6 white obelisks (one tall one at about (96,15)), 3-4 angels or urns, and 2 family plots with low iron fences. About a third of the area should stay open lawn.
- **Trees:** around 25 big trees in total, with more on the upper terrace. Mix broad oaks with dark conifers.

---

## 4. ASCII map (1 char = 2x2 tiles; 80 cols x 64 rows)

The column ruler shows tile x (hundreds, tens, units) every 10 tiles. The row label is the tile y of the top row of each 2x2 cell. This map was generated from the same rectangles as section 3, so where they disagree, the rectangles win.

```
x=    0    0    0    0    0    0    0    0    0    0    1    1    1    1    1    1    
      0    1    2    3    4    5    6    7    8    9    0    1    2    3    4    5    
      0    0    0    0    0    0    0    0    0    0    0    0    0    0    0    0    
y  0  TTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTVVVVVTTTTTTTTTTTTTTTTT
y  2  TRRRRRRR""""""""""fTT*.....####.f**+++gg**gg++++++++++++++VVVVV++++f""......*.TT
y  4  TRRRRRRR"EEEEEEEE"fTT*.....####.f+++++g+**+g++++++++++++++VVVVV++++f""......*.TT
y  6  TRRRRRRR"EEEEEEEE"fTT......####.f+++++gg**gg++++++++++++++VVVVV++++f""........TT
y  8  TRRRRRRR"EEEEEEEE"f**......####.f++gggggggggggggggggggggggggggggg++f""........TT
y 10  TRRRRRRR"EEEEEEEE"fTT.XXXXXXXXX.f^^ss^^^^^^^^**^^^^^^sss^^^^^^^ss^^f^^^^^s^^^^TT
y 12  TRRRRRRR"EEEEEEEE"fTT.XXXXXXXXX.f++gggggggggggggggggggggggggggggg++f#####g####TT
y 14  TRRRRRRR"EEEEEEEE"fTT.XXXXXXXXX.f++++++++++++++++++++ggg+LLLL++++++f#####g####TT
y 16  Tfffmmmm""""""""""fTT.XXXXXXXXX.f++++++++++++++++++++ggg+LLLL++++++f#####g####TT
y 18  Tfffmmmm""""""""""fTT.XXXXXXXXX.f+++++++++++++++++++**g**LLLL++++++f#####g####TT
y 20  T""GGGGGGGGGGGG"""fTT.XXXXXXXXX.f+++++++++++++++++++**g**++++++++++f#####g####TT
y 22  T""GGGGGGGGGGGG"""f.............ffffffffffffffffffff**g**fffffffffff"""""g""""TT
y 24  T""GGGGGGGGGGGG"""f...........................................................TT
y 26  T""GGGGGGGGGGGG"""f..===============================.===.======================x
y 28  T""GGGGGGGGGGGG"""f..===============================.===.======================x
y 30  T""""oooooooo"""""f..................................===......................TT
y 32  T""oooooooooooo"""f..""""""""""""""""""""""""""""""".===."""""""""""""""""""""TT
y 34  T"ooooo""""ooooo""f..................................===......................TT
y 36  T"ooo""""""""ooo""f..WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWBBBBBWWWWWWWWWWWWWWWWWWWWWTT
y 38  Tooo""""""""""ooo"f..W~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~BBBBB~~~~~~~~~~~~~~~~~~~~~~~
y 40  Too"""""**"""""oo"f..W~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~BBBBB~~~~~~~~~~~~~~~~~~~~~~~
y 42  Too"""""**"""""oo"f..W~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~BBBBB~~~~~~~~~~~~~~~~~~~~~~~
y 44  Too"""""**"""""oo"f..W~~~~WWWWWWWWWWWWWWWWWWWWWWWWWWBBBBBWWWWWWWWWWWWWWWWWWWWWTT
y 46  Tooo""""""""""ooo"f..W~~~~W..........................===......................TT
y 48  T"ooo""""""""ooo""f..W~~~~W.==.MMMMMMMMM.==."CCCCCC".===."YYYYYYY".==.""""""""TT
y 50  T"ooooo"mm"ooooo""f..W~~~~W.==.MMMMMMMMM.==."CCCCCC".===."YYYYYYY".==."FFFFFF"TT
y 52  T""ooooommooooo"""f..W~~~~W.==.MMMMMMMMM.==."CCCCCC".===."YYYYYYY".==."FFFFFF"TT
y 54  T""""ooommooo"""""f..W~~~~W.==.MMMMMMMMM.==."CCCCCC".===."YYYYYYY".==."FFFFFF"TT
y 56  Tmmmmmmmmmmmmmmmmmf..W~~~~W.==.MMMMMMMMM.==."CCCCCC".===."YYYYYYY".==."FFFFFF"TT
y 58  T######mmmm#######f..W~~~~W.==...........==."CCCCCC".===."YYYYYYY".==."......"TT
y 60  T######mmmm#######f..W~~~~W.==...........==..........===...........==.........TT
y 62  Tmmmmmmmmmm#######*..BBBBBB.==.=========.==.========.===.=========.==.=========x
y 64  T######mmmm#######*..BBBBBB.==.=========.==.========.===.=========.==.=========x
y 66  T######mmmm#######f..W~~~~W.==...........==..........===...........==.........TT
y 68  Tmmmmmmmmmm#######f..W~~~~W.==.########a.==.####TppT.===.TppTKKKKK.==.QQQQQQQQTT
y 70  T######mmmm#######f..W~~~~W.==.########a.==.####pppp.===.ppppKKKKK.==.QQQQQQQQTT
y 72  Tmmmmmmmmmm#######f..W~~~~W.==.########a.==.####pppp.===.ppppKKKKK.==.QQQQQQQQTT
y 74  Tmmmmmmmmmmmmmmmmmf..W~~~~W.==.########a.==.####pppp.===.ppppKKKKK.==.QQQQQQQQTT
y 76  Tffffff*mm*ffffffff..W~~~~W.==.########a.==.####pppp.===.ppppKKKKK.==.QQQQQQQQTT
y 78  x....................BBBBBB.==...........==..........===...........==.........TT
y 80  x====================BBBBBB.==.=========.==.========.===.=========.==.=========x
y 82  x====================BBBBBB.==.=========.==.========.===.=========.==.=========x
y 84  x====================BBBBBB.==.=========.==.========.===.=========.==.=========x
y 86  x....................BBBBBB.==...........==..........===...........==.........TT
y 88  Tfffffffggfffffffff..Wg~~~W.=="""""""""".==.""""pppp.===.pppp""""".==."""""""*TT
y 90  T"""""""gg""""""""f..Wg~~~W.==aaaaaaaaaa.==.aaaapppp.===.ppppaaaaa.==.aaaaaaa*TT
y 92  T"~~~~""gg""####""f..sg~~~W.==a#########.==.####pppp.===.ppppPPPPP.==.hhhhhhhhTT
y 94  T"~~~~""gg""####""f..Wg~~~W.=="#########.==.####pppp.===.ppppPPPPP.==.hhhhhhhhTT
y 96  T"~~~~""gg""####""f..Wg~~~W.=="#########.==.########.===.####PPPPP.==.hhhhhhhhTT
y 98  T"~~~~""gg""####""f..Wg~~~W.=="#########.==.########.===.####PPPPP.==.hhhhhhhhTT
y100  T"""""......""""""f..W~~~~W.=="kkkkk####.==.########.===.####PPPPP.==.hhhhhhhhTT
y102  T"""""..**..""""""f..W~~~~W.=="kkkkk####.==.########.===.####PPPPP.==.hhhhhhhhTT
y104  Tgggggg.**.gggggggf..BBBBBB.==...........==..........===...........==.........TT
y106  Tgggggg.**.gggggggg..BBBBBB.==.=========.==.========.===.=========.==.=========x
y108  T"""""......""""""g..BBBBBB.==.=========.==.========.===.=========.==.=========x
y110  T"""""""gg""""""""f..BBBBBB.==...........==..........===...........==.........TT
y112  T"""""""gg"""""###f..W~~~~W.=="hhhhhhhhh.==."CCCCCC".===.DDDDDDDD".==.hhhhhhhhTT
y114  TTTT""""gg"""""###f..W~~~~W.=="hhhhhhhhh.==."CCCCCC".===.DDDDDDDD".==.hhhhhhhhTT
y116  TT*g""""gg"""""###f..W~~~~W.=="hhhhhhhhh.==."CCCCCC".===.DDDDDDDD".==.hhhhhhhhTT
y118  TTTT""""gg"""""###f..W~~~~W.=="hhhhhhhhh.==."CCCCCC".===.DDDDDDDD".==.hhhhhhhhTT
y120  TTTT""""gg""""""""f..W~~~~W.=="hhhhhhhhh.==."CCCCCC".===.DDDDDDDD".==.hhhhhhhhTT
y122  fffffffffffffffffff..W~~~~W.==...........==..........===....SS.....==.........TT
y124  HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH
y126  HHHHHHHHHHHHHHHHHHHHHW~~~~WHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH
```

Legend:

| Char | Meaning | Collision |
|---|---|---|
| `=` | asphalt road | walk |
| `.` | sidewalk, concrete walk, platform, paved yard | walk |
| `"` | grass / lawn | walk |
| `a` | brick alley | walk |
| `p` | plaza paving (1962 quadrants) | walk; planters solid |
| `k` | parking lot | walk |
| `g` | gravel path / carriage road | walk |
| `s` | stairs | walk |
| `m` | fair packed dirt / midway | walk |
| `o` | race track dirt | walk; rails solid |
| `+` | cemetery lawn with graves | walk; stones solid |
| `B` | bridge deck | walk; parapets solid |
| `~` | water | solid |
| `W` | flood wall face / coping lip | solid |
| `^` | cliff face (cemetery and hilltop bank) | solid |
| `T` | trees / hedge / border | solid trunks |
| `f` | fence / hedge / wall line | solid |
| `H` | railroad tracks / trestle | solid |
| `x` | roadblock sawhorses at the map edge | solid |
| `#` | generic building (shops, booths, rowhouse-like) | solid |
| `h` | rowhouses | solid |
| `M` | Central Market House | solid |
| `C` | church | solid |
| `Y` | tall hotel | solid |
| `F` | fire station | solid |
| `K` | bank | solid |
| `Q` | courthouse | solid |
| `P` | movie theatre | solid |
| `D` | railroad depot | solid |
| `X` | factory | solid |
| `V` | cemetery chapel | solid |
| `L` | cemetery gatehouse | solid |
| `G` | grandstand | solid |
| `E` | Memorial Hall | solid |
| `R` | barns | solid |
| `*` | focal prop or secret (gate piers, statue, monument, item spot) | per prop |
| `S` | spawn | walk |

### Chunk contents (cx = x/32, cy = y/32)

| | cx0 (x0-31) | cx1 (x32-63) | cx2 (x64-95) | cx3 (x96-127) | cx4 (x128-159) |
|---|---|---|---|---|---|
| **cy0** (y0-31) | barns, Memorial Hall, grandstand | fair east edge, grove (S2), factory (S3), Parkway W | cemetery W: Soldiers' Circle, vault (S4), mausoleum (S5) | cemetery gate, gatehouse, chapel, George/Parkway T | cemetery E wall, Victorian houses, overlook (S6) |
| **cy1** (y32-63) | track and infield (S9), midway N | creek elbow, west path, footbridge, Market House W tower | Market House, Beaver St, Church 1 body | Church 1 steeple, hotel, George bridge | fire station, Duke St, creek exits east |
| **cy2** (y64-95) | midway, fair gate, Carlisle Ave, park N hedge | Market bridge, shoal (S1), Water St, dept store | dept store, five-and-dime, Beaver St | **Continental Square**, plazas, bank | courthouse, rowhouse backs, S7 |
| **cy3** (y96-127) | Penn Park, monument, hobo camp (S8), pump house | King bridge, trestle, rowhouses C-1 | diner, hardware, barber, Church 2 | **depot / spawn**, theatre, drugstore, newsstand | rowhouses B-4 / C-4 |

---

## 5. 1960s dressing list per district
Global era rules:
- **No** modern SUVs, satellite dishes, solar panels, EV chargers, LED screens, graffiti, plastic playgrounds or glass towers.
- Cars should be rounded sedans, wagons and pickups in two-tone pastels (mint, cream, coral, sky). Recolour the sheet 59 cars and avoid the angular ones.
- Signs are **pictograms, colour fields, stripes and bulbs only, with no readable text**.
- Streets get wooden utility poles with crossarms (sheet 30), cast-iron or 1950s cobra-head lamps, fire hydrants, blue mailboxes, phone booths, newspaper boxes, **parking meters** and corner trash cans.

- **Continental Square and Market St:**
  - Traffic-signal poles at all 4 plaza corners, plus a policeman or crossing guard (NPC).
  - Planter trees, benches, pigeons, a bus-stop bench, a shoeshine stand.
  - Striped awnings (red/white, green/white) on every shop, display windows with mannequins, a sidewalk sale rack in front of the five-and-dime.
  - Bunting on the bank and courthouse, 2-3 parked cars per block face along the curbs.
- **Central Market:** produce crates (apples, corn, pumpkins), bushel baskets, flower buckets, a scale on a stand, a farm pickup with crates in the bed, a hand cart, an Amish-style buggy hitched at the curb (a York County touch), a chalkboard price board with scribbles only.
- **Rowhouse lanes (C-1, B-4, C-4):** white marble stoops (a York and Baltimore hallmark), milk crates and bottles, porch awnings, window boxes, laundry lines in the back yards, ash cans in the alley, a kid's bicycle, a hopscotch decal, a cat, garden gnomes.
- **Depot / rail lane:** baggage carts, mail sacks, a station clock, benches, crossbuck signs, a semaphore signal, a parked taxi (checker-style), a newsboy NPC.
- **Creek:** pipe railing, chain-link, outfall pipes with stains, "No Swimming"-type warning signs as pictograms only, an old tyre and a shopping cart in the water, a heron (one bird), weeds in the cracks, the pump house, a fisherman NPC on the shoal secret.
- **Fair:** pennant strings, bulb strings, popcorn and cotton-candy stands, a ring toss, a balloon seller, hay bales, prize ribbons on the barn doors, a tractor, livestock (cows, pigs, chickens; sheet 73 critters if present), a race car or sulky by the grandstand, a ticket booth, litter, sawdust, the ice-cream truck.
- **Penn Park:** the war-memorial column with wreaths, the bandstand with bunting, ducks on the pond, benches, a drinking fountain, metal swings and a seesaw (avoid the plastic playground pieces), the hobo camp's campfire and crates.
- **Factory:** stacked crates and pallets, steel drums, a delivery truck, a coal pile, a time-clock shed, smoke puffs from the stack (animated overhead), a chain-link gate.
- **Cemetery:** headstones of mixed ages, obelisks, angels, urns, family-plot iron fences, a watering can, fresh flowers on one grave (story hook), a groundskeeper NPC with a wheelbarrow, fallen leaves, stone benches, crows, iron lamps along the axis.
- **Hilltop:** wraparound porches, picket fences, a rose garden, a coin telescope, a weather vane, a rich kid's red wagon.

---

## 6. Palette and mood per district
The approach is Earthbound warmth. Each district gets a dominant hue, a support hue and an accent hue. Keep saturation moderate and slightly sun-warmed, and give shadows a purple-blue tint rather than black.

| District | Dominant | Support | Accent | Mood notes |
|---|---|---|---|---|
| Downtown core (square, Market St) | warm brick red-orange (#B5523B-ish) | cream stone, bronze, concrete beige | awning reds, greens and teals; gold signage | Busy, sunny, prosperous "last good years of Main Street". Densest props. |
| Central Market | brick red + slate blue-grey roof | sandstone cream | produce colours (pumpkin orange, apple red, corn yellow), flower pinks | The heart of the town: bustling, warm and abundant. |
| Rowhouse lanes | darker, older brick (maroon-brown) | white stoops and trim | laundry pastels, kids' toys | Homely, repetitive and lived-in. Slightly narrower, cosier views. |
| Codorus Creek | cool concrete grey, slate-teal water | rust brown | a single heron white, a weed green | Cold, industrial and empty. The one place downtown with no awnings, which makes the bridges feel like thresholds. |
| Fairgrounds | sun-bleached tan dirt + barn red | whitewash white rails | festival candy colours (red/white stripes, yellow, sky blue), bulb glow at dusk | Loud, festive and dusty. The most saturated area. |
| Penn Park | soft lawn green | white bandstand, grey stone column | duck-pond blue, flowerbed pinks | Civic, gentle and breezy. |
| Factory | soot grey-brown + corrugated blue-grey | brick | warning yellow, candy-box pink (a nod to the candy works) | Gritty but whimsical. |
| Prospect Hill Cemetery | deep greens (oak and evergreen) | stone greys and marble whites | bronze verdigris (the soldier statue), a few flower reds | Quiet, shaded and reverent. Lower saturation, longer shadows, no music beats. |
| Hilltop (NE) | Victorian slate blue-grey + cream clapboard | lawn green | rose pink | Genteel and a little aloof, with a reward view. |

**Time-of-day hook:** downtown and the fair should look great at dusk, with marquee bulbs, the fair's bulb strings and lit shop windows. The cemetery reads best in late afternoon gold.

---

## 7. Implementation notes for the builder
1. **Paint order:** ground (grass) → roads and sidewalks → creek bed, walls and water → bridges → plazas, paths and terrain (cliffs) → buildings → props → overhead layer (canopies, steeple and tower tips, arches, smokestack, bulb strings).
2. **Collision:** buildings are fully solid. For trees, lamps, signs and hydrants only the base cell is solid. Water, walls, lips, cliffs, fences, rails and parapets are solid. Everything else in the legend marked "walk" is walkable.
3. **Fitting buildings:** if a catalog building is narrower than its block rect, centre it and fill the rest with sidewalk, lawn or alley in keeping with the block. If it is wider, trim at a repeatable middle column. Never move a door off the south row.
4. **Overhead rows:** tall tops may spill north by up to 2 rows as **overhead** tiles: Market towers, steeples, courthouse domes, the hotel roof sign, the smokestack and the grandstand pennants. They must not block the player there.
5. **Verification:** all key points and secrets in this layout have been flood-fill verified as reachable from the spawn (121,122) under the collision rules above. Re-run that check after stamping props, so that no planter or car seals off a path. Keep 2-tile-wide clear lanes on all sidewalks.

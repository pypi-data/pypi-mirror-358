from pylitematic import (
    BlockPosition,
    BlockId,
    BlockState,
    Region,
    Schematic,
    Size3D,
)


air = BlockState("air")
stone = BlockState("stone")
dirt = BlockState("dirt")
grass = BlockState("grass_block")
water = BlockState("water")
lava = BlockState("lava")
sand = BlockState("sand")

cobble = BlockState("cobblestone")
mossy_cobble = BlockState("mossy_cobblestone")

snow = BlockState("snow_block")
ice = BlockState("ice")
pumpkin = BlockState("carved_pumpkin", facing="west")
jack = BlockState("jack_o_lantern", facing="west")

ground = Region(size=Size3D(16, 9, 16))
ground.local[:,:5,:] = stone # 4 stone layers
ground.local[:,5:8,:] = dirt # 3 dirt layers
ground[(ground > dirt) & (ground == BlockId("air"))] = grass # grass above exposed dirt
ground.numpy[2:5,-1,2:5] = water # small pond
ground[ground.relative_to(water, BlockPosition(4, 0, 0))] = lava # lava pool

boulder = Region(size=(4, 4, 4), origin=ground.origin+[6, ground.height, 6])
boulder[:] = mossy_cobble # fill with mossy cobblestone
boulder.numpy[:,-2:,:] = cobble # upper two layers of cobblestone

snow_man = Region(
    size=(1, -3, 1), origin=boulder.origin+[2, boulder.upper.y+3, 1])
snow_man.set_default_view(snow_man.numpy)
snow_man[...] = snow # fill with snow
snow_man[0,-1,0] = pumpkin # pumpkin on top

snow_woman = snow_man.copy(origin=snow_man.origin+[-1, 0, 1])
# snow_woman[snow_woman == snow] = ice # replace snow with ice
snow_woman.where(snow, ice, jack) # replace snow with ice and rest with lanterns

clones = []
start = BlockPosition(1, ground.upper.y, ground.upper.z-1)
for i in range(5):
    clones.append(
        snow_man.copy(origin=start+(i * 3, 3, -i)))

cuboid = Region(origin=(14, ground.upper.y+3, 4), size=(-2,-3,-4))
cuboid[:,-2:0,:] = sand
cuboid.where((cuboid < air) & (cuboid == sand), stone)
for pos, block in cuboid.numpy.items():
    print(f"{pos}:\t{block}")

schem = Schematic(
    name="a_scene", author="Boscawinks", description="A simple scene")
schem.add_region("ground", ground)
schem.add_region("boulder", boulder)
schem.add_region("snow_man", snow_man)
schem.add_region("snow_woman", snow_woman)
for i, clone in enumerate(clones):
    schem.add_region(f"clone_{i+1}", clone)
schem.add_region("cuboid", cuboid)
schem.save(
    f"/mnt/d/minecraft/schematics/Litematica/test/{schem.name}.litematic")

# print(boulder[...,-1])

# from pathlib import Path
# path = Path("/mnt/d/minecraft/schematics/Litematica/turtle/turtle_8x8.litematic")
# turtle = Schematic.load(path)
# for name, reg in turtle.regions():
#     reg[reg != BlockState("air")] = BlockState("blue_wool")
# turtle.save(path.with_suffix(".blue.litematic"))

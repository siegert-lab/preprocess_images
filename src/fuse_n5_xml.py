import numpy as np
import os
import zarr
import re
import xml.etree.ElementTree as ET
import cv2
import json
from tifffile import imwrite
from tifffile import TiffWriter

def parse_affine(text):
    values = list(map(float, text.strip().split()))
    matrix = np.array(values).reshape((3, 4))
    # Convert to 4x4 matrix for homogeneous multiplication
    bottom_row = np.array([[0, 0, 0, 1]])
    return np.vstack((matrix, bottom_row))

def get_tile_positions(xml_path):
    tree = ET.parse(xml_path)
    root = tree.getroot()

    positions = {}
    for reg in root.findall('.//ViewRegistration'):
        setup_id = int(reg.attrib['setup'])

        # Only take setups matching your channel logic
        if setup_id % 4 == 2:
            transforms = reg.findall('.//ViewTransform/affine')
            composed = np.eye(4)

            for t in transforms:
                A = parse_affine(t.text)
                composed = A @ composed  # Matrix multiplication

            offset = composed[:3, 3]  # Extract final translation
            positions[setup_id] = offset.tolist()

    return positions


def create_blending_mask(shape, overlap_fraction=0.1):
    """Create a 3D linear blending mask with soft edges along each axis."""
    z, y, x = shape
    dz = int(z * overlap_fraction)
    dy = int(y * overlap_fraction)
    dx = int(x * overlap_fraction)

    wz = np.ones(z)
    wy = np.ones(y)
    wx = np.ones(x)

    if dz > 0:
        wz[:dz] = np.linspace(0, 1, dz)
        wz[-dz:] = np.linspace(1, 0, dz)
    if dy > 0:
        wy[:dy] = np.linspace(0, 1, dy)
        wy[-dy:] = np.linspace(1, 0, dy)
    if dx > 0:
        wx[:dx] = np.linspace(0, 1, dx)
        wx[-dx:] = np.linspace(1, 0, dx)

    # Outer product to create full 3D blending mask
    return wz[:, None, None] * wy[None, :, None] * wx[None, None, :]

def fuse_channel_2_tiles(n5_path, tile_positions, voxel_size, output_path, overlap_fraction=0.1):
    z = zarr.open(n5_path, mode='r')

    selected_setups = sorted(
        [k for k in z.group_keys() if k.startswith("setup") and int(k[5:]) % 4 == 2],
        key=lambda s: int(s[5:])
    )

    print(f"Selected setups for channel 2: {selected_setups}")
    tiles = []
    positions_px = []

    print(f'{len(selected_setups)} tiles to process')
    for i, setup in enumerate(selected_setups, 1):
        sid = int(setup[5:])
        data = z[f'{setup}/timepoint0/s0'][:]
        offset_um = np.array(tile_positions[sid])
        offset_px = np.round(offset_um[::-1] / voxel_size).astype(int)

        print(f'Tile {i}/{len(selected_setups)} loaded')
        tiles.append(data)
        positions_px.append(offset_px)

    shapes = [t.shape for t in tiles]
    mins = np.min(positions_px, axis=0)
    maxs = np.max([pos + shape for pos, shape in zip(positions_px, shapes)], axis=0)

    size = maxs - mins
    print(f'The size of the fused image is {size}')
    fused = np.zeros(size, dtype=np.float32)
    weight = np.zeros(size, dtype=np.float32)

    for tile, pos in zip(tiles, positions_px):
        pos = pos - mins
        z0, y0, x0 = pos
        z1, y1, x1 = pos + tile.shape

        mask = create_blending_mask(tile.shape, overlap_fraction)
        fused[z0:z1, y0:y1, x0:x1] += tile * mask
        weight[z0:z1, y0:y1, x0:x1] += mask

    fused = fused / np.maximum(weight, 1e-8)
    fused = np.clip(fused, 0, 65535).astype(np.uint16)
    metadata = {}
    # Save metadata as a JSON string
    imwrite(
        output_path,
        fused,
        metadata=metadata  # Optional structured metadata (OME-style)
    )
    print(f"Blended fused channel 2 saved to {output_path}")

def downsample_tile_cv2(tile, factor=2, interpolation=cv2.INTER_AREA):
    """
    Downsample a 3D tile (Z, Y, X) by a factor in Y and X using OpenCV.
    INTER_AREA is good for downsampling.
    """
    z, y, x = tile.shape
    downsampled = np.zeros((z, y // factor, x // factor), dtype=np.float32)
    for i in range(z):
        # OpenCV expects (X, Y) ordering for shape
        downsampled[i] = cv2.resize(tile[i], dsize=(x // factor, y // factor), interpolation=interpolation)
    return downsampled

from scipy.ndimage import zoom

def downsample_tile(tile, xy_factor=2, z_factor=1, order=1):
    """
    Downsample a 3D tile (Z, Y, X) with interpolation using `scipy.ndimage.zoom`.

    `order=1` = linear interpolation, good for general use
    """
    zoom_factors = [1 / z_factor, 1 / xy_factor, 1 / xy_factor]
    return zoom(tile, zoom_factors, order=order).astype(np.float32)


def fuse_channel_2_tiles(n5_path, tile_positions, channel, voxel_size, output_path, overlap_fraction=0.1, metadata=None, downsample_factor_xy=2, downsample_factor_z = 2):
    z = zarr.open(n5_path, mode='r')

    selected_setups = sorted(
        [k for k in z.group_keys() if k.startswith("setup") and int(k[5:]) % 4 == channel],
        key=lambda s: int(s[5:])
    )

    print(f"Selected setups for channel 2: {selected_setups}")
    tiles = []
    positions_px = []

    print(f'{len(selected_setups)} tiles to process')
    for i, setup in enumerate(selected_setups, 1):
        sid = int(setup[5:])
        data = z[f'{setup}/timepoint0/s0'][:]
        offset_um = np.array(tile_positions[sid])

        # Downsample tile before fusion
        if downsample_factor_xy == 1:
            tile = data
        else:
            tile = downsample_tile(tile=data, xy_factor=downsample_factor_xy, z_factor=downsample_factor_z, order=1)
        # Adjust pixel offset accordingly (voxel_size is unchanged)
        offset_px = np.round(offset_um[::-1] / voxel_size).astype(int)
        offset_px[0] = offset_px[0] // downsample_factor_z  # downsample Z
        offset_px[1:] = offset_px[1:] // downsample_factor_xy  # downsample Y & X offsets

        print(f'Tile {i}/{len(selected_setups)} positioned')
        tiles.append(tile)
        positions_px.append(offset_px)

    shapes = [t.shape for t in tiles]
    mins = np.min(positions_px, axis=0)
    maxs = np.max([pos + shape for pos, shape in zip(positions_px, shapes)], axis=0)

    size = maxs - mins
    print(f'The size of the fused image is {size}')
    fused = np.zeros(size, dtype=np.float32)
    weight = np.zeros(size, dtype=np.float32)
    print(f"Memory size of 'fused': {fused.nbytes / 1024 ** 3:.2f} GB")

    i = 0
    for tile, pos in zip(tiles, positions_px):
        i+=1
        pos = pos - mins
        z0, y0, x0 = pos
        z1, y1, x1 = pos + tile.shape

        mask = create_blending_mask(tile.shape, overlap_fraction)
        fused[z0:z1, y0:y1, x0:x1] += tile * mask
        weight[z0:z1, y0:y1, x0:x1] += mask
        print(f'Tile {i}/{len(selected_setups)} fused')


    # Prepare metadata
    if metadata is None:
        metadata = {}
    os.makedirs(output_path, exist_ok=True)

    # Open the TiffWriter
    with TiffWriter(output_path, bigtiff=True) as tif:
        for z in range(fused.shape[0]):
            # Slice current Z-plane
            fused_z = fused[z]
            weight_z = weight[z]

            # Safe division and clipping
            np.divide(fused_z, np.maximum(weight_z, 1e-8), out=fused_z)
            np.clip(fused_z, 0, 65535, out=fused_z)

            # Convert to uint16
            slice_uint16 = fused_z.astype(np.uint16)

            # Write to TIFF file
            tif.write(
                slice_uint16,
                description=json.dumps(metadata) if z == 0 else None,
                contiguous=True
            )

            print(f"Slice {z+1}/{fused.shape[0]} written.")


from watershed_segmentation_py._C_watershed_segmentation import (
    PyParallelWatershedCellRunner, FloatPolygonRoundPolicy, PolygonCategory
)
import numpy as np
from typing import List, Tuple


def get_chunk_polyogn_directly(
    runner: PyParallelWatershedCellRunner,
    chunk_index: int,
    polygon_category: PolygonCategory,
    convert_to_i32: bool,
    round_policy: FloatPolygonRoundPolicy = FloatPolygonRoundPolicy.RoundNearest,
    check_npy: bool = True
) -> List[np.ndarray]:
    """
    this is the helper func to get the chunk nuclei polygon direclyt
    Args:
        runner:the runner object
        chunk_index:int,which chunk you want to get
        polygon_category:nuceli or cell
        round_policy:the policy to convert float -> int
    Returns:
        a list of polygons that detected!
    """
    polygon_shapes: np.ndarray = runner.get_chunk_polygon_shapes(
        chunk_index=chunk_index, polygon_category=polygon_category
    )
    polygon_dtype = np.dtype("i4") if convert_to_i32 else np.dtype("f4")
    npy_polygons = [np.empty(shape=(polygon_shapes[i], 2), dtype=polygon_dtype) for i in range(len(polygon_shapes))]
    runner.get_chunk_npy_polygon_directly(
        npy_polygons=npy_polygons,
        chunk_index=chunk_index,
        polygon_category=polygon_category,
        convert_to_i32=convert_to_i32,
        round_policy=round_policy,
        check_npy=check_npy
    )
    return npy_polygons


def get_polygon_directly(
    runner: PyParallelWatershedCellRunner,
    polygon_category: PolygonCategory,
    convert_to_i32: bool,
    round_policy: FloatPolygonRoundPolicy = FloatPolygonRoundPolicy.RoundNearest,
    check_npy: bool = True
) -> List[np.ndarray]:
    """
    this is the helper func to get the chunk nuclei polygon direclyt
    Args:
        runner:the runner object
        polygon_category:nuceli or cell
        round_policy:the policy to convert float -> int
    Returns:
        a list of polygons that detected!
    """
    polygon_shapes: np.ndarray = runner.get_polygon_shapes(polygon_category=polygon_category)
    polygon_dtype = np.dtype("i4") if convert_to_i32 else np.dtype("f4")
    npy_polygons = [np.empty(shape=(polygon_shapes[i], 2), dtype=polygon_dtype) for i in range(len(polygon_shapes))]
    runner.get_npy_polygon_directly(
        npy_polygons=npy_polygons,
        polygon_category=polygon_category,
        convert_to_i32=convert_to_i32,
        round_policy=round_policy,
        check_npy=check_npy
    )
    return npy_polygons


def check_can_fill_with_runner(runner: PyParallelWatershedCellRunner = None, polygon_category: PolygonCategory = None):
    if polygon_category == PolygonCategory.Nuclei and (not runner.has_nuclei()):
        raise RuntimeError("you specify fill with nuclei,but current runner not have nuclei!maybe forget invoke run?")

    if polygon_category == PolygonCategory.Cell and (not runner.has_cell()):
        raise RuntimeError(
            "you specify fill with cell,but current runner not have any cell!maybe forget invoke run or specify expand_radius = 0.0?"
        )


def get_filled_mask_directly(
    runner: PyParallelWatershedCellRunner,
    fill_value: int,
    polygon_category: PolygonCategory,
    round_policy: FloatPolygonRoundPolicy = FloatPolygonRoundPolicy.RoundNearest
) -> np.ndarray:
    """
    Args:
        runner:a watershed segmentation obj
        fill_value:int,a int value between in 1~255,if not in this range,we will set it to 255!
        polygon_category:nuceli or cell!
        round_policy:floor/round/ceil!
    Returns:
        filled_mask:ndarray with dtype=np.uint8,shape=(h,w) of last running image!
    """
    check_can_fill_with_runner()

    h: int = runner.get_image_height()
    w: int = runner.get_image_width()
    if h <= 0 or w <= 0:
        raise ValueError("the last running image is empty!")

    mask: np.ndarray = np.zeros(shape=(h, w), dtype=np.uint8)
    runner.get_filled_mask_directly(
        mask=mask,
        fill_value=fill_value,
        is_initialized=True,
        polygon_category=polygon_category,
        round_policy=round_policy
    )
    return mask


def get_filled_mask_directly_with_shape(
    runner: PyParallelWatershedCellRunner,
    fill_value: int,
    mask_shape: Tuple[int, int],
    polygon_category,
    round_policy: FloatPolygonRoundPolicy = FloatPolygonRoundPolicy.RoundNearest
) -> np.ndarray:
    """
    Args:
        runner:a watershed segmentation obj
        fill_value:a int value in range [1,255],if not in this range,set it to 255
        mask_shape:a 2 element tuple,if the shape less than the detect running image,just raise RuntimeError!
        polygon_category:if nuclei,we will use the nuclei's polygon to fill the mask else use the cell's
        round_policy:default is nearest!
    Returns:
        a filled mask!
    """
    check_can_fill_with_runner()
    if mask_shape[0] < runner.get_image_height() or mask_shape[1] < runner.get_image_width():
        raise RuntimeError(
            "the specify mask shpae ({},{}) is less than last running image shape ({},{}) this is not allowd!".format(
                mask_shape[0], mask_shape[1], runner.get_image_height(), runner.get_image_width()
            )
        )
    mask = np.zeros(shape=mask_shape, dtype=np.uint8)
    runner.get_filled_mask_directly(
        mask=mask,
        fill_value=fill_value,
        is_initialized=True,
        polygon_category=polygon_category,
        round_policy=round_policy
    )
    return mask

# this is the C library!
# __version__ = "0.0.9.dev"

try:
    from watershed_segmentation_py.version import version as __version__
    from watershed_segmentation_py._C_watershed_segmentation import (
        ColorDeconvolutionStainsType, ColorImageType, ColorTransformType, ErrorCode, get_error_msg, FallbackString,
        FloatPolygonRoundPolicy, ImageColorSpace, MiconPixelSize, PolygonCategory, PolygonSizesInfo, PreferChunkInfo,
        StainChoiceType, StainType, WatershedRunningParams, WrapDataType, compute_averaged_micron_pixel_size,
        compute_overlap, compute_downsample_factor, divide_micron_pixel_size, estimate_min_required_memory,
        PyParallelWatershedCellRunner, set_logger, flush_logger, test_throw_exception
    )
    from watershed_segmentation_py.utils import (
        get_chunk_polyogn_directly, get_polygon_directly, get_filled_mask_directly, get_filled_mask_directly_with_shape
    )
except ImportError:
    print("can not find cxx dynamic library _C_watershed_segmentation")

__all__ = [
    "__version__", "ColorDeconvolutionStainsType", "ColorImageType", "ColorTransformType", "ErrorCode", "get_error_msg",
    "FallbackString", "FloatPolygonRoundPolicy", "ImageColorSpace", "MiconPixelSize", "PolygonCategory",
    "PolygonSizesInfo", "PreferChunkInfo", "StainChoiceType", "StainType", "WatershedRunningParams", "WrapDataType",
    "compute_averaged_micron_pixel_size", "compute_overlap", "compute_downsample_factor", "divide_micron_pixel_size",
    "estimate_min_required_memory", "PyParallelWatershedCellRunner", "get_chunk_polyogn_directly",
    "get_polygon_directly", "get_filled_mask_directly", "get_filled_mask_directly_with_shape", "set_logger",
    "test_throw_exception", "flush_logger"
]

from __future__ import annotations
import numpy
import typing


class ColorDeconvolutionStainsType:
    """
    Members:
      HAndE : H&E color transform!
      HAndDAB : H And DAB color transform!
    """
    HAndDAB: typing.ClassVar[ColorDeconvolutionStainsType] # value = <ColorDeconvolutionStainsType.HAndDAB: 1>
    HAndE: typing.ClassVar[ColorDeconvolutionStainsType]   # value = <ColorDeconvolutionStainsType.HAndE: 0>
    __members__: typing.ClassVar[
        dict[str, ColorDeconvolutionStainsType]
    ]                                                      # value = {'HAndE': <ColorDeconvolutionStainsType.HAndE: 0>, 'HAndDAB': <ColorDeconvolutionStainsType.HAndDAB: 1>}

    def __eq__(self, other: typing.Any) -> bool:
        ...

    def __getstate__(self) -> int:
        ...

    def __hash__(self) -> int:
        ...

    def __index__(self) -> int:
        ...

    def __init__(self, value: int) -> None:
        ...

    def __int__(self) -> int:
        ...

    def __ne__(self, other: typing.Any) -> bool:
        ...

    def __repr__(self) -> str:
        ...

    def __setstate__(self, state: int) -> None:
        ...

    def __str__(self) -> str:
        ...

    @property
    def name(self) -> str:
        ...

    @property
    def value(self) -> int:
        ...


class ColorImageType:
    """
    the color image types....
    Members:
      BrightfieldHAndE : stain with H & E
      BrightfieldHAndDAB : stain with H & DAB
      BrightFieldOther : stain with H & other
      Fluorescence : florescence....sorry,I don't know what is it!
      Other : other stains....
      Unspecified : means that not speicfy any type of color image!
    """
    BrightFieldOther: typing.ClassVar[ColorImageType]   # value = <ColorImageType.BrightFieldOther: 2>
    BrightfieldHAndDAB: typing.ClassVar[ColorImageType] # value = <ColorImageType.BrightfieldHAndDAB: 1>
    BrightfieldHAndE: typing.ClassVar[ColorImageType]   # value = <ColorImageType.BrightfieldHAndE: 0>
    Fluorescence: typing.ClassVar[ColorImageType]       # value = <ColorImageType.Fluorescence: 3>
    Other: typing.ClassVar[ColorImageType]              # value = <ColorImageType.Other: 4>
    Unspecified: typing.ClassVar[ColorImageType]        # value = <ColorImageType.Unspecified: 5>
    __members__: typing.ClassVar[dict[str, ColorImageType]]
    '''
    value = {
        'BrightfieldHAndE': <ColorImageType.BrightfieldHAndE: 0>,
        'BrightfieldHAndDAB': <ColorImageType.BrightfieldHAndDAB: 1>,
        'BrightFieldOther': <ColorImageType.BrightFieldOther: 2>,
        'Fluorescence': <ColorImageType.Fluorescence: 3>,
        'Other': <ColorImageType.Other: 4>,
        'Unspecified': <ColorImageType.Unspecified: 5>
        }
    '''

    def __eq__(self, other: typing.Any) -> bool:
        ...

    def __getstate__(self) -> int:
        ...

    def __hash__(self) -> int:
        ...

    def __index__(self) -> int:
        ...

    def __init__(self, value: int) -> None:
        ...

    def __int__(self) -> int:
        ...

    def __ne__(self, other: typing.Any) -> bool:
        ...

    def __repr__(self) -> str:
        ...

    def __setstate__(self, state: int) -> None:
        ...

    def __str__(self) -> str:
        ...

    @property
    def name(self) -> str:
        ...

    @property
    def value(self) -> int:
        ...


class ColorTransformType:
    """
    transform op kind for color image
    Members:
      Original
      Red
      Green
      Blue
      RedOD
      GreenOD
      BlueOD
      RGBMean
      Hue
      Santuration
      Brightness
      Stain1
      Stain2
      Stain3
      OpticalDensitySum
      HematoxyinHE
      EosinHE
      HematoxylinHDAB
      DABHDAB
      HematoxylinHE8bit
      DABHDAB8bit
      RedChromaticity
      GreenChromaticity
      BlueChromaticity
      GreenDividenByBlue
      ODNormaized
      Brown
      White
      Black
    """
    Black: typing.ClassVar[ColorTransformType]              # value = <ColorTransformType.Black: 30>
    Blue: typing.ClassVar[ColorTransformType]               # value = <ColorTransformType.Blue: 3>
    BlueChromaticity: typing.ClassVar[ColorTransformType]   # value = <ColorTransformType.BlueChromaticity: 25>
    BlueOD: typing.ClassVar[ColorTransformType]             # value = <ColorTransformType.BlueOD: 6>
    Brightness: typing.ClassVar[ColorTransformType]         # value = <ColorTransformType.Brightness: 10>
    Brown: typing.ClassVar[ColorTransformType]              # value = <ColorTransformType.Brown: 28>
    DABHDAB: typing.ClassVar[ColorTransformType]            # value = <ColorTransformType.DABHDAB: 18>
    DABHDAB8bit: typing.ClassVar[ColorTransformType]        # value = <ColorTransformType.DABHDAB8bit: 22>
    EosinHE: typing.ClassVar[ColorTransformType]            # value = <ColorTransformType.EosinHE: 16>
    Green: typing.ClassVar[ColorTransformType]              # value = <ColorTransformType.Green: 2>
    GreenChromaticity: typing.ClassVar[ColorTransformType]  # value = <ColorTransformType.GreenChromaticity: 24>
    GreenDividenByBlue: typing.ClassVar[ColorTransformType] # value = <ColorTransformType.GreenDividenByBlue: 26>
    GreenOD: typing.ClassVar[ColorTransformType]            # value = <ColorTransformType.GreenOD: 5>
    HematoxyinHE: typing.ClassVar[ColorTransformType]       # value = <ColorTransformType.HematoxyinHE: 15>
    HematoxylinHDAB: typing.ClassVar[ColorTransformType]    # value = <ColorTransformType.HematoxylinHDAB: 17>
    HematoxylinHE8bit: typing.ClassVar[ColorTransformType]  # value = <ColorTransformType.HematoxylinHE8bit: 19>
    Hue: typing.ClassVar[ColorTransformType]                # value = <ColorTransformType.Hue: 8>
    ODNormaized: typing.ClassVar[ColorTransformType]        # value = <ColorTransformType.ODNormaized: 27>
    OpticalDensitySum: typing.ClassVar[ColorTransformType]  # value = <ColorTransformType.OpticalDensitySum: 14>
    Original: typing.ClassVar[ColorTransformType]           # value = <ColorTransformType.Original: 0>
    RGBMean: typing.ClassVar[ColorTransformType]            # value = <ColorTransformType.RGBMean: 7>
    Red: typing.ClassVar[ColorTransformType]                # value = <ColorTransformType.Red: 1>
    RedChromaticity: typing.ClassVar[ColorTransformType]    # value = <ColorTransformType.RedChromaticity: 23>
    RedOD: typing.ClassVar[ColorTransformType]              # value = <ColorTransformType.RedOD: 4>
    Santuration: typing.ClassVar[ColorTransformType]        # value = <ColorTransformType.Santuration: 9>
    Stain1: typing.ClassVar[ColorTransformType]             # value = <ColorTransformType.Stain1: 11>
    Stain2: typing.ClassVar[ColorTransformType]             # value = <ColorTransformType.Stain2: 12>
    Stain3: typing.ClassVar[ColorTransformType]             # value = <ColorTransformType.Stain3: 13>
    White: typing.ClassVar[ColorTransformType]              # value = <ColorTransformType.White: 29>
    __members__: typing.ClassVar[
        dict[str, ColorTransformType]
    ]                                                       # value = {'Original': <ColorTransformType.Original: 0>, 'Red': <ColorTransformType.Red: 1>, 'Green': <ColorTransformType.Green: 2>, 'Blue': <ColorTransformType.Blue: 3>, 'RedOD': <ColorTransformType.RedOD: 4>, 'GreenOD': <ColorTransformType.GreenOD: 5>, 'BlueOD': <ColorTransformType.BlueOD: 6>, 'RGBMean': <ColorTransformType.RGBMean: 7>, 'Hue': <ColorTransformType.Hue: 8>, 'Santuration': <ColorTransformType.Santuration: 9>, 'Brightness': <ColorTransformType.Brightness: 10>, 'Stain1': <ColorTransformType.Stain1: 11>, 'Stain2': <ColorTransformType.Stain2: 12>, 'Stain3': <ColorTransformType.Stain3: 13>, 'OpticalDensitySum': <ColorTransformType.OpticalDensitySum: 14>, 'HematoxyinHE': <ColorTransformType.HematoxyinHE: 15>, 'EosinHE': <ColorTransformType.EosinHE: 16>, 'HematoxylinHDAB': <ColorTransformType.HematoxylinHDAB: 17>, 'DABHDAB': <ColorTransformType.DABHDAB: 18>, 'HematoxylinHE8bit': <ColorTransformType.HematoxylinHE8bit: 19>, 'DABHDAB8bit': <ColorTransformType.DABHDAB8bit: 22>, 'RedChromaticity': <ColorTransformType.RedChromaticity: 23>, 'GreenChromaticity': <ColorTransformType.GreenChromaticity: 24>, 'BlueChromaticity': <ColorTransformType.BlueChromaticity: 25>, 'GreenDividenByBlue': <ColorTransformType.GreenDividenByBlue: 26>, 'ODNormaized': <ColorTransformType.ODNormaized: 27>, 'Brown': <ColorTransformType.Brown: 28>, 'White': <ColorTransformType.White: 29>, 'Black': <ColorTransformType.Black: 30>}

    def __eq__(self, other: typing.Any) -> bool:
        ...

    def __getstate__(self) -> int:
        ...

    def __hash__(self) -> int:
        ...

    def __index__(self) -> int:
        ...

    def __init__(self, value: int) -> None:
        ...

    def __int__(self) -> int:
        ...

    def __ne__(self, other: typing.Any) -> bool:
        ...

    def __repr__(self) -> str:
        ...

    def __setstate__(self, state: int) -> None:
        ...

    def __str__(self) -> str:
        ...

    @property
    def name(self) -> str:
        ...

    @property
    def value(self) -> int:
        ...


class ErrorCode:
    """
    the error code mostly function return
    Members:
      Ok
      InvalidMatDimension
      InvalidMatIndex
      InvalidGuassianParam
      InvalidMatShape
      MatShapeMismatch
      MatLayoutMismatch
      InvalidConvKernel
      InvalidRankFilterRandius
      UnsupportedRankFilterType
      UnsupportedNeightborFiltertype
      UnsupportedValueOp
      InvalidMatChannel
      UnsupportedInvokeInplace
      WatershedSegmentationError
      Unknown
      UnexpectedMatLayout
      NullMemoryPool
      ExceedMaxSupportedSize
      EmptyImage
      InvalidbufferSize
      ExcludeDABMaskError
      UnknwonPolygonCategory
      BufferMismatchResourceHandler
      IndxOutofRange
      UninitializedResource
      FilterFlagsMismatchPolygons
      NotSupportedColorTransformType
      NonePositiveValueError
      NotSupportedColorSpace
      TaskEarlyStopping
      NotSupportedStainType
      TaskIsCancelled
      NotNumpylikeInput
      InvalidDtype
      InvalidTileError
      InitializeChunkResourceError
    """
    BufferMismatchResourceHandler: typing.ClassVar[ErrorCode]  # value = <ErrorCode.BufferMismatchResourceHandler: 23>
    EmptyImage: typing.ClassVar[ErrorCode]                     # value = <ErrorCode.EmptyImage: 19>
    ExceedMaxSupportedSize: typing.ClassVar[ErrorCode]         # value = <ErrorCode.ExceedMaxSupportedSize: 18>
    ExcludeDABMaskError: typing.ClassVar[ErrorCode]            # value = <ErrorCode.ExcludeDABMaskError: 21>
    FilterFlagsMismatchPolygons: typing.ClassVar[ErrorCode]    # value = <ErrorCode.FilterFlagsMismatchPolygons: 26>
    IndxOutofRange: typing.ClassVar[ErrorCode]                 # value = <ErrorCode.IndxOutofRange: 24>
    InitializeChunkResourceError: typing.ClassVar[ErrorCode]   # value = <ErrorCode.InitializeChunkResourceError: 36>
    InvalidConvKernel: typing.ClassVar[ErrorCode]              # value = <ErrorCode.InvalidConvKernel: 7>
    InvalidDtype: typing.ClassVar[ErrorCode]                   # value = <ErrorCode.InvalidDtype: 34>
    InvalidGuassianParam: typing.ClassVar[ErrorCode]           # value = <ErrorCode.InvalidGuassianParam: 3>
    InvalidMatChannel: typing.ClassVar[ErrorCode]              # value = <ErrorCode.InvalidMatChannel: 12>
    InvalidMatDimension: typing.ClassVar[ErrorCode]            # value = <ErrorCode.InvalidMatDimension: 1>
    InvalidMatIndex: typing.ClassVar[ErrorCode]                # value = <ErrorCode.InvalidMatIndex: 2>
    InvalidMatShape: typing.ClassVar[ErrorCode]                # value = <ErrorCode.InvalidMatShape: 4>
    InvalidRankFilterRandius: typing.ClassVar[ErrorCode]       # value = <ErrorCode.InvalidRankFilterRandius: 8>
    InvalidTileError: typing.ClassVar[ErrorCode]               # value = <ErrorCode.InvalidTileError: 35>
    InvalidbufferSize: typing.ClassVar[ErrorCode]              # value = <ErrorCode.InvalidbufferSize: 20>
    MatLayoutMismatch: typing.ClassVar[ErrorCode]              # value = <ErrorCode.MatLayoutMismatch: 6>
    MatShapeMismatch: typing.ClassVar[ErrorCode]               # value = <ErrorCode.MatShapeMismatch: 5>
    NonePositiveValueError: typing.ClassVar[ErrorCode]         # value = <ErrorCode.NonePositiveValueError: 28>
    NotNumpylikeInput: typing.ClassVar[ErrorCode]              # value = <ErrorCode.NotNumpylikeInput: 33>
    NotSupportedColorSpace: typing.ClassVar[ErrorCode]         # value = <ErrorCode.NotSupportedColorSpace: 29>
    NotSupportedColorTransformType: typing.ClassVar[ErrorCode] # value = <ErrorCode.NotSupportedColorTransformType: 27>
    NotSupportedStainType: typing.ClassVar[ErrorCode]          # value = <ErrorCode.NotSupportedStainType: 31>
    NullMemoryPool: typing.ClassVar[ErrorCode]                 # value = <ErrorCode.NullMemoryPool: 17>
    Ok: typing.ClassVar[ErrorCode]                             # value = <ErrorCode.Ok: 0>
    TaskEarlyStopping: typing.ClassVar[ErrorCode]              # value = <ErrorCode.TaskEarlyStopping: 30>
    TaskIsCancelled: typing.ClassVar[ErrorCode]                # value = <ErrorCode.TaskIsCancelled: 32>
    UnexpectedMatLayout: typing.ClassVar[ErrorCode]            # value = <ErrorCode.UnexpectedMatLayout: 16>
    UninitializedResource: typing.ClassVar[ErrorCode]          # value = <ErrorCode.UninitializedResource: 25>
    Unknown: typing.ClassVar[ErrorCode]                        # value = <ErrorCode.Unknown: 15>
    UnknwonPolygonCategory: typing.ClassVar[ErrorCode]         # value = <ErrorCode.UnknwonPolygonCategory: 22>
    UnsupportedInvokeInplace: typing.ClassVar[ErrorCode]       # value = <ErrorCode.UnsupportedInvokeInplace: 13>
    UnsupportedNeightborFiltertype: typing.ClassVar[ErrorCode] # value = <ErrorCode.UnsupportedNeightborFiltertype: 10>
    UnsupportedRankFilterType: typing.ClassVar[ErrorCode]      # value = <ErrorCode.UnsupportedRankFilterType: 9>
    UnsupportedValueOp: typing.ClassVar[ErrorCode]             # value = <ErrorCode.UnsupportedValueOp: 11>
    WatershedSegmentationError: typing.ClassVar[ErrorCode]     # value = <ErrorCode.WatershedSegmentationError: 14>
    __members__: typing.ClassVar[
        dict[str, ErrorCode]
    ]                                                          # value = {'Ok': <ErrorCode.Ok: 0>, 'InvalidMatDimension': <ErrorCode.InvalidMatDimension: 1>, 'InvalidMatIndex': <ErrorCode.InvalidMatIndex: 2>, 'InvalidGuassianParam': <ErrorCode.InvalidGuassianParam: 3>, 'InvalidMatShape': <ErrorCode.InvalidMatShape: 4>, 'MatShapeMismatch': <ErrorCode.MatShapeMismatch: 5>, 'MatLayoutMismatch': <ErrorCode.MatLayoutMismatch: 6>, 'InvalidConvKernel': <ErrorCode.InvalidConvKernel: 7>, 'InvalidRankFilterRandius': <ErrorCode.InvalidRankFilterRandius: 8>, 'UnsupportedRankFilterType': <ErrorCode.UnsupportedRankFilterType: 9>, 'UnsupportedNeightborFiltertype': <ErrorCode.UnsupportedNeightborFiltertype: 10>, 'UnsupportedValueOp': <ErrorCode.UnsupportedValueOp: 11>, 'InvalidMatChannel': <ErrorCode.InvalidMatChannel: 12>, 'UnsupportedInvokeInplace': <ErrorCode.UnsupportedInvokeInplace: 13>, 'WatershedSegmentationError': <ErrorCode.WatershedSegmentationError: 14>, 'Unknown': <ErrorCode.Unknown: 15>, 'UnexpectedMatLayout': <ErrorCode.UnexpectedMatLayout: 16>, 'NullMemoryPool': <ErrorCode.NullMemoryPool: 17>, 'ExceedMaxSupportedSize': <ErrorCode.ExceedMaxSupportedSize: 18>, 'EmptyImage': <ErrorCode.EmptyImage: 19>, 'InvalidbufferSize': <ErrorCode.InvalidbufferSize: 20>, 'ExcludeDABMaskError': <ErrorCode.ExcludeDABMaskError: 21>, 'UnknwonPolygonCategory': <ErrorCode.UnknwonPolygonCategory: 22>, 'BufferMismatchResourceHandler': <ErrorCode.BufferMismatchResourceHandler: 23>, 'IndxOutofRange': <ErrorCode.IndxOutofRange: 24>, 'UninitializedResource': <ErrorCode.UninitializedResource: 25>, 'FilterFlagsMismatchPolygons': <ErrorCode.FilterFlagsMismatchPolygons: 26>, 'NotSupportedColorTransformType': <ErrorCode.NotSupportedColorTransformType: 27>, 'NonePositiveValueError': <ErrorCode.NonePositiveValueError: 28>, 'NotSupportedColorSpace': <ErrorCode.NotSupportedColorSpace: 29>, 'TaskEarlyStopping': <ErrorCode.TaskEarlyStopping: 30>, 'NotSupportedStainType': <ErrorCode.NotSupportedStainType: 31>, 'TaskIsCancelled': <ErrorCode.TaskIsCancelled: 32>, 'NotNumpylikeInput': <ErrorCode.NotNumpylikeInput: 33>, 'InvalidDtype': <ErrorCode.InvalidDtype: 34>, 'InvalidTileError': <ErrorCode.InvalidTileError: 35>, 'InitializeChunkResourceError': <ErrorCode.InitializeChunkResourceError: 36>}

    def __eq__(self, other: typing.Any) -> bool:
        ...

    def __getstate__(self) -> int:
        ...

    def __hash__(self) -> int:
        ...

    def __index__(self) -> int:
        ...

    def __init__(self, value: int) -> None:
        ...

    def __int__(self) -> int:
        ...

    def __ne__(self, other: typing.Any) -> bool:
        ...

    def __repr__(self) -> str:
        ...

    def __setstate__(self, state: int) -> None:
        ...

    def __str__(self) -> str:
        ...

    @property
    def name(self) -> str:
        ...

    @property
    def value(self) -> int:
        ...


def get_error_msg(err: ErrorCode) -> str:
    """
    got the message string of error code!
    """
    ...


class FallbackString:

    @typing.overload
    def __init__(self, arg0: str) -> None:
        ...

    @typing.overload
    def __init__(self, arg0: str) -> None:
        ...


class FloatPolygonRoundPolicy:
    """
    the round policy for float value...
    Members:
      RoundUpper : round the value always use ceil,example 4.1 -> 5
      RoundLower : round the value always use floor,example 4.7 -> 4
      RoundNearest : round the value to the nearest int value,example 4.1->4 4.7->5
      Unknown : invalid round policy!
    """
    RoundLower: typing.ClassVar[FloatPolygonRoundPolicy]   # value = <FloatPolygonRoundPolicy.RoundLower: 1>
    RoundNearest: typing.ClassVar[FloatPolygonRoundPolicy] # value = <FloatPolygonRoundPolicy.RoundNearest: 2>
    RoundUpper: typing.ClassVar[FloatPolygonRoundPolicy]   # value = <FloatPolygonRoundPolicy.RoundUpper: 0>
    Unknown: typing.ClassVar[FloatPolygonRoundPolicy]      # value = <FloatPolygonRoundPolicy.Unknown: 3>
    __members__: typing.ClassVar[
        dict[str, FloatPolygonRoundPolicy]
    ]                                                      # value = {'RoundUpper': <FloatPolygonRoundPolicy.RoundUpper: 0>, 'RoundLower': <FloatPolygonRoundPolicy.RoundLower: 1>, 'RoundNearest': <FloatPolygonRoundPolicy.RoundNearest: 2>, 'Unknown': <FloatPolygonRoundPolicy.Unknown: 3>}

    def __eq__(self, other: typing.Any) -> bool:
        ...

    def __getstate__(self) -> int:
        ...

    def __hash__(self) -> int:
        ...

    def __index__(self) -> int:
        ...

    def __init__(self, value: int) -> None:
        ...

    def __int__(self) -> int:
        ...

    def __ne__(self, other: typing.Any) -> bool:
        ...

    def __repr__(self) -> str:
        ...

    def __setstate__(self, state: int) -> None:
        ...

    def __str__(self) -> str:
        ...

    @property
    def name(self) -> str:
        ...

    @property
    def value(self) -> int:
        ...


class ImageColorSpace:
    """
    Members:
      RGB : color image with rgb channel order which used usually!
      BGR : color image with bgr channel order,maybe decode with opencv!
      HSV : HSV color space!
      GrayScale : grayscale...
      Other : not supported other color space...
    """
    BGR: typing.ClassVar[ImageColorSpace]       # value = <ImageColorSpace.BGR: 1>
    GrayScale: typing.ClassVar[ImageColorSpace] # value = <ImageColorSpace.GrayScale: 3>
    HSV: typing.ClassVar[ImageColorSpace]       # value = <ImageColorSpace.HSV: 2>
    Other: typing.ClassVar[ImageColorSpace]     # value = <ImageColorSpace.Other: 4>
    RGB: typing.ClassVar[ImageColorSpace]       # value = <ImageColorSpace.RGB: 0>
    __members__: typing.ClassVar[
        dict[str, ImageColorSpace]
    ]                                           # value = {'RGB': <ImageColorSpace.RGB: 0>, 'BGR': <ImageColorSpace.BGR: 1>, 'HSV': <ImageColorSpace.HSV: 2>, 'GrayScale': <ImageColorSpace.GrayScale: 3>, 'Other': <ImageColorSpace.Other: 4>}

    def __eq__(self, other: typing.Any) -> bool:
        ...

    def __getstate__(self) -> int:
        ...

    def __hash__(self) -> int:
        ...

    def __index__(self) -> int:
        ...

    def __init__(self, value: int) -> None:
        ...

    def __int__(self) -> int:
        ...

    def __ne__(self, other: typing.Any) -> bool:
        ...

    def __repr__(self) -> str:
        ...

    def __setstate__(self, state: int) -> None:
        ...

    def __str__(self) -> str:
        ...

    @property
    def name(self) -> str:
        ...

    @property
    def value(self) -> int:
        ...


class MiconPixelSize:
    height_pixel_size: float
    requested_pixel_size: float
    width_pixel_size: float

    def __init__(self) -> None:
        ...


class PolygonCategory:
    """
    the category of polygon,example,nuclei or cell
    Members:
      Nuclei : means current polygon from nuclei!
      Cell : means current polygon from cell!
      Unknown : invalid polygon category!
    """
    Cell: typing.ClassVar[PolygonCategory]    # value = <PolygonCategory.Cell: 1>
    Nuclei: typing.ClassVar[PolygonCategory]  # value = <PolygonCategory.Nuclei: 0>
    Unknown: typing.ClassVar[PolygonCategory] # value = <PolygonCategory.Unknown: 2>
    __members__: typing.ClassVar[
        dict[str, PolygonCategory]
    ]                                         # value = {'Nuclei': <PolygonCategory.Nuclei: 0>, 'Cell': <PolygonCategory.Cell: 1>, 'Unknown': <PolygonCategory.Unknown: 2>}

    def __eq__(self, other: typing.Any) -> bool:
        ...

    def __getstate__(self) -> int:
        ...

    def __hash__(self) -> int:
        ...

    def __index__(self) -> int:
        ...

    def __init__(self, value: int) -> None:
        ...

    def __int__(self) -> int:
        ...

    def __ne__(self, other: typing.Any) -> bool:
        ...

    def __repr__(self) -> str:
        ...

    def __setstate__(self, state: int) -> None:
        ...

    def __str__(self) -> str:
        ...

    @property
    def name(self) -> str:
        ...

    @property
    def value(self) -> int:
        ...


class PolygonSizesInfo:
    polygon_size: int
    vertex_size: int


class PreferChunkInfo:
    """
    """
    chunk_idx: int
    rh: int
    rw: int
    x1: int
    xi: int
    y1: int
    yi: int

    @typing.overload
    def __init__(self) -> None:
        ...

    @typing.overload
    def __init__(self, arg0: int, arg1: int, arg2: int, arg3: int, arg4: int, arg5: int, arg6: int) -> None:
        ...


class StainChoiceType:
    """
    the stain choice type...
    Members:
      ImageOPticalDensity : means use density transform
      ImageHematoxylin : means use hematoxylin doc...
      Others : other stain...
    """
    ImageHematoxylin: typing.ClassVar[StainChoiceType]    # value = <StainChoiceType.ImageHematoxylin: 1>
    ImageOPticalDensity: typing.ClassVar[StainChoiceType] # value = <StainChoiceType.ImageOPticalDensity: 0>
    Others: typing.ClassVar[StainChoiceType]              # value = <StainChoiceType.Others: 2>
    __members__: typing.ClassVar[
        dict[str, StainChoiceType]
    ]                                                     # value = {'ImageOPticalDensity': <StainChoiceType.ImageOPticalDensity: 0>, 'ImageHematoxylin': <StainChoiceType.ImageHematoxylin: 1>, 'Others': <StainChoiceType.Others: 2>}

    def __eq__(self, other: typing.Any) -> bool:
        ...

    def __getstate__(self) -> int:
        ...

    def __hash__(self) -> int:
        ...

    def __index__(self) -> int:
        ...

    def __init__(self, value: int) -> None:
        ...

    def __int__(self) -> int:
        ...

    def __ne__(self, other: typing.Any) -> bool:
        ...

    def __repr__(self) -> str:
        ...

    def __setstate__(self, state: int) -> None:
        ...

    def __str__(self) -> str:
        ...

    @property
    def name(self) -> str:
        ...

    @property
    def value(self) -> int:
        ...


class StainType:
    """
    Members:
      Hematoxylin : using H&E stain...
      Eosin : using esoin stain...
      DAB : using DAB stain...
    """
    DAB: typing.ClassVar[StainType]         # value = <StainType.DAB: 2>
    Eosin: typing.ClassVar[StainType]       # value = <StainType.Eosin: 1>
    Hematoxylin: typing.ClassVar[StainType] # value = <StainType.Hematoxylin: 0>
    __members__: typing.ClassVar[
        dict[str, StainType]
    ]                                       # value = {'Hematoxylin': <StainType.Hematoxylin: 0>, 'Eosin': <StainType.Eosin: 1>, 'DAB': <StainType.DAB: 2>}

    def __eq__(self, other: typing.Any) -> bool:
        ...

    def __getstate__(self) -> int:
        ...

    def __hash__(self) -> int:
        ...

    def __index__(self) -> int:
        ...

    def __init__(self, value: int) -> None:
        ...

    def __int__(self) -> int:
        ...

    def __ne__(self, other: typing.Any) -> bool:
        ...

    def __repr__(self) -> str:
        ...

    def __setstate__(self, state: int) -> None:
        ...

    def __str__(self) -> str:
        ...

    @property
    def name(self) -> str:
        ...

    @property
    def value(self) -> int:
        ...


class WatershedRunningParams:
    apply_watershed_postprocess: bool
    background_by_reconstruction: bool
    background_radius: float
    brightness_threshold: float
    cell_expansion_radius: float
    exclude_DAB: bool
    guassian_sigma: float
    make_measurements: bool
    max_background: float
    median_radius: float
    merge_all: bool
    polygon_max_area: float
    polygon_min_area: float
    refine_boundary: bool
    smooth_boundaries: bool

    def __init__(self) -> None:
        ...


class WrapDataType:
    """
    Members:
      KINT8 : int8...
      KINT16 : int16
      KINT32 : int32
      KINT64 : int64
      KUINT8 : uint8
      KUINT16 : uint16
      KUINT32 : uint32
      KUINT64 : uint64
      KHALF : half
      KFLOAT : float
      KDOUBLE : double
      KOTHER : other dtype,like int128,etc...we not process now!
    """
    KDOUBLE: typing.ClassVar[WrapDataType] # value = <WrapDataType.KDOUBLE: 10>
    KFLOAT: typing.ClassVar[WrapDataType]  # value = <WrapDataType.KFLOAT: 9>
    KHALF: typing.ClassVar[WrapDataType]   # value = <WrapDataType.KHALF: 8>
    KINT16: typing.ClassVar[WrapDataType]  # value = <WrapDataType.KINT16: 1>
    KINT32: typing.ClassVar[WrapDataType]  # value = <WrapDataType.KINT32: 2>
    KINT64: typing.ClassVar[WrapDataType]  # value = <WrapDataType.KINT64: 3>
    KINT8: typing.ClassVar[WrapDataType]   # value = <WrapDataType.KINT8: 0>
    KOTHER: typing.ClassVar[WrapDataType]  # value = <WrapDataType.KOTHER: 11>
    KUINT16: typing.ClassVar[WrapDataType] # value = <WrapDataType.KUINT16: 5>
    KUINT32: typing.ClassVar[WrapDataType] # value = <WrapDataType.KUINT32: 6>
    KUINT64: typing.ClassVar[WrapDataType] # value = <WrapDataType.KUINT64: 7>
    KUINT8: typing.ClassVar[WrapDataType]  # value = <WrapDataType.KUINT8: 4>
    __members__: typing.ClassVar[
        dict[str, WrapDataType]
    ]                                      # value = {'KINT8': <WrapDataType.KINT8: 0>, 'KINT16': <WrapDataType.KINT16: 1>, 'KINT32': <WrapDataType.KINT32: 2>, 'KINT64': <WrapDataType.KINT64: 3>, 'KUINT8': <WrapDataType.KUINT8: 4>, 'KUINT16': <WrapDataType.KUINT16: 5>, 'KUINT32': <WrapDataType.KUINT32: 6>, 'KUINT64': <WrapDataType.KUINT64: 7>, 'KHALF': <WrapDataType.KHALF: 8>, 'KFLOAT': <WrapDataType.KFLOAT: 9>, 'KDOUBLE': <WrapDataType.KDOUBLE: 10>, 'KOTHER': <WrapDataType.KOTHER: 11>}

    def __eq__(self, other: typing.Any) -> bool:
        ...

    def __getstate__(self) -> int:
        ...

    def __hash__(self) -> int:
        ...

    def __index__(self) -> int:
        ...

    def __init__(self, value: int) -> None:
        ...

    def __int__(self) -> int:
        ...

    def __ne__(self, other: typing.Any) -> bool:
        ...

    def __repr__(self) -> str:
        ...

    def __setstate__(self, state: int) -> None:
        ...

    def __str__(self) -> str:
        ...

    @property
    def name(self) -> str:
        ...

    @property
    def value(self) -> int:
        ...


def compute_averaged_micron_pixel_size(h_pixel_size: float, w_pixel_size: float) -> float:
    """
    compute the average pixel size!
    """


def compute_overlap(have_micron_pixel_size: bool, micron_pixel_size: float, cell_expansion_radius: float) -> int:
    """
    compute the overlap of large image
    Args:
        have_micron_pixel_size:bool,if true,means the image has micron pixel size!
        physical_pixel_sizes:the micron size info...
        cell_expansion_radius:double,the expansion radius value
    Returns:
        overlap:int,the overlap value
    """


def compute_downsample_factor(micron_pixel_size: float, preferred_micon_pixel_size: float, apply_log2: bool) -> float:
    """
    to compute the downsample factor of the image which have micron pixel size!
    Args:
        height_micron_pixel_size:double
        width_micron_pixel_size:double,the pixel size of image
        preferred_micron_pixel_size:double,the preferred_micron_pixel_size,will use it to compute scale!
        bool apply_log2:whether compute with log!
    Returns:
        downsample_factor:double,a value > 1.0f
    """


def set_logger(output_2_terminal: bool, output_2_file: bool, log_file: str, max_keep_days: int = 3) -> None:
    """
    Args:
    output_2_terminal:bool,if true will print to stdout!
    output_2_file:bool,if true will add a file to write log
    log_file:str,the path of log file!
    max_keep_days:int,the keep days of the log file,default is 3 
    """
    ...


def flush_logger() -> None:
    ...


def test_throw_exception() -> None:
    ...


def divide_micron_pixel_size(watershed_params: WatershedRunningParams, pixel_size: float) -> None:
    """
        divide the watershed params with micron pixel size!
    """


def estimate_min_required_memory(height: int, width: int, chunk_size: int, parallel: int, is_fixed: bool) -> int:
    """
    a simple function to estimate the required memory!
    Args:
        height:int,the height of image
        width:int,the wdith of image
        chunk_size:int,the chunk_size you specify,like 2048,4096...
        parallel:int,the parallel level
        is_fixed:bool,whether use fixed size for each chunk!
    Returns:
        int:the memory will used!
    """


ENABLE_PARALEL_MINIMUM_IMAGE_SIZE: int = 4096
LARGE_POLYGON_SHARED_BUFFER_SIZE: int = 8388608
LARGE_TILE_SIZE: int = 4096
POLYOGN_SHARED_BUFFER_SIZE: int = 4194304
SAMLL_TILE_SIZE: int = 2048
SMALL_POLYGON_SHSRED_BUFFER_SIZE: int = 2097152
TILE_SIZE: int = 3072


class PyParallelWatershedCellRunner:
    """
    this is the implementation of watershed for python,
    using numpy.ndarray as input/out
    """

    def __init__(self) -> None:
        ...

    def apply_scale(self, scale_value: float) -> None:
        """
        apply scale for the deteced polygons, x *= scale y*= scale
        Args:
            scale_vaue:float,should >=1.0
        """
        ...

    def apply_transilation(self, offset_x: int, offset_y: int) -> None:
        """
        apply transilation for the detected polygons,like x = x + offset_x,y = y+offset
        Args:
            offset_x:int,should >=0
            offset_y:int,should >=0
        Returns:
            bool:if false,means fail to apply transilation
        """
        ...

    def clear(self, release_memory: bool) -> None:
        """
        clear the source of last watershed segmentation
        Args:
            release_memory:bool,if true,will release the memory of last time!include some image buffer
                this can help you to releae the memory immediately!
        """
        ...

    def get_alive_polygon_indexes(self) -> numpy.ndarray:
        """
        get all the alive polygon indexes....
        """
        ...

    def get_chunk_alive_polygon_indexes(self, chunk_index: int) -> numpy.ndarray:
        """
        get the alived indexes for specify chunk,this is not needed if running with single thread!
        """
        ...

    def get_chunk_npy_polygon(
        self, chunk_index: int, polygon_category: PolygonCategory, convert_to_i32: bool,
        round_policy: FloatPolygonRoundPolicy
    ) -> list[numpy.ndarray]:
        """
        get the detected polygon with chunk index
        Args:
            chunk_index:int,which chunk you want to get
            polygon_category:PolygonCategory enum,can be nuclei or cell
            convert_to_i32:bool,if true,return int32,else return float polygon
            round_policy:if specify convert_to_i32,we will round the float,support round lower,round upper,round nearest!
        Returns:
            bool:if true,means success!
        """
        ...

    def get_chunk_npy_polygon_directly(
        self,
        npy_polygons: list[numpy.ndarray],
        chunk_index: int,
        polygon_category: PolygonCategory,
        convert_to_i32: bool,
        round_policy: FloatPolygonRoundPolicy,
        check_npy: bool = True
    ) -> bool:
        """
        get the detected polygon with chunk index
        Args:
            npy_polygons:a list of arrays,if requires convert_to_i32,dtype is int32,else,dtype is float
                the memory is allocated by python,so can reduce one memory copy,but the shape should be match with c++
                this is low level api,if you do not know the detail,recommend use simple api!
            polygon_category:PolygonCategory enum,can be nuclei or cell
            chunk_index:int,which chunk you want to get
            convert_to_i32:bool,if true,return int32,else return float polygon
            round_policy:if specify convert_to_i32,we will round the float,support round lower,round upper,round nearest!
        Returns:
            bool:if true,means success!
        """
        ...

    def get_chunk_polygon_shapes(self, chunk_index: int, polygon_category: PolygonCategory) -> numpy.ndarray:
        """
        get the shape of polygons,then you can allocate the buffer with python,and not need  copy data from c++ to python,
        for large datas,this can imporve the performence!
        Args:
            chunk_index:int,which chunk you want to get
        """
        ...

    def get_chunk_running_flags(self) -> list[ErrorCode]:
        """
        get the running flags...
        """
        ...

    def get_n_chunks(self) -> int:
        """
        get the n_chunks of running...
        """
        ...

    def get_x_chunks(self) -> int:
        """
        get the x_chunks,along the width
        """
        ...

    def get_y_chunks(self) -> int:
        """
        get the y_chunks,along the height
        """
        ...

    def get_successful_chunks():
        """
        get the finished chunks
        Returns:
        a list of chunk_index,the index is finished chunk index!
        """
        ...

    def get_failed_chunks():
        """
        get the failed chunks
        Returns:
            a list of failed chunk index...
        """

    def get_cancelled_chunks():
        """
        get the cancelled chunks
        Returns:
            a list of failed chunks
        """
        ...

    def get_finished_chunks():
        """
        get the finished chunks;
        Returns:
            a list of finished chunks...
        """
        ...

    def get_chunk_info(chunk_index: int) -> PreferChunkInfo:
        """
    `   get the chunk info with specify chunk index!
        Args:
            chunk_index:int,the index of chunk,be sure < n_chunks
        Returns:
            a chunk info struct like
            the define of ChunkInfo is:
            ChunkIno {
                # chunk index
                uint32_t chunk_index;
                # which chunk
                uint32_t xi;
                uint32_t yi;
                # chunk range!
                uint32_t x1;
                uint32_t y1;
                uint32_t rw;
                uint32_t rh;
            }`
        """

    def get_npy_polygon(
        self, polygon_category: PolygonCategory, convert_to_i32: bool, round_policy: FloatPolygonRoundPolicy
    ) -> list[numpy.ndarray]:
        """
        get the detected polygon of all chunks
        Args:
            polygon_category:PolygonCategory enum,can be nuclei or cell!
            convert_to_i32:bool,if true,return int32,else return float polygon
            round_policy:if specify convert_to_i32,we will round the float,support round lower,round upper,round nearest!
        Returns:
            bool:if true,means success!
        """
        ...

    def get_npy_polygon_directly(
        self,
        npy_polygons: list[numpy.ndarray],
        polygon_category: PolygonCategory,
        convert_to_i32: bool,
        round_policy: FloatPolygonRoundPolicy,
        check_npy: bool = True
    ) -> bool:
        """
        get the detected polygon of all chunks
        Args:
            polygon_category:PolygonCategory enum,can be nuclei or cell!
            convert_to_i32:bool,if true,return int32,else return float polygon
            round_policy:if specify convert_to_i32,we will round the float,support round lower,round upper,round nearest!
        Returns:
            bool:if true,means success!
        """
        ...

    def get_polygon_shapes(self, polygon_category: PolygonCategory) -> numpy.ndarray:
        """
        get the shape of polygons,then you can allocate the buffer with python,and not need  copy data from c++ to python,
        for large datas,this can imporve the performence!
        """
        ...

    def has_cell(self) -> bool:
        """
        whether specify detect cell
        """
        ...

    def has_nuclei(self) -> bool:
        """
        whether specify detect nuclei,this is always true!
        """
        ...

    def is_success(self) -> bool:
        """
            whether the running is success,if not run,will also return false
                if exist failed chunk,also return false!
        """
        ...

    def release_resource_and_buffer() -> None:
        """
        release the buffer of last running!
        """
        ...

    def run(
        self,
        image: numpy.ndarray,
        is_brightfield: bool,
        color_space_type: ImageColorSpace,
        image_type: ColorImageType,
        stain_choice: StainChoiceType,
        exclude_DAB: bool,
        candidate_channel: int,
        watershed_params: WatershedRunningParams,
        downsample_factor: float,
        overlap: int,
        parallel: int,
        release_allocate_buffer: bool = True,
        numa_node: int = -1
    ) -> None:
        """
        run the cell watershed cell segmentation
        Args:
            image:anythin which can convert to numpy.ndarray,should have dtype=np.uint8
            is_brightfield:bool,whether a brightfield image
            color_space_type:enum,the color space of image,like rgb,bgr,grayscal.etc...
            image_type:enum,H&E or others...
            stain_choice:enum,the statin choice of image...
            exclude_DAB:bool,wheter to exclude the pixel from DAB stain
            candidate_channel:if fail to apply color transform,use the candidate channel to detect!
            watershed_params:the packed param of watershed....
            downsample_factor:double,the downsample factor of image,default is 1.0
            overlap:int,the overlap of tile
            parallel:int,determin how many thread used for large image
            numa_node:int,for unix like,to improve the mem access...
        Returns:
            bool:if true,means success
        """
        ...

    def run_with_async(
        self,
        image: numpy.ndarray,
        is_brightfield: bool,
        color_space_type: ImageColorSpace,
        image_type: ColorImageType,
        stain_choice: StainChoiceType,
        exclude_DAB: bool,
        candidate_channel: int,
        watershed_params: WatershedRunningParams,
        downsample_factor: float,
        overlap: int,
        parallel: int,
        release_allocate_buffer: bool = True,
        numa_node: int = -1
    ) -> None:
        """
        same as run func,but run in another thread,will return immediately
        you should invoke .wait to sync the task!
        """
        ...

    def set_cancle(self) -> None:
        """
        set cancel for parallle running mode,then will wating the running task,and the remains task will never be run,
        the status will be set to TaskIsCancelled!the function is thread safe
        """
        ...

    def wait(self) -> None:
        """
        wait for async task...
        """
        ...

    def get_image_height(self) -> int:
        """
        get the height of current detect image!
        """
        ...

    def get_image_width(self) -> int:
        """
        get the width of current detect image!
        """
        ...

    def get_filled_mask(
        self,
        fill_value: int,
        polygon_category: PolygonCategory,
        round_policy: FloatPolygonRoundPolicy = FloatPolygonRoundPolicy.RoundNearest
    ) -> numpy.ndarray:
        """
        get the filled mask,but this function will copy data from c++ -> python!
        Args:
            fill_value:int,must be in 0~255,if not in this range,we will set it -> 255
            polygon_category:nuceli or cell
            round_policy:can be floor,round or ceil,default value is round!
        Retrusn:
            filled_mask:a ndarray with uint8 dtype!
        """
        ...

    def get_filled_mask_directly(
        self,
        mask: numpy.ndarray,
        fill_value: int,
        is_initialized: bool,
        polygon_category: PolygonCategory,
        round_policy: FloatPolygonRoundPolicy = FloatPolygonRoundPolicy.RoundNearest
    ) -> bool:
        """
        get the filled mask,the python must have the right shape,if not match,we will return false
        you can use get_image_height/width to get the right shape of current detected image!
        Args:
            mask:a ndarray with uint8
            fill_value:int,should be between 0~255
            is_initialized:bool,if false,we will fill zero with given array!
            polygon_category:nuceli or cell!
            round_policy:floor/round/ceil!
        Returns:
            bool:if true means ok else means have some error!
        """
        ...

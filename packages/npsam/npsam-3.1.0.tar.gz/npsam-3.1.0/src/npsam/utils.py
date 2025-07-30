# Standard library imports
import gc
import math
import os
import sys
from pathlib import Path
from typing import Any, Optional

# Third-party imports
import cv2
import matplotlib
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import numba as nb
import numpy as np
import pandas as pd
import requests
import tifffile
import torch
from hyperspy.misc.utils import DictionaryTreeBrowser
from hyperspy.signals import BaseSignal, Signal1D, Signal2D
from numba.extending import overload, register_jitable
from PyQt6.QtWidgets import QFileDialog
from skimage.measure import regionprops
from skimage.morphology import remove_small_holes, remove_small_objects
from tqdm import tqdm
from ultralytics import FastSAM

import npsam as ns
from .segment_anything import SamAutomaticMaskGenerator, sam_model_registry


def listify(thing: Any) -> list:
    """
    Converts the input into a list if it is not already a list.
    Args:
        thing (Any): The input object to be converted into a list.
    Returns:
        list: The input wrapped in a list if it was not already a list, otherwise the
        input itself.
    """
    return [thing] if not isinstance(thing, list) else thing


def plot_masks(
    image: "ns.NPSAMImage",
    ax: Optional[plt.Axes] = None,
    alpha: float = 0.3,
    cmap: str = "default",
    filtered: bool = False,
) -> list:
    """
    Plots segmentation masks as filled contours on a given matplotlib axis.
    Parameters
    ----------
    image : NPSAMImage
        The image object containing the image data and segmentation metadata.
    ax : Optional[plt.Axes], default=None
        The matplotlib axes on which to plot. If None, uses the current axes.
    alpha : float, default=0.3
        The alpha (transparency) value for the mask countours.
    cmap : str, default="default"
        The colormap to use for the masks. If "default", a randomized colormap is
        generated.
    filtered : bool, default=False
        If True, only displays masks that have passed filtering as indicated in
        `image.cha["passed_filter"]`.
    Returns
    -------
    list
        A list of matplotlib Patch objects corresponding to the plotted mask contours.
    """
    if ax is None:
        ax = plt.gca()

    if cmap == "default":
        cmap = make_randomized_cmap()
    else:
        cmap = make_randomized_cmap(cmap)

    ax.imshow(image.img.data, cmap="gray")
    ax.axis("off")

    contours = image.seg.metadata.Filtering.Contours.as_dictionary()
    cs = []
    for n in range(len(contours)):
        color = cmap(n + 1)
        c = contours[str(n)]
        cs.append(
            ax.fill(c[:, 1], c[:, 0], linewidth=1, ec=color, fc=(*color[:-1], alpha))[0]
        )

    if filtered:
        for n, visibility in enumerate(image.cha["passed_filter"]):
            cs[n].set_visible(visibility)

    return cs


def get_filepath(
    directory: str = "./",
    filter: Optional[str] = None,
) -> str:
    """
    Opens a file dialog for the user to select a file and returns the selected file
    path.
    Parameters
    ----------
    directory : str, optional
        The initial directory to open in the file dialog. Defaults to './'.
    filter : Optional[str], optional
        A filter string to specify the types of files to display (e.g.,
        "image/jpeg"). Defaults to None.
    Returns
    -------
    str
        The path to the selected file as a string. Returns an empty string if no file is
        selected.
    """
    fname = QFileDialog.getOpenFileName(
        None, "Select file...", directory, filter=filter
    )
    print(f"filepath = '{fname[0]}'")
    return fname[0]


def get_filepaths(
    directory: str = "./",
    filter: Optional[str] = None,
) -> list:
    """
    Opens a file dialog for the user to select one or more files and returns their file
    paths.
    Parameters
    ----------
    directory : str, optional
        The initial directory to open in the file dialog. Defaults to './'.
    filter : Optional[str], optional
        A filter string to specify the types of files to display (e.g.,
        "image/jpeg"). Defaults to None.
    Returns
    -------
    list
        A list of selected file paths as strings.
    Notes
    -----
    This function uses `QFileDialog.getOpenFileNames` from PyQt or PySide. Make sure the
    appropriate Qt bindings are imported and a QApplication is running before calling
    this function.
    """
    fname = QFileDialog.getOpenFileNames(
        None, "Select file(s)...", directory, filter=filter
    )
    print(f"filepath = {fname[0]}".replace(", ", ",\n"))
    return fname[0]


def get_directory_path(directory: str = "./") -> str:
    """
    Opens a dialog for the user to select a directory and returns the selected path.
    Parameters
    ----------
    directory : str, optional
        The initial directory that the dialog will open in. Defaults to './'.
    Returns
    -------
    str
        The path to the selected directory as a string. If no directory is selected,
        returns an empty string.
    """
    folder = QFileDialog.getExistingDirectory(None, "Select a folder...", directory)
    print(f'filepath = "{folder}"')
    return folder


def FastSAM_segmentation(
    image: np.ndarray,
    device: str = "cpu",
    min_mask_region_area: int = 100,
) -> np.ndarray:
    """
    Segments an image using FastSAM and returns the resulting masks.

    Parameters
    ----------
    image : np.ndarray
        Input image array of shape (w, h, c) to be segmented.
    device : str, default='cpu'
        Device to run the segmentation on ('cpu' or 'cuda').
    min_mask_region_area : int, default=100
        Disconnected regions and holes in masks with area smaller than
        min_mask_region_area will be removed.

    Returns
    -------
    np.ndarray
        Array of masks with shape (m, w, h), where m is the number of masks.
    """
    sam_checkpoint = Path(os.path.dirname(__file__)) / "FastSAM.pt"
    if not sam_checkpoint.is_file():
        download_weights("fast")
    model = FastSAM(sam_checkpoint)
    results = model(
        source=image,
        device=device,
        retina_masks=True,  # imgsz=image.shape[0],
        imgsz=int(np.ceil(max(image.shape[0], image.shape[1]) / 32) * 32),
        conf=0.2,
        iou=0.9,
        verbose=False,
    )
    masks = results[0].masks.data.cpu().numpy().astype("uint8")
    if min_mask_region_area > 0:
        for n, mask in enumerate(masks):
            masks[n] = remove_small_holes(masks[n] > 0, min_mask_region_area).astype(
                "uint8"
            )
            masks[n] = remove_small_objects(masks[n] > 0, min_mask_region_area).astype(
                "uint8"
            )
    return masks


def SAM_segmentation(
    image: np.ndarray,
    model_type: str = "huge",
    device: str = "gpu",
    PPS: int = 64,
    min_mask_region_area: int = 100,
    **kwargs: Any,
) -> np.ndarray:
    """
    Segments an image using SAM (Segment Anything Model) and returns the resulting masks.

    Parameters
    ----------
    image : np.ndarray
        Input image array of shape (w, h, c) to be segmented.
    model_type : str, default='huge'
        Model type to use for segmentation. Options are 'huge', 'large', or 'base'.
    device : str, default='gpu'
        Device to run the segmentation on ('gpu' or 'cpu'). If a CUDA compatible GPU is
        available, it is usually much faster
    PPS : int, default=64
        Points per side. Determines the number of sampling points for mask generation.
    min_mask_region_area : int, default=100
        Disconnected regions and holes in masks with area smaller than this value will
        be removed.
    **kwargs : Any
        Additional keyword arguments passed to the SamAutomaticMaskGenerator.

    Returns
    -------
    np.ndarray
        Array of masks with shape (m, w, h), where m is the number of masks.
    """
    model_info = {
        "base": ["vit_b", "sam_vit_b_01ec64.pth"],
        "large": ["vit_l", "sam_vit_l_0b3195.pth"],
        "huge": ["vit_h", "sam_vit_h_4b8939.pth"],
    }
    sam_checkpoint = Path(os.path.dirname(__file__)) / model_info.get(model_type)[1]
    if not sam_checkpoint.is_file():
        download_weights(model_type)
    # set up model
    sam = sam_model_registry[model_info.get(model_type)[0]](
        checkpoint=sam_checkpoint
    ).to(device=device)
    mask_generator = SamAutomaticMaskGenerator(
        sam, points_per_side=PPS, min_mask_region_area=min_mask_region_area, **kwargs
    )
    masks = mask_generator.generate(image)
    masks = np.stack([mask["segmentation"].astype(np.uint8) for mask in masks])
    if device in {"cuda", "cuda:0"}:
        gc.collect()
        torch.cuda.empty_cache()
    return masks


def save_df_to_csv(
    df: pd.DataFrame,
    filepath: str | Path,
) -> None:
    """
    Save a pandas DataFrame to a CSV file, including DataFrame attributes as header
    metadata. The function writes all attributes from `df.attrs` as key-value pairs at
    the top of the file, followed by the CSV representation of the DataFrame. The file
    path is also stored in the attributes under the key 'filepath'.
    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame to be saved.
    filepath : str or Path
        The path to the output CSV file.
    Returns
    -------
    None
    Notes
    -----
    - DataFrame attributes are written as lines in the format `key : value` before the
      CSV data.
    - The 'filepath' attribute is automatically set to the output file's path.
    """
    df.attrs["filepath"] = Path(filepath).as_posix()
    attrs_keys = list(df.attrs.keys())
    attrs_keys.sort()
    with open(filepath, "w", encoding="utf-8") as f:
        for key in attrs_keys:
            f.write(f"{key} : {df.attrs[key]}\n")
        df.to_csv(f, encoding="utf-8", header="true", index=False, lineterminator="\n")


def load_df_from_csv(filepath: str | Path) -> pd.DataFrame:
    """
    Load a pandas DataFrame from a CSV file, attaching metadata from the first few rows
    as DataFrame attributes. The function assumes that the first `metadatarows` lines of
    the CSV file contain metadata in the format "key : value". These metadata entries
    are added to the DataFrame's `.attrs` dictionary. The remaining rows are read as the
    DataFrame.
    Parameters
    ----------
    filepath : str or Path
        Path to the CSV file to load.
    Returns
    -------
    pd.DataFrame
        DataFrame containing the data from the CSV file, with metadata stored in the
        `.attrs` attribute.
    Notes
    -----
    - The number of metadata rows is set by the `metadatarows` variable (default is 3).
    - Each metadata row must be formatted as "key : value".
    """
    metadatarows = 3
    df = pd.read_csv(filepath, skiprows=metadatarows)
    with open(filepath) as f:
        for n in range(metadatarows):
            line = f.readline().strip("\n")
            key, value = line.split(" : ")
            df.attrs[key] = value
    return df


def masks_to_2D(masks: np.ndarray) -> np.ndarray:
    """
    Converts a stack of binary masks into a single 2D labeled array.
    Each mask in the input is assigned a unique integer label, and overlapping regions
    are labeled with their own unique integer based on the order of the masks.
    Parameters
    ----------
    masks : np.ndarray
        A 3D numpy array of shape (N, H, W), where N is the number of masks,
        and each mask is a binary (0 or 1) array of shape (H, W).
    Returns
    -------
    labels : np.ndarray
        A 2D numpy array of shape (H, W) where each pixel contains the label of the mask
        it belongs to. Overlapping areas get their own unique label. Pixels not covered
        by any mask are set to 0.
    """
    weights = np.arange(1, masks.shape[0] + 1)[:, np.newaxis, np.newaxis]
    weighted_masks = masks * weights
    labels = np.sum(weighted_masks, axis=0)
    return labels


def plot_images(filepaths: list[str]) -> None:
    """
    Displays a set of images from the given file paths in a grid layout using
    matplotlib.
    Parameters
    ----------
    filepaths : list of str
        List of file paths to the images to be displayed.
    Returns
    -------
    None
        This function does not return anything. It displays the images in a matplotlib
        figure.
    Notes
    -----
    - Supports displaying up to 3 images per row.
    - If the number of images is not a multiple of 3, empty subplots are hidden.
    - Images are displayed in grayscale.
    """
    n = len(filepaths)
    columns = min(n, 3)
    rows = n // 3 + int(n % 3 != 0)

    fig, axes = plt.subplots(rows, columns, figsize=(5 * columns, 5 * rows))
    if n > 1:
        axes = axes.flatten()
    else:
        axes = [axes]

    for ax, filepath in zip(axes, filepaths):
        img = mpimg.imread(filepath)
        ax.imshow(img, cmap="gray")
        ax.set_title(f"filepath = '{filepath}'", fontsize=8)
        ax.axis("off")

    if n > 3:
        for i in range(n, len(axes)):
            axes[i].axis("off")

    plt.tight_layout()
    plt.show()


def set_scaling(
    signal: BaseSignal | Signal1D | Signal2D,
    scaling: str,
) -> None:
    """
    Sets the scaling for the x and y axes of a HyperSpy signal.

    Parameters
    ----------
    signal : BaseSignal, Signal1D or Signal2D from hyperspy.signals
        The HyperSpy signal whose axes scaling will be set.
    scaling : str
        The scaling to apply to each axis, specified as a string indicating the scale of
        1 pixel, e.g., '2.5 nm', '5 mm', '2.7 µm', or '2.7 um'.

    Returns
    -------
    None
        This function modifies the signal in place.
    """
    for axis in get_x_and_y_axes(signal):
        axis.scale_as_quantity = scaling


def convert_to_units(
    signal: BaseSignal | Signal1D | Signal2D,
    units: str,
) -> None:
    """
    Converts the axes of a HyperSpy signal to the specified units.

    Parameters
    ----------
    signal : BaseSignal, Signal1D, or Signal2D
        The HyperSpy signal whose axes will be converted.
    units : str
        The target units for the axes, e.g., 'nm', 'µm', or 'um'.

    Returns
    -------
    None
        This function modifies the signal in place.
    """
    for axis in get_x_and_y_axes(signal):
        axis.convert_to_units(units)


def load_image_RGB(filepath: str | Path) -> np.ndarray:
    """
    Load an image from the given file path and return it as an RGB NumPy array.
    This function supports TIFF, PNG, and JPEG image formats. For TIFF images, it
    handles both grayscale and multi-channel images, normalizing the pixel values to
    8-bit and stacking to create an RGB image. For PNG and JPEG images, it reads and
    converts the image from BGR to RGB format.
    Parameters
    ----------
    filepath : str or Path
        The path to the image file to be loaded.
    Returns
    -------
    np.ndarray
        The loaded image as an RGB NumPy array with dtype 'uint8' and shape (H, W, 3).
    Raises
    ------
    ValueError
        If the image cannot be read from the given file path.
    """
    if Path(filepath).suffix in {".tif", ".tiff"}:
        try:
            im = tifffile.imread(filepath)
        except ValueError:
            im = cv2.imread(filepath, cv2.IMREAD_UNCHANGED)

        if im.ndim == 3 and im.shape[-1] in {3, 4}:
            im = im[:, :, 0]
        elif im.ndim == 3:
            im = np.mean(im, axis=-1)

        im_shift_to_zero = im - im.min()
        im_max = im_shift_to_zero.max()
        im_normalized = im_shift_to_zero / im_max
        im_max_255 = im_normalized * 255
        im_8bit = im_max_255.astype("uint8")
        im_RGB = np.dstack([im_8bit] * 3)
    elif Path(filepath).suffix in {
        ".png",
        ".jpg",
        ".jpeg",
    }:
        im = cv2.imread(filepath)
        im_RGB = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
    return im_RGB


def make_randomized_cmap(
    cmap: str = "viridis",
    seed: int = 42,
    randomize: bool = True,
) -> matplotlib.colors.ListedColormap:
    """
    Generates a randomized matplotlib colormap with the first color set to black.

    Parameters
    ----------
    cmap : str, optional
        Name of the base matplotlib colormap to use (default is 'viridis').
    seed : int, optional
        Random seed for reproducibility of the color shuffling (default is 42).
    randomize : bool, optional
        If True, randomizes the order of the colormap colors except the first (default
        is True).

    Returns
    -------
    matplotlib.colors.ListedColormap
        A ListedColormap object with the first color as black and the rest randomized
        (if specified).

    Notes
    -----
    The first color in the returned colormap is always black ([0, 0, 0, 1]).
    The rest of the colors are taken from the specified colormap and can be randomized.
    """
    cmap = matplotlib.colormaps[cmap]
    cmap_colors = cmap(np.linspace(0, 1, 2000))
    black_color = np.array([0, 0, 0, 1])
    cmap_rest_colors = cmap_colors[1:, :]
    if randomize:
        np.random.seed(seed)
        np.random.shuffle(cmap_rest_colors)
    randomized_cmap = matplotlib.colors.ListedColormap(
        np.vstack((np.expand_dims(black_color, 0), cmap_rest_colors))
    )
    return randomized_cmap


def is_scaled(signal: BaseSignal | Signal1D | Signal2D) -> bool:
    """
    Check if x and y axes of a signal are scaled.
    Parameters
    ----------
    signal : BaseSignal or Signal1D or Signal2D
        The signal object whose axes are to be checked for scaling.
    Returns
    -------
    bool
        True if all axes are scaled (i.e., not in arbitrary or pixel units), False
        otherwise.
    Notes
    -----
    An axis is considered unscaled if its scale is '1.0', '1.0 ', or '1.0 px'.
    """

    scaled = True
    for axis in get_x_and_y_axes(signal):
        if format(axis.scale_as_quantity, "~") in ["1.0", "1.0 ", "1.0 px"]:
            scaled = False
    return scaled


def get_scaling(signal: BaseSignal | Signal1D | Signal2D) -> str:
    """
    Get the scaling factor of the x-axis of a signal as a formatted string.
    Parameters
    ----------
    signal : BaseSignal or Signal1D or Signal2D
        The signal object from which to extract the scaling information.
    Returns
    -------
    str
        The scaling factor of the x-axis, formatted as a string using the '~' format.
    Examples
    --------
    >>> scaling = get_scaling(my_signal)
    >>> print(scaling)
    '1 nm'
    """
    axes = get_x_and_y_axes(signal)
    return format(axes[0].scale_as_quantity, "~")


def get_x_and_y_axes(signal: BaseSignal | Signal1D | Signal2D) -> list:
    """
    Extracts the appropriate axes (x and y) from a signal object based on its type.
    Parameters
    ----------
    signal : BaseSignal or Signal1D or Signal2D
        The signal object from which to extract axes. Must be an instance of BaseSignal,
        Signal1D, or Signal2D.
    Returns
    -------
    list
        A list of axes corresponding to the signal's x and y axes. For Signal2D, returns
        the signal axes; for BaseSignal and Signal1D, returns the navigation axes.
    Raises
    ------
    ValueError
        If the signal is not an instance of Signal2D, Signal1D, or BaseSignal.
    """
    if isinstance(signal, Signal2D):
        axes = signal.axes_manager.signal_axes
    elif isinstance(signal, (BaseSignal, Signal1D)):
        axes = signal.axes_manager.navigation_axes
    else:
        raise ValueError(
            "The signal argument doesn't seem to be Signal2D, Signal1D or BaseSignal."
        )
    return axes


def preprocess(
    image: BaseSignal | Signal1D | Signal2D,
    crop_and_enlarge: bool = False,
    invert: bool = False,
    double: bool = False,
) -> list:
    """
    Preprocesses a HyperSpy signal image for segmentation.

    This function converts a HyperSpy signal (1D or 2D) to an RGB numpy array, with
    options to crop and enlarge the image into four sections, invert the image, and
    optionally double the dataset by including both original and inverted images. The
    output is a list of RGB image arrays ready for segmentation.

    Parameters
    ----------
    image : BaseSignal | Signal1D | Signal2D
        The input image as a HyperSpy signal object.
    crop_and_enlarge : bool, optional
        If True, crops and enlarges the image into four sections. Default is False.
    invert : bool, optional
        If True, inverts the image(s). Default is False.
    double : bool, optional
        If True and invert is also True, doubles the dataset by including both original
        and inverted images. Ignored if invert is False. Default is False.

    Returns
    -------
    list of numpy.ndarray
        A list of RGB image arrays ready for segmentation.

    Notes
    -----
    - The function assumes the presence of helper functions: PNGize,
      crop_and_enlarge_image, and invert_image.
    - If `double` is True but `invert` is False, a warning is printed and `double` is
      ignored.
    """
    image = PNGize(image.data)
    if crop_and_enlarge:
        images = crop_and_enlarge_image(image)
    else:
        images = [image]
    if invert:
        images = [invert_image(im) for im in images]
        if double:
            images += [invert_image(im) for im in images]
    else:
        if double:
            print("Ignoring double=True, since it requires inversion to be True.")
    return images


def PNGize(image: np.ndarray) -> np.ndarray:
    """
    Converts an image array to a PNG-style RGB image.

    Parameters
    ----------
    image : np.ndarray
        Input image array. If the image is a 2D grayscale array, it will be converted
        to a 3-channel (RGB) grayscale image.

    Returns
    -------
    np.ndarray
        The image as a 3-channel (RGB) array of dtype 'uint8'. If the input is already
        a 3-channel image, it is returned unchanged.

    Notes
    -----
    - If the input is a single-channel (2D) grayscale image, it is normalized to the
      range [0, 255] and stacked into three identical channels to create an RGB image.
    - If the input is already a 3-channel image, no changes are made.
    """
    if image.ndim == 2:
        image_normalized = np.round(
            (image - image.min()) / (image.max() - image.min()) * 255
        ).astype("uint8")
        image = np.dstack([image_normalized] * 3)
    return image


def invert_image(image: np.ndarray) -> np.ndarray:
    """
    Invert the pixel values of an image.
    This function takes a NumPy array representing an image and inverts its pixel
    values.
    For example, a pixel value of 0 becomes 255 and vice versa for an 8-bit image.
    Parameters
    ----------
    image : np.ndarray
        Input image as a NumPy array.
    Returns
    -------
    np.ndarray
        Inverted image as a NumPy array.
    Examples
    --------
    >>> import numpy as np
    >>> import cv2
    >>> img = np.array([[0, 255], [128, 64]], dtype=np.uint8)
    >>> invert_image(img)
    array([[255,   0],
           [127, 191]], dtype=uint8)
    """
    return cv2.bitwise_not(image)


def crop_and_enlarge_image(image: np.ndarray) -> list[np.ndarray]:
    """
    Crops an input image into four quadrants and enlarges each quadrant by a factor of 2
    using nearest-neighbor upsampling.
    The image is divided into northwest (NW), northeast (NE), southwest (SW), and
    southeast (SE) quadrants.

    Parameters
    ----------
    image : np.ndarray
        Input image as a NumPy array of shape (H, W, C), where H is height, W is width,
        and C is the number of channels.
    Returns
    -------
    list of np.ndarray
        A list containing four NumPy arrays corresponding to the enlarged NW, NE, SW,
        and SE quadrants, in that order.
    """
    h = image.shape[0]
    w = image.shape[1]

    nw = np.kron(
        image[: int(h * 0.625), : int(w * 0.625), :], np.ones((2, 2, 1))
    ).astype("uint8")
    ne = np.kron(
        image[: int(h * 0.625), math.ceil(w * 0.375) :, :], np.ones((2, 2, 1))
    ).astype("uint8")
    sw = np.kron(
        image[math.ceil(h * 0.375) :, : int(w * 0.625), :], np.ones((2, 2, 1))
    ).astype("uint8")
    se = np.kron(
        image[math.ceil(h * 0.375) :, math.ceil(w * 0.375) :, :], np.ones((2, 2, 1))
    ).astype("uint8")

    return [nw, ne, sw, se]


def rearrange_masks(
    masks_from_four_crops: list[np.ndarray],
    original_image_shape: tuple,
) -> np.ndarray:
    """
    Rearranges masks from four image crops (northwest, northeast, southwest, southeast)
    into a single array matching the original image's shape.
    Parameters
    ----------
    masks_from_four_crops : list of np.ndarray
        List containing four arrays of masks, each corresponding to a crop: [nw, ne, sw,
        se]. Each array should have shape (num_masks, crop_height, crop_width).
    original_image_shape : tuple
        Tuple (height, width) representing the shape of the original image before
        cropping.
    Returns
    -------
    np.ndarray
        Array of shape (total_masks, height*2, width*2) where all masks are rearranged
        to their original positions in the full image.
    Notes
    -----
    - The function assumes the four crops correspond to the northwest, northeast,
      southwest, and southeast quadrants of the original image.
    - The returned array is of dtype 'uint8'.
    """
    h = original_image_shape[0]
    w = original_image_shape[1]

    nw, ne, sw, se = masks_from_four_crops
    total_masks = len(nw) + len(ne) + len(sw) + len(se)
    rearranged_masks = np.zeros((total_masks, h * 2, w * 2)).astype("uint8")
    rearranged_masks[: len(nw), : nw.shape[1], : nw.shape[2]] = nw
    rearranged_masks[len(nw) : len(nw) + len(ne), : ne.shape[1], -ne.shape[2] :] = ne
    rearranged_masks[
        len(nw) + len(ne) : len(nw) + len(ne) + len(sw), -sw.shape[1] :, : sw.shape[2]
    ] = sw
    rearranged_masks[len(nw) + len(ne) + len(sw) :, -se.shape[1] :, -se.shape[2] :] = se

    return rearranged_masks


def bb_iou(
    boxA: np.ndarray | list[float],
    boxB: np.ndarray | list[float],
) -> float:
    """
    Calculate the Intersection over Union (IoU) between two bounding boxes.
    Parameters
    ----------
    boxA : np.ndarray or list of float
        The first bounding box, specified as [x_min, y_min, x_max, y_max].
    boxB : np.ndarray or list of float
        The second bounding box, specified as [x_min, y_min, x_max, y_max].
    Returns
    -------
    float
        The IoU between the two bounding boxes, a value between 0 and 1.
    Notes
    -----
    IoU is defined as the area of the intersection divided by the area of the union
    of two bounding boxes. If the boxes do not overlap, the IoU is 0.
    """
    xA = np.maximum(boxA[0], boxB[0])
    yA = np.maximum(boxA[1], boxB[1])
    xB = np.minimum(boxA[2], boxB[2])
    yB = np.minimum(boxA[3], boxB[3])

    interArea = np.maximum(0, xB - xA) * np.maximum(0, yB - yA)

    boxAArea = (boxA[2] - boxA[0]) * (boxA[3] - boxA[1])
    boxBArea = (boxB[2] - boxB[0]) * (boxB[3] - boxB[1])

    iou = interArea / (boxAArea + boxBArea - interArea)
    return iou


def remove_overlapping_masks(
    masks: np.ndarray,
    iou_threshold: float = 0.8,
    verbose: bool = False,
    return_indices: bool = False,
) -> np.ndarray | tuple[np.ndarray, list[int]]:
    """
    Removes overlapping masks based on Intersection over Union (IoU) threshold.
    Given an array of binary masks, this function compares the bounding boxes of each
    mask and removes those that overlap above a specified IoU threshold. Optionally, it
    can return the indices of the masks that are kept.
    Parameters
    ----------
    masks : np.ndarray
        Array of binary masks, where each mask is a 2D array.
    iou_threshold : float, optional
        IoU threshold above which masks are considered overlapping and one is removed.
        Default is 0.8.
    verbose : bool, optional
        If True, prints progress and summary information. Default is False.
    return_indices : bool, optional
        If True, returns a tuple of (unique_masks, indices_kept). Default is False.
    Returns
    -------
    np.ndarray or tuple of (np.ndarray, list of int)
        If `return_indices` is False, returns an array of unique masks with overlaps
        removed.
        If `return_indices` is True, returns a tuple containing the array of unique
        masks and a list of indices of the kept masks.
    Notes
    -----
    - The function assumes that `regionprops` and `bb_iou` are defined elsewhere.
    - Only the first region in each mask is considered for bounding box extraction.
    - Masks that are almost identical (IoU >= `iou_threshold`) are considered
      overlapping.
    """
    # This will store the indices of the bboxes to keep
    to_keep = []
    array_of_bboxes = np.array(
        [list(regionprops(mask)[0]["bbox"]) for mask in masks]
    )  # if mask.sum()>0
    for i, boxA in enumerate(array_of_bboxes):
        if verbose:
            print(
                f"Mask {i + 1}/{array_of_bboxes.shape[0]}",
                sep=",",
                end="\r" if i + 1 < array_of_bboxes.shape[0] else "\n",
                flush=True,
            )
        keep = True
        for j, boxB in enumerate(array_of_bboxes):
            if i != j:
                iou = bb_iou(boxA, boxB)
                if iou >= iou_threshold:
                    if i not in to_keep and j not in to_keep:
                        to_keep.append(i)
                    keep = False
                    break
        if keep:
            to_keep.append(i)

    unique_masks = masks[to_keep]

    if verbose:
        print(
            f"{len(masks) - len(unique_masks)} masks have been removed because they were almost indentical."
        )

    if return_indices:
        return unique_masks, to_keep
    return unique_masks


def bin_masks(masks: np.ndarray) -> np.ndarray:
    """
    Bins a stack of boolean masks by combining each 2x2 block into a single pixel.
    For each 2x2 block in the spatial dimensions, the output pixel is set to True if any
    of the four input pixels are True.
    Parameters
    ----------
    masks : np.ndarray
        A 3D boolean or integer array of shape (n, y, x), where n is the number of
        masks, and y and x are the spatial dimensions. Both y and x must be even
        numbers.
    Returns
    -------
    np.ndarray
        A 3D uint8 array of shape (n, y//2, x//2), where each pixel represents the
        logical OR of the corresponding 2x2 block in the input.
    Raises
    ------
    ValueError
        If the spatial dimensions (y or x) of the input array are not even.
    """
    if masks.shape[1] % 2 or masks.shape[2] % 2:
        raise ValueError(
            "The x and y dimensions of the array must be even for 2x2 binning."
        )

    # If one of four pixels in a 2x2 pixel group is True, the binned will also be True
    binned_masks = (
        (
            masks[:, ::2, ::2]
            + masks[:, 1::2, ::2]
            + masks[:, ::2, 1::2]
            + masks[:, 1::2, 1::2]
        )
        > 0
    ).astype("uint8")
    return binned_masks


def stitch_crops_together(
    masks_from_four_crops: list[np.ndarray],
    original_image_shape: tuple,
    iou_threshold: float = 0.8,
    verbose: bool = False,
) -> np.ndarray:
    """
    Stitches together masks from four image crops into a single mask for the original
    image.
    This function takes a list of masks generated from four crops of an image,
    rearranges them to fit the original image shape, removes overlapping masks based on
    Intersection over Union (IoU) threshold, and bins the resulting unique masks.
    Parameters
    ----------
    masks_from_four_crops : list of np.ndarray
        List containing masks from four different crops of the original image.
    original_image_shape : tuple
        The shape (height, width) of the original image to reconstruct the full mask.
    iou_threshold : float, optional
        IoU threshold for considering two masks as overlapping (default is 0.8).
    verbose : bool, optional
        If True, prints detailed information during processing (default is False).
    Returns
    -------
    np.ndarray
        The final binned mask array corresponding to the original image shape, with
        overlapping masks removed.
    """
    print("Rearranging masks.")
    rearranged_masks = rearrange_masks(
        masks_from_four_crops, original_image_shape, verbose=verbose
    )

    print("Removing masks with identical bounding boxes.")
    unique_masks = remove_overlapping_masks(
        rearranged_masks, iou_threshold=iou_threshold, verbose=verbose
    )

    binned_masks = bin_masks(unique_masks)
    return binned_masks


def format_time(elapsed_time: float) -> str:
    """
    Format a time duration given in seconds into a human-readable string.
    Parameters
    ----------
    elapsed_time : float
        The elapsed time in seconds.
    Returns
    -------
    str
        A string representing the elapsed time in minutes and seconds,
        e.g., "2 minutes and 5 seconds".
    Examples
    --------
    >>> format_time(65)
    '1 minute and 5 seconds'
    >>> format_time(120)
    '2 minutes and 0 seconds'
    >>> format_time(45)
    '45 seconds'
    """
    minutes, seconds = divmod(elapsed_time, 60)
    time_string = ""
    if minutes >= 1:
        minute_label = "minute" if minutes == 1 else "minutes"
        time_string += f"{int(minutes)} {minute_label} and "
    second_label = "second" if seconds == 1 else "seconds"
    time_string += f"{round(seconds)} {second_label}"
    return time_string


def seg_params_to_str(seg_params: DictionaryTreeBrowser | str) -> str:
    """
    Converts segmentation parameters to a string representation.
    Parameters
    ----------
    seg_params : DictionaryTreeBrowser or str
        Segmentation parameters, either as a DictionaryTreeBrowser object or a string.
        If a string is provided, it is returned as-is. If a DictionaryTreeBrowser is
        provided, the function constructs a string summarizing the segmentation
        parameters.
    Returns
    -------
    str
        A string representation of the segmentation parameters.
    Notes
    -----
    - If `seg_params` is a string, it is assumed to be an imported segmentation
      description.
    - If `seg_params` is a DictionaryTreeBrowser, the string is constructed based on its
      attributes:
        - `SAM_model` (always included)
        - `PPS` (included if `SAM_model` is not "fast")
        - "C&E" if `crop_and_enlarge` is True
        - "I" if `invert` is True
        - "D" if `double` is True
        - "no EF" if `edge_filter` is False
        - "no SF" if `shape_filter` is False
        - `MMA` (min_mask_region_area) if not equal to 100
    """
    # seg_params = self.seg.metadata.Segmentation
    if isinstance(seg_params, str):
        # Happens when segmentation is imported from elsewhere
        segmentation = seg_params
    else:
        segmentation = (
            seg_params.SAM_model
            + (f", PPS={seg_params.PPS}" if seg_params.SAM_model != "fast" else "")
            + (", C&E" if seg_params.crop_and_enlarge else "")
            + (", I" if seg_params.invert else "")
            + (", D" if seg_params.double else "")
            + (", no EF" if not seg_params.edge_filter else "")
            + (", no SF" if not seg_params.shape_filter else "")
            + (
                f", MMA={seg_params.min_mask_region_area}"
                if seg_params.min_mask_region_area != 100
                else ""
            )
        )
    return segmentation


def download_weights(
    model: str,
    noconfirm: bool = False,
    app: bool = False,
) -> None:
    """
    Downloads model weights for the specified model if not already present.
    Parameters
    ----------
    model : str
        The model type to download weights for. Must be one of 'huge', 'large', 'base',
        or 'fast'.
    noconfirm : bool, optional
        If True, skips the user confirmation prompt and downloads the weights
        automatically. Default is False.
    app : bool, optional
        If True, uses fixed-width progress bar (for app integration); otherwise, uses
        dynamic width. Default is False.
    Returns
    -------
    None
    Notes
    -----
    - Downloads the weights file from a predefined URL and saves it in the same directory as this script.
    - If the directory does not exist, prints an error message.
    - Shows a progress bar during download.
    - Prints a message upon successful download or if the download is stopped or fails.
    """
    model_checkpoints = {
        "huge": [
            "https://osf.io/download/65b0d08399d01005546266f2/",
            "sam_vit_h_4b8939.pth",
            "2.5 GB",
        ],
        "large": [
            "https://osf.io/download/65b0d0624aa63c05c2df18f4/",
            "sam_vit_l_0b3195.pth",
            "1.2 GB",
        ],
        "base": ["https://osf.io/download/k6ce8/", "sam_vit_b_01ec64.pth", "366 MB"],
        "fast": ["https://osf.io/download/p7kmb/", "FastSAM.pt", "144 MB"],
    }
    if not noconfirm:
        ask_for_download = input(
            (
                f"SAM weights were not found. \n"
                f"This is probably because it is the first time running NP-SAM \n"
                f"with this option. Do you want to download the {model} weights "
                f"file (size: {model_checkpoints.get(model)[2]})? Y/n"
            )
        )
    else:
        ask_for_download = ""

    if ask_for_download.lower() in ["y", "yes", ""] or noconfirm:
        directory = os.path.dirname(__file__)

        if not os.path.exists(directory):
            print("NP-SAM is not correctly installed")
            return

        file_path = os.path.join(directory, model_checkpoints.get(model)[1])
        try:
            response = requests.get(model_checkpoints.get(model)[0], stream=True)
            response.raise_for_status()

            total_length = int(response.headers.get("content-length", 0))

            if app:
                with (
                    open(file_path, "wb") as file,
                    tqdm(
                        desc=model_checkpoints.get(model)[1],
                        total=total_length,
                        unit="iB",
                        unit_scale=True,
                        unit_divisor=1024,
                        file=sys.stdout,
                        colour="GREEN",
                        ncols=0,
                        smoothing=0.1,
                    ) as bar,
                ):
                    for data in response.iter_content(chunk_size=1024):
                        size = file.write(data)
                        bar.update(size)
            else:
                with (
                    open(file_path, "wb") as file,
                    tqdm(
                        desc=model_checkpoints.get(model)[1],
                        total=total_length,
                        unit="iB",
                        unit_scale=True,
                        unit_divisor=1024,
                        file=sys.stdout,
                        colour="GREEN",
                        dynamic_ncols=True,
                        smoothing=0.1,
                    ) as bar,
                ):
                    for data in response.iter_content(chunk_size=1024):
                        size = file.write(data)
                        bar.update(size)
            print(f"File downloaded successfully: {file_path}")
        except requests.RequestException as e:
            print(f"Failed to download {model_checkpoints.get(model)[1]}: {e}")
    else:
        print("Download stopped.")


def choose_device() -> str:
    """
    Selects the appropriate device for computation based on CUDA availability and GPU
    memory.
    Returns
    -------
    str
        The device to use for computation: 'cuda' if a CUDA-enabled GPU with more than
        5GB memory is available, otherwise 'cpu'.
    """
    if (
        torch.cuda.is_available()
        and torch.cuda.get_device_properties(0).total_memory / 1024**3 > 5
    ):
        device = "cuda"
    else:
        device = "cpu"
    return device


def choose_SAM_model(
    SAM_model: str,
    device: str,
    verbose=True,
) -> str | None:
    """
    Selects the appropriate SAM (Segment Anything Model) model variant based on user
    input and device capabilities.
    Parameters
    ----------
    SAM_model : str
        The desired SAM model variant. Can be one of {'a', 'auto', 'f', 'fast', 'b',
        'base', 'l', 'large', 'h', 'huge'}.
        'a' or 'auto' selects the model automatically based on device and GPU memory.
    device : str
        The device to use for inference, 'cpu' or 'cuda'.
    verbose : bool, optional
        If True, prints information about the selected model. Default is True.
    Returns
    -------
    str or None
        The selected SAM model variant as a string ('fast', 'base', 'large', or 'huge'),
        or None if the input is invalid.
    Notes
    -----
    - When 'auto' is selected, the function chooses the model based on available GPU
      memory if device is 'cuda'.
    - Prints a message if an invalid input is provided.
    """
    model_mapping = {
        "a": "auto",
        "f": "fast",
        "fastsam": "fast",
        "b": "base",
        "l": "large",
        "h": "huge",
    }
    SAM_model = SAM_model.lower()
    SAM_model = model_mapping.get(SAM_model, SAM_model)

    if SAM_model == "auto":
        if device == "cpu":
            model = "fast"
        elif device == "cuda":
            model = "base"
            if torch.cuda.get_device_properties(0).total_memory / 1024**3 > 7:
                model = "huge"
            elif torch.cuda.get_device_properties(0).total_memory / 1024**3 > 5:
                model = "large"
        if verbose:
            print(f"The {model} SAM model was chosen.\n")
        return model
    elif SAM_model in {"fast", "base", "large", "huge"}:
        model = SAM_model
        return model
    else:
        print(
            "Invalid input. Valid inputs are 'a' for auto, 'h' for huge, 'l' for large, 'b' for base and 'f' for fast."
        )
        return None


@overload(np.all)
def np_all(x, axis=None):
    """
    Compute the logical AND along the specified axis for 2D numpy arrays.
    This function mimics the behavior of `numpy.ndarray.all` with support for the `axis`
    argument, specifically optimized for 2D arrays. It uses JIT-compiled helper
    functions for improved performance.
    Parameters
    ----------
    x : numpy.ndarray
        Input 2D array on which to perform the logical AND operation.
    axis : int or None, optional
        Axis along which to perform the logical AND operation.
        - If `axis=0`, compute the logical AND down the columns.
        - If `axis=1`, compute the logical AND across the rows.
        - If `None`, defaults to axis 1.
    Returns
    -------
    numpy.ndarray
        Array of boolean values resulting from the logical AND operation along the
        specified axis.
    Notes
    -----
    This function is intended for use with 2D arrays only. For higher-dimensional
    arrays, use `numpy.all` directly.
    Examples
    --------
    >>> import numpy as np
    >>> arr = np.array([[True, False], [True, True]])
    >>> np_all(arr, axis=0)
    array([ True, False])
    >>> np_all(arr, axis=1)
    array([False,  True])
    """

    # ndarray.all with axis arguments for 2D arrays.
    @register_jitable
    def _np_all_axis0(arr):
        out = np.logical_and(arr[0], arr[1])
        for v in iter(arr[2:]):
            for idx, v_2 in enumerate(v):
                out[idx] = np.logical_and(v_2, out[idx])
        return out

    @register_jitable
    def _np_all_axis1(arr):
        out = np.logical_and(arr[:, 0], arr[:, 1])
        for idx, v in enumerate(arr[:, 2:]):
            for v_2 in iter(v):
                out[idx] = np.logical_and(v_2, out[idx])
        return out

    def _np_all_impl(x, axis=None):
        if axis == 0:
            return _np_all_axis0(x)
        else:
            return _np_all_axis1(x)

    return _np_all_impl


@nb.njit(cache=True)
def nb_unique_caller(input_data):
    """
    Numba compatible solution to numpy.unique() function.
    Parameters
    ----------
    input_data : np.ndarray
        The input array from which to find unique rows. Must be a 2D NumPy array.
    Returns
    -------
    np.ndarray or None
        An array containing the unique rows of the input array, preserving the order.
        Returns None if the input array is empty.
    Notes
    -----
    This function is designed to be compatible with Numba's JIT compilation.
    It finds unique rows in a 2D array by sorting and comparing adjacent rows.
    """
    data = input_data.copy()
    if len(data) == 0:
        return None

    for i in range(data.shape[1] - 1, -1, -1):
        sorter = data[:, i].argsort(kind="mergesort")
        # mergesort to keep associations
        data = data[sorter]

    idx = [0]

    bool_idx = ~np.all((data[:-1] == data[1:]), axis=1)
    additional_uniques = np.nonzero(bool_idx)[0] + 1

    idx = np.append(idx, additional_uniques)

    return data[idx]

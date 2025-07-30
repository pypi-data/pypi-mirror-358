# Standard library imports
import math
import os
import platform
import subprocess
from collections.abc import MutableSequence
from copy import copy
from datetime import datetime
from pathlib import Path
from time import time
from typing import Any, Callable, Optional, Sequence

import hyperspy.api as hs

# Third-party imports
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy
import skimage
import tifffile
from hyperspy.drawing._widgets.scalebar import ScaleBar
from IPython import get_ipython
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.widgets import RadioButtons, RangeSlider
from skimage.measure import find_contours, label, regionprops_table

from .utils import (
    FastSAM_segmentation,
    SAM_segmentation,
    choose_device,
    choose_SAM_model,
    convert_to_units,
    format_time,
    get_filepath,
    get_filepaths,
    get_scaling,
    is_scaled,
    load_df_from_csv,
    load_image_RGB,
    masks_to_2D,
    nb_unique_caller,
    plot_masks,
    preprocess,
    remove_overlapping_masks,
    save_df_to_csv,
    seg_params_to_str,
    set_scaling,
    stitch_crops_together,
)


class NPSAMImage:
    """
    Represents a single image for segmentation and analysis using NP-SAM.

    The NPSAMImage class loads an image file (microscopy or standard image formats) and
    provides methods for segmentation, mask characterization, filtering, visualization,
    and export of results.

    Key features:
        - Loads an image upon initialization, with optional segmentation file loading.
            (see: __init__, load_image, load_segmentation)
        - Supports segmentation using SAM/FastSAM or importing external segmentation
          masks.
            (see: segment, import_segmentation_from_image, combine)
        - Characterizes segmented masks with geometric and intensity properties.
            (see: characterize)
        - Provides interactive and programmatic filtering of masks based on
          characteristics.
            (see: filter, filter_nogui)
        - Offers visualization tools for masks and individual particles.
            (see: plot_masks, plot_particle)
        - Exports segmentation results and mask characteristics in various formats (CSV,
          PNG, TIFF, NumPy).
            (see: export_filtered_characteristics, export_filtered_masks_png,
            export_filtered_masks_tif, export_filtered_masks_binary,
            export_filtered_masks_numpy, export_all)
        - Generates overview PDF reports with histograms and summary statistics.
            (see: overview)

    This class is designed for use as a standalone object or as a building block for
    batch processing with the NPSAM class.
    """

    def __init__(
        self,
        filepath: Optional[str | Path] = None,
        select_image: Optional[str] = None,
        segmentation_filepath: Optional[str | Path] = None,
    ) -> None:
        """
        Initializes the object by loading an image file and, if available, a
        corresponding segmentation file.

        Parameters:
            filepath (Optional[str | Path]): Path to the image file to load. If None,
            prompts the user to select a file.
            select_image (Optional[str]): Optional parameter to specify which image to
            select from the file, if there are several to choose from, e.g. "HAADF" or
            "BF".
            segmentation_filepath (Optional[str | Path]): Path to a segmentation file to
            load. If None, attempts to load segmentation from the image file path.

        Behavior:
            - Loads the specified image file.
            - Initializes segmentation (`self.seg`) and characteristics (`self.cha`)
              attributes to None.
            - Attempts to load a segmentation file if provided; otherwise, silently
              continues if loading fails.
        """
        if filepath is None:
            filepath = get_filepath()
        self.filepath = filepath
        self.load_image(filepath, select_image=select_image)
        self.seg = None
        self.cha = None
        try:
            self.load_segmentation(filepath=segmentation_filepath)
        except Exception:
            pass

    def __repr__(self) -> str:
        """Returns the image name, masks segmented and how many passed the filtering."""
        # return f"NPSAMImage('{self.filepath}')"
        return self.__str__()

    def __str__(self) -> str:
        """Returns the image name, masks segmented and how many passed the filtering."""
        string = f"<NPSAM: {self.img.metadata.General.title}"
        if self.seg:
            string += f", {len(self.seg)} masks"
        if self.cha is not None:
            if not self.seg.metadata.has_item("Filtering.Conditions"):
                string += ", unfiltered"
            else:
                string += f", {self.cha['passed_filter'].sum()} passed filter"
        string += ">"
        return string

    def load_image(
        self,
        filepath: Optional[str | Path] = None,
        select_image: Optional[str | int] = None,
    ) -> None:
        """
        Loads an image file (e.g., .png, .jpg, .tif) or an electron microscopy file
        (e.g., .emd, .bcf, .dm4) into a HyperSpy signal and assigns it to self.img.

        Parameters:
            filepath (Optional[str | Path]): Path to the image file. If None, prompts
            the user to select a file.
            select_image (Optional[str | int]): If the file contains multiple images,
            specifies which image to select (by index or title, e.g. "HAADF" or "BF").
            If None and multiple images are present, prompts the user.

        Behavior:
            - Loads the image as a HyperSpy signal.
            - Handles both standard image formats and microscopy file formats.
            - If multiple images are present in the file, allows selection by index or
              title.
            - Sets scaling information if not already present.
            - Stores the loaded image in self.img and its filename in self.name.
        """
        filepath = Path(filepath)

        # Hyperspy can't load all three channels in regular images, so we load them
        # without
        if filepath.suffix in [".png", ".jpg", ".jpeg", ".gif"]:
            # Load image file as numpy array
            image_RGB = load_image_RGB(filepath)
            # Create hyperspy signal from image numpy array
            image = hs.signals.Signal1D(image_RGB)
        else:
            # Lazy loading doesn't seem to work with tif files
            if filepath.suffix in [".tif", ".tiff"]:
                lazy = False
            else:
                lazy = True

            if filepath.suffix in [".emd", ".bcf"]:
                # Apparently only works for .emd and .bcf. Throws error for .dm4
                signal = hs.load(filepath, lazy=lazy, select_type="images")
            else:
                signal = hs.load(filepath, lazy=lazy)

            # If there is more than one image in the file, we have to choose
            if isinstance(signal, list):
                # Check for empty list
                if len(signal) == 0:
                    print(f"No images found in {filepath}")
                    return

                # We take selection input until an image is found
                image_found = False
                while not image_found:
                    if select_image is None:
                        print(f"Several signals are present in {filepath.name}:\n")
                        # Print name of the images in the file
                        for subsignal in signal:
                            print(str(subsignal))
                        select_image = input(
                            (
                                "\nPlease choose the image of interest by providing an "
                                "index or the image title:"
                            )
                        )

                    try:
                        # If selection is an index
                        select_image = int(select_image)
                        image = signal[select_image]
                        image_found = True
                    except Exception:
                        # If selection is not an index we check the title of the signal
                        for subsignal in signal:
                            if select_image == subsignal.metadata.General.title:
                                image = subsignal
                                image_found = True
                        if not image_found:
                            print("Image of interest not found.")
                            select_image = None
            else:
                image = signal
            if lazy:
                image.compute(show_progressbar=False)
            image = image.transpose()

        image.metadata.General.filepath = filepath.as_posix()
        image.metadata.General.title = filepath.name
        if not is_scaled(image):
            set_scaling(image, "1 px")
        self.img = image
        self.name = filepath.name

    def set_scaling(
        self,
        scaling: str,
        verbose: bool = True,
    ) -> None:
        """
        Sets the scaling of the image and its segmentation masks.

        Parameters:
            scaling (str): Scaling value as a Pint-compatible quantity (e.g., '1 nm',
            '3.5 µm', '0.3 um', or '4 Å').
            verbose (bool, optional): If True, prints a message upon existing area
            filtering conditions, since these are not updated. Default is True.

        Behavior:
            - Updates the scaling metadata for the image and segmentation masks.
            - Updates the scaling for the characteristics DataFrame if segmentation
              exists.
            - Warns if area filtering conditions are present since they are not updated.
        """
        set_scaling(self.img, scaling)
        try:
            set_scaling(self.seg, scaling)
            self._set_scaling_cha()
            if self.seg.metadata.has_item("Filtering.Conditions") and verbose:
                print("Scaling set, but area filtering conditions not updated.")
                print("Consider rerunning the filter function.")
        except Exception:
            pass

    def get_scaling(self) -> str:
        """
        Retrieves the scaling information of the image and segmentation masks.

        Returns:
            str: The scaling factor and unit as a string (e.g., '1 px', '3.5 µm').
        """
        return get_scaling(self.img)

    def _set_scaling_cha(self) -> None:
        """
        Updates the characteristics DataFrame, `cha`, with scaling information and
        converts pixel-based measurements to physical units.
        This method retrieves the scaling factor (length per pixel) and unit from the
        segmentation data, stores them in the `cha` DataFrame, and then updates various
        geometric properties from pixel units to physical units using the scaling
        factor.
        The following keys in `cha` are updated:
            - "scaling [unit/px]": The scaling factor (length per pixel).
            - "unit": The physical unit (e.g., 'µm', 'mm').
            - "equivalent_diameter_area", "feret_diameter_max", "perimeter",
              "perimeter_crofton": Converted from pixel units to physical units
              (multiplied by scaling factor).
            - "area", "area_convex": Converted from pixel units to physical units
              (multiplied by scaling factor squared).
        Assumes that the corresponding pixel-based properties (with "_px" suffix) are
        already present in `cha`.
        """
        length_per_pixel, unit = get_scaling(self.seg).split()
        length_per_pixel = float(length_per_pixel)
        self.cha["scaling [unit/px]"] = length_per_pixel
        self.cha["unit"] = unit

        for prop in [
            "equivalent_diameter_area",
            "feret_diameter_max",
            "perimeter",
            "perimeter_crofton",
        ]:
            self.cha[prop] = self.cha[prop + "_px"] * length_per_pixel
        for prop in ["area", "area_convex"]:
            self.cha[prop] = self.cha[prop + "_px"] * length_per_pixel**2

    def convert_to_units(self, units: str, verbose: bool = True) -> None:
        """
        Converts the units of the image and segmentation data to the specified units.

        Parameters:
            units (str): The target unit to convert to. Must be compatible with
            Pint, e.g., 'nm', 'µm', 'um', or 'Å'.
            verbose (bool, optional): If True, prints a message upon existing area
            filtering conditions, since these are not updated. Default is True.

        Behavior:
            - Updates the scaling metadata for the image and segmentation masks.
            - Updates the scaling for the characteristics DataFrame if segmentation
              exists.
            - Warns if area filtering conditions are present since they are not updated.
        """
        convert_to_units(self.img, units)
        try:
            convert_to_units(self.seg, units)
            self._set_scaling_cha()
            if self.seg.metadata.has_item("Filtering.Conditions") and verbose:
                print("Scaling set, but area filtering conditions not updated.")
                print("Consider rerunning the filter function.")
        except Exception:
            pass

    def segment(
        self,
        device: str = "auto",
        SAM_model: str = "auto",
        PPS: int = 64,
        shape_filter: bool = True,
        edge_filter: bool = True,
        crop_and_enlarge: bool = False,
        invert: bool = False,
        double: bool = False,
        min_mask_region_area: int = 100,
        stepsize: int = 1,
        verbose: bool = True,
        **kwargs: Any,
    ) -> None:
        """
        Segments the loaded image using either SAM or FastSAM, generating binary masks
        for detected regions and storing them as a HyperSpy signal in the `.seg`
        attribute. Segmentation parameters are also saved in the signal's metadata.
        Parameters
        ----------
        device : str, optional
            Device to use for computation: 'auto', 'cpu', or 'cuda'. Default is 'auto'.
        SAM_model : str, optional
            Model type for segmentation: 'auto', 'huge', 'large', 'base', or 'fast'.
            Default is 'auto'.
        PPS : int, optional
            Points per side for sampling in SAM. A higher value can help finding smaller
            particles but increases computation time. Default is 64.
        shape_filter : bool, optional
            Whether to filter masks based on shape properties (area and solidity). This
            will remove very concave masks. Default is True.
        edge_filter : bool, optional
            Whether to filter out masks that touch the image edges. Default is True.
        crop_and_enlarge : bool, optional
            Whether to crop and enlarge sub-images before segmentation. This helps
            finding smaller particles, since four zoomed-in quadrants of the image are
            segmented. This increases computation time at least by a factor of 4.
            Default is False.
        invert : bool, optional
            Whether to invert the image before segmentation. This works better for some
            images. Default is False.
        double : bool, optional
            Whether to perform segmentation twice (inverted and non-inverted) and merge
            results. Default is False.
        min_mask_region_area : int, optional
            Disconnected regions and holes in masks with area smaller than
            min_mask_region_area will be removed. Default is 100.
        stepsize : int, optional
            Step size for overlap detection during characterization after segmentation.
            A step size of 1 checks every pixel in the image, a step size of 2 checks
            every other pixel and so on. Increasing the step size decreases the
            computation time, but overlapping regions between masks might be missed.
            Default is 1.
        verbose : bool, optional
            If True, prints progress and summary information. Default is True.
        **kwargs : Any
            Additional keyword arguments passed to the segmentation functions.
        Notes
        -----
        - The function preprocesses the image, applies segmentation, filters masks, and
          stores the results.
        - The resulting masks are saved as a HyperSpy Signal2D object in `self.seg`,
          with relevant metadata.
        - If no masks are found, a message is printed and no masks are saved.
        - After segmentation, the `characterize` method is called to further analyze the
          masks.
        Returns
        -------
        None
            The results are stored in the object's attributes `self.seg` and `self.cha`.
        """
        if device.lower() in ["auto", "a"]:
            device = choose_device()

        SAM_model = choose_SAM_model(SAM_model, device, verbose)

        image_shape = self.img.data.shape

        sub_images = preprocess(
            self.img, crop_and_enlarge=crop_and_enlarge, invert=invert, double=double
        )

        list_of_mask_arrays = []
        start = time()
        for sub_image in sub_images:
            if SAM_model == "fast":
                masks = FastSAM_segmentation(sub_image, device, min_mask_region_area)
            else:
                masks = SAM_segmentation(
                    sub_image, SAM_model, device, PPS, min_mask_region_area, **kwargs
                )

            masks = masks[masks.sum(axis=-1).sum(axis=-1) > 0]  # Remove empty masks

            for n, mask in enumerate(masks):
                labels = label(mask)
                if labels.max() > 1:
                    masks[n] = (labels == 1).astype("uint8")
                    for m in np.arange(1, labels.max()) + 1:
                        masks = np.concatenate(
                            (
                                masks,
                                np.expand_dims((labels == m).astype("uint8"), axis=0),
                            )
                        )

            masks = remove_overlapping_masks(masks)

            if edge_filter:
                edge_sums = masks[:, :, [0, 1, 2, -3, -2, -1]].sum(axis=1).sum(
                    axis=1
                ) + masks[:, [0, 1, 2, -3, -2, -1], :].sum(axis=2).sum(axis=1)
                # Only keep those where the edges are empty
                masks = masks[edge_sums == 0]

            if shape_filter:
                list_of_filtered_masks = []
                for mask in masks:
                    props = skimage.measure.regionprops_table(
                        label(mask), properties=["label", "area", "solidity"]
                    )
                    if len(props.get("label")) == 1 and (
                        props.get("area") < 400 or props.get("solidity") > 0.95
                    ):
                        list_of_filtered_masks.append(mask)
                masks = np.stack(list_of_filtered_masks)

            list_of_mask_arrays.append(masks)

        if crop_and_enlarge:
            stitched_masks = []
            for i in range(0, len(list_of_mask_arrays), 4):
                stitched_masks.append(
                    stitch_crops_together(list_of_mask_arrays[i : i + 4], image_shape)
                )
            list_of_mask_arrays = stitched_masks
        if double:
            masks = remove_overlapping_masks(np.concatenate(list_of_mask_arrays))
        else:
            masks = list_of_mask_arrays[0]

        if len(masks) == 0:
            elapsed_time = time() - start
            if verbose:
                print(f"0 masks found for {self.name}, so no masks were saved.")
                print(f"It took {format_time(elapsed_time)}")
        else:
            segmentation_metadata = {
                "SAM_model": SAM_model,
                "PPS": PPS,
                "shape_filter": shape_filter,
                "edge_filter": edge_filter,
                "crop_and_enlarge": crop_and_enlarge,
                "invert": invert,
                "double": double,
                "min_mask_region_area": min_mask_region_area,
            }
            elapsed_time = time() - start
            if verbose:
                print(f"{len(masks)} masks found. It took {format_time(elapsed_time)}")

        self.seg = hs.signals.Signal2D(
            masks,
            metadata={
                "General": {
                    "title": self.img.metadata.General.title,
                    "image_filepath": self.filepath,
                },
                "Segmentation": segmentation_metadata,
                "Filtering": {},
            },
        )
        set_scaling(self.seg, get_scaling(self.img))

        self.characterize(stepsize=stepsize, verbose=verbose)

    def import_segmentation_from_image(
        self,
        filepath: Optional[str | Path] = None,
        stepsize: int = 1,
        verbose: bool = True,
    ) -> None:
        """
        Imports segmentation from an image file (black and white) instead of segmenting
        with SAM.

        Loads a segmentation mask from an image file (e.g., PNG, TIFF), converts it to a
        HyperSpy Signal2D object, and stores it in the `.seg` attribute. The mask is
        expected to be a binary or labeled image where each connected region is treated
        as a separate mask. The method also sets the scaling to match the original image
        and runs characterization on the imported masks.

        Parameters:
            filepath (Optional[str | Path]): Path to the segmentation image file. If
            None, prompts the user to select a file.
            stepsize (int): Step size for overlap detection during characterization.
            Increasing the step size decreases the computation time, but overlapping
            regions between masks might be missed. Default is 1.
            verbose (bool): If True, prints progress information. Default is True.

        Raises:
            ValueError: If the segmentation image dimensions do not match the original
            image.

        Behavior:
            - Loads the segmentation image and binarizes it if necessary.
            - Extracts individual masks from labeled regions.
            - Stores the masks as a HyperSpy Signal2D in `.seg`.
            - Sets scaling to match the original image.
            - Runs characterization on the imported masks.
        """
        if filepath is None:
            filepath = get_filepath()
        segmentation = load_image_RGB(filepath)
        if segmentation.ndim == 3:
            segmentation = segmentation[:, :, 0] > 0
        elif segmentation.ndim == 2:
            segmentation = segmentation > 0
        if segmentation.shape != self.img.data.shape[:2]:
            raise ValueError(
                f"The segmentation image dimensions {segmentation.shape} must match the original image dimensions {self.img.data.shape[:2]}."
            )
        labels = label(segmentation)
        masks = np.stack([labels == n for n in range(1, labels.max() + 1)]).astype(
            "uint8"
        )
        self.seg = hs.signals.Signal2D(
            masks,
            metadata={
                "General": {
                    "title": self.img.metadata.General.title,
                    "image_filepath": self.img.metadata.General.filepath,
                },
                "Filtering": {},
                "Segmentation": f"Imported from file '{filepath}'",
            },
        )
        set_scaling(self.seg, get_scaling(self.img))
        self.characterize(stepsize=stepsize, verbose=verbose)

    def combine(
        self,
        other_segmentation: "str | Path | NPSAMImage",
        iou_threshold: float = 0.2,
        filtered: bool = True,
        edge_filter: bool = True,
    ) -> None:
        """
        Combines the current segmentation with another segmentation, removing
        overlapping masks based on a specified IoU threshold.
        Parameters
        ----------
        other_segmentation : str, Path or NPSAMImage
            The other segmentation to combine with. Can be a file path (str or Path) to
            an image or another NPSAMImage instance.
        iou_threshold : float, optional
            The Intersection-over-Union (IoU) threshold for considering two masks as
            overlapping based on the mask bounding boxes. Default is 0.2.
        filtered : bool, optional
            If True, only masks that have passed filtering are considered for
            combination. If False, all masks are used. Default is True.
        edge_filter : bool, optional
            If True, only masks not touching the edges in the other segmentation are
            considered for combination. Default is True.
        Returns
        -------
        None
        Notes
        -----
        - Overlapping masks are removed based on the IoU threshold.
        - Updates the segmentation data and metadata of the current object.
        """
        if isinstance(other_segmentation, str):
            selfcopy = copy(self)
            selfcopy.import_segmentation_from_image(other_segmentation, verbose=False)
            other_segmentation = selfcopy

        if filtered:
            own_masks = self.seg.data[self.cha["passed_filter"]]
            other_masks = other_segmentation.seg.data[
                other_segmentation.cha["passed_filter"]
            ]
        else:
            own_masks = self.seg.data
            other_masks = other_segmentation.seg.data

        if edge_filter:
            edge_sums = other_masks[:, :, [0, 1, -2, -1]].sum(axis=1).sum(axis=1)
            edge_sums += other_masks[:, [0, 1, -2, -1], :].sum(axis=2).sum(axis=1)
            # Only keep those where the edges are empty
            other_masks = other_masks[edge_sums == 0]

        own_segmentation = seg_params_to_str(self.seg.metadata.Segmentation)
        other_segmentation = seg_params_to_str(
            other_segmentation.seg.metadata.Segmentation
        )
        segmentations = [own_segmentation] * len(own_masks) + [
            other_segmentation
        ] * len(other_masks)

        all_masks = np.concatenate([own_masks, other_masks])

        processed_masks, indices = remove_overlapping_masks(
            all_masks, iou_threshold=iou_threshold, return_indices=True
        )
        kept_segmentations = [segmentations[i] for i in indices]

        self.seg.data = processed_masks
        self.characterize()
        self.cha["segmentation"] = kept_segmentations
        self.seg.metadata.Segmentation = "Combined segmentation"

    def characterize(
        self,
        stepsize: int = 1,
        verbose: bool = True,
    ) -> None:
        """
        Analyze and characterize each mask in the segmentation data.
        This method computes a comprehensive set of region properties for each mask
        using the corresponding image data, and stores the results in a Pandas DataFrame
        assigned to the `.cha` attribute. The computed properties include geometric,
        intensity, and shape descriptors such as area, centroid, eccentricity,
        perimeter, and more.
        Additionally, the method:
            - Converts pixel-based measurements to physical units using image scaling.
            - Identifies and quantifies overlapping regions between masks.
            - Stores the number of overlaps and the indices of overlapping masks.
            - Extracts and saves mask contours in the segmentation metadata.
        Parameters
        ----------
        stepsize : int, optional
            Step size for overlap analysis. Higher values may speed up computation at
            the cost of reduced accuracy. Default is 1 (analyze every pixel).
        verbose : bool, optional
            If True, prints progress information during computation. Default is True.
        Returns
        -------
        None
        Side Effects
        ------------
        - Sets the `self.cha` attribute to a DataFrame containing mask characteristics.
        - Updates `self.seg.metadata.Filtering.Contours` with mask contours.
        Notes
        -----
        - Requires the segmentation data (`self.seg.data`) and image data
          (`self.img.data`) to be properly initialized.
        - The DataFrame includes both pixel and scaled (physical unit) measurements.
        - Overlap analysis may be computationally intensive for large datasets.
        """
        masks = self.seg.data
        dfs_properties = []
        for m, mask in enumerate(masks):
            if verbose:
                print(
                    f"Finding mask characteristics: {m + 1}/{len(masks)}",
                    sep=",",
                    end="\r" if m + 1 < len(masks) else "\n",
                    flush=True,
                )
            if self.img.data.ndim == 3:
                img = self.img.data.mean(axis=2)
            else:
                img = self.img.data
            dfs_properties.append(
                pd.DataFrame(
                    regionprops_table(
                        mask,
                        img,
                        properties=(
                            "area",
                            "area_convex",
                            "axis_major_length",
                            "axis_minor_length",
                            "bbox",
                            "centroid",
                            "centroid_local",
                            "centroid_weighted",
                            "eccentricity",
                            "equivalent_diameter_area",
                            "euler_number",
                            "extent",
                            "feret_diameter_max",
                            "inertia_tensor",
                            "inertia_tensor_eigvals",
                            "intensity_max",
                            "intensity_mean",
                            "intensity_min",
                            "moments_hu",
                            "moments_weighted_hu",
                            "orientation",
                            "perimeter",
                            "perimeter_crofton",
                            "solidity",
                        ),
                    )
                )
            )
        df = pd.concat(dfs_properties)
        length_per_pixel = float(get_scaling(self.seg).split()[0])
        unit = get_scaling(self.seg).split()[1]
        df["scaling [unit/px]"] = length_per_pixel
        df["unit"] = unit
        df["mask"] = np.arange(df.shape[0])
        df["mask_index"] = np.arange(df.shape[0])
        column_to_move = df.pop("mask_index")
        df.insert(0, "mask_index", column_to_move)
        df = df.set_index("mask")

        for prop in [
            "equivalent_diameter_area",
            "feret_diameter_max",
            "perimeter",
            "perimeter_crofton",
        ]:
            df[prop + "_px"] = df[prop]
            df[prop] *= length_per_pixel
        for prop in ["area", "area_convex"]:
            df[prop + "_px"] = df[prop].astype(int)
            df[prop] *= length_per_pixel**2

        flattened_multiple_masks = np.moveaxis(masks[:, masks.sum(axis=0) > 1], 0, -1)
        unique_multiple_masks = nb_unique_caller(flattened_multiple_masks[::stepsize])
        df["overlap"] = 0
        df["overlapping_masks"] = [set() for _ in range(len(df))]

        overlap_counts = np.zeros(len(df), dtype=int)

        if unique_multiple_masks is not None:
            for n, unique in enumerate(unique_multiple_masks):
                if verbose:
                    print(
                        (
                            "Finding areas with overlap: "
                            f"{n + 1}/{len(unique_multiple_masks)}"
                        ),
                        sep=",",
                        end="\r" if n + 1 < len(unique_multiple_masks) else "\n",
                        flush=True,
                    )

                mask_indices = np.where(unique)[0]

                for idx in mask_indices:
                    df.at[idx, "overlapping_masks"].update(mask_indices)
                    df.at[idx, "overlapping_masks"].remove(idx)

                summed_masks = masks[mask_indices].sum(axis=0)
                overlaps = (summed_masks > 1).sum(axis=(0, 1))

                overlap_counts[mask_indices] += overlaps

        df["overlap"] = overlap_counts
        df["number_of_overlapping_masks"] = df["overlapping_masks"].apply(len)

        df["number_of_overlapping_masks"] = [
            len(masks) for masks in df["overlapping_masks"].to_list()
        ]
        df["passed_filter"] = True
        df.attrs = {
            "title": self.img.metadata.General.title,
            "image_filepath": self.filepath,
            "filepath": "Not saved yet",
        }
        self.cha = df
        for n, mask in enumerate(self.seg.data):
            self.seg.metadata.set_item(
                f"Filtering.Contours.{n}", find_contours(mask, 0.5)[0]
            )

    def save_segmentation(
        self,
        save_as: str | Path = None,
        overwrite: Optional[bool] = None,
    ) -> None:
        """
        Saves the current segmentation and characterization results to disk.

        This method saves the segmentation data as a `.hspy` file and the
        characterization data as a `.csv` file for later retrieval. Filtering conditions
        are also stored in the `.hspy` file. If no output path is specified, the files
        are saved in a "NP-SAM_results" subdirectory next to the original file.

        Args:
            save_as (str | Path, optional): The base path (without extension) to save
                the results. If None, saves to a default location based on the original
                file path.
            overwrite (Optional[bool], optional): Whether to overwrite existing files.
                If None, if the file exists it will ask the user.

        Returns:
            None
        """
        if save_as is None:
            filepath = Path(self.filepath).parent / (
                "NP-SAM_results/" + Path(self.filepath).name
            )
        else:
            filepath = Path(save_as)
        # filepath = Path(self.filepath if save_as is None else save_as)
        self.seg.save(filepath.with_suffix(".hspy"), overwrite=overwrite)
        save_df_to_csv(self.cha, filepath.with_suffix(".csv"))

    def load_segmentation(
        self,
        filepath: Optional[str | Path] = None,
    ) -> None:
        """
        Loads segmentation, characterization and filtering from a .hspy and .csv file.

        Parameters:
            filepath (Optional[str | Path]): Path to the segmentation file to load. If
            None, loads from the default NP-SAM_results subfolder next to the original
            image file.

        Behavior:
            - Loads the segmentation data from a .hspy file.
            - Loads the characteristics DataFrame from a .csv file.
            - Updates the object's .seg and .cha attributes accordingly.
        """
        if filepath is None:
            filepath = Path(self.filepath).parent / (
                "NP-SAM_results/" + Path(self.filepath).name
            )
        else:
            filepath = Path(filepath)
        # filepath = Path(self.filepath if filepath is None else filepath)
        self.seg = hs.load(filepath.with_suffix(".hspy"))
        self.cha = load_df_from_csv(filepath.with_suffix(".csv"))

    def plot_masks(
        self,
        cmap: str = "default",
        alpha: float = 0.3,
        figsize: Sequence[float] = [8, 4],
        filtered: bool = False,
        legacy: bool = False,
    ) -> None:
        """
        Plots the original image and the masks found through segmentation.

        Parameters:
            cmap (str): Colormap to use for the masks. Default is "default" which takes
            random colors from viridis.
            alpha (float): Transparency of the masks overlay. Default is 0.3.
            figsize (Sequence[float]): Figure size as [width, height]. Default is
            [8, 4].
            filtered (bool): If True, only plots the masks that passed the filtering
            conditions. Default is False.
            legacy (bool): If True, uses legacy plotting behavior. Default is False.

        Behavior:
            - Displays the original image and the segmentation masks side by side.
            - If filtered is True, only masks passing the filter are shown.
            - Adds a scale bar to the image.
            - Shows the plot using matplotlib.
        """
        fig, axs = plt.subplots(1, 2, figsize=figsize, sharex=True, sharey=True)

        for ax in axs:
            ax.imshow(self.img.data, cmap="gray")
            ax.axis("off")

        scaling, units = self.get_scaling().split()
        scaling = float(scaling)
        _ = ScaleBar(axs[0], units=units, pixel_size=scaling)
        _ = plot_masks(self, ax=axs[1], alpha=alpha, cmap=cmap, filtered=filtered)

        plt.suptitle(self.img.metadata.General.title)
        plt.tight_layout()
        plt.show()

    def plot_particle(
        self,
        mask_index: int,
        cmap: str = "grey",
    ) -> None:
        """
        Given a particle/mask index, it plots the smallest image that contains the given
        mask. It plots both filtered and non-filtered masks.

        Parameters
        ----------
        mask_index : int
            The index of the mask/particle to plot. Must be within the valid range of
            mask indices.
        cmap : str, optional
            The colormap to use for displaying the image. Default is "grey".

        Raises
        ------
        ValueError
            If the provided mask_index is out of the valid range.
        """
        try:
            bbox = self.cha.loc[mask_index, [f"bbox-{n}" for n in range(4)]].tolist()
        except Exception:
            raise ValueError(
                f"Only indices between 0 and {self.cha['mask_index'].max()} are accepted."
            )
        fig, ax = plt.subplots()
        ax.imshow(self.img.data[bbox[0] : bbox[2], bbox[1] : bbox[3]], cmap=cmap)
        plt.show()

    def filter(
        self,
        cmap: str = "default",
        alpha: float = 0.3,
    ) -> None:
        """
        Runs an interactive filtering window to filter masks based on selected
        characteristcs.

        Parameters:
            cmap (str, optional): The colormap to use for mask visualization. Defaults
            to "default" which is viridis.
            alpha (float, optional): The transparency level for the mask overlay,
            between 0 (fully transparent) and 1 (fully opaque). Defaults to 0.3.

        Returns:
            None
        """
        filter(self, cmap=cmap, alpha=alpha)

    def filter_nogui(
        self,
        conditions: dict[str, Sequence[float | int] | int],
    ) -> None:
        """
        Filters the masks based on a set of conditions with respect to the mask
        characteristics, without opening an interactive window.

        Parameters:
            conditions (dict): Dictionary specifying filter conditions. Possible keys:
            - area: tuple (min, max)
            - intensity_mean: tuple (min, max)
            - eccentricity: tuple (min, max)
            - solidity: tuple (min, max)
            - overlap: tuple (min, max)
            - number_of_overlapping_masks: int (maximum allowed)
            - removed_index: list of mask indices to exclude

        Behavior:
            - Updates the 'passed_filter' column in the characteristics DataFrame based
              on the conditions.
            - Stores the filter conditions in the segmentation metadata.
        """
        filter_nogui(self, conditions)

    def list_overview_characteristics(self) -> None:
        """
        Lists the available characteristics for generating an overview PDF.
        This method prints the names of all characteristics that can be used in the
        `overview` method.
        """
        print("Available characteristics for overview:")
        print(
            "area, area_convex, axis_major_length, axis_minor_length, eccentricity, \n"
            "equivalent_diameter_area, extent, feret_diameter_max, intensity_max, \n"
            "intensity_mean, intensity_min, orientation, perimeter, perimeter_crofton,\n"
            "solidity, overlap"
        )

    def overview(
        self,
        save_as: Optional[str | Path] = None,
        characteristics: Sequence[str] = ["area"],
        bin_list: Optional[Sequence[int | str]] = None,
        timestamp: bool = False,
    ) -> None:
        """
        Generates and saves an overview PDF file summarizing the segmentation results
        and histograms of selected mask characteristics for the current image.

        Parameters:
            save_as (Optional[str | Path]): Path to save the resulting PDF file. If
            None, saves to a default location.
            characteristics (Sequence[str]): List of mask characteristics to include in
            the histograms.
            Use ["all"] to include all available characteristics. See available
            characteristics by running the `list_overview_characteristics()` method.
            Default is ["area"].
            bin_list (Optional[Sequence[int | str]]): List specifying the number of bins
            or binning strategy for each characteristic histogram. If None, uses "auto"
            for all.
            timestamp (bool): If True, appends a timestamp to the output filename.
            Default is False.

        Behavior:
            - Includes only those masks that passed the filtering conditions.
            - Plots histograms for the selected characteristics, including summary
              statistics.
            - Adds an overview figure showing the segmentation and filtering parameters.
            - Saves all figures to a single PDF file.
            - Optionally appends a timestamp to the filename.

        Returns:
            None
        """
        if characteristics == ["all"]:
            characteristics = [
                "area",
                "area_convex",
                "axis_major_length",
                "axis_minor_length",
                "eccentricity",
                "equivalent_diameter_area",
                "extent",
                "feret_diameter_max",
                "intensity_max",
                "intensity_mean",
                "intensity_min",
                "orientation",
                "perimeter",
                "perimeter_crofton",
                "solidity",
                "overlap",
            ]

        for n, prop in enumerate(characteristics):
            if prop == "intensity":
                characteristics[n] = "intensity_mean"
            elif prop == "diameter":
                characteristics[n] = "equivalent_diameter_area"
            elif prop == "max diameter":
                characteristics[n] = "feret_diameter_max"
            elif prop == "crofton perimeter":
                characteristics[n] = "perimeter_crofton"
            elif prop == "convex area":
                characteristics[n] = "area_convex"

        df = copy(self.cha[self.cha["passed_filter"]])

        if bin_list is None:
            bin_list = ["auto"] * len(characteristics)

        unit = df["unit"].to_list()[0]
        unit2 = unit + "$^2$" if unit != "px" else unit
        name_dict = {
            "area": f"area ({unit2})",
            "area_convex": f"convex area ({unit2})",
            "eccentricity": "eccentricity",
            "solidity": "solidity",
            "intensity_mean": "mean intensity",
            "equivalent_diameter_area": f"area equivalent diameter ({unit})",
            "feret_diameter_max": f"Max diameter (Feret) ({unit})",
            "orientation": "orientation",
            "perimeter": f"perimeter ({unit})",
            "perimeter_crofton": f"crofton perimeter ({unit})",
            "axis_major_length": f"Major axis length ({unit})",
            "axis_minor_length": f"Minor axis length ({unit})",
            "extent": "Ratio of pixels in the mask the pixels in the bounding box",
            "intensity_max": "Max intensity of the mask",
            "intensity_min": "minimum intensity of the mask",
            "overlap": f"amount of overlap ({unit2})",
        }
        figs = []
        for n, prop in enumerate(characteristics):
            fig, ax = plt.subplots(figsize=(11.7, 8.3))
            ax.set_xlabel(name_dict.get(prop).capitalize(), fontsize=16)
            ax.set_title(
                f"Histogram of {name_dict.get(prop)} for all images", fontsize=18
            )
            df[prop].hist(bins=bin_list[n], ax=ax, edgecolor="k", color="#0081C6")
            ax.grid(False)
            ax.set_ylabel("Count", fontsize=16)
            ax.tick_params(axis="both", which="major", labelsize=14)
            data = df[prop]
            mean = np.mean(data)
            median = np.median(data)
            std_dev = np.std(data)
            variance = np.var(data)
            skewness = scipy.stats.skew(data)
            kurtosis = scipy.stats.kurtosis(data)
            data_range = np.ptp(data)
            q1 = np.percentile(data, 25)
            q3 = np.percentile(data, 75)
            iqr = scipy.stats.iqr(data)
            minimum = np.min(data)
            maximum = np.max(data)
            count = len(data)
            total_sum = np.sum(data)
            coeff_variation = std_dev / mean

            def format_value(val):
                if val == 0:
                    return 0
                elif val < 10:
                    return f"{val:.2f}"
                elif 10 <= val < 100:
                    return f"{val:.1f}"
                elif 100 <= val:
                    return f"{int(val)}"

            x_r = 1 - len(f"Upper quantile: {format_value(q3)}") * 0.0108
            x_m = (
                x_r - 0.025 - len(f"Sum: {format_value(total_sum)}") * 0.0108
                if total_sum > 100000000
                else x_r - 0.155
            )
            x_l = (
                x_m - 0.055 - len(f"Sum: {format_value(variance)}") * 0.0108
                if variance > 1000000000000
                else x_m - 0.22
            )

            stats_text_left = (
                f"Mean: {format_value(mean)}\nStd Dev: {format_value(std_dev)}\n"
                f"Median: {format_value(median)}\nVariance: {format_value(variance)}\n"
                f"Coeff of Variation: {format_value(coeff_variation)}\n"
                f"Total number of masks: {len(df['area'].to_list())}"
            )

            stats_text_middle = (
                f"Skewness: {format_value(skewness)}\nKurtosis: {format_value(kurtosis)}\n"
                f"Count: {count}\nSum: {format_value(total_sum)}\nIQR: {format_value(iqr)}"
            )

            stats_text_right = (
                f"Lower quantile: {format_value(q1)}\nUpper quantile: {format_value(q3)}\n"
                f"Min: {format_value(minimum)}\nMax: {format_value(maximum)}\n"
                f"Range: {format_value(data_range)}"
            )
            n = "i" * int((194 * (1 - x_l + 0.011)))

            text = f"{n}\n{n}\n{n}\n{n}\n{n}\n{n}"
            text_properties = {
                "fontsize": 12,
                "color": "none",
                "verticalalignment": "top",
                "bbox": dict(
                    boxstyle="round,pad=0.3",
                    edgecolor="black",
                    facecolor="white",
                    alpha=0.5,
                ),
            }

            plt.text(x_l, 0.98, text, transform=plt.gca().transAxes, **text_properties)
            for x, txt in zip(
                [x_l, x_m, x_r], [stats_text_left, stats_text_middle, stats_text_right]
            ):
                plt.text(
                    x,
                    0.98,
                    txt,
                    ha="left",
                    va="top",
                    transform=plt.gca().transAxes,
                    fontsize=12,
                )

            figs.append(fig)

        figs.append(self._make_overview_figure())

        if timestamp:
            d = datetime.now()
            stamp = f"_{d.year}{d.month}{d.day}_{d.hour}{d.minute}{d.second}"
        else:
            stamp = ""

        filepath = self._save_as_to_filepath(save_as, end=f"_overview{stamp}.pdf")

        p = PdfPages(filepath)

        for fig in figs:
            fig.savefig(p, format="pdf")

        p.close()
        plt.show()

    def _make_overview_figure(
        self,
        cmap: str = "default",
        alpha: float = 0.3,
    ) -> plt.Figure:
        """
        Helper function to generate an overview figure summarizing segmentation results
        and filtering parameters.
        This method creates a multi-panel matplotlib figure displaying:
            - The original image.
            - The image with segmentation masks overlaid.
            - A histogram of the area distribution of filtered objects.
            - A summary of the segmentation and filtering parameters used.
            - The number of masks removed and remaining after filtering.
        Parameters
        ----------
        cmap : str, optional
            Colormap to use for displaying segmentation masks. Default is "default"
            which is viridis.
        alpha : float, optional
            Transparency level for the segmentation masks overlay. Default is 0.3.
        Returns
        -------
        fig : matplotlib.figure.Figure
            The generated matplotlib Figure object containing the overview.
        Notes
        -----
        - Requires that `self.img`, `self.cha`, and `self.seg` are properly initialized.
        - Uses `plot_masks` and `get_scaling` utility functions.
        - Displays segmentation and filtering parameters extracted from metadata.
        """
        df = self.cha[self.cha["passed_filter"]]

        fig, ax = plt.subplot_mosaic(
            [["left", "right"], ["left2", "right2"]],
            layout="tight",
            figsize=(11.7, 8.3),
        )

        plt.suptitle(self.seg.metadata.General.title, fontsize=18)

        ax["left"].imshow(self.img.data, cmap="gray")
        ax["left"].axis("off")
        ax["left"].set_title("Original image", fontsize=16)
        scaling, units = self.get_scaling().split()
        scaling = float(scaling)
        _ = ScaleBar(ax["left"], units=units, pixel_size=scaling)

        ax["right"].imshow(self.img.data, cmap="gray")
        ax["right"].axis("off")
        ax["right"].set_title("Filtered masks", fontsize=16)
        cs = plot_masks(self, ax=ax["right"], cmap=cmap, alpha=alpha)
        for n, visibility in enumerate(self.cha["passed_filter"]):
            cs[n].set_visible(visibility)

        ax["right2"].axis("off")
        ax["right2"].set_title("Used parameter values", fontsize=16)

        df["area"].hist(bins="auto", ax=ax["left2"], edgecolor="k", color="#0081C6")
        unit = df["unit"].to_list()[0]
        unit2 = unit + "$^2$" if unit != "px" else unit
        ax["left2"].set_title(f"Histogram of area ({unit2})",fontsize=16)
        ax["left2"].set_xlabel(f"Area ({unit2})")
        ax["left2"].grid(False)
        ax["left2"].set_ylabel("Count")

        try:
            filters = self.seg.metadata.Filtering.Conditions.as_dictionary()
        except Exception:
            self.filter_nogui({"min_area": 0})
            filters = self.seg.metadata.Filtering.Conditions.as_dictionary()
        min_area, max_area = filters["area"]
        min_solidity, max_solidity = filters["solidity"]
        min_intensity, max_intensity = filters["intensity_mean"]
        min_eccentricity, max_eccentricity = filters["eccentricity"]
        min_overlap, max_overlap = filters["overlap"]
        overlapping_masks = filters["number_of_overlapping_masks"]
        scaling, unit = get_scaling(self.seg).split()
        scaling = float(scaling)
        removed = (~self.cha["passed_filter"]).sum()
        remain = self.cha["passed_filter"].sum()
        segmentation = seg_params_to_str(self.seg.metadata.Segmentation)

        tab = ax["right2"].table(
            [
                ["Segmentation:",segmentation],
                [f"Area ({unit2}):",f"({min_area:.5g}, {max_area:.5g})"],
                ["Solidity:",f"({min_solidity:.5g}, {max_solidity:.5g})"],
                ["Intensity:",f"({min_intensity:.5g}, {max_intensity:.5g})"],
                ["Eccentricity:",f"({min_eccentricity:.5g}, {max_eccentricity:.5g})"],
                ["Overlap:",f"({min_overlap:.5g}, {max_overlap:.5g})"],
                ["Number of over-\nlapping masks:", f"{overlapping_masks}"],
                [f"Scaling (px/{unit}):", f"{scaling:.5g}"],
                ["", ""],
                [f"{removed} masks removed. {remain} remain.", ""],
            ], 
            cellLoc="left",
            loc="center", 
            edges="open",
            colWidths=[0.25, 0.75],
            fontsize=12,
        )
        for cell in tab.get_celld():
            tab[cell].set_height(1/11)
        tab[6,0].set_height(2/11)
        tab[6,1].set_height(2/11)
        tab.auto_set_font_size(False)
        tab.set_fontsize(12)

        return fig

    def get_filtered_masks(self) -> np.ndarray:
        """
        Retrieve the segmentation masks that have passed the specified filtering
        criteria.

        Returns:
            np.ndarray: An array containing only the masks that satisfy the filter
            conditions.
        """
        return self.seg.data[self.cha["passed_filter"]]

    def export_filtered_characteristics(
        self, save_as: Optional[str | Path] = None
    ) -> None:
        """
        Exports the characteristics of masks that have passed filtering conditions to a
        CSV file.

        Parameters
        ----------
        save_as : Optional[str | Path], optional
            The file path or name to save the exported CSV file. If not provided, a
            default file name with the suffix '_filtered_masks.csv' will be used.

        Returns
        -------
        None

        Notes
        -----
        - Only masks with 'passed_filter' set to True in the `self.cha` DataFrame are
          exported.
        - The exported CSV will include a 'mask_index' column, which is a sequential
          index for the filtered masks.
        - The file is saved using the `save_df_to_csv` utility function.
        """
        filtered_characteristic = self.cha[self.cha["passed_filter"]]
        filtered_characteristic.loc[:, "mask_index"] = np.arange(
            len(filtered_characteristic)
        )
        filepath = self._save_as_to_filepath(save_as, end="_filtered_masks.csv")
        save_df_to_csv(filtered_characteristic, filepath.with_suffix(".csv"))

    def export_filtered_masks_png(
        self,
        save_as: Optional[str | Path] = None,
        cmap: str = "default",
        alpha: float = 0.3,
        dpi: int = 100,
    ) -> None:
        """
        Exports an image of the masks that passed the filtering conditions as a PNG file
        overlaid on the original image.

        Parameters
        ----------
        save_as : Optional[str | Path], optional
            The file path or name to save the exported PNG image. If None, a default
            path is used.
        cmap : str, optional
            The colormap to use for displaying the masks. Defaults to "default" which is
            viridis.
        alpha : float, optional
            The transparency level for the mask overlays. Defaults to 0.3.

        Returns
        -------
        None

        Notes
        -----
        - Only masks that have passed the filtering conditions (as indicated by
          `self.cha["passed_filter"]`) are shown in the exported image.
        - The image is saved with a "_filtered_masks.png" suffix if `save_as` is not
          provided.
        """
        plt.ioff()
        imy, imx = self.img.data.shape[:2]
        fig, ax = plt.subplots(figsize=[imx / dpi, imy / dpi])
        ax.set_position([0, 0, 1, 1])
        ax.axis("off")
        ax.imshow(self.img.data, cmap="gray")
        cs = plot_masks(self, ax=ax, cmap=cmap, alpha=alpha)
        for n, visibility in enumerate(self.cha["passed_filter"]):
            cs[n].set_visible(visibility)
        filepath = self._save_as_to_filepath(save_as, end="_filtered_masks.png")
        fig.savefig(filepath.with_suffix(".png"), dpi=dpi)
        plt.close(fig)
        plt.ion()

    def export_filtered_masks_tif(
        self,
        save_as: Optional[str | Path] = None,
    ) -> None:
        """
        Exports a labeled TIFF image of the masks that passed the filtering conditions.

        The output is a 2D TIFF file where each mask is assigned a unique integer label.
        Background pixels are labeled as 0, and each mask is labeled with a unique
        positive integer.

        Parameters
        ----------
        save_as : Optional[str | Path], optional
            The file path or name to save the exported TIFF image. If None, a default
            path is used.

        Returns
        -------
        None

        Notes
        -----
        - Only masks that have passed the filtering conditions (as indicated by
          `self.cha["passed_filter"]`) are included in the exported image.
        - The image is saved with a "_filtered_masks.tif" suffix if `save_as` is not
          provided.
        """
        labels = masks_to_2D(self.get_filtered_masks())
        filepath = self._save_as_to_filepath(save_as, end="_filtered_masks.tif")
        tifffile.imwrite(filepath.with_suffix(".tif"), labels.astype("uint16"))

    def export_filtered_masks_binary(
        self,
        save_as: Optional[str | Path] = None,
    ) -> None:
        """
        Exports the filtered masks as a binary TIFF image.

        This method retrieves the masks that have passed the filtering conditions,
        converts them into a 2D binary image (where mask pixels are set to 255 and
        background pixels to 0), and saves the result as a `.tif` file. The output
        file is named according to the provided `save_as` parameter, with
        `_filtered_masks_binary.tif` appended if not specified.

        Args:
            save_as (Optional[str | Path], optional): The file path or name to save the
                binary mask image. If not provided, a default name is generated.

        Returns:
            None
        """
        labels = masks_to_2D(self.get_filtered_masks())
        filepath = self._save_as_to_filepath(save_as, end="_filtered_masks_binary.tif")
        tifffile.imwrite(
            filepath.with_suffix(".tif"), ((labels > 0) * 255).astype("uint8")
        )

    def export_filtered_masks_numpy(
        self,
        save_as: Optional[str | Path] = None,
    ) -> None:
        """
        Exports the filtered masks as a compressed NumPy .npz file.

        The exported file contains only the masks that passed the filtering conditions,
        stored under the key 'array'. This file can be loaded later using:

            import numpy as np
            masks = np.load('filename.npz')['array']

        Parameters
        ----------
        save_as : Optional[str | Path], optional
            The file path or name to save the exported .npz file. If None, a default
            path is used with the suffix '_filtered_masks_binary.npz'.

        Returns
        -------
        None

        Notes
        -----
        - Only masks with 'passed_filter' set to True in the `self.cha` DataFrame are
          exported.
        - The saved .npz file contains a single array of shape (N, H, W), where N is the
          number of filtered masks, and H, W are the image dimensions.
        """
        filepath = self._save_as_to_filepath(save_as, end="_filtered_masks_binary.npz")
        np.savez_compressed(
            filepath.with_suffix(".npz"), array=self.get_filtered_masks()
        )

    def export_all(
        self,
        save_as: Optional[str] = None,
    ) -> None:
        """
        Exports all available outputs for the filtered masks and their characteristics.

        This method sequentially exports:
            - The characteristics of filtered masks as a CSV file.
            - An image (PNG) of the filtered masks overlaid on the original image.
            - A labeled TIFF image of the filtered masks.
            - A binary TIFF image of the filtered masks.
            - A compressed NumPy (.npz) file containing the filtered masks.

        Parameters
        ----------
        save_as : Optional[str], optional
            The base file path or name to use for saving the exported files. If None,
            default filenames and locations are used.

        Returns
        -------
        None

        Notes
        -----
        - The binary TIFF and NumPy files are saved with appropriate suffixes.
        - All outputs are generated for the currently filtered masks.
        """
        self.export_filtered_characteristics(save_as=save_as)
        self.export_filtered_masks_png(save_as=save_as, cmap="default")
        self.export_filtered_masks_tif(save_as=save_as)
        self.export_filtered_masks_binary(
            save_as=save_as + "_binary" if save_as else save_as
        )
        self.export_filtered_masks_numpy(save_as=save_as)

    def _save_as_to_filepath(
        self,
        save_as: str | Path,
        end: Optional[str] = None,
    ) -> Path:
        """
        Helper function to determine the output file path for saving results.

        Parameters:
            save_as (str | Path): The desired file path or base name for saving. If
            None, a default path is generated.
            end (Optional[str]): Optional suffix to append to the default filename
            (e.g., "_filtered_masks.csv").

        Returns:
            Path: The resolved file path as a Path object.

        Behavior:
            - If save_as is None, constructs a default path in a "NP-SAM_results"
              subfolder next to the original image file, appending the provided suffix
              (end) to the base filename.
            - If save_as is provided, uses it as the base path.
            - Ensures the parent directory exists.
        """
        if save_as is None:
            filepath = Path(self.filepath).parent / (
                "NP-SAM_results/" + Path(self.filepath).name.split(".")[0] + end
            )
            filepath.parent.mkdir(exist_ok=True)
        else:
            filepath = Path(save_as)

        # if save_as is None:
        #    filepath = Path(self.filepath.split(".")[0] + end)
        # else:
        #    filepath = Path(save_as)
        return filepath


class NPSAM(MutableSequence):
    """
    NPSAM: A container class for batch segmentation and analysis of multiple images
    using NP-SAM.

    This class wraps multiple NPSAMImage objects, enabling streamlined batch processing
    of image segmentation,
    mask characterization, filtering, visualization, and export of results.

    Key features:
        - Loads multiple images from file paths, directories, or NPSAMImage objects.
        - Supports batch segmentation, mask characterization, and filtering across all
          images.
        - Provides methods for setting scaling and unit conversion for all images.
        - Enables interactive and programmatic filtering of masks for each image.
        - Offers batch export of filtered masks and characteristics in various formats
          (CSV, PNG, TIFF, NumPy).
        - Generates overview PDF reports with histograms and summary statistics for all
          images.
        - Supports convenient indexing, addition, and modification of the images.

    Usage:
        - Initialize with a list of file paths, a directory, or NPSAMImage objects.
        - Call .segment() to segment all images.
        - Use .filter() or .filter_nogui() to filter masks based on characteristics.
        - Export results or generate overview reports using the provided export and
          overview methods.

    This class is designed for efficient batch processing and analysis of large image
    datasets.
    """

    def __init__(
        self,
        images: Optional[
            Sequence[str | Path | NPSAMImage] | str | Path | NPSAMImage
        ] = None,
        select_image: Optional[int | str] = None,
        select_files: Optional[str] = "*",
    ) -> None:
        """
        Initializes the object with a list of images or image paths. The images are
        stored as NPSAMImage objects in the `data` attribute. If no images are provided,
        the user is prompted to select image files using the `get_filepaths()` function.
        This method supports loading images from a single file, multiple files, or a
        directory. It also allows selecting a specific image from a file if multiple
        images are present.  If `images` is a directory, it loads all files matching the
        `select_files` pattern, excluding system files like '.DS_Store' and
        'desktop.ini'. If `images` is a single file or an NPSAMImage object, it is
        wrapped in a list for consistency.

        Parameters
        ----------
        images : Optional[str | Path | NPSAMImage], default=None
            The image(s) to load. Can be one or more file path, directory path, or an
            NPSAMImage object.
            If None, the function `get_filepaths()` is called to prompt for image paths.
        select_image : Optional[int | str], default=None
            Index or identifier, e.g. "HAADF" or "BF", to select a specific image if
            there are several in the same file.
        select_files : Optional[str], default="*"
            Glob pattern to select files when `images` is a directory.
        Raises
        ------
        ValueError
            If `images` is provided as a Path that is neither a file nor a directory.
        Notes
        -----
        - If `images` is a directory, all files matching `select_files` are loaded,
          excluding system files like '.DS_Store' and 'desktop.ini'.
        - If `images` is a single file or NPSAMImage, it is wrapped in a list.
        """
        if images is None:
            images = get_filepaths()
        else:
            if isinstance(images, str):
                images = Path(images)
            if isinstance(images, Path):
                if images.is_dir():
                    images = [
                        f
                        for f in images.glob(select_files)
                        if (
                            f.is_file()
                            and ".DS_Store" not in f.as_posix()
                            and "desktop.ini" not in f.as_posix()
                        )
                    ]
                elif images.is_file():
                    images = [images]
                else:
                    raise ValueError(
                        f"images='{images}' is neither a file nor a directory."
                    )
            if isinstance(images, NPSAMImage):
                images = [images]
        self.data = [
            self._validatetype(image, select_image=select_image) for image in images
        ]
        self._update()

    def __repr__(self) -> str:
        """
        Return a string representation of the object with improved readability.
        The method returns the string representation of the object's data attribute
        containing the images, formatting it so that each element is separated by a
        newline for better clarity.
        """
        return repr(self.data).replace(">, <", ">,\n <")

    def __str__(self) -> str:
        """
        Return a string representation of the object with improved readability.
        The method returns the string representation of the object's data attribute
        containing the images, formatting it so that each element is separated by a
        newline for better clarity.
        """
        return str(self.data).replace(">, <", ">,\n <")

    def __len__(self) -> int:
        """
        Return the number of images in the NPSAM object.
        """
        return len(self.data)

    def __getitem__(
        self,
        i: int | slice,
    ) -> NPSAMImage | list[NPSAMImage]:
        """
        Retrieve one or more NPSAMImage objects from the NPSAM object.

        Args:
            i (int or slice): Index or slice specifying which image(s) to retrieve.

        Returns:
            NPSAMImage or list[NPSAMImage]: The image at the specified index if `i` is
            an int, or a new instance containing the selected images if `i` is a slice.

        Raises:
            IndexError: If the index is out of range.
        """
        if isinstance(i, int):
            return self.data[i]
        else:
            return self.__class__(self.data[i])

    def __setitem__(
        self,
        i: int | slice,
        image: NPSAMImage | str | Path | list[NPSAMImage] | list[str] | list[Path],
    ):
        """
        Sets the item(s) at the specified index or slice with the provided image(s).
        Args:
            i (int | slice): The index or slice where the image(s) should be set.
            image (NPSAMImage | str | Path | list[NPSAMImage] | list[str] | list[Path]):
                The image or list of images to assign. Can be an NPSAMImage instance, a
                file path (as str or Path), or a list of these types.
        Raises:
            TypeError: If the provided image(s) are not of a valid type.
            ValueError: If the assignment cannot be completed due to invalid input.
        Side Effects:
            Updates the internal data structure and triggers an update after assignment.
        """
        self.data[i] = self._validatetype(image)
        self._update()

    def __delitem__(
        self,
        i: int | slice,
    ) -> None:
        """
        Remove item(s) at the specified index or slice from the data.
        Args:
            i (int | slice): The index or slice specifying which item(s) to delete.
        Returns:
            None
        Side Effects:
            Modifies the underlying data by removing the specified item(s) and updates
            the object state.
        """
        del self.data[i]
        self._update()

    def __add__(
        self,
        other: Optional["NPSAM | NPSAMImage"],
    ) -> "NPSAM":
        """
        Implements the addition operator for NPSAM objects.
        If `other` is an instance of NPSAM, returns a new NPSAM object with combined
        data from both objects.
        If `other` is an instance of NPSAMImage, returns a new NPSAM object with the
        NPSAMImage appended to the data.
        Raises a TypeError if `other` is not a NPSAM or NPSAMImage.
        Args:
            other (Optional[NPSAM | NPSAMImage]): The object to add to this NPSAM
            instance.
        Returns:
            NPSAM: A new NPSAM object with the combined data.
        Raises:
            TypeError: If `other` is not a NPSAM or NPSAMImage.
        """
        if isinstance(other, NPSAM):
            return self.__class__(self.data + other.data)
        elif isinstance(other, NPSAMImage):
            return self.__class__(self.data + [other])
        else:
            raise TypeError("Can only add NPSAM objects")

    def insert(
        self,
        i: int,
        image: NPSAMImage | str | Path,
    ) -> None:
        """
        Inserts an image into the data list at the specified index.
        Args:
            i (int): The index at which to insert the image.
            image (NPSAMImage | str | Path): The image to insert. Can be an NPSAMImage
            instance, a file path as a string, or a Path object.
        Returns:
            None
        """
        self.data.insert(i, self._validatetype(image))
        self._update()

    def _validatetype(
        self,
        item: NPSAMImage | str | Path,
        select_image: Optional[str] = None,
    ) -> NPSAMImage:
        """
        Validates and converts the input item to an NPSAMImage instance.
        Parameters
        ----------
        item : NPSAMImage | str | Path
            The input to validate. Can be an NPSAMImage instance, a string filepath, or
            a pathlib.Path object.
        select_image : Optional[str], default=None
            An optional image selection parameter when there are multiple images in a
            file, e.g. "HAADF" or "BF".
        Returns
        -------
        NPSAMImage
            The validated or newly constructed NPSAMImage instance.
        Raises
        ------
        TypeError
            If the input item is not an NPSAMImage, string, or Path, or if the Path does
            not point to a file.
        """
        if isinstance(item, NPSAMImage):
            return item
        if isinstance(item, Path):
            if item.is_file():
                return NPSAMImage(item.as_posix(), select_image=select_image)
        if isinstance(item, str):
            return NPSAMImage(item, select_image=select_image)
        raise TypeError("Only NPSAMImage objects or filepaths are supported")

    def _update(self):
        """
        Updates the object's image, segmentation, characteristics, and filepath
        attributes by extracting corresponding data from each element in self.data.
        Assumes that each element in self.data has the attributes: img, seg, cha, and
        filepath.
        Populates:
            - self.img: List of image data from each element.
            - self.seg: List of segmentation data from each element.
            - self.cha: List of characteristcs data from each element.
            - self.filepaths: List of file paths from each element.
        """
        self.img = [image.img for image in self.data]
        self.seg = [image.seg for image in self.data]
        self.cha = [image.cha for image in self.data]
        self.filepaths = [image.filepath for image in self.data]

    def set_scaling(
        self,
        scaling: bool | str | list[str] = True,
    ) -> None:
        """
        Set the scaling for all loaded images and their segmentation masks.
        This method updates the scaling metadata for each image and its segmentation
        mask.
        The scaling can be specified as a single Pint-compatible string (e.g., '1 nm',
        '3.5 µm', '0.3 um', or '4 Å'), a list of such strings (one per image), or
        interactively prompted from the user if not provided.
        Args:
            scaling (bool | str | list[str], optional):
                - If True (default), prompts the user to input scaling for all images
                  (either common or individual).
                - If False, sets scaling to '1 px' for all images.
                - If str, applies the given scaling to all images.
                - If list of str, applies each scaling to the corresponding image.
        Raises:
            ValueError: If the number of scalings does not match the number of images,
            or if the input type is invalid.
        Notes:
            - If segmentation exists, the scaling for the characteristics DataFrame is
              also updated.
            - If area filtering conditions are present in the segmentation metadata, a
              warning is printed (only once).
        """
        if scaling is True:
            common_scaling = input(
                "Do you want to use the same scaling for all images? (Y/n) "
            )
            if common_scaling.lower() in ["y", "yes", ""]:
                scalings = input("What is the scaling? (E.g. '2.5 nm') ")
                scalings = len(self) * [scalings]
            else:
                scalings = []
                for image in self:
                    scalings.append(
                        input(
                            f"What is the scaling for {image.img.metadata.General.title}? (E.g. '2.5 nm') "
                        )
                    )
        elif scaling is False:
            scalings = len(self) * ["1 px"]
        elif isinstance(scaling, str):
            scalings = len(self) * [scaling]
        elif isinstance(scaling, list):
            scalings = scaling
        else:
            raise ValueError("scaling must be given as a string or a list of strings.")

        if len(self) == len(scalings):
            printed_yet = False
            for image, scaling in zip(self, scalings):
                image.set_scaling(scaling, verbose=not printed_yet)
                try:
                    if image.seg.metadata.Filtering.Conditions is not None:
                        printed_yet = True
                except Exception:
                    pass
        else:
            raise ValueError(
                f"The number of scalings ({len(scalings)}) does not correspond to the number of images ({len(self)})."
            )

    def get_scaling(self) -> list[str]:
        """
        Retrieves the scaling information of the images and segmentation masks.

        Returns:
            str: The scaling factor and unit as a string (e.g., '1 px', '3.5 µm').
        """
        return [get_scaling(img) for img in self.img]

    def convert_to_units(
        self,
        units: Optional[str | list[str]] = None,
    ) -> None:
        """
        Convert the units of all loaded images to the specified units.
        Parameters
        ----------
        units : str or list of str, optional
            The target units to convert the images to. Can be a single string (applied
            to all images) or a list of strings (one per image). Units must be
            compatible with Pint, e.g. 'nm', 'µm', 'um', or 'Å'. If not provided, the
            user will be prompted to input the desired units for each image.
        Raises
        ------
        ValueError
            If `units` is not a string or a list of strings, or if the number of units
            does not match the number of images in the collection.
        Notes
        -----
        If `units` is None, the user is interactively prompted to provide units for each
        image or a common unit for all images. The conversion is performed by calling
        `convert_to_units` on each NPSAMImage object.
        """
        if units is None:
            common_units = input(
                "Do you want to convert to the same units for all images? (Y/n) "
            )
            if common_units.lower() in ["y", "yes", ""]:
                units = input("What is the units? (E.g. 'nm') ")
                units = len(self) * [units]
            else:
                units = []
                for image in self:
                    units.append(
                        input(
                            f"What is the units for {image.img.metadata.General.title}? (E.g. 'nm') "
                        )
                    )
        elif isinstance(units, str):
            units = len(self) * [units]
        elif isinstance(units, list):
            pass
        else:
            raise ValueError("units must be given as a string or a list of strings.")

        if len(self) == len(units):
            printed_yet = False
            for image, unit in zip(self, units):
                image.convert_to_units(unit, verbose=not printed_yet)
                try:
                    if image.seg.metadata.Filtering.Conditions is not None:
                        printed_yet = True
                except Exception:
                    pass
        else:
            raise ValueError(
                f"The number of units ({len(units)}) does not correspond to the number of images ({len(self)})."
            )

    def segment(
        self,
        device: str = "auto",
        SAM_model: str = "auto",
        PPS: int = 64,
        shape_filter: bool = True,
        edge_filter: bool = True,
        crop_and_enlarge: bool = False,
        invert: bool = False,
        double: bool = False,
        min_mask_region_area: int = 100,
        stepsize: int = 1,
        verbose: bool = True,
        **kwargs: Any,
    ) -> None:
        """
        Segments the loaded images using either SAM or FastSAM, generating binary masks
        for detected regions and storing them as a list of HyperSpy signals in the
        `.seg` attribute. Segmentation parameters are also saved in the signals'
        metadata.
        Parameters
        ----------
        device : str, optional
            Device to use for computation: 'auto', 'cpu', or 'cuda'. If 'auto', the
            device will be chosen based on the computers hardware, where it will choose
            'cuda' if a CUDA compatible graphics card is available with more than 5 GB
            of dedicated VRAM, otherwise 'cpu'. Default is 'auto'.
        SAM_model : str, optional
            Model type for segmentation: 'auto', 'huge', 'large', 'base', or 'fast'. If
            'auto', the model will be chosen based on the available hardware and
            performance considerations. 'huge' is the most accurate but slowest, while
            'fast' is the fastest but least accurate. 'large' and 'base' are
            intermediate options. If 'fast', FastSAM is used instead of SAM.
            If 'huge', 'large', or 'base', the SAM model is used.
            Default is 'auto'.
        PPS : int, optional
            Points per side for sampling in SAM. A higher value can help finding smaller
            particles but increases computation time. Default is 64.
        shape_filter : bool, optional
            Whether to filter masks based on shape properties (area and solidity). This
            will remove very concave masks. Default is True.
        edge_filter : bool, optional
            Whether to filter out masks that touch the image edges. Default is True.
        crop_and_enlarge : bool, optional
            Whether to crop and enlarge sub-images before segmentation. This helps
            finding smaller particles, since four zoomed-in quadrants of the image are
            segmented. This increases computation time at least by a factor of 4.
            Default is False.
        invert : bool, optional
            Whether to invert the image before segmentation. This works better for some
            images. Default is False.
        double : bool, optional
            Whether to perform segmentation twice (inverted and non-inverted) and merge
            results. Default is False.
        min_mask_region_area : int, optional
            Disconnected regions and holes in masks with area smaller than
            min_mask_region_area will be removed. Default is 100.
        stepsize : int, optional
            Step size for overlap detection during characterization after segmentation.
            A step size of 1 checks every pixel in the image, a step size of 2 checks
            every other pixel and so on. Increasing the step size decreases the
            computation time, but overlapping regions between masks might be missed.
            Default is 1.
        verbose : bool, optional
            If True, prints progress and summary information. Default is True.
        **kwargs : Any
            Additional keyword arguments passed to the segmentation functions.
        Notes
        -----
        - The function preprocesses the image, applies segmentation, filters masks, and
          stores the results.
        - The resulting masks are saved as a list of HyperSpy Signal2D object in
          `self.seg`, with relevant metadata.
        - If no masks are found, a message is printed and no masks are saved.
        - After segmentation, the `characterize` method is called to further analyze the
          masks.
        Returns
        -------
        None
            The results are stored in the object's attributes `self.seg` and `self.cha`.
        """
        if device.lower() in ["auto", "a"]:
            device = choose_device()

        SAM_model = choose_SAM_model(SAM_model, device, verbose)

        for n, image in enumerate(self):
            if len(self) > 1:
                print(f"{n + 1}/{len(self)} - Now working on: {image.name}")

            image.segment(
                device=device,
                SAM_model=SAM_model,
                PPS=PPS,
                shape_filter=shape_filter,
                edge_filter=edge_filter,
                crop_and_enlarge=crop_and_enlarge,
                invert=invert,
                double=double,
                min_mask_region_area=min_mask_region_area,
                stepsize=stepsize,
                verbose=verbose,
                **kwargs,
            )

            if len(self) > 1:
                print("")

            self._update()

    def characterize(
        self,
        stepsize: int = 1,
        verbose: bool = True,
    ) -> None:
        """
        Analyze and characterize each mask in the segmentation data.
        This method computes a comprehensive set of region properties for each mask
        using the corresponding image data, and stores the results in a list of Pandas
        DataFrames assigned to the `.cha` attribute. The computed properties include
        geometric, intensity, and shape descriptors such as area, centroid,
        eccentricity, perimeter, and more.
        Additionally, the method:
            - Converts pixel-based measurements to physical units using image scaling.
            - Identifies and quantifies overlapping regions between masks.
            - Stores the number of overlaps and the indices of overlapping masks.
            - Extracts and saves mask contours in the segmentation metadata.
        Parameters
        ----------
        stepsize : int, optional
            Step size for overlap analysis. Higher values may speed up computation at
            the cost of reduced accuracy. Default is 1 (analyze every pixel).
        verbose : bool, optional
            If True, prints progress information during computation. Default is True.
        Returns
        -------
        None
        Side Effects
        ------------
        - Sets the `self.cha` attribute to a list of DataFrames containing mask
          characteristics.
        - Updates each NPSAMImage object's `self.seg.metadata.Filtering.Contours` with
          mask contours.
        Notes
        -----
        - Requires the images to be segmented first.
        - The DataFrames include both pixel and scaled (physical unit) measurements.
        - Overlap analysis may be computationally intensive for large datasets.
        """
        for im in self:
            im.characterize(stepsize=stepsize, verbose=verbose)

    def save_segmentation(
        self,
        save_as: Optional[str] = None,
        overwrite: Optional[bool] = None,
    ) -> None:
        """
        Saves segmentation, characterization, and filtering results for each image.

        Results are saved to a subfolder named according to the `save_as` argument. If
        `save_as` is None, the results are saved in a folder named 'NP-SAM_results'.
        Each image's results are saved with the same filename as the original image,
        inside the specified subfolder.

        Args:
            save_as (Optional[str], optional): Name of the subfolder to save results in.
            If None, defaults to 'NP-SAM_results'.
            overwrite (Optional[bool], optional): Whether to overwrite existing files.
            Passed to each image's `save_segmentation` method.

        Returns:
            None
        """
        for image in self:
            if save_as is not None:
                filepath = Path(image.filepath).parent / (
                    f"{save_as}/" + Path(image.filepath).name
                )
                filepath.parent.mkdir(exist_ok=True)
                _save_as = filepath.as_posix()
            else:
                _save_as = save_as
            image.save_segmentation(overwrite=overwrite, save_as=_save_as)

    def load_segmentation(
        self,
        foldername: Optional[str] = None,
    ) -> None:
        """
        Loads segmentation, characterization, and filtering results for each loaded
        image.

        For each image, this method loads the segmentation data from a `.hspy` file and
        the characteristics from a `.csv` file located in the specified folder. If
        `foldername` is None, it defaults to the "NP-SAM_results" subfolder next to each
        original image file(s).

        Args:
            foldername (Optional[str], optional): Name of the subfolder containing the
            results to load. If None, defaults to 'NP-SAM_results'.

        Returns:
            None

        Side Effects:
            Updates each image's segmentation and characteristics attributes, and
            updates the NPSAM object state.
        """
        for image in self:
            if foldername is not None:
                filepath = (
                    Path(image.filepath).parent
                    / (f"{foldername}/" + Path(image.filepath).name)
                ).as_posix()
            else:
                filepath = None
            image.load_segmentation(filepath=filepath)
        self._update()

    def plot_masks(
        self,
        cmap: str = "default",
        alpha: int = 0.3,
        figsize: Sequence[float] = [8, 4],
        filtered: bool = False,
    ) -> None:
        """
        Plots the original images and the masks found through segmentation.

        Parameters:
            cmap (str): Colormap to use for the masks. Default is "default" which takes
            random colors from viridis.
            alpha (float): Transparency of the masks overlay. Default is 0.3.
            figsize (Sequence[float]): Figure size as [width, height]. Default is
            [8, 4].
            filtered (bool): If True, only plots the masks that passed the filtering
            conditions. Default is False.

        Behavior:
            - Displays the original image and the segmentation masks side by side.
            - If filtered is True, only masks passing the filter are shown.
            - Adds a scale bar to the image.
            - Shows the plot using matplotlib.
        """
        for image in self:
            image.plot_masks(cmap=cmap, alpha=alpha, figsize=figsize, filtered=filtered)

    def plot_particle(
        self,
        image_index: int,
        mask_index: int,
        cmap: str = "grey",
    ) -> None:
        """
        Plots a specific particle (mask) from a given image using the specified colormap.
        Args:
            image_index (int): Index of the image in the dataset.
            mask_index (int): Index of the particle (mask) to plot within the image.
            cmap (str, optional): Colormap to use for plotting. Defaults to "grey".
        Returns:
            None
        Example:
            >>> s.plot_particle(image_index=0, mask_index=2, cmap="viridis")
        """
        self[image_index].plot_particle(mask_index, cmap=cmap)

    def filter(
        self,
        cmap: str = "default",
        alpha: float = 0.3,
        app: bool = False,
        position: Optional[Sequence[float]] = None,
    ) -> None:
        """
        Opens the interactive filtering GUI where the user can filter the masks based on
        characteristics such as area, intensity, eccentricity, solidity, and overlap.

        Parameters
        ----------
        cmap : str, optional
            The colormap to use for the plotted masks. Default is "default" which is
            viridis.
        alpha : float, optional
            The transparency level for the plotted masks. Default is 0.3.
        app : bool, optional
            This should only be true when the method is called by the NP-SAM windows
            application.
            Default is False.
        position : Optional[Sequence[float]], optional
            The position of the Matplotlib figure that contains the interactive
            filtering GUI. If None, uses the default position. It uses the matplotlib
            figure position argument, e.g. [left, bottom, width, height].
        Returns
        -------
        None
            This method does not return anything. It updates the filtering conditions in
            place, and updates the "passed_filter" column in the characteristics
            DataFrame of each image accordingly.
        """
        self._update()
        filter(self, cmap=cmap, alpha=alpha, app=app, position=position)
        self._update()

    def filter_nogui(
        self,
        conditions: Sequence[dict[str, Sequence[float | int] | int]]
        | dict[str, Sequence[float | int] | int],
    ) -> None:
        """
        Filters the masks based on a set of conditions with respect to the mask
        characteristics, without opening an interactive window.

        Parameters
        ----------
        conditions : dict or list of dict
            Dictionary or list of dictionaries specifying filter conditions. Each
            dictionary can have the following keys:
            - area: tuple (min, max)
            - intensity_mean: tuple (min, max)
            - eccentricity: tuple (min, max)
            - solidity: tuple (min, max)
            - overlap: tuple (min, max)
            - number_of_overlapping_masks: int (maximum allowed)
            - removed_index: list of mask indices to exclude

        Behavior
        --------
        - Updates the 'passed_filter' column in the characteristics DataFrame based on
          the conditions.
        - Stores the filter conditions in the segmentation metadata.
        - If a list of conditions is provided, each entry is applied to the
          corresponding image.
        - If a single dictionary is provided, it is applied to all images.

        Raises
        ------
        ValueError
            If the list of conditions does not match the number of images, or if entries
            are not dictionaries.
        """
        filter_nogui(self, conditions)

    def export_filtered_characteristics(self) -> None:
        """
        Exports the characteristics of masks that have passed the filtering conditions
        to a CSV file.

        For each segmented and filtered image, this method saves a CSV file containing
        only the characteristics of the masks where 'passed_filter' is True. The output
        file is named with the original image name and a '_filtered_masks.csv' suffix,
        and is saved in the default results folder or as specified.

        Returns:
            None
        """
        for image in self:
            image.export_filtered_characteristics()

    def export_filtered_masks_png(
        self,
        cmap: str = "default",
        alpha: float = 0.3,
    ) -> None:
        """
        Exports an image (PNG) of the masks that passed the filtering conditions.

        For each segmented and filtered image, this method saves a PNG file with the
        filtered masks overlaid on the original image. The output file is named with the
        original image name and a '_filtered_masks.png' suffix, and is saved in the
        default results folder.

        Parameters
        ----------
        cmap : str, optional
            The colormap to use for displaying the masks. Defaults to "default"
            (viridis).
        alpha : float, optional
            The transparency level for the mask overlays. Defaults to 0.3.

        Returns
        -------
        None
        """
        for image in self:
            image.export_filtered_masks_png(cmap=cmap, alpha=alpha)

    def export_filtered_masks_tif(self) -> None:
        """
        Exports a labeled TIFF image of the masks that passed the filtering conditions
        for each image.

        The output is a 2D TIFF file where each mask is assigned a unique integer label.
        Background pixels are labeled as 0, and each mask is labeled with a unique
        positive integer.

        Returns
        -------
        None

        Notes
        -----
        - Only masks that have passed the filtering conditions (as indicated by
          `self.cha["passed_filter"]`) are included in the exported image.
        - The image is saved with a "_filtered_masks.tif" suffix if `save_as` is not
          provided.
        """
        for image in self:
            image.export_filtered_masks_tif()

    def export_filtered_masks_binary(self) -> None:
        """
        Export filtered masks as a binary TIFF image.

        Iterates over all images, exporting the masks that have passed the filtering
        criteria as binary `.tif` files. Each mask is saved as a separate image file,
        where mask pixels are set to 1 (particle) and all other pixels are set to 0
        (background).

        Returns:
            None
        """
        for image in self:
            image.export_filtered_masks_binary()

    def export_filtered_masks_numpy(self) -> None:
        """
        Exports the filtered masks as a compressed NumPy .npz file for each image.

        The exported file contains only the masks that passed the filtering conditions,
        stored under the key 'array'. This file can be loaded later using:

            import numpy as np
            masks = np.load('filename.npz')['array']

        Returns
        -------
        None

        Notes
        -----
        - Only masks with 'passed_filter' set to True in the `self.cha` DataFrame are
          exported.
        - The saved .npz file contains a single array of shape (N, H, W), where N is the
          number of filtered masks, and H, W are the image dimensions.
        """
        for image in self:
            image.export_filtered_masks_numpy()

    def export_all(self) -> None:
        """
        Exports all data for each image.

        Iterates over all images contained within the object and calls their
        `export_all` method to perform the export operation.

        For each image, this method calls the following methods in sequence:
            - export_filtered_characteristics: Exports the characteristics of filtered
              masks as a CSV file.
            - export_filtered_masks_png: Exports a PNG image of the filtered masks
              overlaid on the original image.
            - export_filtered_masks_tif: Exports a labeled TIFF image of the filtered
              masks.
            - export_filtered_masks_binary: Exports a binary TIFF image of the filtered
              masks.
            - export_filtered_masks_numpy: Exports a compressed NumPy (.npz) file of the
              filtered masks.

        Returns:
            None
        """
        for image in self:
            image.export_all()

    def list_overview_characteristics(self) -> None:
        """
        Lists the available characteristics for generating an overview PDF.
        This method prints the names of all characteristics that can be used in the
        `overview` method.
        """
        print("Available characteristics for overview:")
        print(
            "area, area_convex, axis_major_length, axis_minor_length, eccentricity,\n"
            "equivalent_diameter_area, extent, feret_diameter_max, intensity_max,\n"
            "intensity_mean, intensity_min, orientation, perimeter, perimeter_crofton,\n"
            "solidity, overlap"
        )

    def overview(
        self,
        characteristics: Sequence[str] = ["area"],
        save_as: Optional[str | Path] = None,
        cmap: str = "default",
        alpha: float = 0.3,
        bin_list: Optional[Sequence[int | str]] = None,
        timestamp: bool = False,
        save_csv: bool = False,
        show_all_figures: bool = False,
    ) -> None:
        """
        Generates and saves an overview PDF file summarizing segmentation results and
        histograms of selected mask characteristics for all images in the collection.

        Parameters
        ----------
        characteristics : Sequence[str], optional
            List of mask characteristics to include in the histograms. Use ["all"] to
            include all available characteristics.
            See available characteristics by running the
            `list_overview_characteristics()` method. Default is ["area"].
        save_as : Optional[str | Path], optional
            Path to save the resulting PDF file. If None, saves to a default location.
        cmap : str, optional
            Colormap to use for mask overlays in overview figures. Default is "default"
            (viridis).
        alpha : float, optional
            Transparency for mask overlays. Default is 0.3.
        bin_list : Optional[Sequence[int | str]], optional
            List specifying the number of bins or binning strategy for each
            characteristic histogram. If None, uses "auto" for all.
        timestamp : bool, optional
            If True, appends a timestamp to the output filename. Default is False.
        save_csv : bool, optional
            If True, also saves the filtered characteristics DataFrame as a CSV file.
            Default is False.
        show_all_figures : bool, optional
            If True, displays all generated figures. If False, closes figures and opens
            the PDF file. Default is False.

        Behavior
        --------
        - Includes only masks that passed the filtering conditions.
        - Plots histograms for the selected characteristics, including summary
          statistics.
        - Adds overview figures for each image showing segmentation and filtering
          parameters.
        - Saves all figures to a single PDF file.
        - Optionally saves a CSV file with filtered characteristics.
        - Optionally appends a timestamp to the filename.

        Returns
        -------
        None
        """
        if characteristics == ["all"]:
            characteristics = [
                "area",
                "area_convex",
                "axis_major_length",
                "axis_minor_length",
                "eccentricity",
                "equivalent_diameter_area",
                "extent",
                "feret_diameter_max",
                "intensity_max",
                "intensity_mean",
                "intensity_min",
                "orientation",
                "perimeter",
                "perimeter_crofton",
                "solidity",
                "overlap",
            ]

        for n, prop in enumerate(characteristics):
            if prop == "intensity":
                characteristics[n] = "intensity_mean"
            elif prop == "diameter":
                characteristics[n] = "equivalent_diameter_area"
            elif prop == "max diameter":
                characteristics[n] = "feret_diameter_max"
            elif prop == "crofton perimeter":
                characteristics[n] = "perimeter_crofton"
            elif prop == "convex area":
                characteristics[n] = "area_convex"

        dfs = []
        imagenumber = 1
        for image in self:
            df_filtered = copy(image.cha[image.cha["passed_filter"]])
            df_filtered["imagename"] = image.cha.attrs["title"]
            df_filtered["imagenumber"] = imagenumber
            imagenumber += 1
            dfs.append(df_filtered)
        df = pd.concat(dfs)

        if bin_list is None:
            bin_list = ["auto"] * len(characteristics)

        unit = df["unit"].to_list()[0]
        unit2 = unit + "$^2$" if unit != "px" else unit
        name_dict = {
            "area": f"area ({unit2})",
            "area_convex": f"convex area ({unit2})",
            "eccentricity": "eccentricity",
            "solidity": "solidity",
            "intensity_mean": "mean intensity",
            "equivalent_diameter_area": f"area equivalent diameter ({unit})",
            "feret_diameter_max": f"Max diameter (Feret) ({unit})",
            "orientation": "orientation",
            "perimeter": f"perimeter ({unit})",
            "perimeter_crofton": f"crofton perimeter ({unit})",
            "axis_major_length": f"Major axis length ({unit})",
            "axis_minor_length": f"Minor axis length ({unit})",
            "extent": "Ratio of pixels in the mask the pixels in the bounding box",
            "intensity_max": "Max intensity of the mask",
            "intensity_min": "minimum intensity of the mask",
            "overlap": f"amount of overlap ({unit2})",
        }
        figs = []
        for n, prop in enumerate(characteristics):
            fig, ax = plt.subplots(figsize=(11.7, 8.3))
            ax.set_xlabel(name_dict.get(prop).capitalize(), fontsize=16)
            ax.set_title(
                f"Histogram of {name_dict.get(prop)} for all images", fontsize=18
            )
            df[prop].hist(bins=bin_list[n], ax=ax, edgecolor="k", color="#0081C6")
            ax.grid(False)
            ax.set_ylabel("Count", fontsize=16)
            ax.tick_params(axis="both", which="major", labelsize=14)
            data = df[prop]
            mean = np.mean(data)
            median = np.median(data)
            std_dev = np.std(data)
            variance = np.var(data)
            skewness = scipy.stats.skew(data)
            kurtosis = scipy.stats.kurtosis(data)
            data_range = np.ptp(data)
            q1 = np.percentile(data, 25)
            q3 = np.percentile(data, 75)
            iqr = scipy.stats.iqr(data)
            minimum = np.min(data)
            maximum = np.max(data)
            count = len(data)
            total_sum = np.sum(data)
            coeff_variation = std_dev / mean

            def format_value(val):
                if val == 0:
                    return 0
                elif val < 10:
                    return f"{val:.2f}"
                elif 10 <= val < 100:
                    return f"{val:.1f}"
                elif 100 <= val:
                    return f"{int(val)}"

            x_r = 1 - len(f"Upper quantile: {format_value(q3)}") * 0.0108
            x_m = (
                x_r - 0.025 - len(f"Sum: {format_value(total_sum)}") * 0.0108
                if total_sum > 100000000
                else x_r - 0.155
            )
            x_l = (
                x_m - 0.055 - len(f"Sum: {format_value(variance)}") * 0.0108
                if variance > 1000000000000
                else x_m - 0.22
            )

            stats_text_left = (
                f"Mean: {format_value(mean)}\nStd Dev: {format_value(std_dev)}\n"
                f"Median: {format_value(median)}\nVariance: {format_value(variance)}\n"
                f"Coeff of Variation: {format_value(coeff_variation)}\n"
                f"Total number of masks: {len(df['area'].to_list())}"
            )

            stats_text_middle = (
                f"Skewness: {format_value(skewness)}\nKurtosis: {format_value(kurtosis)}\n"
                f"Count: {count}\nSum: {format_value(total_sum)}\nIQR: {format_value(iqr)}"
            )

            stats_text_right = (
                f"Lower quantile: {format_value(q1)}\nUpper quantile: {format_value(q3)}\n"
                f"Min: {format_value(minimum)}\nMax: {format_value(maximum)}\n"
                f"Range: {format_value(data_range)}"
            )
            n = "i" * int((194 * (1 - x_l + 0.011)))

            text = f"{n}\n{n}\n{n}\n{n}\n{n}\n{n}"
            text_properties = {
                "fontsize": 12,
                "color": "none",
                "verticalalignment": "top",
                "bbox": dict(
                    boxstyle="round,pad=0.3",
                    edgecolor="black",
                    facecolor="white",
                    alpha=0.5,
                ),
            }

            plt.text(x_l, 0.98, text, transform=plt.gca().transAxes, **text_properties)
            for x, txt in zip(
                [x_l, x_m, x_r], [stats_text_left, stats_text_middle, stats_text_right]
            ):
                plt.text(
                    x,
                    0.98,
                    txt,
                    ha="left",
                    va="top",
                    transform=plt.gca().transAxes,
                    fontsize=12,
                )

            figs.append(fig)

        for image in self:
            figs.append(image._make_overview_figure(cmap=cmap, alpha=alpha))

        if timestamp:
            d = datetime.now()
            stamp = f"_{d.year}{d.month}{d.day}_{d.hour}{d.minute}{d.second}"
        else:
            stamp = ""

        parent_folder = Path(self[0].filepath).parent

        if save_as is None:
            filepath = parent_folder / f"NP-SAM_results/NP-SAM_overview{stamp}.pdf"
        else:
            filepath = Path(save_as)
        filepath.parent.mkdir(exist_ok=True)
        p = PdfPages(filepath)

        for fig in figs:
            fig.savefig(p, format="pdf")

        if save_csv:
            file_p = Path(filepath.as_posix().split(".")[0] + "_filtered_dataframe.csv")
            first_column = df.pop("imagename")
            second_column = df.pop("imagenumber")
            df.insert(0, "imagename", first_column)
            df.insert(1, "imagenumber", second_column)
            df.to_csv(file_p, encoding="utf-8", header="true", index=False)

        p.close()

        if show_all_figures:
            plt.show()
        else:
            for fig in figs:
                plt.close(fig)
            if platform.system() == "Darwin":  # macOS
                subprocess.call(("open", filepath))
            elif platform.system() == "Windows":  # Windows
                os.startfile(filepath)
            else:  # linux variants
                subprocess.call(("xdg-open", filepath))


def filter(
    images: NPSAM | NPSAMImage,
    cmap: str = "default",
    alpha: float = 0.3,
    app: bool = False,
    position: Optional[Sequence[float]] = None,
) -> None:
    """
    Runs an interactive filtering window to filter masks based on selected
    characteristcs for one or more images.
    Parameters:
        images (NPSAM | NPSAMImage): The image or images to be filtered. Can be a single
        NPSAMImage or an NPSAM collection.
        cmap (str, optional): The colormap to use for displaying images. Defaults to
        "default" (viridis).
        alpha (float, optional): The transparency level for mask overlays in the GUI.
        Defaults to 0.3.
        app (bool, optional): If True, runs the GUI as a standalone application. If
        False, attempts to set the matplotlib backend for interactive use. This is
        usually true when called by the NP-SAM Windows applicaltion. Defaults to False.
        position (Sequence[float], optional): The initial position or coordinates for
        the GUI window or filter. Uses the Matplotlib figure position argument, e.g.
        [left, bottom, width, height].
        Defaults to None.
    Notes:
        - If `app` is False, the function attempts to set the matplotlib backend to 'qt'
          for interactive plotting.
        - Launches an interactive filter GUI for the provided images.
    """
    if not app:
        original_backend = matplotlib.get_backend()
        if original_backend != "QtAgg":
            try:
                # matplotlib.use("QtAgg") # For some reason this doesn't work
                get_ipython().magic("matplotlib qt")
                print("Matplotlib backend was set to 'qt'.")
            except Exception:
                print("Could not set matplotlib backend to 'qt'.")

    images = NPSAM(images) if not isinstance(images, NPSAM) else images
    filtergui = ImageFilter(images, app=app, position=position, cmap=cmap, alpha=alpha)
    filtergui.filter()


class ImageFilter:
    def __init__(
        self,
        images: NPSAM | NPSAMImage,
        cmap: str = "default",
        alpha: float = 0.3,
        app: bool = False,
        position: Optional[Sequence[float]] = None,
    ) -> None:
        """
        Initialize the NP-SAM interactive mask filtering GUI.
        Parameters
        ----------
        images : NPSAM or NPSAMImage
            The segmented image(s) to be filtered. If not an instance of NPSAM, it will
            be converted.
        cmap : str, optional
            The colormap to use for visualization of masks. Default is "default"
            (viridis).
        alpha : float, optional
            The alpha value for mask overlays. Default is 0.3.
        app : bool, optional
            If True, sets the matplotlib backend to "tkagg". This is done when using the
            Windows application. Default is False.
        position : Sequence[float], optional
            The initial position for the filtering GUI. Uses the Matplotlib figure
            position argument, e.g. [left, bottom, width, height]. Default is None.
        Returns
        -------
        None
        Notes
        -----
        Initializes various attributes related to visualization, filtering, and UI
        elements.
        """
        # Set all kinds of variables
        self.images = NPSAM(images) if not isinstance(images, NPSAM) else images
        self.image_index = 0
        self.app = app
        if self.app is True:
            matplotlib.use("tkagg")
        self.position = position
        self.cmap = cmap
        self.alpha = alpha
        self.buttons = {}
        self.overlapping_masks_dict = {"0": 0, "1": 1, "2": 2, "∞": np.inf}
        self.pressed_keys = set()
        self.slider_color = "#65B6F3"
        self.radio_color = "#387FBE"
        self.fig = None
        self.sliders = {}
        self.val_text = {}

        self.directory = Path(__file__).resolve().parent / "button_images"
        self.characteristics_for_filtering = [
            "area",
            "solidity",
            "intensity_mean",
            "eccentricity",
            "overlap",
        ]
        self.characteristics_format = {
            "area": "Area (px)",
            "solidity": "Solidity",
            "intensity_mean": "Intensity",
            "eccentricity": "Eccentricity",
            "overlap": "Overlap",
        }

    def apply_filters(self) -> None:
        """
        Apply a series of filters to the 'cha' DataFrame based on conditions chosen with
        the interactive slider, etc.
        The method updates the 'passed_filter' column in the 'cha' DataFrame, marking
        each row as True if the mask satisfies all the chosen criteria.
        After applying the filters, the method calls 'plot_filtered_masks()' to
        visualize the results.
        Returns:
            None
        """
        self.cha["passed_filter"] = (
            (self.cha["area"] >= self.conditions.get_item("area")[0])
            & (self.cha["area"] <= self.conditions.get_item("area")[1])
            & (self.cha["solidity"] >= self.conditions.get_item("solidity")[0])
            & (self.cha["solidity"] <= self.conditions.get_item("solidity")[1])
            & (
                self.cha["intensity_mean"]
                >= self.conditions.get_item("intensity_mean")[0]
            )
            & (
                self.cha["intensity_mean"]
                <= self.conditions.get_item("intensity_mean")[1]
            )
            & (self.cha["eccentricity"] >= self.conditions.get_item("eccentricity")[0])
            & (self.cha["eccentricity"] <= self.conditions.get_item("eccentricity")[1])
            & (self.cha["overlap"] >= self.conditions.get_item("overlap")[0])
            & (self.cha["overlap"] <= self.conditions.get_item("overlap")[1])
            & (~self.cha["mask_index"].isin(self.conditions.get_item("removed_index")))
            & (
                self.cha["number_of_overlapping_masks"]
                <= self.conditions.get_item("number_of_overlapping_masks")
            )
        )
        self.plot_filtered_masks()

    def plot_filtered_masks(self) -> None:
        """
        Updates the visibility of mask contours based on filtering conditions and
        updates the status text.
        Iterates over the 'passed_filter' column in the 'cha' DataFrame, setting the
        visibility of each corresponding mask in 'cs' accordingly. Also updates the
        'text' attribute to display the number of masks removed and the number remaining
        after filtering.
        Returns:
            None
        """
        for n, visibility in enumerate(self.cha["passed_filter"]):
            self.cs[n].set_visible(visibility)
        self.text.set_text(
            f"{(~self.cha['passed_filter']).sum()} masks removed. {self.cha['passed_filter'].sum()} remain."
        )

    def create_button(
        self,
        x: float,
        y: float,
        w: float,
        h: float,
        default_img_path: str,
        hover_img_path: str,
        click_action: Callable,
        rotate=False,
    ) -> plt.Axes:
        """
        Creates a custom button on a matplotlib figure using image files for default and
        hover states.
        Parameters
        ----------
        x : float
            The x-position of the button in figure coordinates (0 to 1).
        y : float
            The y-position of the button in figure coordinates (0 to 1).
        w : float
            The width of the button in figure coordinates (0 to 1).
        h : float
            The height of the button in figure coordinates (0 to 1).
        default_img_path : str
            Path to the image file used for the button's default appearance.
        hover_img_path : str
            Path to the image file used for the button's hover appearance.
        click_action : Callable
            Function to be called when the button is clicked.
        rotate : bool, optional
            If True, rotates the button images by flipping them vertically and
            horizontally. Default is False.
        Returns
        -------
        plt.Axes
            The matplotlib Axes object containing the button.
        Notes
        -----
        The button is added to the figure and responds to mouse click events by calling
        the provided `click_action`.
        The button's appearance changes on hover using the specified images.
        """
        ax = plt.axes([x, y, w, h], frameon=False)
        ax.set_axis_off()

        default_img = matplotlib.image.imread(self.directory / default_img_path)
        hover_img = matplotlib.image.imread(self.directory / hover_img_path)
        if rotate:
            default_img = np.flipud(np.fliplr(default_img))
            hover_img = np.flipud(np.fliplr(hover_img))

        img_display = ax.imshow(default_img)

        self.buttons[ax] = {
            "default": default_img,
            "hover": hover_img,
            "display": img_display,
        }
        ax.figure.canvas.mpl_connect(
            "button_press_event",
            lambda event: self.on_button_click(event, ax, click_action),
        )
        return ax

    def on_hover(
        self,
        event: matplotlib.backend_bases.Event,
    ) -> None:
        """
        Handles hover events over interactive axes, updating button images accordingly.
        When the mouse hovers over an axis associated with a button, this method updates
        the displayed image to the "hover" state. When the mouse leaves the axis, it
        reverts the image to the "default" state. Redraws the figure canvas if any
        updates are made.
        Args:
            event (matplotlib.backend_bases.Event): The matplotlib event object
            containing information about the mouse movement, including the axes
            currently hovered.
        Returns:
            None
        """
        redraw_required = False
        for ax, img_info in self.buttons.items():
            if ax.get_visible():
                if event.inaxes == ax:
                    if not np.array_equal(
                        img_info["display"].get_array(), img_info["hover"]
                    ):
                        img_info["display"].set_data(img_info["hover"])
                        ax.draw_artist(img_info["display"])
                        redraw_required = True
                elif not np.array_equal(
                    img_info["display"].get_array(), img_info["default"]
                ):
                    img_info["display"].set_data(img_info["default"])
                    ax.draw_artist(img_info["display"])
                    redraw_required = True
        if redraw_required:
            try:
                self.fig.canvas.update()
            except AttributeError:
                self.fig.canvas.draw_idle()

    def on_button_click(
        self,
        event: matplotlib.backend_bases.Event,
        ax: plt.Axes,
        action: Callable,
    ) -> None:
        """
        Handles a button click event within a specified matplotlib Axes.
        Parameters:
            event (matplotlib.backend_bases.Event): The matplotlib event object
            triggered by the button click.
            ax (plt.Axes): The Axes instance to check if the event occurred within.
            action (Callable): The function to execute if the event occurred within the
            specified Axes.
        Returns:
            None
        """
        if event.inaxes == ax:
            action()

    def on_key_press(
        self,
        event: matplotlib.backend_bases.Event,
    ) -> None:
        """
        Handles key press events for interactive slider and navigation controls.
        This method updates the value of a slider or triggers navigation and undo/redo
        actions based on the key pressed by the user. The step size for slider
        adjustment can be modified by holding down the Shift or Ctrl keys.
        Parameters
        ----------
        event : matplotlib.backend_bases.Event
            The key press event containing information about the pressed key.
        Key Bindings
        ------------
        - Arrow keys (up, down, left, right): Adjust the slider values.
            - Shift: Increase adjustment step to 1% of slider range.
            - Ctrl: Increase adjustment step to 10% of slider range.
            - No modifier: Default adjustment step is 0.1% of slider range.
        - 'z': Restore the last removed item.
        - 'a': Restore all removed items.
        - 'enter': Move to the next image or perform final save if at the last image.
        - 'backspace': Move to the previous image if not at the first image.
        Returns
        -------
        None
        """
        slider = self.last_interacted_slider
        low, high = slider.val
        self.pressed_keys.add(event.key)

        step = 0.001 * (slider.valmax - slider.valmin)
        if "shift" in self.pressed_keys:
            step = 0.01 * (slider.valmax - slider.valmin)
        elif ("ctrl" in self.pressed_keys) or ("control" in self.pressed_keys):
            step = 0.1 * (slider.valmax - slider.valmin)

        if event.key in {"up", "shift+up", "ctrl+up"}:
            val = (low + step, high)
            slider.set_val(val)
        elif event.key in {"down", "shift+down", "ctrl+down"}:
            val = (low - step, high)
            slider.set_val(val)
        elif event.key in {"right", "shift+right", "ctrl+right"}:
            val = (low, high + step)
            slider.set_val(val)
        elif event.key in {"left", "shift+left", "ctrl+left"}:
            val = (low, high - step)
            slider.set_val(val)

        if event.key == "z":
            self.return_last_removed()
        elif event.key == "a":
            self.return_all_removed()
        elif event.key == "enter":
            if self.image_index < len(self.filepaths) - 1:
                self.update_next()
            else:
                self.final_save()
        elif event.key == "backspace":
            if self.image_index != 0:
                self.update_previous()

    def on_key_release(
        self,
        event: matplotlib.backend_bases.Event,
    ) -> None:
        """
        Handles the key release event by removing the released key from the set of
        currently pressed keys.
        Parameters
        ----------
        event : matplotlib.backend_bases.Event
            The key release event containing information about the released key.
        Returns
        -------
        None
        """
        if event.key in self.pressed_keys:
            self.pressed_keys.remove(event.key)

    def on_click(
        self,
        event: matplotlib.backend_bases.Event,
    ) -> None:
        """
        Handles mouse click events on the axes with filtered mask to remove clicked
        masks. When the user clicks within the `ax_filtered` axes, this method checks if
        the click occurred within the bounding box of any filtered item. If so, it
        appends the index of the selected item to the "removed_index" condition, applies
        the filters, and updates the figure.
        Args:
            event (matplotlib.backend_bases.Event): The mouse click event containing
            information about the click, including the axes and coordinates.
        Returns:
            None
        """
        if event.inaxes == self.ax_filtered:
            for idx, row in self.cha[self.cha["passed_filter"]].iterrows():
                if (
                    row["bbox-1"] <= event.xdata <= row["bbox-3"]
                    and row["bbox-0"] <= event.ydata <= row["bbox-2"]
                ):
                    self.conditions.get_item("removed_index").append(idx)
                    self.apply_filters()
                    self.fig.canvas.draw()
                    break

    def return_all_removed(self) -> None:
        """
        Resets the 'removed_index' condition to an empty list, reapplies filters, and
        updates the figure canvas.
        This method is typically used to restore all previously removed items by
        clearing the 'removed_index' filter, reapplying any active filters, and
        redrawing the associated figure to reflect the changes.
        """
        self.conditions.set_item("removed_index", [])
        self.apply_filters()
        self.fig.canvas.draw()

    def return_last_removed(self) -> None:
        """
        Restores the last removed item by popping the most recent index from the
        'removed_index' list in conditions, reapplying filters, and updating the figure
        canvas.
        If there are no removed indices to restore, the method does nothing.
        Raises:
            None explicitly. IndexError is caught and ignored if 'removed_index' is
            empty.
        """

        try:
            self.conditions.get_item("removed_index").pop()
            self.apply_filters()
            self.fig.canvas.draw()
        except IndexError:
            pass

    def final_save(self) -> None:
        """
        Applies filters to the current data and closes the associated matplotlib figure.
        This method first applies any defined filters to the data by calling
        `apply_filters()`, and then closes the GUI window.
        Returns:
            None
        """
        self.apply_filters()
        plt.close(self.fig)

    def update_next(self) -> None:
        """
        Advances to the next image, applies filters, updates the image index,
        stores the current window position, and applies additional filtering.
        This method performs the following steps:
        1. Applies any set filters to the current image or dataset.
        2. Increments the image index to point to the next image.
        3. Retrieves and stores the current window geometry/position,
           handling differences depending on the application context.
        4. Applies further filtering operations as needed.
        Attributes used:
            self.app: Determines the application context for window geometry retrieval.
            self.fig: The figure object whose window geometry is accessed.
            self.image_index: The current index of the image being processed.
            self.position: Stores the window geometry.
        """
        self.apply_filters()

        self.image_index += 1

        if self.app:
            self.position = self.fig.canvas.manager.window.wm_geometry()
        else:
            self.position = self.fig.canvas.manager.window.geometry()

        self.filter()

    def update_previous(self) -> None:
        """
        Goes back to the previous image, applies filters, updates the image index,
        stores the current window position, and applies additional filtering.
        This method performs the following steps:
        1. Applies any set filters to the current image or dataset.
        2. Decreases the image index to point to the previous image.
        3. Retrieves and stores the current window geometry/position,
           handling differences depending on the application context.
        4. Applies further filtering operations as needed.
        Attributes used:
            self.app: Determines the application context for window geometry retrieval.
            self.fig: The figure object whose window geometry is accessed.
            self.image_index: The current index of the image being processed.
            self.position: Stores the window geometry.
        """
        self.apply_filters()

        self.image_index -= 1

        if self.app:
            self.position = self.fig.canvas.manager.window.wm_geometry()
        else:
            self.position = self.fig.canvas.manager.window.geometry()

        self.filter()

    def create_slider(
        self,
        characteristic: str,
    ) -> None:
        """
        Creates and configures a RangeSlider widget for a given characteristic.
        This method initializes a RangeSlider on the specified axes for the provided
        characteristic, sets its minimum and maximum values based on the data, and
        initializes its value from the current conditions. It also sets up a callback
        to update the slider when its value changes, hides the default value text,
        and adds a custom text label above the slider displaying the current range.
        Args:
            characteristic (str): The name of the characteristic for which to create the
            slider.
        Returns:
            None
        """
        ax = self.slider_axes[characteristic]

        slider = RangeSlider(
            ax,
            "",
            valmin=self.cha[characteristic].min(),
            valmax=self.cha[characteristic].max(),
            valinit=self.conditions.get_item(characteristic),
        )
        slider.on_changed(lambda val: self.update_slider(val, characteristic))
        slider.valtext.set_visible(False)
        self.sliders[characteristic] = slider

        self.val_text[characteristic] = ax.text(
            0,
            1.12,
            f"{self.characteristics_format[characteristic]}: ({self.conditions.get_item(characteristic)[0]:.5g}, {self.conditions.get_item(characteristic)[1]:.5g})",
            fontsize=14,
            ha="left",
            va="center",
            transform=ax.transAxes,
        )

    def update_slider(
        self,
        val: tuple[float, float],
        characteristic: str,
    ) -> None:
        """
        Updates the slider value and associated UI elements for a given characteristic.
        Parameters:
            val (Tuple[float, float]): The new value range selected by the slider.
            characteristic (str): The name of the characteristic associated with the
            slider.
        Side Effects:
            - Updates the last interacted slider.
            - Sets the new value for the characteristic in the conditions.
            - Updates the displayed text for the slider value.
            - Applies filters based on the updated conditions.
        """
        self.last_interacted_slider = self.sliders[characteristic]
        self.conditions.set_item(characteristic, val)

        self.val_text[characteristic].set_text(
            f"{self.characteristics_format[characteristic]}: ({self.conditions.get_item(characteristic)[0]:.5g}, {self.conditions.get_item(characteristic)[1]:.5g})",
        )

        self.apply_filters()

    def create_overlapping_masks_radio(
        self,
        ax: plt.Axes,
    ) -> None:
        """
        Creates and configures a set of radio buttons on the given matplotlib Axes to
        select the number of overlapping masks.
        The radio buttons allow the user to choose between 0, 1, 2, or an infinite
        number ("∞") of overlapping masks. The initial active button is determined by
        the value of 'number_of_overlapping_masks' from the conditions attribute. The
        method customizes the appearance and position of the radio buttons and their
        labels, and adds a descriptive text label to the Axes. It also sets up a
        callback to handle changes in the selected radio button.
        Parameters
        ----------
        ax : matplotlib.axes.Axes
            The matplotlib Axes object on which to draw the radio buttons and label.
        Returns
        -------
        None
        """
        ax.set_aspect("equal")
        valinit = self.conditions.get_item("number_of_overlapping_masks")
        if isinstance(valinit, str) or valinit > 2:
            valinit = 3
        self.radio_overlapping_masks = RadioButtons(
            ax,
            ("0", "1", "2", "∞"),
            active=valinit,
            activecolor=self.radio_color,
        )

        dists = [0, 0.12, 0.2245, 0.325]
        for i, (circle, radio_label) in enumerate(
            zip(
                self.radio_overlapping_masks.circles,
                self.radio_overlapping_masks.labels,
            )
        ):
            new_x = 0.53 + dists[i]
            new_y = 0.5
            circle.set_center((new_x, new_y))
            circle.set_radius(0.02)
            radio_label.set_position((new_x + 0.03, new_y))
            radio_label.set_fontsize(14)

        self.overlapping_masks_val_text = ax.text(
            0,
            0.5,
            "Number of \noverlapping masks:",
            fontsize=14,
            ha="left",
            va="center",
            transform=ax.transAxes,
        )

        self.radio_overlapping_masks.on_clicked(self.update_overlapping_masks)

    def update_overlapping_masks(
        self,
        label: str,
    ) -> None:
        """
        Updates the number of overlapping masks to the chosen radio button
        ("0", "1", "2" or "∞") and applies the filtering conditions.
        This method sets the "number_of_overlapping_masks" condition based on the value
        associated with the provided label in the `overlapping_masks_dict`. It then
        applies any relevant filters and redraws the figure canvas to reflect the
        changes.
        Args:
            label (str): The label for which to update the overlapping masks count.
        Returns:
            None
        """
        self.conditions.set_item(
            "number_of_overlapping_masks", self.overlapping_masks_dict[label]
        )
        self.apply_filters()
        self.fig.canvas.draw()

    def initiate_filter_values(self) -> None:
        """
        Initializes default filter values in the segmentation metadata.
        For each characteristic specified in `self.characteristics_for_filtering`, this
        method checks if a corresponding filter condition exists in the segmentation
        metadata. If not, it sets the filter condition to the minimum and maximum
        values of that characteristic.
        Additionally, it ensures that default values are set for:
          - "number_of_overlapping_masks" (set to infinity if not present)
          - "removed_index" (set to an empty list if not present)
        Finally, it updates `self.conditions` with the current filtering conditions from
        the segmentation metadata.
        """
        for characteristic in self.characteristics_for_filtering:
            if not self.seg.metadata.has_item(f"Filtering.Conditions.{characteristic}"):
                self.seg.metadata.set_item(
                    f"Filtering.Conditions.{characteristic}",
                    (self.cha[characteristic].min(), self.cha[characteristic].max()),
                )
        if not self.seg.metadata.has_item(
            "Filtering.Conditions.number_of_overlapping_masks"
        ):
            self.seg.metadata.set_item(
                "Filtering.Conditions.number_of_overlapping_masks", np.inf
            )
        if not self.seg.metadata.has_item("Filtering.Conditions.removed_index"):
            self.seg.metadata.set_item("Filtering.Conditions.removed_index", [])
        self.conditions = self.seg.metadata.get_item("Filtering.Conditions")

    def create_figure(self) -> None:
        """
        Creates and configures the main matplotlib figure and its axes for the
        filtering GUI.
        This method initializes the figure layout, including image display axes, slider
        axes for filtering, radio buttons, and various control buttons (save/close,
        next, previous, plus one, plus all).
        It also sets the window geometry depending on the application mode, adds a text
        area and a title, and connects relevant matplotlib events (keyboard and mouse)
        to their respective handlers.
        Side Effects:
            - Sets up self.fig and various axes and button attributes.
            - Connects event handlers for key and mouse events.
            - Displays the figure window.
        """
        self.fig = plt.figure(figsize=(8, 8))

        self.ax_img = plt.axes([0, 0.51, 0.5, 0.41])
        self.ax_all = plt.axes(
            [0.5, 0.51, 0.5, 0.41], sharex=self.ax_img, sharey=self.ax_img
        )
        self.ax_filtered = plt.axes(
            [0, 0.05, 0.5, 0.41], sharex=self.ax_img, sharey=self.ax_img
        )

        if self.app:
            self.fig.canvas.manager.window.wm_geometry(self.position)
        else:
            try:
                self.fig.canvas.manager.window.setGeometry(self.position)
            except Exception:
                pass

        # Create axes for sliders and radiobuttons
        self.slider_axes = {
            c: plt.axes(
                [0.525, 0.430 - n * 0.055, 0.45, 0.03], fc=self.slider_color, zorder=1
            )
            for n, c in enumerate(self.characteristics_for_filtering)
        }
        self.ax_radio_overlapping_masks = plt.axes(
            [0.525, -0.12, 0.5, 0.6], frameon=False
        )

        # Create buttons
        self.close_and_save_button = self.create_button(
            0.835,
            0.01,
            0.14,
            0.085,
            "Save_close.png",
            "Save_close_dark.png",
            self.final_save,
        )

        self.next_button = self.create_button(
            0.68, 0.01, 0.14, 0.085, "arrow.png", "arrow_dark.png", self.update_next
        )

        self.previous_button = self.create_button(
            0.525,
            0.01,
            0.14,
            0.085,
            "arrow.png",
            "arrow_dark.png",
            self.update_previous,
            rotate=True,
        )

        self.plus_one_button = self.create_button(
            0.1,
            0.0,
            0.10,
            0.05,
            "plus_one.png",
            "plus_one_dark.png",
            self.return_last_removed,
        )

        self.plus_all_button = self.create_button(
            0.3,
            0.0,
            0.10,
            0.05,
            "plus_all.png",
            "plus_all_dark.png",
            self.return_all_removed,
        )

        self.text = self.fig.text(
            0.752, 0.12, "", fontsize=16, horizontalalignment="center"
        )

        self.fig.suptitle("", fontsize=16)

        self.fig.canvas.mpl_connect("key_press_event", self.on_key_press)
        self.fig.canvas.mpl_connect("key_release_event", self.on_key_release)
        self.fig.canvas.mpl_connect("button_press_event", self.on_click)
        self.fig.canvas.mpl_connect("motion_notify_event", self.on_hover)

        self.fig.show()

    def filter(
        self,
        image_index: int = None,
    ) -> None:
        """
        Displays and updates the interactive filtering GUI for the selected image.
        This method sets up the visualization and interactive widgets (sliders, radio
        buttons, navigation buttons) for filtering masks based on their characteristics.
        It updates the figure with the current image, mask contours, and initializes or
        resets all relevant axes and controls.
        Parameters
        ----------
        image_index : int, optional
            Index of the image to display and filter. If None, uses the current image
            index.
        Returns
        -------
        None
        Side Effects
        ------------
        - Updates the current image and associated data.
        - Initializes or resets matplotlib figure and axes.
        - Creates or updates sliders and radio buttons for mask filtering.
        - Shows or hides navigation buttons based on the image index.
        - Applies current filter settings and redraws the figure.
        """
        if image_index is not None:
            self.image_index = image_index

        self.NPSAMImage = self.images[self.image_index]
        self.img = self.NPSAMImage.img
        self.seg = self.NPSAMImage.seg
        self.cha = self.NPSAMImage.cha
        self.contours = self.seg.metadata.Filtering.Contours.as_dictionary()
        self.initiate_filter_values()

        if self.fig is None:
            self.create_figure()
        self.fig.show()

        self.all_axes = (
            [self.ax_img, self.ax_all, self.ax_filtered]
            + [self.slider_axes[key] for key in self.slider_axes]
            + [self.ax_radio_overlapping_masks]
        )
        for ax in self.all_axes:
            ax.cla()

        string_title = (
            f"{self.image_index + 1}/{len(self.images)} - {self.img.metadata.General.title}"
            if len(self.images) > 1
            else self.img.metadata.General.title
        )
        self.fig.suptitle(string_title, fontsize=16)

        im_titles = ["Image", "All masks", "Filtered masks"]
        for ax, title in zip([self.ax_img, self.ax_all, self.ax_filtered], im_titles):
            ax.imshow(self.img.data, cmap="gray")
            ax.set_title(title)
            ax.axis("off")

        _ = plot_masks(self.NPSAMImage, self.ax_all, alpha=self.alpha, cmap=self.cmap)
        self.cs = plot_masks(
            self.NPSAMImage, self.ax_filtered, alpha=self.alpha, cmap=self.cmap
        )

        if self.cha["unit"][0] == "px":
            self.characteristics_format["area"] = "Area (px)"
        else:
            self.characteristics_format["area"] = f"Area ({self.cha['unit'][0]}$^2$)"
        # Create sliders
        for characteristic in self.characteristics_for_filtering:
            self.create_slider(characteristic)
        self.last_interacted_slider = self.sliders["area"]
        # Create radio buttons
        self.create_overlapping_masks_radio(self.ax_radio_overlapping_masks)

        if self.image_index < len(self.images) - 1:
            self.next_button.set_visible(True)
        else:
            self.next_button.set_visible(False)
        if self.image_index != 0:
            self.previous_button.set_visible(True)
        else:
            self.previous_button.set_visible(False)

        self.apply_filters()
        self.fig.canvas.draw()


def filter_nogui(
    images: NPSAMImage | NPSAM,
    conditions: Sequence[dict[str, Sequence[float | int] | int]]
    | dict[str, Sequence[float | int] | int],
) -> None:
    """
    Filters the masks based on a set of conditions with respect to the mask
    characteristics, without opening an interactive window.

    Parameters
    ----------
    images : NPSAMImage | NPSAM
        The image(s) or collection of images to filter.
    conditions : dict or list of dict
        Dictionary or list of dictionaries specifying filter conditions. Each dictionary
        can have the following keys:
            - area: tuple (min, max)
            - intensity_mean: tuple (min, max)
            - eccentricity: tuple (min, max)
            - solidity: tuple (min, max)
            - overlap: tuple (min, max)
            - number_of_overlapping_masks: int (maximum allowed)
            - removed_index: list of mask indices to exclude

    Behavior
    --------
    - Updates the 'passed_filter' column in the characteristics DataFrame based on the
      conditions.
    - Stores the filter conditions in the segmentation metadata.
    - If a list of conditions is provided, each entry is applied to the corresponding
      image.
    - If a single dictionary is provided, it is applied to all images.

    Raises
    ------
    ValueError
        If the list of conditions does not match the number of images, or if entries are
        not dictionaries.
    """
    images = NPSAM(images) if not isinstance(images, NPSAM) else images

    if isinstance(conditions, dict):
        conditions = [conditions] * len(images)
        if len(images) > 1:
            print("The filtering conditions will be used for all images.")
    elif isinstance(conditions, list):
        if len(conditions) == len(images):
            for entry in conditions:
                if not isinstance(entry, dict):
                    raise ValueError(
                        (
                            "The list entries must be dictionaries containing the filter ",
                            "conditions.",
                        )
                    )
        elif len(conditions) == 1:
            conditions = conditions * len(images)
            print("The filtering conditions will be used for all images.")
        else:
            raise ValueError(
                (
                    "The length of the list with filtering conditions does not have the ",
                    "same length as the list with images.",
                )
            )

    for image, filter_conditions in zip(images, conditions):
        cha = image.cha
        filters = {
            "area": (math.floor(cha["area"].min()), math.ceil(cha["area"].max())),
            "solidity": (0, 1),
            "intensity_mean": (
                math.floor(cha["intensity_mean"].min()),
                math.ceil(cha["intensity_mean"].max()),
            ),
            "eccentricity": (0, 1),
            "overlap": (0, np.inf),
            "number_of_overlapping_masks": np.inf,
            "removed_index": [],
        }

        filters.update(filter_conditions)

        cha["passed_filter"] = (
            (cha["area"] >= filters["area"][0])
            & (cha["area"] <= filters["area"][1])
            & (cha["solidity"] >= filters["solidity"][0])
            & (cha["solidity"] <= filters["solidity"][1])
            & (cha["intensity_mean"] >= filters["intensity_mean"][0])
            & (cha["intensity_mean"] <= filters["intensity_mean"][1])
            & (cha["eccentricity"] >= filters["eccentricity"][0])
            & (cha["eccentricity"] <= filters["eccentricity"][1])
            & (cha["overlap"] >= filters["overlap"][0])
            & (cha["overlap"] <= filters["overlap"][1])
            & (
                cha["number_of_overlapping_masks"]
                <= filters["number_of_overlapping_masks"]
            )
            & (~cha["mask_index"].isin(filters["removed_index"]))
        )

        image.seg.metadata.set_item("Filtering.Conditions", filters)

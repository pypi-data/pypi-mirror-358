from __future__ import annotations
from pydantic import BaseModel, ConfigDict
from annotated_types import Union, Gt, Ge, Lt, Le, Len, MinLen, MaxLen
from typing import Annotated, Sequence, Literal, TypeAlias
import json
import numpy as np
import base64
import os.path
from swanplot.cname import cname, pname, pythontocss
from PIL import Image
import io


class Model(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        validate_default=True,
        validate_assignment=True,
        use_attribute_docstrings=True,
    )


class ColorScheme(Model):
    colors: Annotated[Sequence[cname], MinLen(2)] = ["black", "white"]
    positions: Annotated[Sequence[Annotated[float, Ge(0), Le(1)]], Len(len(colors))] = [
        0,
        1,
    ]


class Fig(Model):
    compact: bool = False
    t_unit: str = ""
    x_unit: str = ""
    y_unit: str = ""
    c_unit: str = ""
    t_axis: Sequence[float] | None = None
    x_axis: Sequence[float] | None = None
    y_axis: Sequence[float] | None = None
    max_intensity: float | None = None
    min_intensity: float | None = None
    x_bins: int | None = None
    y_bins: int | None = None
    max_points: int | None = None
    width: int | None = None
    height: int | None = None
    margin: int = 40
    timesteps: int = 1
    x_label: str = ""
    y_label: str = ""
    t_label: str = ""
    c_label: str = ""
    loop: bool = False


ColorStrings: TypeAlias = Annotated[Sequence[cname | pname], MinLen(2)]
"""
Type alias for a sequence of color strings used in colormap (cmap) inputs.

This type allows for CSS color names and Python single-letter color names. 
The sequence must contain at least two color strings to ensure proper color mapping.
"""

IntensityValues: TypeAlias = Annotated[
    Sequence[Annotated[float, Ge(0), Le(1)]], MinLen(2)
]
"""
Type alias for a sequence of intensity values for colormap (cmap) inputs.

This type permits float values within the closed interval [0, 1]. 
The sequence must contain at least two float values to define positions effectively.
"""

GraphTypes: TypeAlias = Literal["2dhistogram"]
"""
Type alias for specifying the type of graphical representation.

Currently, this type supports only the "2dhistogram" representation.
"""

DataAxes: TypeAlias = Union[Literal["t", "x", "y", "c"], Literal[0, 1, 2, 3]]
"""
Type alias for specifying data cube axes.

This type allows the use of axis identifiers as either string labels ("t", "x", "y", "c") 
or numeric indices (0, 1, 2, 3) to represent the respective axes in a data cube.
"""

StringInput: TypeAlias = str | Annotated[Sequence[str], MaxLen(4)]
"""
Type alias for input strings in the set_label function.

This type allows for either a single string or a sequence of strings, 
with the latter being limited to a maximum length of 4 strings. 
This ensures concise labeling while accommodating multiple labels if needed.
"""

AxesInput: TypeAlias = DataAxes | Annotated[Sequence[DataAxes], MaxLen(4)]
"""
Type alias for specifying axes in the set_label function.

This type allows for a single axis, defined by the DataAxes type alias, 
or a sequence of axes, with the sequence limited to a maximum length of 4. 
This provides flexibility in labeling while maintaining a manageable number of axes.
"""


class Graph(Model):
    color_scheme: ColorScheme = ColorScheme()
    """
        
    """
    type: GraphTypes | None = None
    """
        
    """
    data: str | None = None
    """
        
    """
    options: Fig = Fig()
    """
        
    """


class axes:
    """
    A class to represent axes for plotting data, including color schemes,
    data options, and methods for plotting and saving figures.
    """

    def __init__(self):
        self.graph = Graph()

    def _plot(
        self,
        a: np.ndarray,
    ):
        """
        Plot the data as frames.

        :param a: A 2D NumPy array where each column represents a point in
                  the format [timestep, x, y].
        """
        # pts = dict()
        # frames = list()
        # for i in range(a.shape[1]):
        #     t = float(a[0, i])
        #     x = float(a[1, i])
        #     y = float(a[2, i])
        #     if t in pts.keys():
        #         pts.update({float(t): [*pts[t], Point(x=x, y=y)]})
        #     else:
        #         pts.update({float(t): Point(x=x, y=y)})
        # print(pts)
        # for t in pts.keys():
        #     frames.append(Frame(timestep=t, pts=pts[t]))
        # self.graph.data = frames
        # self.graph.type = "frame"
        # return

    def hist(
        self,
        datacube: np.ndarray,
    ):
        """
        Create a histogram from the provided 3D image data.

        This method generates a TIFF image from the data and updates the
        figure options with intensity and axis information.

        :param datacube: A 3D NumPy array representing the image data, where
                         the first dimension corresponds to timesteps.
        """
        ims = list()
        for t in range(datacube.shape[0]):
            ims.append(Image.fromarray((datacube[t, ...]).astype(np.uint8), mode="L"))
        output = io.BytesIO()
        ims[0].save(output, "tiff", save_all=True, append_images=ims[1:])
        self.graph.data = base64.b64encode(output.getvalue()).decode("utf-8")
        extremes = np.array([i.getextrema() for i in ims])
        self.graph.options.max_intensity = int(extremes.max())
        self.graph.options.min_intensity = int(extremes.min())
        self.graph.options.compact = True
        if self.graph.options.t_axis == None:
            self.graph.uniform_ticks(start=0, end=datacube.shape[0] - 1, axis="t")
        self.graph.options.timesteps = datacube.shape[0]
        if self.graph.options.x_axis == None:
            self.graph.uniform_ticks(start=0, end=datacube.shape[1], axis="x")
        self.graph.options.x_bins = datacube.shape[1]
        if self.graph.options.y_axis == None:
            self.graph.uniform_ticks(start=0, end=datacube.shape[2], axis="y")
        self.graph.options.y_bins = datacube.shape[2]
        if self.graph.options.width == None:
            self.graph.options.width = (
                datacube.shape[1] + 2 * self.graph.options.margin
                if datacube.shape[1] >= 256
                else 256 + 2 * self.graph.options.margin
            )
        if self.graph.options.height == None:
            self.graph.options.height = (
                datacube.shape[2] + 2 * self.graph.options.margin
                if datacube.shape[2] >= 256
                else 256 + 2 * self.graph.options.margin
            )
        self.graph.type = "histogram"
        return

    def figsize(
        self,
        width: Annotated[int, Ge(256)],
        height: Annotated[int, Ge(256)],
        margin: Annotated[int, Ge(40)] | None = None,
    ):
        """
        Set the figure's dimensions and margin.

        If no margin is provided, and width and height are already set,
        the provided width and height are assumed to be the total width
        and total height of the figure.

        :param width: Width of the figure in pixels.
        :param height: Height of the figure in pixels.
        :param margin: Margin around the figure in pixels (optional).
        """
        if margin == None:
            if self.graph.options.width == None and self.graph.options.height == None:
                self.graph.options.width = width + 2 * self.graph.options.margin
                self.graph.options.height = height + 2 * self.graph.options.margin
            else:
                if width <= 296 or height <= 296:
                    raise Exception(
                        f"Total width or height is not large enough,{width},{height}"
                    )
                self.graph.options.width = width
                self.graph.options.height = height
        else:
            self.graph.options.width = width + 2 * margin
            self.graph.options.height = height + 2 * margin

    def set_unit(self, unit: str, axis: DataAxes):
        """
        Set the unit for the specified axis.

        This method updates the unit of measurement for the specified axis
        (time, x, y, or c) in the figure options.

        :param unit: The unit to set for the specified axis.
        :param axis: The axis for which to set the unit. Can be "t", "x", "y",
                     "c" or their corresponding integer values (0, 1, 2, 3).
        """
        match axis:
            case "t" | 0:
                self.graph.options.t_unit = unit
            case "x" | 1:
                self.graph.options.x_unit = unit
            case "y" | 2:
                self.graph.options.y_unit = unit
            case "c" | 3:
                self.graph.options.y_unit = unit

    def uniform_ticks(
        self,
        start: float,
        end: float,
        axis: DataAxes,
    ):
        """
        Generate and set uniform ticks for the specified axis.

        This method creates evenly spaced ticks between the specified start
        and end values for the given axis.

        :param start: The start value for the axis.
        :param end: The end value for the axis.
        :param axis: The axis for which to set the ticks. Can be "t", "x", "y",
                     "c" or their corresponding integer values (0, 1, 2, 3).
        :raises Exception: If the number of timesteps is not defined.
                           Set uniform ticks for the specified axis.
        """
        if self.graph.options.timesteps == None:
            raise Exception(
                f"Data has not been loaded and therefore ticks number cannot be verified"
            )
        input = np.linspace(start, end, self.graph.options.timesteps).tolist()
        match axis:
            case "t" | 0:
                self.graph.options.t_axis = input
            case "x" | 1:
                self.graph.options.x_axis = input
            case "y" | 2:
                self.graph.options.y_axis = input
            case "c" | 3:
                self.graph.options.c_axis = input

    def custom_ticks(self, input: Sequence[float], axis: DataAxes):
        """
        Set custom ticks for the specified axis.

        This method allows the user to define specific tick values for the
        given axis, ensuring the number of ticks matches the number of
        timesteps in the data.

        :param input: A sequence of float values representing the custom ticks.
        :param axis: The axis for which to set the custom ticks. Can be "t",
                     "x","y","c" or their corresponding integer values (0, 1, 2, 3).
        :raises Exception: If the number of timesteps is not defined or if the
                          length of provided ticks does not match the number of timesteps.
        """
        if self.graph.options.timesteps == None:
            raise Exception(
                f"Data has not been loaded and therefore ticks number cannot be verified"
            )
        if len(input) != self.graph.options.timesteps:
            raise Exception(
                f"The length of provided ticks is not the same as the number of timesteps in your data {self.graph.options.timesteps}"
            )
        match axis:
            case "t" | 0:
                self.graph.options.t_axis = input
            case "x" | 1:
                self.graph.options.x_axis = input
            case "y" | 2:
                self.graph.options.y_axis = input
            case "c" | 3:
                self.graph.options.c_axis = input

    def set_label(self, string: StringInput, axis: AxesInput):
        """
        Assign labels to the specified axis.

        This method updates the label for the specified axis (time, x, y, or c)
        in the figure options. It can handle both single strings and sequences
        of strings.

        :param string: The label(s) to set for the specified axis.
        :param axis: The axis for which to set the label. Can be "t", "x", "y",
                     "c" or their corresponding integer values (0, 1, 2, 3).
        :raises Exception: If the provided string and axis types do not match
                          or if their lengths are inconsistent.
        """
        if isinstance(string, Sequence) != isinstance(axis, Sequence):
            raise Exception("Provided a list and a single value for string and axis")
        if isinstance(string, Sequence) and isinstance(axis, Sequence):
            if len(string) != len(axis):
                raise Exception("Provided string and axis are not of the same length")
        input = [string] if isinstance(string, str) else string
        axes = [axis] if isinstance(axis, str) or isinstance(axis, int) else axis

        for a, b in zip(input, axes):
            match b:
                case "t" | 0:
                    self.graph.options.t_label = a
                case "x" | 1:
                    self.graph.options.x_label = a
                case "y" | 2:
                    self.graph.options.y_label = a

    def set_loop(self, loop: bool = True):
        """
        Configure whether the plot should loop.

        This method sets the looping behavior of the plot, allowing it to
        repeat indefinitely if desired.

        :param loop: If True, the plot will loop; otherwise, it will not.
        """
        self.graph.options.loop = loop

    def cmap(
        self,
        colors: ColorStrings,
        positions: IntensityValues,
    ):
        """
        Set the color map for the axes.

        This method defines the color scheme for the plot by specifying the
        colors and their corresponding positions in the color map.

        :param colors: A sequence of colors to use in the color scheme.
                       Can include color names or CSS color values.
        :param positions: A sequence of float values representing the positions
                          corresponding to the colors, ranging from 0 to 1.
        """
        output = list()
        for color in colors:
            if color in pname:
                output.append(pythontocss[color])
            else:
                output.append(color)
        self.graph.color_scheme = ColorScheme(colors=colors, positions=positions)
        return

    def savefig(
        self,
        fname: str,
        style: Literal["pretty", "compact"] = "compact",
        format: Literal["json", "tiff"] | None = None,
        force: bool = False,
        print_website: bool = True,
    ):
        """
        Save the figure to a specified file.

        This method allows the user to save the figure in either JSON or TIFF
        format, with options for output style and file extension verification.

        :param fname: The filename to save the figure to.
        :param style: The style of the output (pretty or compact).
        :param format: The format to save the figure in (currently supports json and tiff) defaults to json if no extension is filename is bare.
        :param force: If True, allows saving with a different file extension than the specified format.
        :param print_website: If True, prints a message with the upload link after saving.
        :raises Exception: If the specified format does not match the file extension and force is False.
        """
        ext = os.path.splitext(fname)[1]
        if ext == "" and format == None:
            input = "json"
        if ext != "" and format == None:
            if ext[1:] not in ["json", "tiff"] and not force:
                raise Exception("extension provided is not a supported extension")
            elif force:
                input = "json"
            else:
                input = ext[1:]
        input = ext[1:] if format == None else format
        fname = fname + "." + str(format) if ext == "" else fname

        if not force and ext != "." + input and ext != "":
            raise Exception(
                f"you choose the format {format} but your file extension is {ext}"
            )
        match input:
            case "tiff":
                with open(fname, "wb") as file:
                    file.write(base64.b64decode(self.graph.data))
            case "json":
                with open(fname, "w") as file:
                    indentation: int
                    match style:
                        case "pretty":
                            indentation = 4
                        case "compact":
                            indentation = 0
                    output = json.dumps(self.graph.model_dump(), indent=indentation)
                    file.write(output)
                    if print_website:
                        print(f"upload {fname} to https://animate.deno.dev")

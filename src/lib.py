"""General library with useful functions.

Author: Patrik Nemeth
Xlogin: xnemet04
School: Vysoke Uceni Technicke v Brne, Fakulta Informacnich Technologii
"""
import numpy as np
from PIL import Image, ImageDraw
import os

def vals2Grayscale(vals):
    """Redistribute (normalize) values in parameter `vals` to range of an 8 bit grayscale image.
    This method implicitly converts the `vals` datatype to a float32 for the calculations and
    returns an array of uint8.
    
    Parameters
    ----------
    vals : numpy_array
        An array of values.

    Returns
    -------
        An array of the same size as `vals` with its values normalized to range 0-255.
    """
    vals = np.float32(vals)
    vMin = np.amin(vals)
    vMax = np.amax(vals)
    return np.uint8((vals - vMin) * (255 / (vMax - vMin)))

def overlay(img, overlayImg, marker, fill=None, outline=None, offset=3):
    """Overlays markers over the input image `img`. The markers' position is determined by the image `overlayImg` -
    where `overlayImg` contains nonzero values, these positions will be used as positions for the markers.
    The type of marker `marker` determines the shape and color of the marker.
    
    Parameters
    ----------
    img : numpy_array
        The base image, onto which the markers will be placed.
    overlayImg : numpy_array
        An overlay image. The markers will be placed on positions where this image is nonzero.
    marker : str
        Specifies the marker type. May be of three values: "square", "circle" or "triangle".
    fill : str
        Specifies the color of the inside of the marker. Accepts rgb colors specified in a string in this format "rgb(x,y,z)",
        where the xyz values range from 0-255. If None, the fill is transparent.
    outline : str
        Specifies the color of the marker border. Accepts rgb colors specified in a string in this format "rgb(x,y,z)",
        where the xyz values range from 0-255.
    offset : int
        Specifies the distance of each corner of the marker from it's center - adjusts the size of the marker.

    Returns
    -------
        The overlaid image of the same size as `img` as a numpy array."""
    if not isinstance(marker, str):
        raise TypeError("The marker type must be specified by a string. See docstring for accepted values.")

    # prevent changing the originals by reference
    overlayImg = np.copy(overlayImg).astype(np.uint8)
    img = np.copy(img).astype(np.uint8)

    img = (img - np.amin(img)) * (255 / (np.amax(img) - np.amin(img))).astype(np.uint8)

    rows,cols = np.where(overlayImg)
    img = Image.fromarray(img)
    img = img.convert("RGB")
    draw = ImageDraw.Draw(img)

    if marker == "square":
        for x, y in zip(cols,rows):
            draw.rectangle([x-offset, y-offset, x+offset, y+offset], fill=fill, outline=outline)
    elif marker == "circle":
        for x, y in zip(cols,rows):
            draw.ellipse([x-offset, y-offset, x+offset, y+offset], fill=fill, outline=outline)
    elif marker == "triangle":
        for x, y in zip(cols,rows):
            draw.polygon([x, y-offset, x+offset, y+offset, x-offset, y+offset], fill=fill, outline=outline)
    else:
        raise ValueError("The specified marker type of the overlay is not recognised.")

    return np.asarray(img)

"""Module to recalculate the map with the current Gaussian Process model."""

import io
import logging
import os
import pickle
import shutil
import time
import zipfile

import geopandas as gpd
import numpy as np
import pandas as pd
import rasterio
import requests
from datasets import Dataset, DatasetDict, load_dataset
from huggingface_hub import hf_hub_download
from matplotlib import pyplot as plt
from rasterio.control import GroundControlPoint as GCP
from rasterio.crs import CRS
from rasterio.transform import from_gcps
from shapely.validation import make_valid
from tqdm import tqdm

from .map_based_model import MapBasedModel
from .utils.utils_data import get_points
from .utils.utils_models import fit_gpr_silent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


HERE = os.path.dirname(os.path.abspath(__file__))

# 180 degree meridian in epsg 3857
MERIDIAN = 20037508


class GPMap(MapBasedModel):
    def __init__(self, region="world", resolution=10, version="prod", visual: bool = False):
        """Initialize the GPMap object.

        Loading the latest map and model from Hugging Face.
        """
        logger.info("Initializing GPMap...")
        self.visual = visual

        self.cache_dir = f"{HERE}/cache"

        os.makedirs(f"{self.cache_dir}/hitchmap", exist_ok=True)
        self.points_path = f"{HERE}/cache/hitchmap/dump.sqlite"
        hitchmap_url = "https://hitchmap.com/dump.sqlite"
        try:
            response = requests.get(hitchmap_url)
            response.raise_for_status()  # Check for HTTP request errors
            with open(self.points_path, "wb") as file:
                file.write(response.content)
                logger.info(f"Downloaded Hitchmap data to: {self.points_path}")
        except Exception as e:
            logger.info(f"Failed to download Hitchmap data with {e}. Might be that on older version is still available.")

        if not os.path.isfile(self.points_path):
            raise FileNotFoundError(f"No Hitchmap data found at {self.points_path}.")

        if os.path.exists("models/kernel.pkl"):
            self.gpr_path = "models/kernel.pkl"
        else:
            REPO_ID = "Hitchwiki/heatchmap-models"
            FILENAME = "Unfitted_GaussianProcess_TransformedTargetRegressorWithUncertainty.pkl"
            self.gpr_path = hf_hub_download(repo_id=REPO_ID, filename=FILENAME)

        with open(self.gpr_path, "rb") as file:
            self.gpr = pickle.load(file)

        super().__init__(method=type(self.gpr).__name__, region=region, resolution=resolution, version=version, verbose=False)

        map_dataset_dict = load_dataset("Hitchwiki/hitchhiking-heatmap", cache_dir=f"{HERE}/cache/huggingface")
        # choosing the latest map; dataset splits correspond to maps until a certain date
        splits = list(map_dataset_dict.keys())
        if len(splits) == 0:
            logger.info("No map found in huggingface dataset. Recalculating whole map.")
            self.map_dataset = None
            self.raw_raster = None
            self.uncertainties = None
        else:
            # selecting the latest map
            split = splits[-1]
            logger.info(f"Loading map from {split}.")
            self.map_dataset = map_dataset_dict[split]
            self.map_dataset = self.map_dataset.with_format("np")
            self.raw_raster = self.map_dataset["waiting_times"] if "waiting_times" in self.map_dataset.column_names else None
            self.uncertainties = self.map_dataset["uncertainties"] if "uncertainties" in self.map_dataset.column_names else None
            if self.raw_raster is None:
                logger.info("No waiting times found in map.")
            if self.uncertainties is None:
                logger.info("No uncertainties found in map.")

        # set latest date to consider from the new records that will be used to recalculate the map
        # this is today, thus in the resulting map, all records until today will be covered
        # there is no problem if the acutal latest entry is from earlier than today
        self.last_record_time = pd.Timestamp.now()
        try:
            # set earliest date to consider from the new records that will be used to recalculate the map
            # overlaps with the last date of the previous map to not leave out any records from that day
            self.begin = pd.to_datetime(split, format="%Y.%m.%d")
            logger.info(f"Last map update was on {self.begin.date()}.")
        except Exception as e:
            raise Exception(f"No map update found with {e}. Check huggingface.") from e

        self.batch_size = 10000
        self.recalc_radius = 800000  # TODO: determine from model largest influence radius

        self.shapely_countries = f"{self.cache_dir}/countries/ne_110m_admin_0_countries.shp"
        if not os.path.exists(self.shapely_countries):
            output_dir = f"{self.cache_dir}/countries"
            os.makedirs(output_dir, exist_ok=True)
            # URL for the 110m countries shapefile from Natural Earth
            url = "https://naturalearth.s3.amazonaws.com/110m_cultural/ne_110m_admin_0_countries.zip"

            # Download the dataset
            logger.info("Downloading countries dataset...")
            response = requests.get(url)
            response.raise_for_status()  # Raise an error for bad responses

            # Extract the zip file
            logger.info("Extracting files...")
            with zipfile.ZipFile(io.BytesIO(response.content)) as z:
                z.extractall(output_dir)

            logger.info(f"Countries dataset downloaded and extracted to: {output_dir}")

        else:
            logger.info(f"Countries dataset already exists at: {self.shapely_countries}")
        
        logger.info("GPMap initialized successfully.")

    def recalc_map(self):
        """Recalculate the map with the current Gaussian Process model.

        Overrides the stored np.array raster of the map.
        """
        logger.info("Recalculating map...")
        # fit model to new data points
        self.points = get_points(self.points_path, until=self.last_record_time)
        self.points["lon"] = self.points.geometry.x
        self.points["lat"] = self.points.geometry.y

        X = self.points[["lon", "lat"]].values
        y = self.points["wait"].values

        # the model was optimized once and stored
        # now we only need to fit it to all data points once and can then use it to predicti the map
        self.gpr.regressor.optimizer = None
        # CAUTION: this part takes a lot of ram (>8 GB) as the full training dataset has to be loaded into RAM at once
        self.gpr = fit_gpr_silent(self.gpr, X, y)

        self.get_map_grid()
        self.get_recalc_raster()

        logger.info("Compute pixels that are expected to differ...")
        start = time.time()
        to_predict = []
        pixels_to_predict = []
        for x, vertical_line in tqdm(enumerate(self.grid.transpose()), total=len(self.grid.transpose())):
            for y, coords in enumerate(vertical_line):
                if self.recalc_raster[y][x] == 0:
                    continue
                this_point = [float(coords[0]), float(coords[1])]
                to_predict.append(this_point)
                pixels_to_predict.append((y, x))
                # batching the model calls
                if len(to_predict) == self.batch_size:
                    waiting_times, uncertainties = self.gpr.predict(np.array(to_predict), return_std=True)
                    for i, (y, x) in enumerate(pixels_to_predict):
                        self.raw_raster[y][x] = waiting_times[i]
                        self.uncertainties[y][x] = uncertainties[i]

                    # Skipping: because the re-entry point in case the run fails cannot be determined easily so far
                    # logger.info("Intermediate upload of map to Huggingface Hub.")
                    # self.upload()

                    to_predict = []
                    pixels_to_predict = []

        if len(to_predict) > 0:
            waiting_times, uncertainties = self.gpr.predict(np.array(to_predict), return_std=True)
            for i, (y, x) in enumerate(pixels_to_predict):
                self.raw_raster[y][x] = waiting_times[i]
                self.uncertainties[y][x] = uncertainties[i]

        logger.info(f"Time elapsed to compute full map: {time.time() - start}")
        logger.info(
            f"For map of shape: {self.raw_raster.shape} that is {self.raw_raster.shape[0] * self.raw_raster.shape[1]} pixels and "
            + f"an effective time per pixel of {(time.time() - start) / (self.raw_raster.shape[0] * self.raw_raster.shape[1])} "
            + "seconds"
        )
        logger.info(
            f"Only {self.recalc_raster.sum()} pixels were recalculated. "
            + f"That is {self.recalc_raster.sum() / (self.raw_raster.shape[0] * self.raw_raster.shape[1]) * 100}% "
            + "of the map."
        )
        if self.recalc_raster.sum() > 0:
            logger.info(f"And time per recalculated pixel was {(time.time() - start) / self.recalc_raster.sum()} seconds")

        logger.info("Map recalculation finished.")

    def show_raster(self, raster: np.array):
        """Show the raster in a plot.

        Args:
            raster (np.array): 2D np.array of the raster to be shown.

        """
        plt.imshow(raster, cmap="viridis", interpolation="nearest")
        plt.colorbar()
        plt.xlabel("Longitude")
        plt.ylabel("Latitude")
        plt.show()

    def pixel_from_point(self, point) -> tuple[int, int]:
        """For a given point by coordinates, determines the pixel in the raster that best corresponds to it."""
        lats = self.Y.transpose()[0]
        lat_index = None
        for i, lat in enumerate(lats):
            if lat >= point["lat"] and point["lat"] >= lats[i + 1]:
                lat_index = i
                break

        lons = self.X[0]
        lon_index = None
        for i, lon in enumerate(lons):
            if lon <= point["lon"] and point["lon"] <= lons[i + 1]:
                lon_index = i
                break

        result = (lat_index, lon_index)

        return result

    def get_recalc_raster(self):
        """Creats 2d np.array of raster where only pixels that are 1 should be recalculated."""
        logger.info("Creating raster of pixels to recalculate...")
        recalc_radius_pixels = int(np.ceil(abs(self.recalc_radius / (self.grid[0][0][0] - self.grid[0][0][1]))))
        self.get_landmass_raster()

        if self.raw_raster is None or self.uncertainties is None:
            logger.info("No map found. Recalculating whole map.")
            self.recalc_raster = np.ones(self.grid.shape[1:])
        else:
            logger.info("Recalculating only around new points.")
            self.recalc_raster = np.zeros(self.grid.shape[1:])

            new_points = get_points(self.points_path, begin=self.begin, until=self.last_record_time)
            new_points["lon"] = new_points.geometry.x
            new_points["lat"] = new_points.geometry.y
            self.latest_date = new_points["datetime"].max()
            logger.info(f"Recalculating map for {len(new_points)} new points from {self.begin.date()} to {self.last_record_time.date()}.")  # noqa: E501
            for i, point in new_points.iterrows():
                lat_pixel, lon_pixel = self.pixel_from_point(point)

                for i in range(lat_pixel - recalc_radius_pixels, lat_pixel + recalc_radius_pixels):
                    for j in range(lon_pixel - recalc_radius_pixels, lon_pixel + recalc_radius_pixels):
                        if i < 0 or j < 0 or i >= self.recalc_raster.shape[0] or j >= self.recalc_raster.shape[1]:
                            continue
                        self.recalc_raster[i, j] = 1

        self.show_raster(self.recalc_raster) if self.visual else None

        logger.info("Report reduction of rasters.")
        logger.info(
            f"{int(self.recalc_raster.sum())} out of {self.recalc_raster.shape[0] * self.recalc_raster.shape[1]} pixels "
            + "are around new points - that is "
            + f"{round(self.recalc_raster.sum() / (self.recalc_raster.shape[0] * self.recalc_raster.shape[1]), 2) * 100} %"
        )
        self.recalc_raster = self.recalc_raster * self.landmass_raster
        self.show_raster(self.recalc_raster) if self.visual else None
        logger.info(
            f"{int(self.landmass_raster.sum())} out of {self.landmass_raster.shape[0] * self.landmass_raster.shape[1]} "
            + "pixels are landmass - that is "
            + f"{round(self.landmass_raster.sum() / (self.landmass_raster.shape[0] * self.landmass_raster.shape[1]), 2) * 100} %"
        )
        logger.info(
            f"{int(self.recalc_raster.sum())} out of {self.recalc_raster.shape[0] * self.recalc_raster.shape[1]} pixels are "
            + "around new points- that is "
            + f"{round(self.recalc_raster.sum() / (self.recalc_raster.shape[0] * self.recalc_raster.shape[1]), 2) * 100} %"
        )

    def get_landmass_raster(self):
        """Creates raster of landmass as np.array"""
        logger.info("Creating raster of landmass...")
        self.landmass_raster = np.ones(self.grid.shape[1:])

        polygon_vertices_x, polygon_vertices_y, pixel_width, pixel_height = self.define_raster()

        # handling special case when map spans over the 180 degree meridian
        if polygon_vertices_x[0] > 0 and polygon_vertices_x[2] < 0:
            polygon_vertices_x[2] = 2 * MERIDIAN + polygon_vertices_x[2]
            polygon_vertices_x[3] = 2 * MERIDIAN + polygon_vertices_x[3]

        # https://gis.stackexchange.com/questions/425903/getting-rasterio-transform-affine-from-lat-and-long-array

        # lower/upper - left/right
        ll = (polygon_vertices_x[0], polygon_vertices_y[0])
        ul = (polygon_vertices_x[1], polygon_vertices_y[1])  # in lon, lat / x, y order
        ur = (polygon_vertices_x[2], polygon_vertices_y[2])
        lr = (polygon_vertices_x[3], polygon_vertices_y[3])
        cols, rows = pixel_width, pixel_height

        # ground control points
        gcps = [
            GCP(0, 0, *ul),
            GCP(0, cols, *ur),
            GCP(rows, 0, *ll),
            GCP(rows, cols, *lr),
        ]

        # seems to need the vertices of the map polygon
        transform = from_gcps(gcps)

        # cannot use np.float128 to write to tif
        self.landmass_raster = self.landmass_raster.astype(np.float64)

        # save the colored raster using the above transform
        # important: rasterio requires [0,0] of the raster to be in the upper left and [rows, cols] in the lower right corner
        # TODO find out why raster is getting smaller in x direction when stored as tif (e.g. 393x700 -> 425x700)
        with rasterio.open(
            self.landmass_path,
            "w",
            driver="GTiff",
            height=self.landmass_raster.shape[0],
            width=self.landmass_raster.shape[1],
            count=1,
            crs=CRS.from_epsg(3857),
            transform=transform,
            dtype=self.landmass_raster.dtype,
        ) as destination:
            destination.write(self.landmass_raster, 1)

        landmass_rasterio = rasterio.open(self.landmass_path)

        nodata = 0

        countries = gpd.read_file(self.shapely_countries)
        countries = countries.to_crs(epsg=3857)
        countries = countries[countries.NAME != "Antarctica"]
        country_shapes = countries.geometry
        country_shapes = country_shapes.apply(lambda x: make_valid(x))

        out_image, out_transform = rasterio.mask.mask(landmass_rasterio, country_shapes, nodata=nodata)

        self.landmass_raster = out_image[0]
        self.show_raster(self.landmass_raster) if self.visual else None

        # cleanup
        os.remove(self.landmass_path)
        logger.info("Landmass raster created successfully.")

    def upload(self, latest_timestamp_in_dataset: pd.Timestamp = None):
        """Uploads the recalculated map to the Hugging Face model hub.

        Clean cached files.
        """
        logger.info("Uploading map to Hugging Face dataset hub...")
        if latest_timestamp_in_dataset is None:
            latest_timestamp_in_dataset = self.last_record_time

        logger.info(f"Shape of uploading map: {self.raw_raster.shape}")
        data_dict = {"waiting_times": self.raw_raster, "uncertainties": self.uncertainties}
        dataset = Dataset.from_dict(data_dict)
        dataset = dataset.with_format("np")
        dataset_dict = DatasetDict({latest_timestamp_in_dataset.strftime("%Y.%m.%d"): dataset})

        dataset_dict.push_to_hub("Hitchwiki/hitchhiking-heatmap")
        logger.info("Successfully uploaded new map to Hugging Face dataset hub.")
    
    def cleanup(self):
        shutil.rmtree(self.cache_dir)

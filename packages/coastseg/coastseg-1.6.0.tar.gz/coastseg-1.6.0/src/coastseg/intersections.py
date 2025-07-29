import os
import geopandas as gpd
import pandas as pd
import numpy as np
import shapely
import warnings
from typing import List, Tuple
from shapely.geometry import LineString, MultiPoint, Point

# coastseg imports
from coastseg import file_utilities
from coastseg.common import get_transect_settings
from coastseg.common import convert_date_gdf, convert_points_to_linestrings
from shapely.geometry import Point

warnings.filterwarnings("ignore")


def add_classifier_scores_to_transects(session_path, good_bad_csv, good_bad_seg_csv):
    """Adds new columns to the geojson file with the model scores from the image_classification_results.csv and segmentation_classification_results.csv files

    Args:
        geojson_path (gpd.GeoDataFrame): A GeoDataFrame of extracted transects that contains the date column
        good_bad_csv (str): The path to the image_classification_results.csv file
        good_bad_seg_csv (str): The path to the segmentation_classification_results.csv file
    """

    def update_file_if_exists(filepath: str, update_function) -> None:
        if os.path.exists(filepath):
            update_function(filepath, good_bad_csv, good_bad_seg_csv)

    # Update time series CSV to include model scores
    csv_path = os.path.join(session_path, "raw_transect_time_series_merged.csv")
    update_file_if_exists(csv_path, file_utilities.join_model_scores_to_time_series)

    # Update GeoJSON vector and point files that contain the transect intersections with the extracted shorelines
    geojson_files = [
        os.path.join(session_path, "raw_transect_time_series_vectors.geojson"),
        os.path.join(session_path, "raw_transect_time_series_points.geojson"),
    ]

    for geojson_path in geojson_files:
        update_file_if_exists(
            geojson_path, file_utilities.join_model_scores_to_geodataframe
        )


def wgs84_to_utm_file(geojson_file):
    """
    Converts wgs84 to UTM
    inputs:
    geojson_file (path): path to a geojson in wgs84
    outputs:
    geojson_file_utm (path): path to a geojson in utm
    """

    geojson_file_utm = os.path.splitext(geojson_file)[0] + "_utm.geojson"

    gdf_wgs84 = gpd.read_file(geojson_file)
    utm_crs = gdf_wgs84.estimate_utm_crs()

    gdf_utm = gdf_wgs84.to_crs(utm_crs)
    gdf_utm.to_file(geojson_file_utm)
    return geojson_file_utm


def LineString_to_arr(line):
    """
    Makes an array from linestring
    inputs:
    line (shapely.geometry.LineString): shapely linestring
    outputs:
    coords (List[tuples]): list of x,y coordinate pairs
    """
    listarray = []
    for pp in line.coords:
        listarray.append(pp)
    nparray = np.array(listarray)
    return nparray


def arr_to_LineString(coords):
    """
    Makes a line feature from an array of xy tuples
    inputs:
    coords (List[tuples]): list of x,y coordinate pairs
    outputs:
    line (shapely.geometry.LineString): shapely linestring
    """
    points = [None] * len(coords)
    i = 0
    for xy in coords:
        points[i] = shapely.geometry.Point(xy)
        i = i + 1
    line = shapely.geometry.LineString(points)
    return line


def chaikins_corner_cutting(coords, refinements=3):
    """
    Smooths out lines or polygons with Chaikin's method
    inputs:
    coords (list of tuples): [(x1,y1), (x..,y..), (xn,yn)]
    outputs:
    coords (list of tuples): [(x1,y1), (x..,y..), (xn,yn)],
                              this is the smooth line
    """
    i = 0
    for _ in range(refinements):
        L = coords.repeat(2, axis=0)
        R = np.empty_like(L)
        R[0] = L[0]
        R[2::2] = L[1:-1:2]
        R[1:-1:2] = L[2::2]
        R[-1] = L[-1]
        coords = L * 0.75 + R * 0.25
        i = i + 1
    return coords


def smooth_lines(lines, refinements=2):
    """
    Smooths out shorelines with Chaikin's method
    Shorelines need to be in UTM (or another planar coordinate system)

    inputs:
    shorelines (gdf): gdf of extracted shorelines in UTM
    refinements (int): number of refinemnets for Chaikin's smoothing algorithm
    outputs:
    new_lines (gdf): gdf of smooth lines in UTM
    """
    lines = wgs84_to_utm_df(lines)
    lines["geometry"] = lines["geometry"]
    new_geometries = [None] * len(lines)
    new_lines = lines.copy()
    for i in range(len(new_lines)):
        simplify_param = new_lines["simplify_param"].iloc[i]
        line = new_lines.iloc[i]["geometry"]
        line = line.simplify(simplify_param)
        coords = LineString_to_arr(line)
        refined = chaikins_corner_cutting(coords, refinements=refinements)
        refined_geom = arr_to_LineString(refined)
        new_geometries[i] = refined_geom
    new_lines["geometry"] = new_geometries
    return new_lines


def explode_multilinestrings(gdf):
    """
    Explodes any MultiLineString objects in a GeoDataFrame into individual LineStrings,
    and returns a new GeoDataFrame with these LineStrings replacing the original MultiLineStrings.

    Parameters:
    gdf (GeoDataFrame): A GeoDataFrame containing various geometry types.

    Returns:
    GeoDataFrame: A new GeoDataFrame with MultiLineStrings exploded into LineStrings.
    """
    # Filter out MultiLineStrings
    multilinestrings = gdf[gdf["geometry"].type == "MultiLineString"]

    # Explode the MultiLineStrings, if any are present
    if not multilinestrings.empty:
        exploded_multilinestrings = multilinestrings.explode().reset_index(drop=True)

        # Remove original MultiLineStrings from the original DataFrame
        gdf = gdf[gdf["geometry"].type != "MultiLineString"]

        # Append exploded MultiLineStrings back to the original DataFrame
        final_gdf = pd.concat([gdf, exploded_multilinestrings], ignore_index=True)
    else:
        # No MultiLineStrings present, return original DataFrame unchanged
        final_gdf = gdf

    return final_gdf


def get_simplify_param(satname: str) -> Tuple[float, float]:
    """Returns distance threshold and simplify parameter based on satellite name."""
    sat_params = {
        "L5": (45, np.sqrt(30**2 * 3) / 2),
        "L7": (45, np.sqrt(30**2 * 3) / 2),
        "L8": (45, np.sqrt(30**2 * 3) / 2),
        "L9": (45, np.sqrt(30**2 * 3) / 2),
        "S2": (15, np.sqrt(10**2 * 3) / 2),
        "PS": (8, np.sqrt(5**2 * 3) / 2),
    }
    default_params = (30, np.sqrt(20**2 * 3) / 2)
    return sat_params.get(satname, default_params)


def break_line_at_distance(points: List[Point], threshold: float) -> List[List[Point]]:
    """Splits a list of points into chunks where the distance exceeds a threshold."""
    if len(points) < 2:
        return [points]

    segments = []
    current_segment = [points[0]]

    for i in range(1, len(points)):
        if points[i - 1].distance(points[i]) > threshold:
            segments.append(current_segment)
            current_segment = []
        current_segment.append(points[i])

    if current_segment:
        segments.append(current_segment)
    return segments


def create_geometries(segments: List[List[Point]], geom_type: str):
    """Creates LineStrings or MultiPoints from point chunks.

    Example:
        segments = [[Point(0, 0), Point(1, 1)], [Point(2, 2), Point(3, 3)]]
        create_geometries(segments, 'LineString')
        # Returns: [LineString([(0, 0), (1, 1)]), LineString([(2, 2), (3, 3)])]

    Args:
        segments: List of lists of Point objects, where each sublist represents a segment.
        geom_type: 'LineString' or 'MultiPoint'.

    """
    geometries = []
    for seg in segments:
        if len(seg) == 1:
            continue  # Skip single-point segments
        if geom_type == "linestring":
            geometries.append(LineString(seg))
        elif geom_type == "multipoint":
            geometries.append(MultiPoint(seg))
    return geometries


def split_line(
    extracted_shorelines_gdf: gpd.GeoDataFrame,
    geom_type: str,
    smooth: bool = True,
) -> gpd.GeoDataFrame:
    """
    Splits shoreline lines into multiple geometries based on distance thresholds.

    Args:
        extracted_shorelines_gdf: Input shoreline GeoDataFrame in EPSG:4326.
        geom_type: 'LineString' or 'MultiPoint'.
        smooth: Whether to apply line smoothing.

    Returns:
        GeoDataFrame with split and optionally smoothed geometries in EPSG:4326.
    """
    if geom_type.lower() not in {"linestring", "multipoint"}:
        raise ValueError("geom_type must be 'LineString' or 'MultiPoint'.")

    # Project to UTM
    gdf_utm = wgs84_to_utm_df(extracted_shorelines_gdf.copy())
    gdf_utm = explode_multilinestrings(gdf_utm)
    source_crs = gdf_utm.crs
    all_segments = []

    for _, row in gdf_utm.iterrows():
        satname = row.get("satname", "Unknown")
        dist_thresh, simplify_param = get_simplify_param(satname)
        line_geom = row.geometry

        if not isinstance(line_geom, LineString):
            continue

        coords = list(line_geom.coords)
        points = [Point(x, y) for x, y in coords]
        point_segments = break_line_at_distance(points, dist_thresh)
        geometries = create_geometries(point_segments, geom_type.lower())

        for geom in geometries:
            seg_data = row.drop(labels="geometry").to_dict()
            seg_data["geometry"] = geom
            seg_data["simplify_param"] = simplify_param
            all_segments.append(seg_data)

    # Create new GeoDataFrame
    result_gdf = gpd.GeoDataFrame(all_segments, crs=source_crs)
    result_gdf["date"] = pd.to_datetime(result_gdf["date"]).dt.tz_localize("UTC")

    if smooth:
        result_gdf = smooth_lines(result_gdf)

    return utm_to_wgs84_df(result_gdf)


def wgs84_to_utm_df(geo_df):
    """
    Converts gdf from wgs84 to UTM
    inputs:
    geo_df (geopandas dataframe): a geopandas dataframe in wgs84
    outputs:
    geo_df_utm (geopandas  dataframe): a geopandas dataframe in utm
    """
    utm_crs = geo_df.estimate_utm_crs()
    gdf_utm = geo_df.to_crs(utm_crs)
    return gdf_utm


def utm_to_wgs84_df(geo_df):
    """
    Converts gdf from utm to wgs84
    inputs:
    geo_df (geopandas dataframe): a geopandas dataframe in utm
    outputs:
    geo_df_wgs84 (geopandas  dataframe): a geopandas dataframe in wgs84
    """
    wgs84_crs = "epsg:4326"
    gdf_wgs84 = geo_df.to_crs(wgs84_crs)
    return gdf_wgs84


def cross_distance(start_x, start_y, end_x, end_y):
    """distance formula, sqrt((x_1-x_0)^2 + (y_1-y_0)^2)"""
    dist = np.sqrt((end_x - start_x) ** 2 + (end_y - start_y) ** 2)
    return dist


def transect_timeseries(
    shorelines_gdf,
    transects_gdf,
):
    """
    Generates timeseries of shoreline cross-shore position
    given a geojson/shapefile containing shorelines and a
    geojson/shapefile containing cross-shore transects.
    Computes interesection points between shorelines
    and transects. Saves the merged transect timeseries.

    inputs:
    shorelines_gdf (geopandas dataframe): geodataframe containing shorelines as Linestrings or multilinestrings in crs 4326
    transects_gdf (geopandas dataframe): geodataframe containing transects in crs 4326
    """

    # load transects, project to utm, get start x and y coords
    transects_gdf = wgs84_to_utm_df(transects_gdf)
    crs = transects_gdf.crs

    # if the transects only have an id column rename it to transect_id
    if (
        "id" in [col.lower() for col in transects_gdf.columns]
        and "transect_id" not in transects_gdf.columns
    ):
        id_column_name = [col for col in transects_gdf.columns if col.lower() == "id"][
            0
        ]
        transects_gdf = transects_gdf.rename(columns={id_column_name: "transect_id"})
    else:
        id_column_name = "transect_id"

    transects_gdf = transects_gdf.reset_index(drop=True)
    transects_gdf["geometry_saved"] = transects_gdf["geometry"]
    coords = transects_gdf["geometry_saved"].get_coordinates()
    coords = coords[~coords.index.duplicated(keep="first")]
    transects_gdf["x_start"] = coords["x"]
    transects_gdf["y_start"] = coords["y"]

    # load shorelines, project to utm, smooth
    shorelines_gdf = wgs84_to_utm_df(shorelines_gdf)

    # join all the shorelines that occured on the same date together
    shorelines_gdf = shorelines_gdf.dissolve(by="date")
    shorelines_gdf = shorelines_gdf.reset_index()

    # if the shorelines are multipoints convert them to linestrings because this function does not work well with multipoints
    if "MultiPoint" in [
        geom_type for geom_type in shorelines_gdf["geometry"].geom_type
    ]:
        shorelines_gdf = convert_points_to_linestrings(
            shorelines_gdf, group_col="date", output_crs=crs
        )

    # spatial join shorelines to transects
    joined_gdf = gpd.sjoin(shorelines_gdf, transects_gdf, predicate="intersects")

    # get points, keep highest cross distance point if multipoint (most seaward intersection)
    joined_gdf["intersection_point"] = joined_gdf.geometry.intersection(
        joined_gdf["geometry_saved"]
    )
    # reset the index because running the intersection function changes the index
    joined_gdf = joined_gdf.reset_index(drop=True)

    for i in range(len(joined_gdf["intersection_point"])):
        point = joined_gdf["intersection_point"].iloc[i]
        start_x = joined_gdf["x_start"].iloc[i]
        start_y = joined_gdf["y_start"].iloc[i]
        if type(point) == shapely.MultiPoint:
            points = [shapely.Point(coord) for coord in point.geoms]
            points = gpd.GeoSeries(points, crs=crs)
            coords = points.get_coordinates()
            dists = [None] * len(coords)
            for j in range(len(coords)):
                dists[j] = cross_distance(
                    start_x, start_y, coords["x"].iloc[j], coords["y"].iloc[j]
                )
            max_dist_idx = np.argmax(dists)
            last_point = points[max_dist_idx]
            # This new line  updates the shoreline at index (i) for a single value. We only want to update a single shoreline
            joined_gdf.at[i, "intersection_point"] = (
                last_point  # is only edits a single intersection point
            )

    # get x's and y's for intersections
    intersection_coords = joined_gdf["intersection_point"].get_coordinates()
    joined_gdf["shore_x"] = intersection_coords["x"]
    joined_gdf["shore_y"] = intersection_coords["y"]

    # get cross distance
    joined_gdf["cross_distance"] = cross_distance(
        joined_gdf["x_start"],
        joined_gdf["y_start"],
        joined_gdf["shore_x"],
        joined_gdf["shore_y"],
    )
    ##clean up columns
    joined_gdf = joined_gdf.rename(columns={"date": "dates"})
    keep_columns = [
        "dates",
        "satname",
        "geoaccuracy",
        "cloud_cover",
        "transect_id",
        "shore_x",
        "shore_y",
        "cross_distance",
        "x",
        "y",
    ]

    # get start of each transect
    transects_gdf = gpd.GeoDataFrame(
        geometry=gpd.points_from_xy(joined_gdf["x_start"], joined_gdf["y_start"]),
        crs=crs,
    )
    transects_gdf = transects_gdf.to_crs("epsg:4326")

    # convert the x and y intersection points to the final crs (4326) to match the rest of joined_df
    points_gdf = gpd.GeoDataFrame(
        geometry=gpd.points_from_xy(joined_gdf["shore_x"], joined_gdf["shore_y"]),
        crs=crs,
    )
    points_gdf = points_gdf.to_crs("epsg:4326")

    # you have to reset the index here otherwise the intersection point won't match the row correctly
    # recall that the shorelines were group by dates and that changed the index
    joined_gdf = joined_gdf.rename(columns={"date": "dates"}).reset_index(drop=True)

    joined_gdf["shore_x"] = points_gdf.geometry.x
    joined_gdf["shore_y"] = points_gdf.geometry.y
    joined_gdf["x"] = transects_gdf.geometry.x
    joined_gdf["y"] = transects_gdf.geometry.y

    # convert the joined_df back to CRS 4326
    joined_gdf = utm_to_wgs84_df(joined_gdf)

    for col in joined_gdf.columns:
        if col not in keep_columns:
            joined_gdf = joined_gdf.drop(columns=[col], errors="ignore")

    joined_df = joined_gdf.reset_index(drop=True)

    # convert the dates column from panddas dateime object to UTC with +00:00 timezone
    joined_df["dates"] = pd.to_datetime(joined_df["dates"])
    # sort by dates
    joined_df = joined_df.sort_values(by="dates")

    # check if the dates column is already in UTC
    if joined_df["dates"].dt.tz is None:
        joined_df["dates"] = joined_df["dates"].dt.tz_localize("UTC")

    return joined_df


def save_timeseries_to_lines(timeseries_df, save_location, ext: str = "raw"):
    """
    Saves the timeseries of shoreline intersection points as a geojson file with CRS 4326.
    The output file will contain the columns 'dates', 'transect_id', 'cross_distance', 'shore_x', and 'shore_y'.

    Args
    timeseries_gdf (geopandas.GeoDataFrame): The timeseries dataframe containing the cross shore distance values.
        Should contain the columns 'dates', 'transect_id', 'cross_distance', 'shore_x', and 'shore_y'.
    save_location (str): The directory path to save the files to.
    extension (str, optional): A string to append to the beginning of the saved file names to indicate whether tide correction
    was applied or not. Defaults to 'raw'.

    Returns
        None
    """
    # save the time series of along shore points as points to a geojson (saves shore_x and shore_y as x and y coordinates in the geojson)
    cross_shore_pts = convert_date_gdf(
        timeseries_df.drop(
            columns=["x", "y", "shore_x", "shore_y", "cross_distance", "transect_id"],
            errors="ignore",
        ).to_crs("epsg:4326")
    )
    # rename the dates column to date
    cross_shore_pts.rename(columns={"dates": "date"}, inplace=True)
    new_gdf_shorelines_wgs84 = convert_points_to_linestrings(
        cross_shore_pts, group_col="date", output_crs="epsg:4326"
    )

    new_gdf_shorelines_wgs84_path = os.path.join(
        save_location, f"{ext}_transect_time_series_vectors.geojson"
    )
    new_gdf_shorelines_wgs84.to_file(new_gdf_shorelines_wgs84_path)


def save_timeseries_to_points(timeseries_df, save_location, ext: str = "raw"):
    """
    Saves the timeseries of shoreline intersections as series of lines as a geojson file with CRS 4326.
    The output file will contain the columns 'dates', 'transect_id', 'cross_distance', 'shore_x', and 'shore_y'.

    Args
    timeseries_gdf (geopandas.GeoDataFrame): The timeseries dataframe containing the cross shore distance values.
        Should contain the columns 'dates', 'transect_id', 'cross_distance', 'shore_x', and 'shore_y'.
    save_location (str): The directory path to save the files to.
    extension (str, optional): A string to append to the beginning of the saved file names to indicate whether tide correction
    was applied or not. Defaults to 'raw'.

    Returns
        None
    """
    timeseries_df_cleaned = convert_date_gdf(
        timeseries_df.drop(
            columns=["x", "y", "shore_x", "shore_y", "cross_distance"], errors="ignore"
        )
        .rename(columns={"dates": "date"})
        .to_crs("epsg:4326")
    )
    timeseries_df_cleaned.to_file(
        os.path.join(save_location, f"{ext}_transect_time_series_points.geojson"),
        driver="GeoJSON",
    )


def save_transects_timeseries_to_geojson(
    timeseries_df, save_location, ext: str = "raw"
):
    """
    Saves the transect timeseries (should be in CRS EPSG:4326) to geojson in 2 forms.
    1. A geojson file with CRS 4326 with the shoreline intersection points saved as MultiPoints for each date
    2. A geojson file with CRS 4326 with the shoreline intersection points saved as MultilineStrings/LineStrings for each date

    Args:
        timeseries_df (pandas.DataFrame): The timeseries dataframe containing the cross shore distance values.
            Should contain the columns 'dates', 'transect_id', 'cross_distance', 'shore_x', and 'shore_y'.
        save_location (str): The directory path to save the files to.
        extension (str, optional): A string to append to the beginning of the saved file names to indicate whether tide correction
        was applied or not. Defaults to 'raw'.
    Returns:
        None
    """
    merged_timeseries_gdf = gpd.GeoDataFrame(
        timeseries_df,
        geometry=[
            Point(xy) for xy in zip(timeseries_df["shore_x"], timeseries_df["shore_y"])
        ],
        crs="EPSG:4326",
    )  # type: ignore
    # save the time series of along shore points as points to a geojson (saves shore_x and shore_y as x and y coordinates in the geojson)
    save_timeseries_to_points(merged_timeseries_gdf, save_location, ext)
    save_timeseries_to_lines(merged_timeseries_gdf, save_location, ext)


def save_transects(
    save_location: str,
    transect_timeseries_df,
    settings: dict,
    ext: str = "raw",
    good_bad_csv: str = "",
    good_bad_seg_csv: str = "",
):
    """
    Saves the transect timeseries to a csv file, the transects as a dictionary to a json file and the transect settings to a json file

    Saves the files:
    1. raw_transect_time_series_merged.csv: contains all the columns
    2. raw_transect_time_series.csv: contains only the cross_distance and dates columns
    3. transects_cross_distances.json: contains the cross distances for each transect organized by date
    4. transects_settings.json: contains the settings for the transect analysis

    inputs:
    save_location (str): directory to save the csv files at
    transect_timeseries_df (pd.DataFrame): dataframe containing the transect timeseries
        - This is the merged csv that contains the columns 'dates', 'transect_id', 'cross_distance'
    settings (dict): dictionary containing the settings for the transect analysis
    ext (str): A string to append to the beginning of the saved file names to indicate whether tide correction was applied or not. Defaults to 'raw'.
    """
    # convert the transect_id column to string
    transect_timeseries_df["transect_id"] = transect_timeseries_df[
        "transect_id"
    ].astype(str)

    save_transects_timeseries(transect_timeseries_df, save_location)
    save_transects_timeseries_to_geojson(transect_timeseries_df, save_location, ext)
    add_classifier_scores_to_transects(save_location, good_bad_csv, good_bad_seg_csv)

    # save transect settings to file
    transect_settings = get_transect_settings(settings)
    transect_settings_path = os.path.join(save_location, "transects_settings.json")
    file_utilities.to_file(transect_settings, transect_settings_path)

    # Create a dictionary organized by transect id containing the cross distance for each unqiue date the transect intersected
    # Example: {1: [10, 15], 2: [20, 25]} corresponds to 2 unique dates
    transects_dict = create_transect_dictionary(transect_timeseries_df)
    save_path = os.path.join(save_location, "transects_cross_distances.json")
    file_utilities.to_file(transects_dict, save_path)


def create_transect_dictionary(df):
    """
    Creates a dictionary organized by transect id from a dataframe containing the transect ids, dates, and cross_distance values.

    This function sorts the input DataFrame by the 'dates' column and then
    creates a dictionary where each key is a unique transect ID and the
    corresponding value is a list of 'cross_distance' values for that transect,
    organized by date.

    Parameters:
    df (pandas.DataFrame): A DataFrame containing at least the columns
                           'transect_id', 'dates', and 'cross_distance'.

    Returns:
    dict: A dictionary where keys are transect IDs and values are lists of
          'cross_distance' values.

    Example:
    >>> df = pd.DataFrame({
    ...     'transect_id': [1, 2, 1, 2],
    ...     'dates': ['2021-01-01', '2021-01-01', '2021-01-02', '2021-01-02'],
    ...     'cross_distance': [10, 20, 15, 25]
    ... })
    >>> create_transect_dictionary(df)
    {1: [10, 15], 2: [20, 25]}
    """
    df = df.sort_values(by=["dates"])
    transect_dictionary = {}
    unique_dates = df["dates"].unique()
    unique_dates = sorted(unique_dates)

    # Loop through all the transect ids and create an array of size equal to the number of unique dates and fill with corresponding shoreline intersection or nans
    for transect_id in np.unique(df["transect_id"]):
        dates_mask = {date: np.nan for date in unique_dates}

        transect = df[df["transect_id"] == transect_id]
        # fill in the dates mask if the date is in the transect
        for index, row in transect.iterrows():
            dates_mask[row["dates"]] = row["cross_distance"]
        transect_dictionary[transect_id] = list(dates_mask.values())
    return transect_dictionary


def save_transects_timeseries(transect_timeseries_df, save_location):
    """
    Saves two version of the transect timeseries to a csv file
    1. raw_transect_time_series_merged.csv: contains all the columns
    2. raw_transect_time_series.csv: contains only the cross_distance and dates columns


    inputs:
    transect_timeseries_df (pd.DataFrame): dataframe containing the transect timeseries
    save_location (str): directory to save the csv files at
    """

    # 1. Save the raw transect time series merged with all the columns to a csv file
    timeseries_output_path = os.path.join(
        save_location, "raw_transect_time_series_merged.csv"
    )
    transect_timeseries_df.to_csv(timeseries_output_path, index=False)

    # 2. Save the raw transect time series with only the cross_distance and dates columns to a csv file
    transect_timeseries_matrix = transect_timeseries_df.pivot(
        index="dates", columns="transect_id", values="cross_distance"
    )
    transect_timeseries_matrix.columns.name = None
    transect_timeseries_matrix.reset_index(
        inplace=True
    )  # this turns the dates row index into a column

    # sort the rows by the transect IDs
    sorted_columns = [transect_timeseries_matrix.columns[0]] + sorted(
        transect_timeseries_matrix.columns[1:],
        key=lambda x: int("".join(filter(str.isdigit, x))),
    )
    transect_timeseries_matrix = transect_timeseries_matrix[sorted_columns]

    timeseries_output_path = os.path.join(save_location, "raw_transect_time_series.csv")
    transect_timeseries_matrix.to_csv(timeseries_output_path, index=False)

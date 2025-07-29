import numpy as np
from typing import Optional, Tuple, List

def infer_lonlat(columns: List[str]) -> Optional[Tuple[str, str]]:
    """从DataFrame的列名中推断经纬度列名

    此函数用于自动识别数据中的经纬度列名。支持多种常见的经纬度列名格式。

    参数:
        columns: DataFrame中的列名列表

    返回:
        如果找到匹配的经纬度列名对，返回(经度列名, 纬度列名)的元组；否则返回None

    支持的列名对:
        - ("longitude", "latitude")
        - ("lon", "lat")
        - ("lng", "lat")
        - ("fused_centroid_x", "fused_centroid_y")
        - ("fused_centroid_x_left", "fused_centroid_y_left")
        - ("fused_centroid_x_right", "fused_centroid_x_right")
    """
    columns_set = set(columns)
    allowed_column_pairs = [
        ("longitude", "latitude"),
        ("lon", "lat"),
        ("lng", "lat"),
        ("fused_centroid_x", "fused_centroid_y"),
        ("fused_centroid_x_left", "fused_centroid_y_left"),
        ("fused_centroid_x_right", "fused_centroid_x_right"),
    ]
    for allowed_column_pair in allowed_column_pairs:
        if (
            allowed_column_pair[0] in columns_set
            and allowed_column_pair[1] in columns_set
        ):
            return allowed_column_pair
    return None

def resolve_crs(gdf, crs, verbose=False):
    """将GeoDataFrame重新投影到指定的坐标参考系统(CRS)

    此函数用于处理地理数据的坐标系统转换。如果指定"utm"作为目标CRS，
    会自动计算并转换到合适的UTM投影。

    参数:
        gdf: 需要转换的GeoDataFrame
        crs: 目标坐标参考系统
        verbose: 是否打印日志信息，默认为False

    返回:
        转换后的GeoDataFrame

    异常:
        ValueError: 当gdf没有CRS且无法进行重投影时抛出
    """
    if str(crs).lower() == "utm":
        if gdf.crs is None:
            gdf = gdf.set_crs(4326)
            if verbose:
                print("No crs exists on `gdf`. Assuming it's WGS84 (epsg:4326).")

        utm_crs = gdf.estimate_utm_crs()
        if gdf.crs == utm_crs:
            if verbose:
                print(f"CRS is already {utm_crs}.")
            return gdf
        else:
            if verbose:
                print(f"Converting from {gdf.crs} to {utm_crs}.")
            return gdf.to_crs(utm_crs)

    elif (gdf.crs is not None) & (gdf.crs != crs):
        old_crs = gdf.crs
        if verbose:
            print(f"Converting from {old_crs} to {crs}.")
        return gdf.to_crs(crs)
    elif gdf.crs is None:
        raise ValueError("gdf.crs is None and reprojection could not be performed.")
    else:
        if verbose:
            print(f"crs is already {crs}.")
        return gdf


def df_to_gdf(df, cols_lonlat=None, verbose=False):
    """将DataFrame转换为GeoDataFrame

    此函数将包含经纬度信息的DataFrame转换为GeoDataFrame。
    如果未指定经纬度列名，会自动尝试推断。

    参数:
        df: 输入的DataFrame
        cols_lonlat: 经纬度列名元组(经度列名, 纬度列名)，如果为None则自动推断
        verbose: 是否打印日志信息，默认为False

    返回:
        转换后的GeoDataFrame

    异常:
        ValueError: 当找不到经纬度列时抛出
    """
    import json

    import pyarrow as pa
    import shapely
    from geopandas.io.arrow import _arrow_to_geopandas

    geo_metadata = {
        "primary_column": "geometry",
        "columns": {"geometry": {"encoding": "WKB", "crs": 4326}},
        "version": "1.0.0-beta.1",
    }
    arrow_geo_metadata = {b"geo": json.dumps(geo_metadata).encode()}
    if not cols_lonlat:
        cols_lonlat = infer_lonlat(list(df.columns))
        if not cols_lonlat:
            raise ValueError("no latitude and longitude columns were found.")

        assert (
            cols_lonlat[0] in df.columns
        ), f"column name {cols_lonlat[0]} was not found."
        assert (
            cols_lonlat[1] in df.columns
        ), f"column name {cols_lonlat[1]} was not found."

        if verbose:
            print(
                f"Converting {cols_lonlat} to points({cols_lonlat[0]},{cols_lonlat[0]})."
            )
    geoms = shapely.points(df[cols_lonlat[0]], df[cols_lonlat[1]])
    table = pa.Table.from_pandas(df)
    table = table.append_column("geometry", pa.array(shapely.to_wkb(geoms)))
    table = table.replace_schema_metadata(arrow_geo_metadata)
    try:
        df = _arrow_to_geopandas(table)
    except:
        df = _arrow_to_geopandas(table.drop(["__index_level_0__"]))
    return df

def to_gdf(
    data,
    crs=None,
    cols_lonlat=None,
    col_geom="geometry",
    verbose: bool = False,
):
    """将各种输入数据转换为GeoDataFrame

    这是一个通用的转换函数，支持多种输入格式转换为GeoDataFrame：
    - 字典格式的xyz坐标
    - xyz瓦片坐标列表
    - 边界框坐标
    - DataFrame/Series
    - GeoDataFrame/GeoSeries
    - Shapely几何对象

    参数:
        data: 输入数据，支持多种格式
        crs: 坐标参考系统，默认为None
        cols_lonlat: 经纬度列名元组，默认为None
        col_geom: 几何列名，默认为"geometry"
        verbose: 是否打印日志信息，默认为False

    返回:
        转换后的GeoDataFrame

    异常:
        ValueError: 当无法转换数据或缺少必要的CRS信息时抛出
    """
    import geopandas as gpd
    import shapely
    import pandas as pd
    import mercantile
    
    # Convert xyz dict to xyz array
    if isinstance(data, dict) and set(data.keys()) == {'x', 'y', 'z'}:
        try:
            data = [int(data['x']), int(data['y']), int(data['z'])]
        except (ValueError, TypeError):
            pass     
            
    
    if data is None or (isinstance(data, (list, tuple, np.ndarray))):
        
        data = [327, 791, 11] if data is None else data #if no data, get a tile in SF
        
        if len(data) == 3: # Handle xyz tile coordinates
            x, y, z = data
            tile = mercantile.Tile(x, y, z)
            bounds = mercantile.bounds(tile)
            gdf = gpd.GeoDataFrame(
                {"x": [x], "y": [y], "z": [z]},
                geometry=[shapely.box(bounds.west, bounds.south, bounds.east, bounds.north)],
                crs=4326
            )
            return gdf[['x', 'y', 'z', 'geometry']]
         
        elif len(data) == 4: # Handle the bounds case specifically        
            return gpd.GeoDataFrame({}, geometry=[shapely.box(*data)], crs=crs or 4326)        
        
    if cols_lonlat:
        if isinstance(data, pd.Series):
            raise ValueError(
                "Cannot pass a pandas Series or a geopandas GeoSeries in conjunction "
                "with cols_lonlat."
            )
        gdf = df_to_gdf(data, cols_lonlat, verbose=verbose)
        if verbose:
            print(
                "cols_lonlat was passed so original CRS was assumed to be EPSG:4326."
            )
        if crs:
            gdf = resolve_crs(gdf, crs, verbose=verbose)
        return gdf
    if isinstance(data, gpd.GeoDataFrame):
        gdf = data
        if crs:
            gdf = resolve_crs(gdf, crs, verbose=verbose)
        elif gdf.crs is None:
            raise ValueError("Please provide crs. usually crs=4326.")
        return gdf
    elif isinstance(data, gpd.GeoSeries):
        gdf = gpd.GeoDataFrame(data=data)
        if crs:
            gdf = resolve_crs(gdf, crs, verbose=verbose)
        elif gdf.crs is None:
            raise ValueError("Please provide crs. usually crs=4326.")
        return gdf
    elif type(data) in (pd.DataFrame, pd.Series):
        if type(data) is pd.Series:
            data = pd.DataFrame(data)
            if col_geom in data.index:
                data = data.T
        if (col_geom in data.columns) and (not cols_lonlat):
            if type(data[col_geom][0]) == str:
                gdf = gpd.GeoDataFrame(
                    data.drop(columns=[col_geom]),
                    geometry=shapely.from_wkt(data[col_geom]),
                )
            else:
                gdf = gpd.GeoDataFrame(data)
            if gdf.crs is None:
                if crs:
                    gdf = gdf.set_crs(crs)
                else:
                    raise ValueError("Please provide crs. usually crs=4326.")
            elif crs:
                gdf = resolve_crs(gdf, crs, verbose=verbose)
        elif not cols_lonlat:
            cols_lonlat = infer_lonlat(data.columns)
            if not cols_lonlat:
                raise ValueError("no latitude and longitude columns were found.")
            if crs:
                if verbose:
                    print(
                        f"cols_lonlat was passed so crs was set to wgs84(4326) and {crs=} was ignored."
                    )
            # This is needed for Python 3.8 specifically, because otherwise creating the GeoDataFrame modifies the input DataFrame
            data = data.copy()
            gdf = df_to_gdf(data, cols_lonlat, verbose=verbose)
        return gdf
    elif (
        isinstance(data, shapely.geometry.base.BaseGeometry)
        or isinstance(data, shapely.geometry.base.BaseMultipartGeometry)
        or isinstance(data, shapely.geometry.base.EmptyGeometry)
    ):
        if not crs:
            raise ValueError("Please provide crs. usually crs=4326.")
        return gpd.GeoDataFrame(geometry=[data], crs=crs)
    else:
        raise ValueError(
            f"Cannot convert data of type {type(data)} to GeoDataFrame. Please pass a GeoDataFrame, GeoSeries, DataFrame, Series, or shapely geometry."
        )
def mercantile_kring(tile, k):
    """生成指定瓦片周围的k-ring瓦片集合

    此函数用于生成以给定瓦片为中心，k为半径的瓦片集合。
    注意：目前未处理全球边界处的无效瓦片（如负值）。

    参数:
        tile: 中心瓦片
        k: 半径大小

    返回:
        包含所有k-ring瓦片的列表
    """
    import mercantile

    result = []
    for x in range(tile.x - k, tile.x + k + 1):
        for y in range(tile.y - k, tile.y + k + 1):
            result.append(mercantile.Tile(x, y, tile.z))
    return result


def mercantile_kring_list(tiles, k):
    """为多个瓦片生成k-ring瓦片集合

    此函数为输入的每个瓦片生成k-ring，并合并结果。

    参数:
        tiles: 输入瓦片列表
        k: 半径大小

    返回:
        合并后的唯一瓦片列表
    """
    a = []
    for tile in tiles:
        a.extend(mercantile_kring(tile, k))
    return list(set(a))

def mercantile_polyfill(geom, zooms=[15], compact=True, k=None):
    """将几何对象填充为瓦片集合

    此函数将输入的几何对象转换为覆盖该区域的瓦片集合。
    可以选择是否简化瓦片集合，以及是否扩展k-ring。

    参数:
        geom: 输入的几何对象
        zooms: 缩放级别列表，默认为[15]
        compact: 是否简化瓦片集合，默认为True
        k: k-ring扩展半径，默认为None

    返回:
        包含瓦片信息的GeoDataFrame
    """
    import geopandas as gpd
    import mercantile
    import shapely

    gdf = to_gdf(geom , crs = 4326)
    geometry = gdf.geometry[0]

    tile_list = list(mercantile.tiles(*geometry.bounds, zooms=zooms))
    gdf_tiles = gpd.GeoDataFrame(
        tile_list,
        geometry=[shapely.box(*mercantile.bounds(i)) for i in tile_list],
        crs=4326,
    )
    gdf_tiles_intersecting = gdf_tiles[gdf_tiles.intersects(geometry)]

    if k:
        temp_list = gdf_tiles_intersecting.apply(
            lambda row: mercantile.Tile(row.x, row.y, row.z), 1
        )
        clip_list = mercantile_kring_list(temp_list, k)
        if not compact:
            gdf = gpd.GeoDataFrame(
                clip_list,
                geometry=[shapely.box(*mercantile.bounds(i)) for i in clip_list],
                crs=4326,
            )
            return gdf
    else:
        if not compact:
            return gdf_tiles_intersecting
        clip_list = gdf_tiles_intersecting.apply(
            lambda row: mercantile.Tile(row.x, row.y, row.z), 1
        )
    simple_list = mercantile.simplify(clip_list)
    gdf = gpd.GeoDataFrame(
        simple_list,
        geometry=[shapely.box(*mercantile.bounds(i)) for i in simple_list],
        crs=4326,
    )
    return gdf  # .reset_index(drop=True)

def estimate_zoom(bounds, target_num_tiles=1):
    """估算适合给定边界的缩放级别

    此函数用于计算能够覆盖给定边界框的合适缩放级别。
    可以指定目标瓦片数量，函数会估算达到该数量所需的缩放级别。

    参数:
        bounds: 边界框，可以是坐标列表、GeoDataFrame、Shapely几何对象或mercantile瓦片
        target_num_tiles: 目标瓦片数量，默认为1

    返回:
        估算的缩放级别（0-20）

    异常:
        TypeError: 当边界类型无效时抛出
        ImportError: 当缺少mercantile包时抛出
    """
    import geopandas as gpd
    import mercantile
    import shapely

    HAS_GEOPANDAS = True
    HAS_MERCANTILE = True 
    HAS_SHAPELY = True
    GPD_GEODATAFRAME = gpd.GeoDataFrame
    MERCANTILE_TILE = mercantile.Tile
    SHAPELY_GEOMETRY = shapely.geometry.base.BaseGeometry

    # Process input bounds to get standard format
    if HAS_GEOPANDAS and isinstance(bounds, GPD_GEODATAFRAME):
        bounds = bounds.total_bounds
    elif HAS_SHAPELY and isinstance(bounds, SHAPELY_GEOMETRY):
        bounds = bounds.bounds
    elif HAS_MERCANTILE and isinstance(bounds, MERCANTILE_TILE):
        return bounds.z
    elif not isinstance(bounds, list):
        raise TypeError(f"Invalid bounds type: {type(bounds)}")

    if not HAS_MERCANTILE:
        raise ImportError("This function requires the mercantile package.")
    
    import mercantile
    import math
    

    if target_num_tiles == 1:
        minx, miny, maxx, maxy = bounds
        centroid = (minx + maxx) / 2, (miny + maxy) / 2
        width = (maxx - minx) - 1e-11
        height = (maxy - miny) - 1e-11
        
        for z in range(20, 0, -1):
            tile = mercantile.tile(*centroid, zoom=z)
            west, south, east, north = mercantile.bounds(tile)
            if width <= (east - west) and height <= (north - south):
                break
        return z
    

    else:
        minx, miny, maxx, maxy = bounds
        miny = max(miny,-89.9999993) #there is a bug in the mercentile that adds an epsilon to lat lngs and causes issue
        maxy = min(maxy,89.9999993) #there is a bug in the mercentile that adds an epsilon to lat lngs and causes issue
        max_zoom = 20
        x_min, y_min, _ = mercantile.tile(minx, maxy, max_zoom)
        x_max, y_max, _ = mercantile.tile(maxx, miny, max_zoom)
        delta_x = x_max - x_min + 1
        delta_y = y_max - y_min + 1

        zoom = math.log2(math.sqrt(target_num_tiles) / max(delta_x, delta_y)) + max_zoom
        zoom = int(math.floor(zoom)) 
        current_num_tiles = len(mercantile_polyfill(bounds, zooms=[zoom], compact=False))
        if current_num_tiles>=target_num_tiles:
            return zoom
        else:
            return zoom+1


def get_tiles(
    bounds=None, target_num_tiles=1, zoom=None, max_tile_recursion=6, as_gdf=True, verbose=False
):
    """获取覆盖指定区域的瓦片集合

    此函数用于生成覆盖指定区域的瓦片集合。可以通过指定目标瓦片数量
    或直接指定缩放级别来控制瓦片密度。

    参数:
        bounds: 边界区域，默认为None
        target_num_tiles: 目标瓦片数量，默认为1
        zoom: 指定缩放级别，默认为None
        max_tile_recursion: 最大递归深度，默认为6
        as_gdf: 是否返回GeoDataFrame格式，默认为True
        verbose: 是否打印日志信息，默认为False

    返回:
        如果as_gdf为True，返回包含瓦片信息的GeoDataFrame；
        否则返回瓦片坐标数组

    异常:
        ValueError: 当目标瓦片数量小于1时抛出
    """
    bounds = to_gdf(bounds)
    import mercantile
    import geopandas as gpd
    import numpy as np

    if bounds.empty or bounds.geometry.isna().any() or len(bounds) == 0:
        if verbose:
            print("Warning: Empty or invalid bounds provided")
        return gpd.GeoDataFrame(columns=["geometry", "x", "y", "z"])

    if np.isnan(bounds.total_bounds).any():
        if verbose:
            print("Warning: Empty or invalid bounds provided")
        return gpd.GeoDataFrame(columns=["geometry", "x", "y", "z"])
    
    if zoom is not None:
        if verbose: 
            print("zoom is provided; target_num_tiles will be ignored.")
        target_num_tiles = None

    if target_num_tiles is not None and target_num_tiles < 1:
        raise ValueError("target_num_tiles should be more than zero.")

    if target_num_tiles == 1:
        
        tile = mercantile.bounding_tile(*bounds.total_bounds)
        if verbose: 
            print(to_gdf((0,0,0)))
        gdf = to_gdf((tile.x, tile.y, tile.z))
    else:
        zoom_level = (
            zoom
            if zoom is not None
            else estimate_zoom(bounds, target_num_tiles=target_num_tiles)
        )
        base_zoom = estimate_zoom(bounds, target_num_tiles=1)
        if zoom_level > (base_zoom + max_tile_recursion + 1):
            zoom_level = base_zoom + max_tile_recursion + 1
            if zoom:
                if verbose: 
                    print(
                    f"Warning: Maximum number of tiles is reached ({zoom=} > {base_zoom+max_tile_recursion+1=} tiles). Increase {max_tile_recursion=} to allow for deeper tile recursion"
                    )
            else:
                if verbose: 
                    print(
                    f"Warning: Maximum number of tiles is reached ({target_num_tiles} > {4**max_tile_recursion-1} tiles). Increase {max_tile_recursion=} to allow for deeper tile recursion"
                    )

        gdf = mercantile_polyfill(bounds, zooms=[zoom_level], compact=False)
        if verbose: 
            print(f"Generated {len(gdf)} tiles at zoom level {zoom_level}")

    return gdf if as_gdf else gdf[["x", "y", "z"]].values


# if __name__ == '__main__':
#     print(get_tiles(bounds=[121.08086409327214,38.77162660341702,125.60723128077215,41.327721448378014],target_num_tiles=16))

    
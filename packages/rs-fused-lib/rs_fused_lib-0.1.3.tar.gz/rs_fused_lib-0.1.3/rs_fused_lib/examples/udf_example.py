from rs_fused_lib.core.udf import udf
import rs_fused_lib
import pandas as pd
import geopandas


@udf
def add(a: int, b: int) -> int:
    return a + b

import pandas as pd
@udf
def create_dataFrame(row_num: int, col_num: int) -> pd.DataFrame:
    import numpy
    import pandas
    return pandas.DataFrame(numpy.random.randn(row_num, col_num))



@udf
def create_geodataframe(row_num: int, col_num: int) -> geopandas.GeoDataFrame:
    import geopandas
    import pandas
    import numpy
    from shapely.geometry import Point
    row_num = utils_num(row_num, 10)
    col_num = utils_num(col_num, 10)
    df = pandas.DataFrame(numpy.random.randn(row_num, col_num))
    geometry = [Point(0,0) for _ in range(len(df))]
    return geopandas.GeoDataFrame(df, geometry=geometry)



def utils_num(a: int, b: int) -> int:
    return utils_num2(a, b)

def utils_num2(a: int, b: int) -> int:
    return a + b + 1

fused_udf = create_geodataframe.to_fused()
print("====================fused_udf save success==============================")
print("====================fused_udf load: ",fused_udf.id,"==============================")

fused_udf_load = rs_fused_lib.load(fused_udf.id)
print("====================fused_udf_load load success==============================")

print("====================fused_udf_load.utils==============================")
utils = fused_udf_load.utils
print("====================utils==============================")
print(utils.__annotations__)
utils_result = utils.get_tiles(bounds=[121.08086409327214,38.77162660341702,125.60723128077215,41.327721448378014],target_num_tiles=16)
print(f"====================utils_result======{type(utils_result)}========================")

print("====================utils_result run==============================")
result = rs_fused_lib.run(utils_result,parameters={"bounds":[121.08086409327214,38.77162660341702,125.60723128077215,41.327721448378014],"target_num_tiles":16})
print("====================result==============================")
print(result)
print("===================udf id run==============================")
udf_id_metod_result = rs_fused_lib.run("UDF_create_geodataframe", parameters={"row_num":3,"col_num":5})
print("====================udf_id_metod_result==============================")
print(udf_id_metod_result)



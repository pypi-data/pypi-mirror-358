import requests
from rs_fused_lib.core.udf import UDF
from rs_fused_lib.common.serializers import DataFrameSerializer
from rs_fused_lib.config import get_base_url

def save_udf(
    udf: dict,
):
    url = f"{get_base_url()}/save_udf"
    response = requests.post(
        url,
        json=udf
    )
    if response.status_code != 200:
        raise Exception(f"Failed to save UDF: {response.json()}")
    return UDF(**response.json())

def run_udf(
    udf_id: str,
    x: int,
    y: int,
    z: int,
    parameters: dict,
): 
    url = f"{get_base_url()}/run_udf/{udf_id}"
    response = requests.post(url, json={"x": x, "y": y, "z": z, "kwargs": parameters})
    if response.status_code != 200:
        raise Exception(f"Failed to run UDF: {response.json()}")
    resContent = response.json()
    if resContent['result'] is not None:
        result = DataFrameSerializer.from_json(resContent['result'])
        return result
    else:
        return None

def run_udf_instance_server(
    udf_instance: UDF,
    x: int,
    y: int,
    z: int,
    parameters: dict,
):
    url = f"{get_base_url()}/run_udf_instance"
    response = requests.post(url, json={"udf_instance": udf_instance.model_dump(), "x": x, "y": y, "z": z, "parameters": parameters})
    if response.status_code != 200:
        raise Exception(f"Failed to run UDF: {response.json()}")
    resContent = response.json()
    if resContent['result'] is not None:
        result = DataFrameSerializer.from_json(resContent['result'])
        return result
    
def load_udf(
    udf_id: str,
):
    """加载UDF函数
    
    Args:
        udf_id: UDF ID
        
    Returns:
        UDF: UDF对象，包含解析后的util_code
    """
    url = f"{get_base_url()}/load_udf/{udf_id}"
    response = requests.post(url)
    if response.status_code != 200:
        raise Exception(f"Failed to load UDF: {response.json()}")
    
    # 获取响应数据
    data = response.json()
    
    # 创建UDF实例
    udf_instance = UDF(**data)
    
    # 如果存在util_code，确保它被正确解析
    if udf_instance.util_code:
        # 触发utils属性的初始化，这将解析util_code并设置_cached_utils
        _ = udf_instance.utils
    
    return udf_instance

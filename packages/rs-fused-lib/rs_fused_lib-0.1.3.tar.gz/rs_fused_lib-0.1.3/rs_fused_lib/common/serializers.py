import json
import base64
import io
import pandas as pd
import geopandas as gpd
from typing import Union, Dict, Any
from rs_fused_lib.common.logger import logger

class DataFrameSerializer:
    
    @staticmethod
    def to_json(df: Union[pd.DataFrame, gpd.GeoDataFrame]) -> Dict[str, Any]:
        """
        将DataFrame或GeoDataFrame转换为JSON格式
        
        Args:
            df: pandas DataFrame或GeoDataFrame对象
            
        Returns:
            Dict: 包含序列化数据的字典
        """
        try:
            # 将DataFrame转换为JSON字符串
            if isinstance(df, gpd.GeoDataFrame):
                return {
                    'type': 'geodataframe',
                    'data': json.loads(df.to_json())
                }
            else:
                json_str = df.to_json()
            data = json.loads(json_str)
            return {
                'type': 'dataframe',
                'data': data,
            }
            
        except Exception as e:
            logger.error(f"序列化DataFrame失败: {str(e)}")
            raise
    
    @staticmethod
    def from_json(json_data: Dict[str, Any]) -> Union[pd.DataFrame, gpd.GeoDataFrame]:
        """
        从JSON格式恢复DataFrame或GeoDataFrame
        
        Args:
            json_data: 包含序列化数据的字典
            
        Returns:
            DataFrame或GeoDataFrame对象
        """
        try:
            data_type = json_data.get('type')
            data = json_data.get('data', [])
            
            # 如果是GeoDataFrame，添加几何信息
            if data_type == 'geodataframe':
                return gpd.GeoDataFrame.from_features(data.get('features'))
            
            # 创建DataFrame
            df = pd.DataFrame.from_dict(data)
            return df
            
        except Exception as e:
            logger.error(f"反序列化DataFrame失败: {str(e)}")
            raise
        
        
    @staticmethod
    def to_parquet_base64(df: Union[pd.DataFrame, gpd.GeoDataFrame]) -> str:
        """
        将DataFrame或GeoDataFrame转换为Base64编码的Parquet格式
        
        Args:
            df: pandas DataFrame或GeoDataFrame对象
            
        Returns:
            str: Base64编码的Parquet数据
        """
        try:
            buffer = io.BytesIO()
            df.to_parquet(buffer)
            buffer.seek(0)
            return base64.b64encode(buffer.getvalue()).decode('utf-8')
        except Exception as e:
            logger.error(f"转换为Parquet格式失败: {str(e)}")
            raise
    
    @staticmethod
    def from_parquet_base64(base64_str: str) -> Union[pd.DataFrame, gpd.GeoDataFrame]:
        """
        从Base64编码的Parquet格式恢复DataFrame或GeoDataFrame
        
        Args:
            base64_str: Base64编码的Parquet数据
            
        Returns:
            DataFrame或GeoDataFrame对象
        """
        try:
            buffer = io.BytesIO(base64.b64decode(base64_str))
            return pd.read_parquet(buffer)
        except Exception as e:
            logger.error(f"从Parquet格式恢复失败: {str(e)}")
            raise
    
    @staticmethod
    def to_csv_base64(df: Union[pd.DataFrame, gpd.GeoDataFrame]) -> str:
        """
        将DataFrame或GeoDataFrame转换为Base64编码的CSV格式
        
        Args:
            df: pandas DataFrame或GeoDataFrame对象
            
        Returns:
            str: Base64编码的CSV数据
        """
        try:
            buffer = io.StringIO()
            df.to_csv(buffer, index=False)
            buffer.seek(0)
            return base64.b64encode(buffer.getvalue().encode('utf-8')).decode('utf-8')
        except Exception as e:
            logger.error(f"转换为CSV格式失败: {str(e)}")
            raise
    
    @staticmethod
    def from_csv_base64(base64_str: str) -> pd.DataFrame:
        """
        从Base64编码的CSV格式恢复DataFrame
        
        Args:
            base64_str: Base64编码的CSV数据
            
        Returns:
            DataFrame对象
        """
        try:
            buffer = io.StringIO(base64.b64decode(base64_str).decode('utf-8'))
            return pd.read_csv(buffer)
        except Exception as e:
            logger.error(f"从CSV格式恢复失败: {str(e)}")
            raise 
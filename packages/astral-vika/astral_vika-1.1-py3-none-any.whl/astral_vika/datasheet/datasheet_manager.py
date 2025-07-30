"""
维格表数据表管理器

兼容原vika.py库的DatasheetManager类
"""
from typing import Dict, Any, Optional, List
from .datasheet import Datasheet
from ..utils import get_dst_id
from ..exceptions import ParameterException


class DatasheetManager:
    """
    数据表管理器，提供数据表相关操作
    
    兼容原vika.py库的DatasheetManager接口
    """
    
    def __init__(self, space):
        """
        初始化数据表管理器
        
        Args:
            space: 空间实例
        """
        self._space = space
    
    def get(
        self,
        dst_id_or_url: str,
        field_key: str = "name",
        field_key_map: Optional[Dict[str, str]] = None
    ) -> Datasheet:
        """
        获取数据表实例
        
        Args:
            dst_id_or_url: 数据表ID或URL
            field_key: 字段键类型 ("name" 或 "id")
            field_key_map: 字段映射字典
            
        Returns:
            数据表实例
        """
        dst_id = get_dst_id(dst_id_or_url)
        
        return Datasheet(
            apitable=self._space._apitable,
            dst_id=dst_id,
            spc_id=self._space._space_id,
            field_key=field_key,
            field_key_map=field_key_map
        )
    
    async def acreate(
        self,
        name: str,
        description: Optional[str] = None,
        folder_id: Optional[str] = None,
        pre_filled_records: Optional[List[Dict[str, Any]]] = None
    ) -> Datasheet:
        """
        创建数据表（异步）
        
        Args:
            name: 数据表名称
            description: 数据表描述
            folder_id: 文件夹ID
            pre_filled_records: 预填充记录
            
        Returns:
            创建的数据表实例
        """
        response = await self._acreate_datasheet(name, description, folder_id, pre_filled_records)
        datasheet_data = response.get('data', {})
        dst_id = datasheet_data.get('id')
        
        if not dst_id:
            raise ParameterException("Failed to create datasheet: no ID returned")
        
        return self.get(dst_id)
    
    async def aexists(self, dst_id_or_url: str) -> bool:
        """
        检查数据表是否存在（异步）
        
        Args:
            dst_id_or_url: 数据表ID或URL
            
        Returns:
            数据表是否存在
        """
        try:
            dst_id = get_dst_id(dst_id_or_url)
            # 尝试获取数据表的字段信息来验证存在性
            datasheet = self.get(dst_id)
            await datasheet.aget_fields()
            return True
        except Exception:
            return False
    
    def delete(self, dst_id_or_url: str) -> bool:
        """
        删除数据表
        
        Args:
            dst_id_or_url: 数据表ID或URL
            
        Returns:
            是否删除成功
        """
        # 注意：维格表API可能不支持直接删除数据表
        # 这个方法主要是为了接口兼容性
        raise NotImplementedError(
            "Datasheet deletion is not supported by Vika API. "
            "Please delete the datasheet through the web interface."
        )
    
    async def alist(self) -> List[Dict[str, Any]]:
        """
        获取空间中的数据表列表（异步）
        
        Returns:
            数据表列表
        """
        # 通过节点管理器获取数据表节点
        nodes_response = await self._space.nodes._aget_nodes()
        nodes_data = nodes_response.get('data', {}).get('nodes', [])
        
        datasheets = []
        for node in nodes_data:
            if node.get('type') == 'Datasheet':
                datasheets.append({
                    'id': node.get('id'),
                    'name': node.get('name'),
                    'type': node.get('type'),
                    'icon': node.get('icon'),
                    'parentId': node.get('parentId')
                })
        
        return datasheets
    
    async def aget_datasheet_info(self, dst_id_or_url: str) -> Dict[str, Any]:
        """
        获取数据表基本信息（异步）
        
        Args:
            dst_id_or_url: 数据表ID或URL
            
        Returns:
            数据表基本信息
        """
        datasheet = self.get(dst_id_or_url)
        meta = await datasheet.aget_meta()
        
        fields = await datasheet.aget_fields()
        views = await datasheet.aget_views()
        
        return {
            'id': datasheet.dst_id,
            'spaceId': datasheet.space_id,
            'fieldCount': len(fields),
            'viewCount': len(views),
            'meta': meta
        }
    
    # 内部API调用方法
    async def _acreate_datasheet(
        self,
        name: str,
        description: Optional[str] = None,
        folder_id: Optional[str] = None,
        pre_filled_records: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """创建数据表的内部API调用"""
        endpoint = f"spaces/{self._space._space_id}/datasheets"
        
        data = {"name": name}
        if description:
            data["description"] = description
        if folder_id:
            data["folderId"] = folder_id
        if pre_filled_records:
            data["preFilledRecords"] = pre_filled_records
        
        return await self._space._apitable.request_adapter.post(endpoint, json=data)
    
    def __call__(
        self,
        dst_id_or_url: str,
        field_key: str = "name",
        field_key_map: Optional[Dict[str, str]] = None
    ) -> Datasheet:
        """
        支持直接调用获取数据表
        
        Args:
            dst_id_or_url: 数据表ID或URL
            field_key: 字段键类型
            field_key_map: 字段映射字典
            
        Returns:
            数据表实例
        """
        return self.get(dst_id_or_url, field_key, field_key_map)
    
    def __str__(self) -> str:
        return f"DatasheetManager({self._space})"
    
    def __repr__(self) -> str:
        return f"DatasheetManager(space={self._space._space_id})"


__all__ = ['DatasheetManager']

import inspect
from typing import Any, Callable, Dict, Optional, TypeVar, Union, List
from pydantic import Field, BaseModel
import rs_fused_lib.api.udf_api as udf_api
import os
T = TypeVar('T')

class AttrDict(dict):
    """Dictionary where keys can also be accessed as attributes"""
    def __getattribute__(self, __name: str) -> Any:
        try:
            return super().__getattribute__(__name)
        except AttributeError:
            if __name in self:
                return self[__name]
            else:
                raise

    def __dir__(self) -> List[str]:
        return list(self.keys())

class UDF(BaseModel):
    """
    UDF基类，用于表示UDF函数
    """
    id: Optional[str] = Field(None, description="UDF ID")
    name: Optional[str] = Field(None, description="函数名")
    description: Optional[str] = Field(None, description="函数描述")
    func: Optional[Callable|None] = Field(None, description="函数")
    parameters: Optional[List[Dict[str, Any]]] = Field(None, description="函数参数")
    return_type: Optional[str] = Field(None, description="返回值类型")
    code: Optional[str] = Field(..., description="函数代码")
    code_path: Optional[str] = Field(None, description="函数代码路径")
    metadata_path: Optional[str] = Field(None, description="元数据路径")   
    author: Optional[str] = Field(None, description="作者")
    version: Optional[str] = Field(None, description="版本")
    created_at: Optional[str] = Field(None, description="创建时间")
    storage_path: Optional[str] = Field(None, description="存储路径")
    storage_type: Optional[str] = Field("temporary_file", description="存储类型")
    util_code: Optional[str] = Field(None, description="工具代码")
    util_code_path: Optional[str] = Field(None, description="工具代码路径")
    execute_step: Optional[list[dict]] = Field(default_factory=list, description="待执行步骤")
    
    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)
        
    def __str__(self):
        return f"UDF(name='{self.name}', description='{self.description}')"
        
    def __repr__(self):
        return self.__str__()
        
    def to_fused(
        self,
        overwrite: bool | None = None,
    ) -> 'UDF':
        func = self.func
        self.func = None
        try:
            saveResult = udf_api.save_udf(self.model_dump())
        finally:
            self.func = func
        return saveResult
    
    @property
    def utils(self):
        if self.util_code is None:
            return None
        import ast
        import types
        from dataclasses import dataclass
        
        @dataclass
        class PendingFunction:
            name: str
            args: list
            return_type: str
            code: str
            udf: 'UDF'
            
            def __call__(self, *args, **kwargs):
                step = {
                    'function': self.name,
                    'args': args,
                    'kwargs': kwargs,
                    'arg_types': dict(self.args),
                    'return_type': self.return_type,
                    'code': self.code,
                    'status': 'pending'
                }
                self.udf.execute_step.append(step)
                return self.udf
        
        utils_module = types.ModuleType('utils')
        
        tree = ast.parse(self.util_code.strip())
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                lines = self.util_code.strip().splitlines()
                func_code = '\n'.join(lines[node.lineno-1:node.end_lineno])
                
                func_ast = ast.parse(func_code)
                func_def = func_ast.body[0]
                
                args = []
                for arg in func_def.args.args:
                    arg_name = arg.arg
                    if hasattr(arg, 'annotation') and arg.annotation is not None:
                        if isinstance(arg.annotation, ast.Name):
                            arg_type = arg.annotation.id
                        elif isinstance(arg.annotation, ast.Attribute):
                            arg_type = f"{arg.annotation.value.id}.{arg.annotation.attr}"
                        elif isinstance(arg.annotation, ast.Constant):
                            arg_type = str(arg.annotation.value)
                        elif isinstance(arg.annotation, ast.Subscript):
                            value = arg.annotation.value
                            if isinstance(value, ast.Name):
                                arg_type = value.id
                            elif isinstance(value, ast.Attribute):
                                arg_type = f"{value.value.id}.{value.attr}"
                            else:
                                arg_type = 'Any'
                        else:
                            arg_type = 'Any'
                    else:
                        arg_type = 'Any'
                    args.append((arg_name, arg_type))
                    
                return_type = 'Any'
                if hasattr(func_def, 'returns') and func_def.returns is not None:
                    if isinstance(func_def.returns, ast.Name):
                        return_type = func_def.returns.id
                    elif isinstance(func_def.returns, ast.Attribute):
                        return_type = f"{func_def.returns.value.id}.{func_def.returns.attr}"
                    elif isinstance(func_def.returns, ast.Constant):
                        return_type = str(func_def.returns.value)
                    elif isinstance(func_def.returns, ast.Subscript):
                        value = func_def.returns.value
                        if isinstance(value, ast.Name):
                            return_type = value.id
                        elif isinstance(value, ast.Attribute):
                            return_type = f"{value.value.id}.{value.attr}"
                    
                pending_func = PendingFunction(
                    name=func_def.name,
                    args=args,
                    return_type=return_type,
                    code=func_code,
                    udf=self
                )
                
                setattr(utils_module, func_def.name, pending_func)
                    
        return utils_module
        
def udf(func: T = None) -> Union[Callable[[T], UDF], UDF]:
    if func is None:
        return udf
        
    # 获取函数定义的模块
    module = inspect.getmodule(func)
    if module is None or module.__name__ == '__main__':
        # 如果是__main__模块，尝试从函数对象获取全局变量
        module = func.__globals__
    
    # 获取源文件路径
    if isinstance(module, dict):
        file_path = module.get('__file__')
    else:
        file_path = getattr(module, '__file__', None)
    
    # 尝试加载对应的 _utils 文件
    util_code = None
    if file_path:
        # 构建 _utils 文件路径
        file_dir = os.path.dirname(file_path)
        file_name = os.path.splitext(os.path.basename(file_path))[0]
        utils_file_path = os.path.join(file_dir, f"{file_name}_utils.py")
        
        # 如果 _utils 文件存在，读取其内容
        if os.path.exists(utils_file_path):
            try:
                with open(utils_file_path, 'r', encoding='utf-8') as f:
                    util_code = f.read()
            except Exception as e:
                print(f"Warning: Failed to read utils file {utils_file_path}: {e}")
    
    # 获取所有引用的函数
    referenced_funcs = []  # 使用列表来保持顺序
    processed_funcs = set()  # 用于记录已处理的函数，避免循环引用
    
    if file_path:
        # 读取源文件内容
        with open(file_path, 'r') as f:
            file_content = f.read()
            
        # 使用ast解析源文件
        import ast
        tree = ast.parse(file_content)
        
        def collect_referenced_functions(func_node):
            """递归收集函数引用的其他函数"""
            if func_node.name in processed_funcs:
                return
            processed_funcs.add(func_node.name)
            
            # 收集当前函数中引用的所有名称
            referenced_names = set()
            for node in ast.walk(func_node):
                if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                    referenced_names.add(node.id)
            
            # 查找这些名称对应的函数定义
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    if node.name in referenced_names and not node.name == func_node.name:
                        # 获取函数源代码
                        start_line = node.lineno
                        end_line = node.end_lineno
                        lines = file_content.splitlines()
                        func_source = '\n'.join(lines[start_line-1:end_line])
                        if func_source and not func_source.strip().startswith('@udf'):
                            # 递归收集这个函数引用的其他函数
                            collect_referenced_functions(node)
                            # 添加当前函数的源代码
                            referenced_funcs.append(func_source)
        
        # 获取当前函数的AST节点
        current_func_node = None
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == func.__name__:
                current_func_node = node
                break
                
        if current_func_node:
            # 收集所有被引用的函数
            collect_referenced_functions(current_func_node)
            
            # 获取当前函数的源代码（不包括装饰器）
            start_line = current_func_node.lineno
            end_line = current_func_node.end_lineno
            lines = file_content.splitlines()
            # 跳过装饰器行
            while lines[start_line-1].strip().startswith('@'):
                start_line += 1
            main_func_source = '\n'.join(lines[start_line-1:end_line])
            referenced_funcs.append(main_func_source)
    
    # 使用被引用的函数代码，确保依赖函数在前
    full_code = '\n'.join(referenced_funcs)
        
    udf_instance = UDF(
        func=func,
        name=func.__name__,
        description=func.__doc__,
        parameters= [{"name": k, "type": str(v), "description": func.__annotations__[k].__doc__} for k, v in func.__annotations__.items() if k != 'return'],
        return_type=str(func.__annotations__['return']),
        code=full_code,
        author=func.__author__ if hasattr(func, '__author__') else None,
        version=func.__version__ if hasattr(func, '__version__') else None,
        util_code=util_code  # 添加 util_code
    )
    return udf_instance


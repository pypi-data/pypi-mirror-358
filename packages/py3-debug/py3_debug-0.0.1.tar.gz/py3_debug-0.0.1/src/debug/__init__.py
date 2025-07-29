import functools
import inspect
import logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# 创建控制台 handler
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
# 添加到 logger
logger.addHandler(ch)
# 添加格式：包含 pathname 和 lineno（用于 PyCharm 点击跳转）

# 添加到 logger
logger.addHandler(ch)

def log_method_call(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        frame = inspect.currentframe()
        try:
            code_context = inspect.getframeinfo(frame.f_back)
            file_path = code_context.filename
            line_number = code_context.lineno

            # 记录方法调用
            calling_msg = f"{file_path}:{line_number} - Calling {func.__name__}"
            logger.debug(calling_msg)

            # 获取参数（去掉 self）
            params = {
                k: repr(v) for k, v in inspect.getcallargs(func, *args, **kwargs).items()
                if k != 'self'
            }
            params_msg = f"{file_path}:{line_number} - Parameters: {params}"
            logger.debug(params_msg)

            result = func(*args, **kwargs)

            # 记录返回值
            returned_msg = f"{file_path}:{line_number} - Returned: {repr(result)}"
            logger.debug(returned_msg)

            return result
        finally:
            del frame
    return wrapper

def debug(cls):
    for name, method in inspect.getmembers(cls, predicate=inspect.isfunction):
        if not (name.startswith('__') and name.endswith('__')):  # 排除魔术方法
            setattr(cls, name, log_method_call(method))
    return cls


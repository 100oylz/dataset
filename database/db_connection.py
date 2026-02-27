"""
数据库连接模块

提供 MySQL 数据库连接管理和连接池功能
使用 pymysql 作为驱动
"""

import os
import logging
from contextlib import contextmanager
from typing import Any, Dict, List, Optional, Tuple, Union

import pymysql
from pymysql.cursors import DictCursor
from pymysql.connections import Connection

# 配置日志
logger = logging.getLogger(__name__)


class DatabaseConfig:
    """
    数据库配置类
    
    从环境变量读取配置，支持 direnv 加载
    """
    
    def __init__(self):
        """从环境变量初始化配置"""
        self.host = os.getenv("MYSQL_HOST", "localhost")
        self.port = int(os.getenv("MYSQL_PORT", "3306"))
        self.database = os.getenv("MYSQL_DATABASE", "fl_dataset_db")
        self.user = os.getenv("MYSQL_USER", "fl_user")
        self.password = os.getenv("MYSQL_PASSWORD", "flpassword")
        self.root_password = os.getenv("MYSQL_ROOT_PASSWORD", "rootpassword")
        
        # 连接池配置
        self.pool_size = int(os.getenv("MYSQL_POOL_SIZE", "5"))
        self.max_overflow = int(os.getenv("MYSQL_MAX_OVERFLOW", "10"))
        self.pool_timeout = int(os.getenv("MYSQL_POOL_TIMEOUT", "30"))
        self.pool_recycle = int(os.getenv("MYSQL_POOL_RECYCLE", "3600"))
    
    @property
    def connection_params(self) -> Dict[str, Any]:
        """获取连接参数字典"""
        return {
            "host": self.host,
            "port": self.port,
            "database": self.database,
            "user": self.user,
            "password": self.password,
            "charset": "utf8mb4",
            "cursorclass": DictCursor,
            "autocommit": False,
        }
    
    @property
    def database_url(self) -> str:
        """获取数据库 URL"""
        return (
            f"mysql+pymysql://{self.user}:{self.password}"
            f"@{self.host}:{self.port}/{self.database}?charset=utf8mb4"
        )
    
    def __repr__(self) -> str:
        return f"DatabaseConfig({self.host}:{self.port}/{self.database})"


class DatabaseConnection:
    """
    数据库连接管理器
    
    单例模式管理数据库连接
    """
    
    _instance = None
    _config: Optional[DatabaseConfig] = None
    _connection: Optional[Connection] = None
    
    def __new__(cls):
        """单例模式"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, config: Optional[DatabaseConfig] = None):
        """
        初始化数据库连接
        
        Args:
            config: 数据库配置，如果为 None 则使用默认配置
        """
        if config is not None:
            self._config = config
        elif self._config is None:
            self._config = DatabaseConfig()
    
    @property
    def config(self) -> DatabaseConfig:
        """获取当前配置"""
        if self._config is None:
            self._config = DatabaseConfig()
        return self._config
    
    def connect(self) -> Connection:
        """
        建立数据库连接
        
        Returns:
            数据库连接对象
            
        Raises:
            pymysql.Error: 连接失败
        """
        try:
            if self._connection is None or not self._connection.open:
                self._connection = pymysql.connect(**self.config.connection_params)
                logger.info(f"数据库连接已建立: {self.config}")
            return self._connection
        except pymysql.Error as e:
            logger.error(f"数据库连接失败: {e}")
            raise
    
    def close(self) -> None:
        """关闭数据库连接"""
        if self._connection and self._connection.open:
            self._connection.close()
            self._connection = None
            logger.info("数据库连接已关闭")
    
    def is_connected(self) -> bool:
        """检查连接是否有效"""
        try:
            if self._connection and self._connection.open:
                # 发送 ping 检查连接
                self._connection.ping(reconnect=False)
                return True
            return False
        except pymysql.Error:
            return False
    
    def reconnect(self) -> Connection:
        """重新建立连接"""
        self.close()
        return self.connect()
    
    @contextmanager
    def cursor(self):
        """
        获取数据库游标的上下文管理器
        
        使用示例：
            with db.cursor() as cursor:
                cursor.execute("SELECT * FROM table")
                result = cursor.fetchall()
        """
        conn = self.connect()
        cursor = conn.cursor()
        try:
            yield cursor
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"数据库操作失败: {e}")
            raise
        finally:
            cursor.close()
    
    @contextmanager
    def transaction(self):
        """
        事务上下文管理器
        
        使用示例：
            with db.transaction() as cursor:
                cursor.execute("INSERT INTO table ...")
                cursor.execute("UPDATE table ...")
        """
        conn = self.connect()
        cursor = conn.cursor()
        try:
            yield cursor
            conn.commit()
            logger.debug("事务已提交")
        except Exception as e:
            conn.rollback()
            logger.error(f"事务回滚: {e}")
            raise
        finally:
            cursor.close()
    
    def execute(
        self,
        sql: str,
        params: Optional[Union[Tuple, Dict]] = None
    ) -> int:
        """
        执行 SQL 语句
        
        Args:
            sql: SQL 语句
            params: 参数
            
        Returns:
            受影响的行数
        """
        with self.cursor() as cursor:
            return cursor.execute(sql, params)
    
    def fetchone(
        self,
        sql: str,
        params: Optional[Union[Tuple, Dict]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        查询单条记录
        
        Args:
            sql: SQL 语句
            params: 参数
            
        Returns:
            单条记录字典，无结果返回 None
        """
        with self.cursor() as cursor:
            cursor.execute(sql, params)
            return cursor.fetchone()
    
    def fetchall(
        self,
        sql: str,
        params: Optional[Union[Tuple, Dict]] = None
    ) -> List[Dict[str, Any]]:
        """
        查询多条记录
        
        Args:
            sql: SQL 语句
            params: 参数
            
        Returns:
            记录字典列表
        """
        with self.cursor() as cursor:
            cursor.execute(sql, params)
            return cursor.fetchall()
    
    def insert(
        self,
        table: str,
        data: Dict[str, Any],
        ignore: bool = False
    ) -> int:
        """
        插入数据
        
        Args:
            table: 表名
            data: 数据字典
            ignore: 是否使用 INSERT IGNORE
            
        Returns:
            新插入记录的主键 ID
        """
        columns = ', '.join(f"`{k}`" for k in data.keys())
        placeholders = ', '.join(['%s'] * len(data))
        
        ignore_str = "IGNORE" if ignore else ""
        sql = f"INSERT {ignore_str} INTO `{table}` ({columns}) VALUES ({placeholders})"
        
        with self.cursor() as cursor:
            cursor.execute(sql, tuple(data.values()))
            return cursor.lastrowid
    
    def update(
        self,
        table: str,
        data: Dict[str, Any],
        where: str,
        where_params: Optional[Union[Tuple, Dict]] = None
    ) -> int:
        """
        更新数据
        
        Args:
            table: 表名
            data: 更新数据字典
            where: WHERE 条件
            where_params: WHERE 参数
            
        Returns:
            受影响的行数
        """
        set_clause = ', '.join(f"`{k}` = %s" for k in data.keys())
        sql = f"UPDATE `{table}` SET {set_clause} WHERE {where}"
        
        params = tuple(data.values())
        if where_params:
            if isinstance(where_params, dict):
                params += tuple(where_params.values())
            else:
                params += tuple(where_params)
        
        with self.cursor() as cursor:
            return cursor.execute(sql, params)
    
    def delete(
        self,
        table: str,
        where: str,
        params: Optional[Union[Tuple, Dict]] = None
    ) -> int:
        """
        删除数据
        
        Args:
            table: 表名
            where: WHERE 条件
            params: 参数
            
        Returns:
            受影响的行数
        """
        sql = f"DELETE FROM `{table}` WHERE {where}"
        with self.cursor() as cursor:
            return cursor.execute(sql, params)


# 全局数据库连接实例
db = DatabaseConnection()


def get_db() -> DatabaseConnection:
    """
    获取数据库连接实例
    
    Returns:
        DatabaseConnection 实例
    """
    return db


def init_database() -> bool:
    """
    初始化数据库连接并测试
    
    Returns:
        是否初始化成功
    """
    try:
        config = DatabaseConfig()
        logger.info(f"正在连接数据库: {config.host}:{config.port}/{config.database}")
        
        connection = DatabaseConnection(config)
        if connection.is_connected():
            logger.info("数据库连接成功")
            return True
        
        # 尝试连接
        connection.connect()
        logger.info("数据库初始化成功")
        return True
        
    except pymysql.Error as e:
        logger.error(f"数据库初始化失败: {e}")
        return False


def close_database() -> None:
    """关闭数据库连接"""
    db.close()

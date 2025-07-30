import os
from contextlib import asynccontextmanager

import aiosqlite
from nonebot import logger

from ..config import g_bIsDebug, g_pConfigManager, g_sPlantPath, g_sResourcePath
from ..request import g_pRequestManager


class CPlantManager:
    def __init__(self):
        try:
            os.mkdir(g_sPlantPath)
        except FileExistsError:
            pass

    @classmethod
    async def cleanup(cls):
        if hasattr(cls, "m_pDB") and cls.m_pDB:
            await cls.m_pDB.close()

    @classmethod
    async def init(cls) -> bool:
        try:
            _ = os.path.exists(g_sPlantPath)

            if g_bIsDebug:
                cls.m_pDB = await aiosqlite.connect(
                    str(g_sPlantPath.parent / "plant-test.db")
                )
            else:
                cls.m_pDB = await aiosqlite.connect(str(g_sPlantPath))

            cls.m_pDB.row_factory = aiosqlite.Row
            return True
        except Exception as e:
            logger.warning("初始化植物数据库失败", e=e)
            return False

    @classmethod
    @asynccontextmanager
    async def _transaction(cls):
        await cls.m_pDB.execute("BEGIN;")
        try:
            yield
        except:
            await cls.m_pDB.execute("ROLLBACK;")
            raise
        else:
            await cls.m_pDB.execute("COMMIT;")

    @classmethod
    async def executeDB(cls, command: str) -> bool:
        """执行自定义SQL

        Args:
            command (str): SQL语句

        Returns:
            bool: 是否执行成功
        """
        if not command:
            logger.warning("数据库语句长度为空！")
            return False

        try:
            async with cls._transaction():
                await cls.m_pDB.execute(command)
            return True
        except Exception as e:
            logger.warning(f"数据库语句执行出错: {command}", e=e)
            return False

    @classmethod
    async def getPlantByName(cls, name: str) -> dict | None:
        """根据作物名称查询记录

        Args:
            name (str): 作物名称

        Returns:
            dict | None: 返回记录字典，未找到返回None
        """
        try:
            async with cls.m_pDB.execute(
                "SELECT * FROM plant WHERE name = ?", (name,)
            ) as cursor:
                row = await cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            logger.warning(f"查询作物失败: {name}", e=e)
            return None

    @classmethod
    async def getPlantPhaseByName(cls, name: str) -> list[int]:
        """根据作物名称获取作物各个阶段

        Args:
            name (str): 作物名称

        Returns:
            list: 阶段数组
        """
        try:
            async with cls.m_pDB.execute(
                "SELECT phase FROM plant WHERE name = ?", (name,)
            ) as cursor:
                row = await cursor.fetchone()

                if not row:
                    return []

                phase = row[0].split(",")

                seen = set()
                result = []

                for x in phase:
                    num = int(x)

                    if num not in seen:
                        seen.add(num)
                        result.append(num)

                return result
        except Exception as e:
            logger.warning(f"查询作物阶段失败: {name}", e=e)
            return []

    @classmethod
    async def getPlantPhaseNumberByName(cls, name: str) -> int:
        """根据作物名称获取作物总阶段数

        Args:
            name (str): 作物名称

        Returns:
            int: 总阶段数
        """
        try:
            async with cls.m_pDB.execute(
                "SELECT phase FROM plant WHERE name = ?", (name,)
            ) as cursor:
                row = await cursor.fetchone()

                if not row:
                    return -1

                phase = row[0].split(",")

                # 去重
                seen = set()
                result = []
                for x in phase:
                    if x not in seen:
                        seen.add(x)
                        result.append(x)

                return len(result)
        except Exception as e:
            logger.warning(f"查询作物阶段失败: {name}", e=e)
            return -1

    @classmethod
    async def getPlantAgainByName(cls, name: str) -> int:
        """根据作物名称获取作物再次成熟时间

        Args:
            name (str): 作物名称

        Returns:
            int: 再次成熟时间 单位:h
        """

        try:
            async with cls.m_pDB.execute(
                "SELECT phase FROM plant WHERE name = ?", (name,)
            ) as cursor:
                row = await cursor.fetchone()

                if not row:
                    return -1

                phase = row[0].split(",")
                again = phase[-1] - phase[3] / 60 / 60

                return again

        except Exception as e:
            logger.warning(f"查询作物阶段失败: {name}", e=e)
            return -1

    @classmethod
    async def existsPlant(cls, name: str) -> bool:
        """判断作物是否存在

        Args:
            name (str): 作物名称

        Returns:
            bool: 存在返回True，否则False
        """
        try:
            async with cls.m_pDB.execute(
                "SELECT 1 FROM plant WHERE name = ? LIMIT 1", (name,)
            ) as cursor:
                row = await cursor.fetchone()
                return True if row else False
        except Exception as e:
            logger.warning(f"检查作物存在性失败: {name}", e=e)
            return False

    @classmethod
    async def countPlants(cls, onlyBuy: bool = False) -> int:
        """获取作物总数

        Args:
            onlyBuy (bool): 若为True，仅统计isBuy=1的记录，默认False

        Returns:
            int: 符合条件的记录数
        """
        try:
            if onlyBuy:
                sql = "SELECT COUNT(*) FROM plant WHERE isBuy = 1"
                params: tuple = ()
            else:
                sql = "SELECT COUNT(*) FROM plant"
                params: tuple = ()
            async with cls.m_pDB.execute(sql, params) as cursor:
                row = await cursor.fetchone()
                return row[0] if row else 0
        except Exception as e:
            logger.warning(f"统计作物数量失败, onlyBuy={onlyBuy}", e=e)
            return 0

    @classmethod
    async def listPlants(cls) -> list[dict]:
        """查询所有作物记录"""
        try:
            async with cls.m_pDB.execute(
                "SELECT * FROM plant ORDER BY level"
            ) as cursor:
                rows = await cursor.fetchall()
                return [dict(r) for r in rows]
        except Exception as e:
            logger.warning("查询所有作物失败", e=e)
            return []

    @classmethod
    async def downloadPlant(cls) -> bool:
        """遍历所有作物，下载各阶段图片及icon文件到指定文件夹

        Returns:
            bool: 全部下载完成返回True，如有失败返回False
        """
        success = True
        baseUrl = g_pConfigManager.farm_server_url

        baseUrl = baseUrl.rstrip("/") + ":8998/file"
        try:
            plants = await cls.listPlants()
            for plant in plants:
                name = plant["name"]
                phaseCount = await cls.getPlantPhaseNumberByName(name)
                saveDir = os.path.join(g_sResourcePath, "plant", name)
                begin = 0 if plant["general"] == 0 else 1

                for idx in range(begin, phaseCount + 1):
                    fileName = f"{idx}.png"
                    fullPath = os.path.join(saveDir, fileName)

                    if os.path.exists(fullPath):
                        continue

                    url = f"{baseUrl}/{name}/{idx}.png"
                    if not await g_pRequestManager.download(url, saveDir, f"{idx}.png"):
                        success = False

                iconName = "icon.png"
                iconPath = os.path.join(saveDir, iconName)
                if not os.path.exists(iconPath):
                    iconUrl = f"{baseUrl}/{name}/{iconName}"
                    if not await g_pRequestManager.download(iconUrl, saveDir, iconName):
                        success = False

            return success
        except Exception as e:
            logger.warning(f"下载作物资源异常: {e}")
            return False

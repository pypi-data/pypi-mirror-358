from pathlib import Path

from nonebot import require
from nonebot.plugin import get_plugin_config
from pydantic import BaseModel

require("nonebot_plugin_localstore")

import nonebot_plugin_localstore as store

# 签到状态
g_bSignStatus = True

# 是否处于Debug模式
g_bIsDebug = False

# 数据库文件目录
g_sDBPath = store.get_plugin_data_dir() / "nonebot_plugin_farm/farm_db"

# 数据库文件路径
g_sDBFilePath = g_sDBPath / "farm.db"

# 农场资源文件目录
g_sResourcePath = Path(__file__).resolve().parent / "resource"

# 农场作物数据库
g_sPlantPath = g_sResourcePath / "db/plant.db"

# 农场配置文件目录
g_sConfigPath = Path(__file__).resolve().parent / "config"

# 农场签到文件路径
g_sSignInPath = g_sConfigPath / "sign_in.json"

# 土地等级上限
g_iSoilLevelMax = 3

# 农场同一文本
g_sTranslation = {
    "basic": {
        "notFarm": "尚未开通农场，快at我发送 开通农场 开通吧 🌱🚜",
        "point": "你的当前农场币为: {point} 🌾💰",
    },
    "register": {
        "success": "✅ 农场开通成功！\n💼 初始资金：{point}农场币 🥳🎉",
        "repeat": "🎉 您已经开通农场啦~ 😄",
        "error": "⚠️ 开通失败，请稍后再试 💔",
    },
    "buySeed": {
        "notSeed": "🌱 请在指令后跟需要购买的种子名称",
        "notNum": "❗️ 请输入购买数量！",
        "noLevel": "🔒 你的等级不够哦，努努力吧 💪",
        "noPoint": "💰 你的农场币不够哦~ 快速速氪金吧！💸",
        "success": "✅ 成功购买{name}，花费{total}农场币，剩余{point}农场币 🌾",
        "errorSql": "❌ 购买失败，执行数据库错误！🛑",
        "error": "❌ 购买出错！请检查需购买的种子名称！🔍",
    },
    "sowing": {
        "notSeed": "🌱 请在指令后跟需要播种的种子名称",
        "noSeed": "❌ 没有在你的仓库发现{name}种子，快去买点吧！🛒",
        "noNum": "⚠️ 播种失败！仓库中的{name}种子数量不足，当前剩余{num}个种子 🍂",
        "success": "✅ 播种{name}成功！仓库剩余{num}个种子 🌱",
        "success2": "✅ 播种数量超出开垦土地数量，已将可播种土地成功播种{name}！仓库剩余{num}个种子 🌾",
        "error": "❌ 播种失败，请稍后重试！⏳",
    },
    "harvest": {
        "append": "🌾 收获作物：{name}，数量为：{num}，经验为：{exp} ✨",
        "exp": "✨ 累计获得经验：{exp} 📈",
        "no": "🤷‍♂️ 没有可收获的作物哦~ 不要试图拔苗助长 🚫",
        "error": "❌ 收获失败，请稍后重试！⏳",
    },
    "eradicate": {
        "success": "🗑️ 成功铲除荒废作物，累计获得经验：{exp} ✨",
        "error": "❌ 没有可以铲除的作物 🚜",
    },
    "reclamation": {
        "confirm": "⚠️ 回复“是”将执行开垦 ⛏️",
        "timeOut": "⏰ 等待开垦回复超时，请重试",
        "perfect": "🌟 你已经开垦了全部土地 🎉",
        "next": "🔜 下次开垦所需条件：等级：{level}，农场币：{num} 💰",
        "next2": "🔜 下次开垦所需条件：等级：{level}，农场币：{num}，物品：{item} 📦",
        "nextLevel": "📈 当前用户等级{level}，升级所需等级为{next} ⏳",
        "noNum": "💰 当前用户农场币不足，升级所需农场币为{num} 💸",
        "success": "✅ 开垦土地成功！🌱",
        "error": "❌ 获取开垦土地条件失败！",
        "error1": "❌ 执行开垦失败！",
        "error2": "❌ 未知错误{e}💥",
    },
    "sellPlant": {
        "no": "🤷‍♀️ 你仓库没有可以出售的作物 🌾",
        "success": "💰 成功出售所有作物，获得农场币：{point}，当前农场币：{num} 🎉",
        "success1": "💰 成功出售{name}，获得农场币：{point}，当前农场币：{num} 🥳",
        "error": "❌ 出售作物{name}出错：仓库中不存在该作物 🚫",
        "error1": "❌ 出售作物{name}出错：数量不足 ⚠️",
    },
    "stealing": {
        "noTarget": "🎯 请在指令后跟需要at的人 👤",
        "targetNotFarm": "🚜 目标尚未开通农场，快邀请ta开通吧 😉",
        "max": "❌ 你今天可偷次数到达上限啦，手下留情吧 🙏",
        "info": "🤫 成功偷到作物：{name}，数量为：{num} 🍒",
        "noPlant": "🌱 目标没有作物可以被偷 🌾",
        "repeat": "🚫 你已经偷过目标啦，请手下留情 🙏",
    },
    "changeName": {
        "noName": "✏️ 请在指令后跟需要更改的农场名",
        "success": "✅ 更新农场名成功！🎉",
        "error": "❌ 农场名不支持特殊符号！🚫",
        "error1": "❌ 更新农场名失败！💔",
    },
    "signIn": {
        "success": "📝 签到成功！累计签到天数：{day}\n🎁 获得经验{exp}，获得金币{num} 💰",
        "grandTotal": "\n🎉 成功领取累计签到奖励：\n✨ 额外获得经验{exp}，额外获得金币{num} 🥳",
        "grandTotal1": "，额外获得点券{num} 🎫",
        "grandTotal2": "\n🌱 获得{name}种子 * {num} 🌟",
        "error": "❗️ 签到功能异常！",
        "error1": "❌ 签到失败！未知错误 💔",
    },
    "soilInfo": {
        "success": "土地成功升级至{name}，效果为：{text}",
        "timeOut": "等待土地升级回复超时，请重试",
        "error": "土地信息尚未查询到",
        "error1": "该土地已经升至满级啦~",
        "red": "增产+10%",
        "black": "增产+20% 时间-20%",
        "gold": "增产+28% 经验+28% 时间-20%",
        "amethyst": "增产+30% 经验+30% 时间-25% 幸运+1%",
        "aquamarine": "增产+32% 经验+32% 时间-28% 幸运+1%",
        "blackcrystal": "增产+32% 经验+40% 时间-28% 幸运+2%",
    },
}


class Config(BaseModel):
    farm_draw_quality: str = "low"
    farm_server_url: str = "http://diuse.work"


g_pConfigManager = get_plugin_config(Config)

from mcp.server.fastmcp import FastMCP  # 使用工具期望的路径
import random

mcp = FastMCP("JsonDiffServiceTest")

# json对比工具
@mcp.tool()
def jsonDiff(expectKey, actualKey) -> str:
    """执行json字符串对比"""
    random_number = random.random()
    if random_number > 0.5:
        return "{\"is_identical\":false,\"message\":{\"consensus_count\":2,\"disconsensus_count\":1,\"summary\":\"结论:核验失败。运营输入3条，后台配置3条,一致数量2条，不一致数量1条。\",\"expected_count\":3,\"actual_count\":3},\"differences\":{\"values_changed\":{\"root[2]['startSegKm']\":{\"new_value\":25,\"old_value\":5}}}}"
    else:
        return "{\"differences\":{},\"is_identical\":true,\"message\":{\"consensus_count\":3,\"disconsensus_count\":0,\"summary\":\"结论:核验成功。运营输入3条，后台配置3条,一致数量3条，不一致数量0条。\",\"expected_count\":3,\"actual_count\":3}}"


if __name__ == "__main__":
    mcp.run(transport="stdio")
# Create server parameters for stdio connection
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
import asyncio
from Base.selectLLM import selectLLM
from Base.Constant.runConfig import RUN_MODE


llm = selectLLM(str(RUN_MODE.value))


server_params = StdioServerParameters(  
    command="python",
    # Make sure to update to the full absolute path to your ARL_server.py file
    args=["ARL_server.py"],
)


async def run_agent():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await load_mcp_tools(session)

            # 创建智能代理
            agent = create_react_agent(llm, tools)

            # 输入内容（数据包 + 描述）
            # user_prompt = """
            # 这是一个 HTTP 数据包：
            #
            # GET /api/getLastVersionByName/8627.json HTTP/1.1
            # accept: */*
            # Connection: keep-alive
            # Content-Type: application/octet-stream
            # User-Agent: Dalvik/2.1.0 (Linux; U; Android 12; Pixel 4 Build/SP1A.210812.015)
            # Host: qsjs.dzhsj.cn:8413
            # Accept-Encoding: gzip, deflate, br
            #
            # 请你从这个数据包中提取 Host 中的主域名，
            # 然后调用合适的工具，列出该主域名下的所有子域名。
            # 先创建任务，然后等待任务完成后再获取子域名。
            # """
            user_prompt = """
                       dzhsj.cn 然后调用合适的工具，列出该主域名下的所有文件泄露。
                       """

            result = await agent.ainvoke({"messages": user_prompt}, config={"recursion_limit": 1000})
            return result

# Run the async function
if __name__ == "__main__":

    result = asyncio.run(run_agent())
    print(result["messages"])
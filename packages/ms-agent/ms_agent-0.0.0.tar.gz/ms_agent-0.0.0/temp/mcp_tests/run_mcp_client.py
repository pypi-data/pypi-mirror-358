from datetime import datetime
from ms_agent.tools.mcp.mcp_client import MCPClient


DEFAULT_SYSTEM = f"""You are an assistant that helps generate comprehensive documentations or \
webpages from gathered information. Today is {datetime.now().strftime("%Y-%m-%d")}.

    ## Planning

    You need to create a CONCISE, FOCUSED plan with ONLY meaningful, actionable steps, \
    rely on the plan after you made it.

    If you are making website, just make one single step for writing code to avoid too much messages. \
    When developing a website, please implement complete and ready-to-use code. \
    There is no need to save space when implementing the code. Please implement every line of code. \
    Use proper event delegation or direct event binding

    Give your final result(documentation/code) in <result></result> block.

    Here shows a plan example:

     ```
    1. Research & Content Gathering:
       1.1. Search and collect comprehensive information on [topic] using user's language
       1.2. Identify and crawl authoritative sources for detailed content
       1.3. Crawl enough high-quality medias(e.g. image links) from compatible platforms

    2. Content Creation & Organization:
       2.1. Develop main content sections with complete information
       2.3. Organize information with logical hierarchy and flow

    3. Design & Animation Implementation:
       3.1. Create responsive layout with modern aesthetic, with all the useful information collected
       3.2. Implement key animations for enhanced user experience
       3.3. Write the final code...
    ```

    When executing specific task steps, please pay attention to the consistency of the previous and next content. \
    When generating a series of images, you need to ensure that the images are generated consistently. \
    Please clearly describe the main features such as color, type, and shape when generating each image.

    History messages of the previous main step will not be kept, \
    so you need to WRITE a concise but essential summary_and_result \
    when calling `notebook---advance_to_next_step` for each sub-step.
    In the later steps, you can only see the plans you made and the summary_and_result from the previous steps.
    So you must MINIMIZE DEPENDENCIES between the the steps in the plan.
    Note: The URL needs to retain complete information.

    Here are some summary_and_result examples:

    · Topic X has three primary categories: A, B, and C
    · Latest statistics show 45% increase in adoption since 2023
    · Expert consensus indicates approach Y is most effective
    · Primary source: https://example.com/comprehensive-guide (contains detailed sections on implementation)
    · Images: ["https://example.com/image1.jpg?Expires=a&KeyId=b&Signature=c", "https://example.com/image2.jpg", \
    "https://example.com/diagram.png"] (Please copy the entire content of the url without doing any changes)
    · Reference documentation: https://docs.example.com/api (sections 3.2-3.4 particularly relevant)
    · Will focus on mobile-first approach due to 78% of users accessing via mobile devices
    · Selected blue/green color scheme based on industry standards and brand compatibility
    · Decided to implement tabbed interface for complex data presentation
    · CODE:
    ```
    ... # complete and ready-to-use code here
    ```
    """

async def main():


    mcp_servers = {'mcpServers': {'MiniMax-MCP': {'type': 'sse', 'url': 'https://mcp.api-inference.modelscope.cn/sse/0c73b1853bab4b'}, 'amap-maps': {'type': 'sse', 'url': 'https://mcp.api-inference.modelscope.cn/sse/6d2f001a63354d'}, 'edgeone-pages-mcp': {'type': 'sse', 'url': 'https://mcp.api-inference.modelscope.cn/sse/84bbb7e9777b4e'}, 'notebook': {}}}
    api_config = {'api_key': '42cdfb50-a8e4-41a1-a28a-869b36cf720e', 'model': 'Qwen/Qwen3-235B-A22B', 'model_server': 'https://api-inference.modelscope.cn/v1/', 'model_type': 'openai_fn_call'}

    kwargs = {}
    if 'qwen3' in api_config['model'].lower():
        kwargs.update({'stream': True, 'max_tokens': 16384, 'extra_body': {'enable_thinking': False}})
    elif 'claude' in api_config['model'].lower():
        kwargs.update({'max_tokens': 64000})

    client = MCPClient(
        mcp_servers=mcp_servers,
        api_config=api_config,
    )

    try:
        # query = "查找阿里云谷园区附近咖啡馆"
        # query = "做一个图文并茂的绘本故事，部署成一个网页。"
        query = "找一下杭州云谷园区周围的咖啡厅"
        messages = [
            {
                'role': 'system',
                'content': DEFAULT_SYSTEM,
            },
            {
                'role': 'user',
                'content': query,
            },
        ]
        await client.connect_all_servers(None)

        async for chunk in client.process_query(messages=messages, **kwargs):
            print(f'{chunk}', end='', flush=True)
    finally:
        await client.cleanup()


if __name__ == '__main__':
    import asyncio
    asyncio.run(main())


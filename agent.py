import asyncio
import requests
import xml.etree.ElementTree as ET
import sys
from mcp_agent.core.fastagent import FastAgent
from mcp_agent.core.direct_decorators import agent

fast = FastAgent("SiteMapCrawler")

def fetch_sitemap_urls(sitemap_url):
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
    }
    response = requests.get(sitemap_url, headers=headers)
    print(f"[DEBUG] Fetched: {sitemap_url} (status: {response.status_code})")
    if response.status_code != 200:
        raise Exception(f"Failed to fetch sitemap from {sitemap_url}. Status code: {response.status_code}")
    namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
    root = ET.fromstring(response.content)
    urls = [loc.text for loc in root.findall('.//ns:loc', namespace) if loc.text]
    print(f"[DEBUG] Extracted {len(urls)} URLs. First 10: {urls[:10]}")
    return urls

@fast.agent(
    "metrics_generator_agent",
    instruction="Given the full content of a website's root page (Markdown or HTML), extract a list of important page types, categories, or features that should be prioritized for crawling (e.g., API reference, documentation, tutorials, release notes, etc). Return a Python list of keywords or patterns that can be used to evaluate the importance of URLs in the sitemap."
)
async def metrics_generator_agent(agent, root_content: str):
    pass

def url_evaluator_agent(urls, metrics):
    results = []
    for url in urls:
        score = "LOW"
        for kw in metrics:
            if kw.lower() in url.lower():
                score = "HIGH"
                break
        results.append({"url": url, "score": score})
    print(f"[DEBUG] url_evaluator_agent: {sum(1 for r in results if r['score']=='HIGH')} HIGH, {sum(1 for r in results if r['score']=='LOW')} LOW")
    return results

@fast.agent(
    "content_fetcher_agent",
    instruction="Fetch the content of the given URL as Markdown using Fetch MCP.",
    servers=["fetch"]
)
async def content_fetcher_agent(agent, url: str):
    try:
        markdown = await agent.mcp.fetch.fetch_markdown(url=url, max_length=100000)
        if isinstance(markdown, str):
            return markdown
        else:
            return "[ERROR] fetch_markdown did not return string"
    except Exception as e:
        return f"[ERROR] Exception: {e}"

@fast.agent(
    "content_cleaner_agent",
    instruction="Given the Markdown content of a web page, remove navigation, footer, sidebar, ads, duplicated explanations, and error messages. Do NOT summarize or rewrite the content, just remove obvious noise and keep the main text as Markdown. Return only the cleaned Markdown."
)
async def content_cleaner_agent(agent, markdown: str):
    pass

def save_crawled_content(contents, filename="site_crawl_result.md"):
    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n\n".join(contents))
    print(f"[INFO] Saved {len(contents)} pages to {filename}")

async def main():
    # ユーザ入力からroot URLを受け付ける
    if len(sys.argv) > 1:
        root_url = sys.argv[1]
    else:
        root_url = input("Enter the root URL (e.g. https://fast-agent.ai/): ").strip()
    if not root_url.startswith("http"):
        print("Please provide a valid URL (e.g. https://example.com/)")
        return
    sitemap_url = root_url.rstrip("/") + "/sitemap.xml"
    urls = fetch_sitemap_urls(sitemap_url)
    async with fast.run() as agent:
        print(f"[INFO] Fetching root page: {root_url}")
        root_content = await agent.content_fetcher_agent(root_url)
        print(f"[INFO] Generating evaluation metrics from root page content...")
        metrics = await agent.metrics_generator_agent(root_content)
        print(f"[INFO] Metrics generated: {metrics}")
        evaluated = url_evaluator_agent(urls, metrics)
        target_urls = [r["url"] for r in evaluated if r["score"] == "HIGH"]
        print(f"[INFO] Fetching and cleaning content for {len(target_urls)} URLs via Fetch MCP + LLM...")
        contents = []
        for url in target_urls:
            print(f"[INFO] Fetching: {url}")
            markdown = await agent.content_fetcher_agent(url)
            cleaned = await agent.content_cleaner_agent(markdown)
            contents.append(f"# {url}\n\n{cleaned}\n")
    save_crawled_content(contents)

if __name__ == "__main__":
    asyncio.run(main())
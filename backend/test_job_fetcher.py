import asyncio
from app.services.job_fetcher.service import JobFetcher

async def main():
    job_fetcher = JobFetcher()
    results = await job_fetcher.search_jobs("Software Engineer Intern", limit=20)
    for job in results:
        print(f"{job.title} - {job.company} ({job.location})")

if __name__ == "__main__":
    asyncio.run(main())

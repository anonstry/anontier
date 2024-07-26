from dynaconf import settings
from hydrogram import Client

# from git.repo import Repo
# from apscheduler.schedulers.asyncio import AsyncIOScheduler

client: Client = Client(
    name=settings.TELEGRAM_APP_NAME,
    api_id=settings.TELEGRAM_API_ID,
    api_hash=settings.TELEGRAM_API_HASH,
    bot_token=settings.TELEGRAM_BOT_TOKEN,
)

# repository = Repo(search_parent_directories=True)

# latest_repository_tag = sorted(
#     repository.tags, key=lambda tag: tag.commit.committed_datetime
# )[-1].name
# latest_repository_commit_shorted = repository.git.rev_parse(
#     repository.head.commit.hexsha, short=True
# )
# print(f"Lastest repository tag is: {latest_repository_tag}")
# print(f"Lastest repository commit shorted is {latest_repository_commit_shorted}")

# scheduler = AsyncIOScheduler()

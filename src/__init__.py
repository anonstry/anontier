from dynaconf import settings
from hydrogram.client import Client

# from git.repo import Repo
# from apscheduler.schedulers.asyncio import AsyncIOScheduler

client: Client = Client(
    name=settings.TELEGRAM_APP_NAME,
    api_id=settings.TELEGRAM_API_ID,
    api_hash=settings.TELEGRAM_API_HASH,
    bot_token=settings.TELEGRAM_BOT_TOKEN,
    plugins=dict(root="src.modules"),
    # plugins=dict(root="src.modules", exclude=["experimental"]),
)

# instancies = dict() # With all clients


# git_repository = Repo(search_parent_directories=True)
# git_repository_remote_link = (
#     git_repository.remotes[0]
#     .config_reader.get("url")
#     .replace("git@github.com:", "https://github.com/")
# )
# #latest_git_repository_tag = sorted
# #    git_repository.tags, key=lambda tag: tag.commit.committed_datetime
# #)[-1].name
# latest_git_repository_commit_shorted = git_repository.git.rev_parse(
#     git_repository.head.commit.hexsha, short=True
# )

# scheduler = AsyncIOScheduler()

import asyncio, logging, os, json, datetime as dt
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
from .config import settings
from .db import SessionLocal, Source, PostRaw, init_db
from sqlalchemy.exc import IntegrityError

log = logging.getLogger(__name__)

async def ensure_sources(session, client):
    for u in settings.SOURCE_USERNAMES:
        if not u: 
            continue
        s = session.query(Source).filter_by(username=u).first()
        if not s:
            # try fetch title
            try:
                entity = await client.get_entity(u)
                title = getattr(entity, "title", None) or getattr(entity, "first_name", None) or u
            except Exception:
                title = u
            s = Source(username=u, title=title, enabled=True, style_profile={})
            session.add(s)
            session.commit()

async def poll_sources():
    init_db()
    session = SessionLocal()
    client = TelegramClient(
        session=f"{settings.SESSION_DIR}/user_client",
        api_id=settings.TG_API_ID,
        api_hash=settings.TG_API_HASH,
        system_version="4.16.30-vx" # quieter
    )
    await client.connect()
    if not await client.is_user_authorized():
        log.error("User client not authorized. Run interactive login once to create session file in /sessions.")
        # In production, you can exec into the container and run a helper to login.
        return

    await ensure_sources(session, client)

    while True:
        try:
            sources = session.query(Source).filter_by(enabled=True).all()
            for src in sources:
                try:
                    async for msg in client.iter_messages(src.username, limit=20):
                        if not msg:
                            continue
                        text = msg.message or ""
                        media = None
                        if msg.photo:
                            media = {"type":"photo"}
                        pr = PostRaw(
                            source_id=src.id,
                            tg_post_id=msg.id,
                            message=text,
                            media=media,
                            posted_at=msg.date
                        )
                        session.add(pr)
                        try:
                            session.commit()
                        except IntegrityError:
                            session.rollback()
                except Exception as e:
                    log.warning(f"Error polling {src.username}: {e}")
            await asyncio.sleep(settings.POLL_INTERVAL_SEC)
        except Exception as e:
            log.error(f"poll loop error: {e}")
            await asyncio.sleep(10)
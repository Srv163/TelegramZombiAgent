import asyncio, logging, random, datetime as dt
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import select
from .config import settings
from .db import SessionLocal, init_db, PostRaw, PostZombie, PublishQueue, Source
from .transformer import zombify, safety_guard, is_too_similar
from .publisher import publish_text

log = logging.getLogger(__name__)

def rand_delay():
    mins = random.randint(settings.PUBLISH_DELAY_MIN, settings.PUBLISH_DELAY_MAX)
    return dt.timedelta(minutes=mins)

async def transform_new_raw():
    session = SessionLocal()
    q = session.query(PostRaw).filter(
        ~PostRaw.id.in_(session.query(PostZombie.raw_id))
    ).order_by(PostRaw.posted_at.desc()).limit(20)
    raws = q.all()
    for r in raws:
        src = session.query(Source).get(r.source_id)
        out = zombify(r.message or "", src.style_profile if src else None,
                      level=settings.ZOMBIE_LEVEL, length=settings.POST_LENGTH)
        flags = safety_guard(out)
        if flags.get("blocked"):
            continue
        if is_too_similar(r.message or "", out):
            continue
        z = PostZombie(raw_id=r.id, zombie_text=out, zombie_media=None,
                       zombie_level=settings.ZOMBIE_LEVEL, safety_flags=flags, similarity_score=0.0)
        session.add(z)
        session.commit()
        eta = (r.posted_at or dt.datetime.utcnow()) + rand_delay()
        pq = PublishQueue(zombie_id=z.id, scheduled_at=eta, status='queued')
        session.add(pq)
        session.commit()

async def publish_due():
    session = SessionLocal()
    now = dt.datetime.utcnow()
    q = session.query(PublishQueue).filter(
        PublishQueue.status=='queued',
        PublishQueue.scheduled_at <= now
    ).order_by(PublishQueue.scheduled_at.asc()).limit(10)
    items = q.all()
    for it in items:
        z = session.query(PostZombie).get(it.zombie_id)
        if not z: 
            continue
        msg_id = await publish_text(settings.TARGET_CHANNEL_ID, z.zombie_text)
        if msg_id:
            it.status='posted'
            it.result_msg_id = msg_id
            session.commit()
        else:
            it.status='failed'
            session.commit()

def setup_scheduler():
    init_db()
    scheduler = AsyncIOScheduler(timezone=settings.TIMEZONE)
    scheduler.add_job(transform_new_raw, 'interval', minutes=2)
    scheduler.add_job(publish_due, 'interval', seconds=30)
    scheduler.start()
    return scheduler
import datetime
from aihelp import generate_prompt
def create_journal_entry(db, journal_model, user_id, content, tag = None, source = 'web'):
    if not content or not str(content).strip():
        raise ValueError("Content cannot be empty.")
    content = content.strip()
    insight = generate_prompt(content)
    new_entry = journal_model(
        user_id=user_id,
        content=content,
        date = datetime.datetime.now().strftime("%B %d, %Y at %I:%M %p"),
        mood=insight.get("mood"),
        reflection=insight.get("reflection"),
        follow_up=insight.get("follow_up"),
        tag=tag,
        source=source
      
    )
    db.session.add(new_entry)
    db.session.commit()
    return new_entry

"""
Idempotent database seed script for the Learner Engagement Platform.
Loads sample learner data from CSV and fallback nudges from JSON.
"""

import asyncio
import csv
import json
import logging
import os
import sys
from pathlib import Path
from typing import List, Dict, Any
from uuid import uuid4

# Add backend to path for imports
backend_path = str(Path(__file__).parent.parent)
sys.path.insert(0, backend_path)

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..lib_db import AsyncSessionLocal, create_tables
from ..models import Learner, Nudge

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def load_learners_from_csv(session: AsyncSession, csv_path: str) -> int:
    """
    Load learners from CSV file with upsert logic by email.
    Returns the number of learners processed.
    """
    if not os.path.exists(csv_path):
        logger.error(f"CSV file not found: {csv_path}")
        return 0
    
    processed_count = 0
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for row in reader:
                try:
                    # Check if learner already exists by email
                    result = await session.execute(
                        select(Learner).where(Learner.email == row['email'])
                    )
                    existing_learner = result.scalar_one_or_none()
                    
                    if existing_learner:
                        # Update existing learner
                        existing_learner.name = row['name']
                        existing_learner.phone = row.get('phone', '')
                        existing_learner.program = row['program']
                        existing_learner.last_login = row.get('last_login', '')
                        existing_learner.completed_percent = float(row.get('completed_percent', 0))
                        existing_learner.avg_quiz_score = float(row.get('avg_quiz_score', 0))
                        existing_learner.consecutive_missed_sessions = int(row.get('consecutive_missed_sessions', 0))
                        existing_learner.risk_score = float(row.get('risk_score', 0))
                        existing_learner.risk_label = row.get('risk_label', 'low')
                        
                        logger.info(f"Updated existing learner: {row['email']}")
                    else:
                        # Create new learner
                        learner = Learner(
                            id=row.get('id', str(uuid4())),
                            name=row['name'],
                            email=row['email'],
                            phone=row.get('phone', ''),
                            program=row['program'],
                            last_login=row.get('last_login', ''),
                            completed_percent=float(row.get('completed_percent', 0)),
                            avg_quiz_score=float(row.get('avg_quiz_score', 0)),
                            consecutive_missed_sessions=int(row.get('consecutive_missed_sessions', 0)),
                            risk_score=float(row.get('risk_score', 0)),
                            risk_label=row.get('risk_label', 'low')
                        )
                        session.add(learner)
                        logger.info(f"Created new learner: {row['email']}")
                    
                    processed_count += 1
                    
                except Exception as e:
                    logger.error(f"Error processing learner row {row}: {e}")
                    continue
            
            await session.commit()
            logger.info(f"Successfully processed {processed_count} learners from CSV")
            
    except Exception as e:
        logger.error(f"Error reading CSV file {csv_path}: {e}")
        await session.rollback()
        return 0
    
    return processed_count

async def load_fallback_nudges(session: AsyncSession, json_path: str) -> int:
    """
    Load fallback nudges from JSON file as orphan records (no learner_id).
    Returns the number of nudges processed.
    """
    if not os.path.exists(json_path):
        logger.error(f"JSON file not found: {json_path}")
        return 0
    
    processed_count = 0
    
    try:
        with open(json_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            
            # Expect data to be a list of nudge templates
            nudges_data = data if isinstance(data, list) else data.get('nudges', [])
            
            for nudge_data in nudges_data:
                try:
                    # Check if this fallback nudge already exists by content
                    result = await session.execute(
                        select(Nudge).where(
                            Nudge.content == nudge_data['content'],
                            Nudge.learner_id == 'fallback'
                        )
                    )
                    existing_nudge = result.scalar_one_or_none()
                    
                    if not existing_nudge:
                        # Create new fallback nudge as orphan record
                        nudge = Nudge(
                            id=nudge_data.get('id', str(uuid4())),
                            learner_id='fallback',  # Special ID for fallback nudges
                            channel=nudge_data.get('channel', 'in-app'),
                            type=nudge_data.get('type', 'motivation'),
                            content=nudge_data['content'],
                            gpt_prompt_version=nudge_data.get('prompt_version', 'fallback'),
                            gpt_fallback=True,
                            status='template'
                        )
                        session.add(nudge)
                        logger.info(f"Created fallback nudge: {nudge_data.get('type', 'unknown')}")
                        processed_count += 1
                    else:
                        logger.info(f"Fallback nudge already exists: {nudge_data.get('type', 'unknown')}")
                    
                except Exception as e:
                    logger.error(f"Error processing nudge data {nudge_data}: {e}")
                    continue
            
            await session.commit()
            logger.info(f"Successfully processed {processed_count} fallback nudges from JSON")
            
    except Exception as e:
        logger.error(f"Error reading JSON file {json_path}: {e}")
        await session.rollback()
        return 0
    
    return processed_count

async def seed_database() -> None:
    """
    Main seeding function that orchestrates the entire process.
    """
    logger.info("Starting database seeding process...")
    
    try:
        # Ensure tables exist
        await create_tables()
        logger.info("Database tables created/verified")
        
        # Get paths relative to project root
        project_root = Path(__file__).parent.parent.parent
        csv_path = project_root / "prompts" / "mock_learners.csv"
        json_path = project_root / "prompts" / "fallback_nudges.json"
        
        async with AsyncSessionLocal() as session:
            # Load learners from CSV
            learners_count = await load_learners_from_csv(session, str(csv_path))
            
            # Load fallback nudges from JSON
            nudges_count = await load_fallback_nudges(session, str(json_path))
            
            logger.info(f"Seeding completed successfully!")
            logger.info(f"- Processed {learners_count} learners")
            logger.info(f"- Processed {nudges_count} fallback nudges")
            
    except Exception as e:
        logger.error(f"Database seeding failed: {e}")
        raise

if __name__ == "__main__":
    """
    Run the seed script directly.
    Usage: python backend/scripts/seed.py
    """
    try:
        asyncio.run(seed_database())
        logger.info("Seed script completed successfully")
    except Exception as e:
        logger.error(f"Seed script failed: {e}")
        sys.exit(1)
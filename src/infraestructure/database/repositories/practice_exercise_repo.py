from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, func, between, desc
from datetime import datetime, timedelta, timezone

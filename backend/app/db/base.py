from sqlalchemy.orm import declarative_base

Base = declarative_base()

from app.models.inspector import Inspector
from app.models.inspection import Inspection
from app.models.inspection_image import InspectionImage
from app.models.structured_data import StructuredData
from app.models.checklist import Checklist
from app.models.evaluation import Evaluation
from app.models.rule_evaluation import RuleEvaluation
from app.models.report import Report

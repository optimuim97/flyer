from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


quotation_features = db.Table(
    "quotation_features",
    db.Column("quotation_id", db.Integer, db.ForeignKey("quotations.id", ondelete="CASCADE"), primary_key=True),
    db.Column("feature_id", db.Integer, db.ForeignKey("features.id", ondelete="CASCADE"), primary_key=True),
)


class ProjectType(db.Model):
    __tablename__ = "project_types"
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(80), unique=True, nullable=False)
    name = db.Column(db.String(160), nullable=False)
    description = db.Column(db.Text)
    icon = db.Column(db.String(40))
    sort_order = db.Column(db.Integer, default=0)

    def to_dict(self):
        return {
            "id": self.id,
            "slug": self.slug,
            "name": self.name,
            "description": self.description,
            "icon": self.icon,
        }


class Feature(db.Model):
    __tablename__ = "features"
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(80), unique=True, nullable=False)
    name = db.Column(db.String(160), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(80))
    sort_order = db.Column(db.Integer, default=0)

    def to_dict(self):
        return {
            "id": self.id,
            "slug": self.slug,
            "name": self.name,
            "description": self.description,
            "category": self.category,
        }


class Quotation(db.Model):
    __tablename__ = "quotations"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(160), nullable=False)
    email = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(40))
    company = db.Column(db.String(200))
    project_type_id = db.Column(db.Integer, db.ForeignKey("project_types.id"))
    description = db.Column(db.Text)
    budget = db.Column(db.String(80))
    deadline = db.Column(db.String(80))
    status = db.Column(db.String(40), default="nouveau", nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    project_type = db.relationship("ProjectType")
    features = db.relationship("Feature", secondary=quotation_features, lazy="joined")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "company": self.company,
            "project_type": self.project_type.to_dict() if self.project_type else None,
            "description": self.description,
            "budget": self.budget,
            "deadline": self.deadline,
            "status": self.status,
            "features": [f.to_dict() for f in self.features],
            "created_at": self.created_at.isoformat(),
        }

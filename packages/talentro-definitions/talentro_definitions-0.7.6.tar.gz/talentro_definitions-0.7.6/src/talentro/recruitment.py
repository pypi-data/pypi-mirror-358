from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class TalentroVacancyLocation:
    street: str = ""
    house_number: str = ""
    zip_code: str = ""
    city: str = ""
    state: str = ""
    country: str = ""


@dataclass
class TalentroSalary:
    min: float = 0.0
    max: float = 0.0
    currency: str = "EUR"
    interval: str = "Month"


@dataclass
class TalentroHours:
    min: int = 0
    max: int = 40
    fte: float = 1.0


@dataclass
class TalentroContactDetails:
    first_name: str = ""
    last_name: str = ""
    phone_number: str = ""
    email: str = ""
    role: str = ""


@dataclass
class TalentroCandidate:
    id: str
    email: str = ""
    first_name: str = ""
    last_name: str = ""
    phone_number: str = ""
    hashed_email: str = ""
    cv: str = ""
    motivation_letter: str = ""
    linked_in: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = None


@dataclass
class TalentroVacancy:
    reference_number: str
    name: str
    description: str
    date: datetime
    url: str = ""
    company: str = ""
    recruiter: TalentroContactDetails = field(default_factory=TalentroContactDetails)
    location: TalentroCandidate = field(default_factory=TalentroVacancyLocation)
    salary: TalentroSalary = field(default_factory=TalentroSalary)
    hours: TalentroHours = field(default_factory=TalentroHours)
    category: [str] = ""
    experience: [str] = ""
    education: [str] = ""


@dataclass
class TalentroApplication:
    id: str
    status: str
    source: str
    candidate: TalentroCandidate = field(default_factory=TalentroCandidate)
    vacancy: TalentroVacancy = field(default_factory=TalentroVacancy)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = None
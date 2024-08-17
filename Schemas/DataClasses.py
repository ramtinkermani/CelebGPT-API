from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from enum import Enum

def entityclass(cls):
    """
    Custom Decorator to mark Entity Classes whose schema will be sent to LLM
    to return the result with that schema
    """
    cls.is_custom_class = True  # Add an attribute to mark the class
    return cls

@dataclass
class Gender(Enum):
    MALE = 'Male'
    FEMALE = 'Female'

@dataclass
class CelebTypes(Enum):
    ACTOR = 'Actor'
    DIRECTOR = 'Director'
    PRODUCER = 'Producer'
    ENTREPRENEUR = 'Entrepreneur'
    MUSICIAN = 'Musician'
    SINGER = 'Singer'
    POLITICIAN = 'Politician'
    ATHLETE = 'Athlete'
    WRITER = 'Writer'
    COMEDIAN = 'Comedian'
    MODEL = 'Model'
    DANCER = 'Dancer'
    INFLUENCER = 'Influencer'
    PHILANTHROPIST = 'Philanthropist'
    SCIENTIST = 'Scientist'
    VISUAL_ARTIST = 'VisualArtist'
    FASHION_DESIGNER = 'FashionDesigner'
    CHEF = 'Chef'
    JOURNALIST = 'Journalist'
    MOVIE = "Movie"
    TV_SHOW = "TvShow"
    BOOK = "Book"

@dataclass
class Relationship:
    partner: str
    start_year: int
    end_year: int


@dataclass
class Person:
    firstname: str
    lastname: str
    birthdate: datetime
    gender: Gender
    birth_country: str
    birth_state: str
    birth_city: str
    residence_country: str
    residence_state: str
    residence_city: str
    known_for: str
    # celebType: CelebTypes
    relationships: List[str]


# Well-Known People Types
@entityclass
@dataclass
class Actor(Person):
    movies: List[str]
    tv_shows: List[str]
    imdb_id: str


@entityclass
@dataclass
class Director(Person):
    films_directed: List[str]
    tv_shows: List[str]


@entityclass
@dataclass
class Producer(Person):
    films_produced: List[str]
    tv_series: List[str]


@entityclass
@dataclass
class Entrepreneur(Person):
    companies_founded: List[str]
    industries_involved: List[str]

@entityclass
@dataclass
class Musician(Person):
    albums: List[str]
    instruments_played: List[str]


@entityclass
@dataclass
class Singer(Person):
    albums: List[str]
    genres: List[str]


@entityclass
@dataclass
class Politician(Person):
    office_positions: List[str]
    policies: List[str]


@entityclass
@dataclass
class Athlete(Person):
    sports: List[str]
    teams: List[str]
    championships_won: List[str]


@entityclass
@dataclass
class Writer(Person):
    books_published: List[str]
    genres: List[str]


@entityclass
@dataclass
class Comedian(Person):
    comedy_specials: List[str]
    tours: List[str]


@entityclass
@dataclass
class Model(Person):
    modeling_agencies: List[str]
    major_campaigns: List[str]


@entityclass
@dataclass
class Dancer(Person):
    dance_styles: List[str]
    performances: List[str]


@entityclass
@dataclass
class Influencer(Person):
    social_media_channels: List[str]
    major_endorsements: List[str]


@entityclass
@dataclass
class Philanthropist(Person):
    organizations_supported: List[str]
    causes_championed: List[str]


@entityclass
@dataclass
class Scientist(Person):
    field_of_study: List[str]
    major_contributions: List[str]


@entityclass
@dataclass
class VisualArtist(Person):
    mediums_used: List[str]
    exhibitions: List[str]


@entityclass
@dataclass
class FashionDesigner(Person):
    fashion_labels: List[str]
    signature_styles: List[str]


@entityclass
@dataclass
class Chef(Person):
    restaurants_owned: List[str]
    culinary_styles: List[str]


@entityclass
@dataclass
class Journalist(Person):
    publications_worked_for: List[str]
    major_stories_covered: List[str]


# Well-Known Entity Types
@entityclass
@dataclass
class Movie:
    genre: str
    year: int
    director: List[str]
    writer: List[str]
    cast: List[str]
    music: List[str]
    imdb_id: str

@entityclass
@dataclass
class TvShow:
    genre: str
    year_start: int
    year_end: int
    num_seasons: int
    director: List[str]
    writer: List[str]
    cast: List[str]
    music: List[str]
    imdb_id: str

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

# Add "Base" inheritence to each class when working on it to allow running
# `alembic revision --autogenerate` to take into account the model


class MasterWord(Base):
    """Class to represent the master word table"""

    # Table name
    __tablename__ = "master_words"

    # Columns
    id = Column(Integer, primary_key=True, nullable=False)
    to_complete = Column(String, nullable=False, unique=True)
    solution = Column(String, nullable=False)
    dialogue = Column(String, nullable=False)
    image_url= Column(String, nullable=False)

    # Relationships
    jumbles = relationship(
        "Jumble", back_populates="master_word"
        )  # query "MasterWord.jumbles"


class Jumble(Base):
    """Class to represent the jumbles table"""

    # Table name
    __tablename__ = "jumbles"

    # Columns
    id = Column(Integer, primary_key=True, nullable=False)
    master_word_id = Column(
        Integer, ForeignKey("master_words.id"), nullable=False
        )

    # Relationships
    master_word = relationship(
        "MasterWord", back_populates="jumbles"
        )  # query "Jumble.master_word"
    jumble_options = relationship(
        "JumbleOption", back_populates="jumble"
        )  # query "Jumble.jumble_options"


class JumbleOption(Base):
    """Class to represent the jumble options table"""

    # Table name
    __tablename__ = "jumble_options"

        # Columns
    id = Column(Integer, primary_key=True, nullable=False)
    jumble_id = Column(
        Integer, ForeignKey("jumbles.id"), nullable=False
        )
    # master_word_id = Column(
    #     Integer, ForeignKey("master_words.id"), nullable=False
    #     )
    word= Column(String, nullable=False)
    score= Column(Integer, nullable=False)
    defs= Column(String, nullable=True)
    level= Column(String, nullable=False)
    placeholder= Column(String, nullable=False)

    # Relationships
    jumble = relationship(
        "Jumble", back_populates="jumble_options"
        )  # query "JumbleOption.jumble"
